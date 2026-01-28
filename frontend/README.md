# 🛒 Frontend - Интернет-магазин

## Описание проекта

Frontend часть интернет-магазина с модульной архитектурой. Проект реализует Clean Architecture и работает с FastAPI backend через REST API.

---

## Структура проекта

```
frontend/
├── core/                      # Ядро приложения
│   ├── config.js             # Конфигурация (API URL, etc.)
│   ├── event-bus.js          # Event Bus для модульной коммуникации
│   └── shared/               # Общие утилиты
│       ├── api.js            # Базовый API клиент
│       ├── formatters.js     # Форматирование данных
│       ├── validators.js     # Валидация форм
│       └── storage.js        # LocalStorage wrapper
│
└── modules/                   # Модули приложения
    ├── catalog/              # Каталог товаров
    └── cart/                 # Корзина покупок
```

---

## Модули системы

### 📦 Модуль Catalog (Каталог товаров)

**Назначение:** Просмотр товаров и категорий.

**Основной функционал:**
- Просмотр списка товаров с пагинацией
- Просмотр деталей товара
- Просмотр категорий
- Поиск и фильтрация товаров
- Отображение дерева категорий

**Интеграция с API:**
```javascript
GET    /api/products              - Список товаров
GET    /api/products/search       - Поиск товаров
GET    /api/products/:id          - Детали товара

GET    /api/categories            - Список категорий
GET    /api/categories/tree       - Дерево категорий
GET    /api/categories/:id        - Детали категории
```

**События Event Bus:**
```javascript
// Публикует:
'catalog:product-selected'  - Выбран товар
'catalog:category-changed'  - Изменена категория

// Подписывается на (опционально):
'cart:item-added'           - Обновление доступности
```

**Структура модуля:**
```
modules/catalog/
├── README.md
│
├── domain/                  # Бизнес-логика
│   ├── entities/
│   │   ├── product.entity.js
│   │   └── category.entity.js
│   └── value-objects/
│       └── filter.vo.js
│
├── application/             # Use Cases
│   └── use-cases/
│       ├── get-products.use-case.js
│       ├── get-product-details.use-case.js
│       ├── get-categories.use-case.js
│       └── search-products.use-case.js
│
├── infrastructure/          # Внешние зависимости
│   └── api/
│       ├── product.api.js
│       └── category.api.js
│
└── presentation/            # UI
    ├── pages/
    │   ├── catalog.html
    │   └── product-details.html
    ├── components/
    │   ├── product-card.component.js
    │   ├── category-tree.component.js
    │   └── product-filter.component.js
    ├── controllers/
    │   └── catalog.controller.js
    └── styles/
        └── catalog.css
```

---

### 🛒 Модуль Cart (Корзина покупок)

**Назначение:** Управление корзиной покупок.

**Основной функционал:**
- Отображение товаров в корзине
- Добавление/удаление товаров
- Изменение количества товаров
- Расчёт итоговой суммы
- Очистка корзины
- Сохранение в LocalStorage

**Интеграция с API:**
```javascript
GET    /api/cart                  - Получить корзину
POST   /api/cart/items            - Добавить товар
PUT    /api/cart/items/:id        - Изменить количество
DELETE /api/cart/items/:id        - Удалить товар
DELETE /api/cart                  - Очистить корзину
```

**События Event Bus:**
```javascript
// Публикует:
'cart:item-added'         - Товар добавлен
'cart:item-removed'       - Товар удалён
'cart:item-quantity-changed' - Количество изменено
'cart:cleared'            - Корзина очищена
'cart:total-changed'      - Изменилась сумма

// Подписывается на:
'catalog:product-selected' - Добавление товара из каталога
```

**Структура модуля:**
```
modules/cart/
├── README.md
│
├── domain/                  # Бизнес-логика
│   ├── entities/
│   │   ├── cart.entity.js
│   │   └── cart-item.entity.js
│   └── services/
│       └── cart-calculator.service.js
│
├── application/             # Use Cases
│   └── use-cases/
│       ├── get-cart.use-case.js
│       ├── add-item.use-case.js
│       ├── remove-item.use-case.js
│       ├── update-quantity.use-case.js
│       └── clear-cart.use-case.js
│
├── infrastructure/          # Внешние зависимости
│   ├── api/
│   │   └── cart.api.js
│   └── storage/
│       └── cart-storage.js
│
└── presentation/            # UI
    ├── pages/
    │   └── cart.html
    ├── components/
    │   ├── cart-list.component.js
    │   ├── cart-item.component.js
    │   └── cart-summary.component.js
    ├── controllers/
    │   └── cart.controller.js
    └── styles/
        └── cart.css
```

