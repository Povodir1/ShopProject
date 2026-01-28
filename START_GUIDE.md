# 🚀 Shop Application - Quick Start Guide

## ✅ Application Status

Both backend and frontend are **RUNNING**:

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database**: PostgreSQL (e_shop) with 11 categories and 23 products

---

## 🔄 Full Request Cycle

### From Button Click to Database

```
User Click (Frontend)
    ↓
Event Bus (catalog:product-selected)
    ↓
Cart Controller (add-item.use-case)
    ↓
Cart API Repository
    ↓
FastAPI Backend (POST /api/cart/items)
    ↓
Database Query (PostgreSQL)
    ↓
Response → Frontend Update
```

---

## 📡 API Endpoints (Working)

### Categories
```bash
GET http://localhost:8000/api/categories        # List all categories
GET http://localhost:8000/api/categories/tree   # Get category tree
GET http://localhost:8000/api/categories/{id}   # Get category details
```

### Products
```bash
GET http://localhost:8000/api/products          # List products (pagination)
GET http://localhost:8000/api/products/search   # Search products
GET http://localhost:8000/api/products/{id}     # Get product details
```

### Cart
```bash
GET    http://localhost:8000/api/cart           # Get cart
POST   http://localhost:8000/api/cart/items     # Add item to cart
PUT    http://localhost:8000/api/cart/items/{id} # Update quantity
DELETE http://localhost:8000/api/cart/items/{id} # Remove item
DELETE http://localhost:8000/api/cart           # Clear cart
```

---

## 🛠️ Management Commands

### Start Backend
```bash
cd /home/pavel/ShopProject/backend
venv/bin/uvicorn core.app:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend
```bash
cd /home/pavel/ShopProject/frontend
npm run dev
```

### Database Migration
```bash
cd /home/pavel/ShopProject/backend
venv/bin/alembic upgrade head
```

### Seed Database
```bash
cd /home/pavel/ShopProject/backend
PYTHONPATH=/home/pavel/ShopProject/backend venv/bin/python scripts/seed_db.py
```

---

## 📦 Database Content

### Categories (11)
- Accessories, Beverages, Clothing, Electronics, Food
- Kids, Laptops, Men, Phones, Snacks, Women

### Products (23)
- **Phones**: iPhone 15 Pro ($1199), Samsung Galaxy S24 Ultra ($1299), Google Pixel 8 Pro ($999)
- **Laptops**: MacBook Pro 16" ($2499), Dell XPS 15 ($1899), ThinkPad X1 Carbon ($1649)
- **Accessories**: AirPods Pro 2 ($249), Sony WH-1000XM5 ($399), MagSafe Charger ($39)
- **Clothing**: T-Shirts, Jeans, Dresses, Leggings, etc.
- **Food**: Coffee, Tea, Juice, Nuts, Chocolate, Protein Bars

---

## 🧪 Testing the Full Cycle

### 1. View Products in Browser
Open: http://localhost:3000/catalog.html

### 2. Add Product to Cart
Click "Add to Cart" on any product → Event fires → API call → Database update

### 3. View Cart
Open: http://localhost:3000/cart.html

### 4. Test API Directly
```bash
# Get products
curl http://localhost:8000/api/products

# Add item to cart
curl -X POST http://localhost:8000/api/cart/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": "<id>", "quantity": 1}'

# Get cart
curl http://localhost:8000/api/cart
```

---

## 📊 Architecture Diagram

```
┌─────────────────┐
│  Frontend (Vite) │
│  Port: 3000      │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│  Port: 8000     │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│  PostgreSQL     │
│  Database       │
│  e_shop         │
└─────────────────┘
```

---

## 🐛 Troubleshooting

### Backend Not Responding
```bash
# Check logs
tail -f /tmp/backend.log

# Restart backend
cd /home/pavel/ShopProject/backend
venv/bin/uvicorn core.app:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Not Loading
```bash
# Check logs
tail -f /tmp/frontend.log

# Restart frontend
cd /home/pavel/ShopProject/frontend
npm run dev
```

### Database Empty
```bash
# Re-seed database
cd /home/pavel/ShopProject/backend
PYTHONPATH=/home/pavel/ShopProject/backend venv/bin/python scripts/seed_db.py
```

---

## 📝 Project Structure

```
ShopProject/
├── backend/           # FastAPI application
│   ├── core/         # Configuration, database
│   ├── modules/      # Feature modules (catalog, cart)
│   ├── scripts/      # Utility scripts
│   └── venv/         # Python virtual environment
│
├── frontend/         # Vite application
│   ├── core/         # App config, event bus, shared utils
│   ├── modules/      # Feature modules (catalog, cart)
│   ├── styles/       # Global styles (KOI design system)
│   └── node_modules/ # npm dependencies
│
└── README.md         # Project documentation
```

---

## 🎨 Design System: KOI

- **Theme**: Dark mode
- **Primary Accent**: #7c3aed (Purple)
- **Background**: #0f172a (Dark slate)
- **Typography**: System fonts with clear hierarchy
- **Spacing**: 4px base unit (8, 12, 16, 20, 24, 32, 40, 48, 64)

---

**Status**: ✅ All systems operational
**Last Updated**: 2026-01-28 17:52
