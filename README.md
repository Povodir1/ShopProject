<<<<<<< HEAD
# 🛒 ShopProject

Интернет-магазин с модульной архитектурой. Backend на FastAPI + Frontend на Vanilla JS с Clean Architecture внутри каждого модуля.

---

## Структура проекта

```
ShopProject/
├── backend/                    # FastAPI приложение
│   ├── core/                  # Ядро (конфигурация, БД, DI)
│   │   ├── config.py          # Конфигурация приложения
│   │   ├── database.py        # SQLAlchemy + подключение к БД
│   │   └── dependencies.py    # Dependency Injection
│   │
│   ├── modules/               # Модули доменной области
│   │   ├── catalog/           # Каталог товаров
│   │   └── cart/              # Корзина покупок
│   │
│   ├── alembic/               # Миграции БД
│   ├── main.py                # Точка входа приложения
│   └── requirements.txt       # Зависимости Python
│
├── frontend/                  # Vanilla JS приложение
│   ├── core/                  # Ядро фронтенда
│   │   ├── config.js          # Конфигурация
│   │   ├── event-bus.js       # Event Bus для модулей
│   │   └── shared/            # Общие утилиты (api.js, formatters.js, storage.js)
│   │
│   ├── modules/               # Модули фронтенда
│   │   ├── catalog/           # Каталог товаров
│   │   └── cart/              # Корзина покупок
│   │
│   ├── styles/                # Общие стили
│   ├── index.html             # Точка входа приложения
│   └── DESIGN_SYSTEM_QUICK_REFERENCE.md  # Дизайн-система KOI
│
├── ARCHITECTURE_RULES.md      # Правила архитектуры для AI
└── README.md                  # Этот файл
```

---

## Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - веб-фреймework
- **SQLAlchemy 2.0** - ORM
- **Alembic** - миграции БД
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных

### Frontend
- **HTML5, CSS3** - разметка и стили
- **JavaScript (ES6+)** - логика приложения
- **Event Bus** - модульная коммуникация
- **Дизайн-система KOI** - темная тема

---

## Установка и запуск

### Требования
- Python 3.11+
- PostgreSQL 14+
- Современный браузер

### Backend

```bash
cd backend

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env: DATABASE_URL

# Миграции БД
alembic upgrade head

# Запуск (режим разработки)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API документация: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Простое запуска через HTTP сервер
python -m http.server 3000

# Или через npx serve
npx serve . -p 3000
```

Приложение будет доступно по адресу: http://localhost:3000

---

## Модули системы

### 📦 Catalog (Каталог товаров)

**Backend** ([`backend/modules/catalog/`](backend/modules/catalog/)):
- `domain/` - сущности Product, Category
- `application/` - use cases для работы с товарами
- `infrastructure/` - SQLAlchemy модели, репозитории
- `presentation/` - FastAPI routes

**Frontend** ([`frontend/modules/catalog/`](frontend/modules/catalog/)):
- `domain/` - entities (Product, Category, Filter)
- `application/` - use cases (getProducts, getProductDetails, searchProducts)
- `infrastructure/` - API клиенты (product.api.js, category.api.js)
- `presentation/` - HTML страницы, компоненты, контроллеры

**API Endpoints:**
```
GET    /api/products              - Список товаров
GET    /api/products/search       - Поиск товаров
GET    /api/products/:id          - Детали товара
GET    /api/categories            - Список категорий
GET    /api/categories/:id        - Детали категории
```

---

### 🛒 Cart (Корзина покупок)

**Backend** ([`backend/modules/cart/`](backend/modules/cart/)):
- `domain/` - сущности Cart, CartItem
- `application/` - use cases для управления корзиной
- `infrastructure/` - SQLAlchemy модели, репозитории
- `presentation/` - FastAPI routes

**Frontend** ([`frontend/modules/cart/`](frontend/modules/cart/)):
- `domain/` - entities (Cart, CartItem)
- `application/` - use cases (getCart, addItem, removeItem, updateQuantity)
- `infrastructure/` - API клиент, LocalStorage
- `presentation/` - HTML страница, компоненты, контроллеры

**API Endpoints:**
```
GET    /api/cart                  - Получить корзину
POST   /api/cart/items            - Добавить товар
PUT    /api/cart/items/:id        - Изменить количество
DELETE /api/cart/items/:id        - Удалить товар
DELETE /api/cart                  - Очистить корзину
```

---

## Архитектура

### Модульная архитектура

Модули **НЕ** импортируют друг друга напрямую. Коммуникация через:
- **Backend**: Event Bus (в планах)
- **Frontend**: Event Bus (реализован в [`core/event-bus.js`](frontend/core/event-bus.js))

### Clean Architecture внутри модулей

```
Presentation → Application → Domain ← Infrastructure
                                ↑
                        НЕ ЗАВИСИТ НИ ОТ КОГО!
```

**Domain**: чистая бизнес-логика (без зависимостей)
**Application**: use cases (сценарии использования)
**Infrastructure**: внешние зависимости (API, БД, Storage)
**Presentation**: UI / API routes

Подробнее: [`ARCHITECTURE_RULES.md`](ARCHITECTURE_RULES.md)

---

## Дизайн-система KOI

Проект использует дизайн-систему **KOI** с тёмной темой.

### Основные цвета

```css
/* Фоны */
--bg-primary: #0f172a    /* Основной фон */
--bg-card: #1e293b       /* Карточки */
--bg-input: #334155      /* Инпуты */

/* Текст */
--text-primary: #f1f5f9  /* Основной текст */
--text-secondary: #e2e8f0

/* Акценты */
--accent-primary: #7c3aed /* Фиолетовый */
```

### Компоненты

- **Кнопки**: Primary (градиент), Secondary (граница), Danger, Ghost
- **Инпуты**: Small (32px), Medium (40px), Large (48px)
- **Бейджи**: Success, Error, Warning, Info, Neutral

Подробнее: [`frontend/DESIGN_SYSTEM_QUICK_REFERENCE.md`](frontend/DESIGN_SYSTEM_QUICK_REFERENCE.md)

---

## Event Bus (Frontend)

Коммуникация между модулями без прямых зависимостей:

```javascript
import eventBus from '/core/event-bus.js';

// Публикация
eventBus.publish('cart:item-added', { productId: 123, quantity: 2 });

// Подписка
const unsubscribe = eventBus.subscribe('cart:item-added', (data) => {
  console.log('Добавлен товар:', data.productId);
});

// Отписка
unsubscribe();
```

---

## Разработка

### Правила

- Модули общаются только через Event Bus (фронтенд) или API (бэкенд)
- Domain слой НЕ зависит от внешних библиотек
- Соблюдать принципы SOLID
- README.md в каждом модуле с описанием


## Документация

- [Архитектурные правила](ARCHITECTURE_RULES.md) - правила для AI и разработчиков
- [Backend README](backend/README.md) - документация бэкенда
- [Frontend README](frontend/README.md) - документация фронтенда
- [Дизайн-система KOI](frontend/DESIGN_SYSTEM_QUICK_REFERENCE.md) - компоненты UI

---

## API Документация

После запуска backend:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---


**Версия:** 1.0
**Дата последнего обновления:** 28.01.2026
=======
# ShopProject
>>>>>>> 55c00df920af40eebade6faaf6fab4969da88ee3