---

## Технологический стек

### Frontend
- **HTML5** - разметка
- **CSS3** - стилизация
- **JavaScript (ES6+)** - логика приложения
- **Event Bus** - модульная коммуникация

### Инструменты (опционально)
- **Vite** / **Webpack** - сборка
- **ESLint** - линтинг
- **Prettier** - форматирование
- **Playwright** - E2E тесты

---

## 🎨 Дизайн-система KOI

Проект использует дизайн-систему **KOI** с тёмной темой по умолчанию.

### Основные цвета

#### Фоны
```
Основной:    #0f172a
Карточки:    #1e293b
Инпуты:      #334155
Hover:       #475569
```

#### Текст
```
Основной:    #f1f5f9
Вторичный:   #e2e8f0
Третичный:   #cbd5e0
Мутный:      #94a3b8
```

#### Акценты
```
Основной:    #7c3aed (фиолетовый)
Hover:       #6d28d9
Вторичный:   #8b5cf6
```

#### Семантические цвета
```
Успех:       #10b981 (зелёный)
Ошибка:      #ef4444 (красный)
Внимание:    #f59e0b (жёлтый)
Инфо:        #3b82f6 (синий)
```

---

### Отступы (кратны 4px)

```
4px   - xs    - минимальные отступы
8px   - sm    - маленькие отступы
12px  - md    - средние в компонентах
16px  - base  - БАЗОВЫЙ отступ (использовать чаще всего)
20px  - lg    - увеличенные отступы
24px  - xl    - большие между секциями
32px  - 2xl   - очень большие
40px  - 3xl   - между блоками
48px  - 4xl   - секции страницы
64px  - 5xl   - максимальные отступы
```

---

### Типографика

#### Размеры шрифтов
```
32px - H1 (Заголовки страниц, font-weight: 700)
24px - H2 (Заголовки секций, font-weight: 600)
20px - H3 (Заголовки карточек, font-weight: 600)
18px - H4 (Подзаголовки, font-weight: 600)
16px - Body Large (Основной текст, font-weight: 400)
14px - Body Regular (Вторичный текст, font-weight: 400)
13px - Body Small (Подписи, font-weight: 500)
12px - Caption (Вспомогательный, font-weight: 400)
```

#### Вес шрифта
```
400 - Regular (обычный текст)
500 - Medium (метки, важный текст)
600 - Semibold (кнопки, заголовки карточек)
700 - Bold (заголовки страниц)
```

---

### Скругления

```
4px   - xs    - чекбоксы, переключатели
6px   - sm    - маленькие кнопки
8px   - base  - кнопки (默认值), таблицы
10px  - md    - инпуты, селекты
12px  - lg    - карточки
16px  - xl    - большие карточки
20px  - 2xl   - модальные окна
50%   - full  - круглые элементы (аватары)
```

---

### Тени (тёмная тема)

```
1 - Минимальная:  0 2px 4px rgba(0,0,0,0.3)
2 - Малая:        0 4px 8px rgba(0,0,0,0.4)
3 - Средняя:      0 10px 20px rgba(0,0,0,0.5)
4 - Большая:      0 15px 35px rgba(0,0,0,0.6)
5 - Акцентная:    0 10px 30px rgba(124,58,237,0.4) - для фиолетовых элементов
```

---

### Анимации

#### Длительность
```
150ms - Очень быстро (tooltip, hover на small элементах)
200ms - Быстро (hover кнопок, карточек)
300ms - Нормально (основные переходы, появление модалок)
500ms - Медленно (закрытие модалок, сложные анимации)
```

#### Easing функции
```
ease          - универсальные переходы
ease-in       - появление элементов
ease-out      - исчезновение элементов
ease-in-out   - плавные движения, слайды
```

---

### Кнопки

#### Размеры
```
Small:   32px высота, padding 16px, шрифт 13px
Medium:  40px высота, padding 20px, шрифт 14px (по умолчанию)
Large:   48px высота, padding 32px, шрифт 16px
```

#### Типы кнопок
```
Primary:    Градиент #7c3aed → #8b5cf6, белый текст
Secondary:  Граница 2px #7c3aed, прозрачный фон, текст #e2e8f0
Danger:     Фон #ef4444, белый текст
Ghost:      Прозрачный фон, текст #e2e8f0
```

