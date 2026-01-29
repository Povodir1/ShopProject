# План контейнеризации ShopProject для Docker Swarm

## Обзор

Контейнеризация веб-приложения с развертыванием в Docker Swarm кластере из 3 серверов для повышения отказоустойчивости.

**Архитектура приложения:**
- **Frontend**: Vanilla JavaScript (статические файлы)
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (на отдельном сервере, вне Swarm)

**Инфраструктура:**
- **3 сервера**: 1 manager + 2 workers
- **Registry**: Локальный registry внутри Swarm
- **Load Balancer**: Nginx сервисы в Swarm

---

## Структура файлов для создания

```
/home/pavel/ShopProject/
├── docker/
│   ├── frontend/
│   │   └── Dockerfile                    # Контейнер для фронтенда
│   ├── backend/
│   │   ├── Dockerfile                    # Контейнер для бэкенда
│   │   └── entrypoint.sh                 # Скрипт запуска с миграциями
│   ├── swarm/
│   │   └── docker-stack.yml              # Конфигурация Swarm стека
│   ├── compose/
│   │   └── docker-compose.yml            # Для локального тестирования
│   └── nginx/
│       ├── nginx.conf                    # Для локального тестирования
│       └── nginx-swarm.conf              # Для Swarm продакшена
├── frontend/
│   └── core/config.js                    # ИЗМЕНИТЬ: API URL для Swarm
├── backend/
│   └── core/config.py                    # Уже поддерживает env переменные
└── .env.swarm                            # Переменные окружения для Swarm
```

---

## Шаг 1: Создание Dockerfile для сервисов

### 1.1 Frontend Dockerfile
**Файл**: `docker/frontend/Dockerfile`

```dockerfile
# Multi-stage build
FROM node:18-alpine AS builder
WORKDIR /app
COPY frontend/ .

# Production stage - nginx для статики
FROM nginx:1.25-alpine
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app /usr/share/nginx/html

# Non-root user
RUN addgroup -g 1001 -S shop && \
    adduser -S -D -H -u 1001 -h /usr/share/nginx/html -s /sbin/nologin -G shop -g shop shop && \
    chown -R shop:shop /usr/share/nginx/html

USER shop
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### 1.2 Backend Dockerfile
**Файл**: `docker/backend/Dockerfile`

```dockerfile
# Builder stage
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH=/root/.local/bin:$PATH
RUN apt-get update && apt-get install -y postgresql-client curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY backend/ .
RUN mkdir -p /app/logs /app/tmp && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.3 Backend Entrypoint
**Файл**: `docker/backend/entrypoint.sh`

```bash
#!/bin/bash
set -e

# Ждем готовности базы данных
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

# Запускаем миграции только на лидере
if [ "$RUN_MIGRATIONS" = "true" ]; then
    alembic upgrade head
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-4}
```

---

## Шаг 2: Конфигурация Nginx

### 2.1 Nginx для Swarm
**Файл**: `docker/nginx/nginx-swarm.conf`

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # Upstream backend servers (Swarm service discovery)
    upstream backend {
        least_conn;
        server backend:8000 max_fails=3 fail_timeout=30s;
    }

    # Upstream frontend servers (Swarm service discovery)
    upstream frontend {
        least_conn;
        server frontend:8080 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API proxy to backend
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://backend;
            proxy_http_version 1.1;

            # Headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            # Buffering
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;

            # Error handling
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        }

        # Frontend static files
        location / {
            limit_req zone=general_limit burst=50 nodelay;

            proxy_pass http://frontend;
            proxy_http_version 1.1;

            # Headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Error pages
        error_page 502 503 504 /50x.html;
        location = /50x.html {
            return 503 "Service temporarily unavailable";
        }
    }
}
```

---

## Шаг 3: Docker Swarm Stack конфигурация

### 3.1 Основной stack файл
**Файл**: `docker/swarm/docker-stack.yml`

```yaml
version: '3.8'

