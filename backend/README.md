# DesiDeliver Backend

Django backend for the DesiDeliver Indian grocery supply management system.

## Features

- **User Management**: Custom user model with business information
- **Product Catalog**: Product and category management
- **Shopping Cart**: Cart and cart item management
- **Order Management**: Order processing and tracking
- **Admin Interface**: Django admin panel for all models

## Technology Stack

- **Framework**: Django 5.2.5
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: Django REST Framework
- **Authentication**: Django built-in + JWT support
- **CORS**: django-cors-headers

## Project Structure

```
backend/
├── desideliver_backend/     # Main project settings
├── users/                   # User management app
├── products/                # Product catalog app
├── cart/                    # Shopping cart app
├── orders/                  # Order management app
├── manage.py               # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

## Models Overview

### Users App
- **CustomUser**: Extended user model with business information
- Business details, contact info, address, verification status

### Products App
- **Category**: Product categories (Spices, Rice, Lentils, etc.)
- **Product**: Individual products with pricing, inventory, and details

### Cart App
- **Cart**: User shopping cart
- **CartItem**: Individual items in cart with quantities

### Orders App
- **Order**: Customer orders with status tracking
- **OrderItem**: Individual items in orders

## Admin Interface

Access the admin panel at `/admin/` after creating a superuser.

### Admin Features
- User management with business information
- Product catalog management
- Cart monitoring
- Order tracking and management
- Category organization

## API Endpoints (Coming Soon)

- Authentication endpoints
- Product catalog endpoints
- Cart management endpoints
- Order processing endpoints

## Development Notes

- Uses SQLite for development (easy setup)
- Configured for PostgreSQL in production
- CORS enabled for React frontend integration
- REST framework ready for API development

## Next Steps

1. Implement API views and serializers
2. Add authentication endpoints
3. Create product catalog API
4. Implement cart functionality
5. Build order processing system