#### Состояния кнопок
```
Default:    Согласно типу кнопки
Hover:      Затемнение на 10%, трансформация translateY(-1px)
Active:     Трансформация translateY(0)
Disabled:   Opacity 50%, pointer-events: none
Loading:    Спиннер вместо текста или слева от текста
```

---

### Инпуты

#### Размеры
```
Small:   32px высота, padding 12px, шрифт 13px
Medium:  40px высота, padding 14px, шрифт 14px (по умолчанию)
Large:   48px высота, padding 16px, шрифт 16px
```

#### Состояния
```
Default:  Фон #334155, граница 1px #475569, текст #f1f5f9
Focus:    Граница 1px #7c3aed, обводка 0 0 0 3px rgba(124,58,237,0.1)
Error:    Граница 1px #ef4444, обводка rgba(239,68,68,0.1)
Disabled: Фон #1e293b, граница 1px #334155, opacity 60%
```

---

### Бейджи

#### Размеры
```
Small:   20px высота, padding 6px 10px, шрифт 11px
Medium:  24px высота, padding 8px 12px, шрифт 12px (по умолчанию)
Large:   28px высота, padding 10px 14px, шрифт 13px
```

#### Типы бейджей
```
Success:  Фон rgba(16,185,129,0.2), текст #10b981
Error:    Фон rgba(239,68,68,0.2), текст #ef4444
Warning:  Фон rgba(245,158,11,0.2), текст #f59e0b
Info:     Фон rgba(59,130,246,0.2), текст #3b82f6
Neutral:  Фон #334155, текст #e2e8f0
```

---

### Breakpoints (адаптивность)

```
Mobile Small:   320px - 479px   - Очень маленькие экраны
Mobile:         480px - 767px   - Мобильные устройства
Tablet:         768px - 1023px  - Планшеты
Desktop:        1024px - 1439px - Настольные компьютеры
Desktop Large:  1440px+         - Большие экраны
```

#### Медиа-запросы
```css
/* Mobile First подход */
.component { /* стили для мобильных */ }

@media (min-width: 768px) {
  /* стили для планшетов и выше */
}

@media (min-width: 1024px) {
  /* стили для десктопа и выше */
}
```

---

### Иконки

#### Размеры
```
16px - Mini  (inline с текстом, в кнопках small)
20px - Small (в кнопках medium)
24px - Medium (в навигации, списках)
32px - Large (в заголовках секций)
48px - XLarge (в пустых состояниях)
64px - Огромные (в hero секциях, больших empty states)
```

---

## Чеклист компонента дизайна

При создании нового UI компонента проверить:

- [ ] Цвета используются только из палитры
- [ ] Все отступы кратны 4px
- [ ] Шрифты соответствуют шкале
- [ ] Есть hover эффекты
- [ ] Поддерживаются состояния (default, hover, active, disabled)
- [ ] Проверена контрастность (WCAG AA минимум)
- [ ] Добавлены aria-атрибуты (aria-label, aria-describedby)
- [ ] Работает клавиатурная навигация (Tab, Enter, Space)
- [ ] Компонент адаптивен (mobile first)
- [ ] Есть состояние загрузки (loading state)
- [ ] Есть состояние ошибки (error state)
- [ ] Плавные переходы (transition 150-300ms)

### CSS переменные для быстрой разработки

```css
:root {
  /* Фоны */
  --bg-primary: #0f172a;
  --bg-card: #1e293b;
  --bg-input: #334155;
  --bg-hover: #475569;

  /* Текст */
  --text-primary: #f1f5f9;
  --text-secondary: #e2e8f0;
  --text-tertiary: #cbd5e0;
  --text-muted: #94a3b8;

  /* Акценты */
  --accent-primary: #7c3aed;
  --accent-hover: #6d28d9;
  --accent-secondary: #8b5cf6;

  /* Семантика */
  --color-success: #10b981;
  --color-error: #ef4444;
  --color-warning: #f59e0b;
  --color-info: #3b82f6;

  /* Отступы */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-base: 16px;
  --spacing-lg: 20px;
  --spacing-xl: 24px;
  --spacing-2xl: 32px;

  /* Скругления */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-base: 8px;
  --radius-md: 10px;
  --radius-lg: 12px;

  /* Тени */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 20px rgba(0,0,0,0.5);
  --shadow-accent: 0 10px 30px rgba(124,58,237,0.4);

  /* Анимации */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-normal: 300ms ease;
  --transition-slow: 500ms ease;
}
```

