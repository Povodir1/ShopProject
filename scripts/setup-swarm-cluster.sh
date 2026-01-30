#!/bin/bash

# Docker Swarm 3-Node Cluster Setup Script
# Этот скрипт помогает настроить 3-нодовый Docker Swarm кластер

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода colored сообщений
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, запущен ли на Linux
check_os() {
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "Этот скрипт предназначен для Linux систем"
        exit 1
    fi
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен"
        print_info "Установка Docker..."

        # Установка Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER

        print_success "Docker установлен"
        print_warning "Выйдите из системы и войдите снова для применения изменений"
        exit 0
    fi
    print_success "Docker уже установлен: $(docker --version)"
}

# Инициализация Manager ноды
init_manager() {
    print_info "Инициализация Manager ноды..."

    # Получить IP адрес
    MANAGER_IP=$(hostname -I | awk '{print $1}')

    print_info "Используем IP адрес: $MANAGER_IP"
    read -p "Продолжить с этим IP? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        read -p "Введите IP адрес: " MANAGER_IP
    fi

    # Инициализация Swarm
    docker swarm init --advertise-addr $MANAGER_IP

    print_success "Swarm кластер инициализирован"

    # Получить worker токен
    WORKER_TOKEN=$(docker swarm join-token worker -q)

    # Сохранить токен в файл
    cat > worker-join-command.sh <<EOF
#!/bin/bash
docker swarm join --token $WORKER_TOKEN $MANAGER_IP:2377
EOF
    chmod +x worker-join-command.sh

    print_success "Worker токен сохранен в worker-join-command.sh"
    print_info "Передайте этот файл на worker ноды и выполните его"

    # Настроить лейблы
    NODE_NAME=$(hostname)
    docker node update --label-add app.type=app $NODE_NAME
    docker node update --label-add db.type=database $NODE_NAME

    print_success "Лейблы настроены для Manager ноды"
}

# Добавление Worker ноды
join_worker() {
    print_info "Режим присоединения Worker ноды"

    if [ ! -f "worker-join-command.sh" ]; then
        print_error "Файл worker-join-command.sh не найден"
        print_info "Скопируйте этот файл с Manager ноды"
        exit 1
    fi

    # Выполнить команду join
    bash worker-join-command.sh

    print_success "Worker нода добавлена в кластер"

    # Получить имя ноды
    NODE_NAME=$(hostname)

    # Настроить лейбл (только app.type, так как worker ноды не содержат БД)
    print_info "Настройка лейблов для worker ноды..."
    print_warning "Выполните следующую команду на Manager ноде:"
    echo "docker node update --label-add app.type=app $NODE_NAME"
}

# Развертывание стека
deploy_stack() {
    print_info "Развертывание стека..."

    if [ ! -f "docker-compose.swarm.yml" ]; then
        print_error "Файл docker-compose.swarm.yml не найден"
        exit 1
    fi

    # Проверить наличие .env.swarm
    if [ ! -f ".env.swarm" ]; then
        print_error "Файл .env.swarm не найден"
        exit 1
    fi

    # Собрать образы
    print_info "Сборка Docker образов..."
    docker build -t shop-frontend:latest ./frontend
    docker build -t shop-backend:latest ./backend

    # Развернуть стек
    print_info "Деплой стека..."
    export $(cat .env.swarm | grep -v '^#' | xargs)
    docker stack deploy -c docker-compose.swarm.yml shop

    print_success "Стек развернут"
    print_info "Проверьте статус: docker service ls"
}

# Проверка статуса кластера
check_status() {
    print_info "Статус Swarm кластера:"
    echo ""
    docker node ls
    echo ""
    print_info "Сервисы:"
    docker service ls
    echo ""
    print_info "Распределение контейнеров:"
    docker service ps shop --no-trunc
}

# Главное меню
show_menu() {
    echo ""
    echo "=========================================="
    echo "  Docker Swarm 3-Node Cluster Setup"
    echo "=========================================="
    echo "1. Инициализировать Manager ноду"
    echo "2. Присоединить Worker ноду"
    echo "3. Развернуть стек"
    echo "4. Проверить статус кластера"
    echo "5. Выход"
    echo "=========================================="
    read -p "Выберите опцию [1-5]: " choice

    case $choice in
        1)
            check_os
            check_docker
            init_manager
            ;;
        2)
            check_os
            check_docker
            join_worker
            ;;
        3)
            check_docker
            deploy_stack
            ;;
        4)
            check_docker
            check_status
            ;;
        5)
            print_info "Выход..."
            exit 0
            ;;
        *)
            print_error "Неверный выбор"
            ;;
    esac
}

# Главная функция
main() {
    # Проверка прав root
    if [[ $EUID -ne 0 ]] && ! groups | grep -q docker; then
        print_error "Этот скрипт должен быть запущен с правами docker или root"
        print_info "Добавьте пользователя в группу docker: sudo usermod -aG docker \$USER"
        exit 1
    fi

    # Запуск меню
    while true; do
        show_menu
    done
}

# Запуск
main