services:
  # Backend API - 3 реплики
  backend:
    image: localhost:5000/shop-backend:${TAG:-latest}
    environment:
      DB_HOST: ${DB_HOST}
      DB_PORT: ${DB_PORT:-5432}
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: /run/secrets/db_password
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
      DEBUG: "false"
      RUN_MIGRATIONS: "false"
    networks:
      - shop-network
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        max_attempts: 3
      placement:
        constraints:
          - node.labels.backend == true
    secrets:
      - db_password

  # Frontend - 2 реплики
  frontend:
    image: localhost:5000/shop-frontend:${TAG:-latest}
    networks:
      - shop-network
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        max_attempts: 3
      placement:
        constraints:
          - node.labels.frontend == true

  # Nginx Load Balancer - 2 реплики на manager-ах
  nginx:
    image: nginx:1.25-alpine
    ports:
      - target: 80
        published: 80
        protocol: tcp
        mode: host
    networks:
      - shop-network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.labels.lb == true
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf

  # Локальный registry
  registry:
    image: registry:2
    ports:
      - target: 5000
        published: 5000
        protocol: tcp
        mode: ingress
    networks:
      - shop-network
    deploy:
      placement:
        constraints:
          - node.role == manager
    volumes:
      - registry_data:/var/lib/registry

networks:
  shop-network:
    driver: overlay
    driver_opts:
      encrypted: "true"

secrets:
  db_password:
    external: true

configs:
  nginx_config:
    external: true

volumes:
  registry_data:
```

### 3.2 Переменные окружения
**Файл**: `.env.swarm`

```env
# Registry
TAG=v1.0.0

# Database (внешний сервер)
DB_HOST=192.168.1.XXX  # IP сервера с БД
DB_PORT=5432
DB_NAME=e_shop
DB_USER=postgres

# Allowed Origins
ALLOWED_ORIGINS=http://IP_MANAGER_NODE,https://shop.yourdomain.com
```

---

## Шаг 4: Модификация кода приложения

### 4.1 Frontend config.js
**Файл**: `frontend/core/config.js`

**ИЗМЕНИТЬ**:
```javascript
// Было:
apiBaseUrl: 'http://localhost:8000/api',

// Стать:
apiBaseUrl: window.location.hostname === 'localhost'
  ? 'http://localhost:8000/api'
  : '/api',  // Проксируется через nginx
```

**Backend** не требует изменений - уже использует переменные окружения.

---

## Шаг 5: Развертывание

### 5.1 Инициализация Swarm (на первом сервере)

```bash
# Manager node
docker swarm init --advertise-addr <IP_MANAGER_1>

# Получить токены для join
docker swarm join-token manager
docker swarm join-token worker
```

### 5.2 Добавление серверов в кластер

```bash
# На втором сервере (manager)
docker swarm join --token <MANAGER_TOKEN> <IP_MANAGER_1>:2377

# На третьем сервере (worker)
docker swarm join --token <WORKER_TOKEN> <IP_MANAGER_1>:2377
```

### 5.3 Настройка меток на нодах

```bash
# Manager 1 - также load balancer
docker node update --label-add lb=true manager-1

# Manager 2 - также load balancer
docker node update --label-add lb=true manager-2

# Worker 1 - frontend + backend
docker node update --label-add frontend=true worker-1
docker node update --label-add backend=true worker-1

# Worker 2 - backend (остается место для будущего масштабирования)
docker node update --label-add backend=true worker-2
```

### 5.4 Создание secrets и configs

```bash
# Пароль базы данных
echo "your_secure_password" | docker secret create db_password -

# Nginx конфиг
docker config create nginx_config docker/nginx/nginx-swarm.conf
```

### 5.5 Сборка и публикация образов

```bash
# Frontend
docker build -f docker/frontend/Dockerfile -t localhost:5000/shop-frontend:v1.0.0 .
docker push localhost:5000/shop-frontend:v1.0.0