**Полная документация:** См. [DESIGN_SYSTEM_QUICK_REFERENCE.md](DESIGN_SYSTEM_QUICK_REFERENCE.md)

---

## Архитектурные принципы

### Clean Architecture

```
Presentation → Application → Domain ← Infrastructure
                                ↑
                        НЕ ЗАВИСИТ НИ ОТ КОГО!
```

**Domain:**
- Чистая бизнес-логика
- Сущности (Entities)
- Value Objects
- Доменные сервисы
- НЕТ зависимостей от фреймворков

**Application:**
- Use Cases (сценарии использования)
- Орхестрация бизнес-логики
- Использует Domain

**Infrastructure:**
- API клиенты
- Storage (LocalStorage, SessionStorage)
- Реализация внешних зависимостей

**Presentation:**
- HTML шаблоны
- Компоненты UI
- Контроллеры (связь UI с Use Cases)

### Модульная архитектура

- Каждый модуль независим
- Коммуникация через Event Bus
- Общие утилиты в `core/shared`
- Прямые импорты между модулями ЗАПРЕЩЕНЫ

---

## Принципы SOLID

### S - Single Responsibility
Каждый класс/функция имеет одну ответственность:
- `ProductCardComponent` - только отображение карточки товара
- `GetProductsUseCase` - только получение списка товаров
- `CartCalculatorService` - только расчёт суммы

### O - Open/Closed
Открыт для расширения, закрыт для модификации:
```javascript
// ❌ ПЛОХО
function renderProduct(product, view = 'card') {
  if (view === 'card') { /* ... */ }
  else if (view === 'list') { /* ... */ }
  // Нужно менять функцию для нового view
}

// ✅ ХОРОШО
class ProductRenderer {
  render(product) { throw new Error('Implement me'); }
}

class CardProductRenderer extends ProductRenderer { /* ... */ }
class ListProductRenderer extends ProductRenderer { /* ... */ }
```

### L - Liskov Substitution
Подклассы должны заменять родительские классы:
```javascript
// Все ApiClient должны иметь одинаковый интерфейс
class ApiClient {
  async get(url) { throw new Error('Implement me'); }
}

class ProductApiClient extends ApiClient {
  async get(url) { /* реализация */ }
}
```

### I - Interface Segregation
Много специфичных интерфейсов лучше одного общего:
```javascript
// ✅ ХОРОШО - разделённые интерфейсы
class ProductRepository {
  async findById(id) { }
}

class SearchableProductRepository {
  async search(query) { }
}
```

### D - Dependency Inversion
Зависимость от абстракций:
```javascript
// ✅ ХОРОШО - внедрение зависимостей
class GetProductsUseCase {
  constructor(productRepository) {
    this.productRepository = productRepository;
  }
}

const useCase = new GetProductsUseCase(new ProductApiRepository());
```

---

## Event Bus

Event Bus обеспечивает коммуникацию между модулями без прямых зависимостей.

### Использование

**Публикация события:**
```javascript
import eventBus from '/core/event-bus.js';

eventBus.publish('cart:item-added', {
  productId: 123,
  quantity: 2,
  price: 999
});
```

**Подписка на событие:**
```javascript
eventBus.subscribe('cart:item-added', (data) => {
  console.log('Добавлен товар:', data.productId);
  updateCartCounter();
});
```

**Отписка:**
```javascript
const unsubscribe = eventBus.subscribe('cart:total-changed', handler);

// Позже
unsubscribe();
```

---

## Установка и запуск

### Требования
- Node.js 18+ (для сборки, если используется)
- Современный браузер (Chrome, Firefox, Safari, Edge)

### Установка (с Vite)
```bash
npm create vite@latest frontend -- --template vanilla
cd frontend
npm install
```

### Разработка
```bash
npm run dev
```

### Сборка для продакшена
```bash
npm run build
npm run preview
```

### Без сборки (простой вариант)
Просто открыть `index.html` в браузере через HTTP сервер:
```bash
python -m http.server 8000
# или
npx serve .
```

---

## Конфигурация

### Переменные окружения

Создать файл `.env` или настроить в `core/config.js`:

```javascript
// core/config.js
export default {
  API_BASE_URL: 'http://localhost:8000',
  API_TIMEOUT: 10000,
  STORAGE_KEY_PREFIX: 'shop_',
  CART_SYNC_INTERVAL: 30000, // мс
};
```

---

## API Документация

Backend API документация доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Примеры реализации

### Use Case (Получение товаров)

```javascript
// modules/catalog/application/use-cases/get-products.use-case.js
export class GetProductsUseCase {
  constructor(productRepository) {
    this.productRepository = productRepository;
  }

  async execute(filters = {}) {
    const products = await this.productRepository.findAll(filters);

    return products.map(product => ({
      id: product.id,
      name: product.name,
      price: product.price,
      imageUrl: product.image_url,
      // Маппинг доменной сущности в DTO
    }));
  }
}
```

### API Repository

```javascript
// modules/catalog/infrastructure/api/product.api.js
import api from '/core/shared/api.js';

export class ProductApiRepository {
  async findAll(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await api.get(`/api/products?${params}`);
    return response.data;
  }

  async findById(id) {
    const response = await api.get(`/api/products/${id}`);
    return response.data;
  }
}
```

### Controller

```javascript
// modules/catalog/presentation/controllers/catalog.controller.js
import { GetProductsUseCase } from '../../application/use-cases/get-products.use-case.js';
import { ProductApiRepository } from '../../infrastructure/api/product.api.js';
import eventBus from '/core/event-bus.js';

export class CatalogController {
  constructor() {
    this.getProductsUseCase = new GetProductsUseCase(
      new ProductApiRepository()
    );
  }

  async loadProducts(filters = {}) {
    try {
      const products = await this.getProductsUseCase.execute(filters);
      this.renderProducts(products);
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  }

  renderProducts(products) {
    // Отрисовка товаров
    const container = document.querySelector('.products-grid');
    container.innerHTML = products.map(p => `
      <div class="product-card" data-product-id="${p.id}">
        <img src="${p.imageUrl}" alt="${p.name}">
        <h3>${p.name}</h3>
        <p class="price">$${p.price}</p>
        <button class="btn-add-to-cart">Add to Cart</button>
      </div>
    `).join('');

    // Подписка на клики
    container.querySelectorAll('.btn-add-to-cart').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const productId = e.target.closest('.product-card').dataset.productId;
        eventBus.publish('catalog:product-selected', { productId });
      });
    });
  }
}
```

### Component

```javascript
// modules/catalog/presentation/components/product-card.component.js
export class ProductCardComponent {
  render(product) {
    return `
      <article class="product-card" data-product-id="${product.id}">
        <img src="${product.imageUrl}" alt="${product.name}" class="product-image">
        <div class="product-info">
          <h3 class="product-name">${product.name}</h3>
          <p class="product-price">$${product.price.toFixed(2)}</p>
          <button class="btn-add-to-cart" type="button">
            Add to Cart
          </button>
        </div>
      </article>
    `;
  }
}
```

---

## Naming Conventions

### Файлы
```
Entities:           product.entity.js
Value Objects:      money.vo.js, date-range.vo.js
Use Cases:          get-products.use-case.js
Services:           cart-calculator.service.js
API:                product.api.js, cart.api.js
Controllers:        catalog.controller.js
Components:         product-card.component.js
Pages:              catalog.html, cart.html
Styles:             catalog.css, cart.css
```

### Классы
```javascript
// PascalCase для классов
class GetProductsUseCase { }
class ProductCardComponent { }
class CartCalculatorService { }

// camelCase для методов и переменных
async execute() { }
const productId = 123;
```

---

#

---

## Безопасность

### Защита
- Валидация данных на клиенте (до отправки на сервер)
- XSS защита (экранирование HTML)
- CSRF токены (если используется)
- HTTPS в продакшене

---

## Логирование

Использовать единый логгер из `core/shared/logger.js`:

```javascript
import logger from '/core/shared/logger.js';

logger.info('Product loaded', { productId: 123 });
logger.error('Failed to add to cart', { error: err.message });
```

---

## Чеклист для разработки

При создании нового функционала:

- [ ] Определён модуль (или используется существующий)
- [ ] Domain слой НЕ зависит от внешних библиотек
- [ ] Use Case содержит бизнес-логику
- [ ] API/Repository использует интерфейс из Domain
- [ ] Модули НЕ импортируют друг друга напрямую
- [ ] Общение через Event Bus
- [ ] README.md модуля обновлён
- [ ] Названия файлов следуют конвенции
- [ ] Соблюдены принципы SOLID
- [ ] Добавлены валидация и обработка ошибок
- [ ] Написаны тесты

---

## Контакты и поддержка

**Версия:** 1.0
**Статус:** 📝 В разработке
**Последнее обновление:** 28.01.2026