# Backend
docker build -f docker/backend/Dockerfile -t localhost:5000/shop-backend:v1.0.0 .
docker push localhost:5000/shop-backend:v1.0.0
```

### 5.6 Деплой стека

```bash
export $(cat .env.swarm | xargs)
docker stack deploy -c docker/swarm/docker-stack.yml shop
```

---

## Шаг 6: Проверка и верификация

### 6.1 Проверка сервисов

```bash
# Список сервисов
docker service ls

# Статус реплик
docker service ps shop_frontend
docker service ps shop_backend
docker service ps shop_nginx

# Логи
docker service logs shop_backend --tail 50 -f
```

### 6.2 Тестирование

1. **Доступность фронтенда**: `http://<IP_MANAGER_NODE>/`
2. **API endpoint**: `http://<IP_MANAGER_NODE>/api/docs`
3. **Health check**: `http://<IP_MANAGER_NODE>/health`
4. **Тест отказоустойчивости**: остановить один backend контейнер

---

## Распределение сервисов по 3 серверам

### Сервер 1 (Manager-1 + LB)
- Manager role
- Nginx (port 80)
- Registry (port 5000)

### Сервер 2 (Manager-2 + LB)
- Manager role
- Nginx (port 80)

### Сервер 3 (Worker)
- Backend replica
- Frontend replica

### Внешний сервер
- PostgreSQL (не в Swarm)

---

## Масштабирование

```bash
# Масштабировать backend до 5 реплик
docker service scale shop_backend=5

# Масштабировать frontend до 3 реплик
docker service scale shop_frontend=3
```

---

## Обновление приложения

```bash
# Собрать новую версию
docker build -f docker/backend/Dockerfile -t localhost:5000/shop-backend:v1.1.0 .
docker push localhost:5000/shop-backend:v1.1.0

# Обновить сервис (rolling update)
docker service update --image localhost:5000/shop-backend:v1.1.0 shop_backend

# Откат при проблемах
docker service rollback shop_backend
```

---

## Критические файлы для создания/изменения

| Файл | Действие | Приоритет |
|------|----------|-----------|
| `docker/frontend/Dockerfile` | Создать | Критичный |
| `docker/backend/Dockerfile` | Создать | Критичный |
| `docker/backend/entrypoint.sh` | Создать | Критичный |
| `docker/swarm/docker-stack.yml` | Создать | Критичный |
| `docker/nginx/nginx-swarm.conf` | Создать | Критичный |
| `frontend/core/config.js` | Изменить | Критичный |
| `.env.swarm` | Создать | Критичный |
| `docker/compose/docker-compose.yml` | Создать | Опционально (для локального тестирования) |
| `docker/nginx/nginx.conf` | Создать | Опционально (для локального тестирования) |

---

## Проверочный список

**Подготовка:**
- [ ] Установлен Docker на всех 3 серверах
- [ ] Настроен PostgreSQL на внешнем сервере
- [ ] Созданы все Dockerfile
- [ ] Создан docker-stack.yml
- [ ] Создан nginx-swarm.conf
- [ ] Изменен frontend/core/config.js
- [ ] Создан .env.swarm с актуальными IP

**Развертывание:**
- [ ] Инициализирован Swarm (1 manager + 2 workers)
- [ ] Настроены метки на нодах
- [ ] Созданы secrets (db_password)
- [ ] Созданы configs (nginx_config)
- [ ] Собраны и запушены образы
- [ ] Деплой стека выполнен

**Проверка:**
- [ ] Все сервисы в статусе running
- [ ] Фронтенд доступен через nginx
- [ ] API отвечает на запросы
- [ ] База данных подключена
- [ ] Health checks проходят
- [ ] Тест failover успешен

---

## Примечания

1. **База данных**: Останется на одном сервере, не в контейнере (по требованию)
2. **Registry**: Локальный registry потребует ~500MB диска и будет доступен только внутри сети
3. **Миграции БД**: Выполняются только на одном контейнере (через переменную RUN_MIGRATIONS)
4. **Health checks**: Автоматический перезапуск при падении сервисов
5. **Rolling updates**: Нулевой простой при обновлениях
6. **Rollback**: Мгновенный откат к предыдущей версии
