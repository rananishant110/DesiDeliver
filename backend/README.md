# DesiDeliver Backend

Django backend for the DesiDeliver Indian grocery supply management system.

## Features

- **User Management**: Custom user model with business information
- **Product Catalog**: Product and category management
- **Shopping Cart**: Cart and cart item management
- **Order Management**: Order processing and tracking
- **Support Tickets**: Customer support ticketing system
- **Email Notifications**: Automated email notifications for orders and tickets
- **Async Tasks**: Celery integration for background job processing
- **Admin Interface**: Django admin panel for all models

## Technology Stack

- **Framework**: Django 5.2.5
- **Database**: PostgreSQL 15 (production) / SQLite (legacy)
- **Cache & Message Broker**: Redis 7
- **API**: Django REST Framework 3.16.1
- **Authentication**: JWT (Simple JWT)
- **CORS**: django-cors-headers
- **Task Queue**: Celery 5.3.4 with Redis broker
- **Monitoring**: Flower for Celery task monitoring
- **WSGI Server**: Gunicorn 21.2.0 (production)
- **Static Files**: WhiteNoise 6.6.0
- **Containerization**: Docker & Docker Compose

## Project Structure

```
backend/
├── desideliver_backend/     # Main project settings
│   ├── settings/            # Split settings (base, local, production)
│   ├── celery.py           # Celery configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── users/                   # User management app
├── products/                # Product catalog app
├── cart/                    # Shopping cart app
├── orders/                  # Order management app
│   └── tasks.py            # Celery async tasks for orders
├── tickets/                 # Support ticketing app
│   ├── models.py           # Ticket, Comment, History models
│   ├── views.py            # Ticket API endpoints
│   ├── serializers.py      # DRF serializers
│   ├── email_service.py    # Email notification service
│   └── templates/          # Email HTML templates
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── entrypoint.sh           # Container initialization script
├── .dockerignore           # Docker build exclusions
├── .env.example            # Environment variables template
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── DOCKER_README.md        # Comprehensive Docker documentation
└── README.md               # This file
```

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose 2.0+ (included with Docker Desktop)
- Git

### 1. Clone and Setup Environment
```bash
cd backend
cp .env.example .env
# Edit .env file with your configuration (optional for development)
```

### 2. Start All Services
```bash
docker-compose up -d
```

This starts 6 services:
- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Cache & message broker
- **Django Backend** (port 8000) - API server
- **Celery Worker** - Background task processor
- **Celery Beat** - Scheduled task runner
- **Flower** (port 5555) - Celery monitoring UI

### 3. Create Superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Access the Application
- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Celery Monitor (Flower)**: http://localhost:5555

### 5. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### 6. Stop Services
```bash
docker-compose down
```

## Common Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Run Django commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell

# Run tests
docker-compose exec backend python manage.py test

# View service status
docker-compose ps

# Restart a specific service
docker-compose restart backend

# Access Django shell
docker-compose exec backend python manage.py shell

# Access PostgreSQL shell
docker-compose exec db psql -U desideliver_user -d desideliver_dev

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Traditional Setup (Legacy - Not Recommended)

<details>
<summary>Click to expand non-Docker setup instructions</summary>

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
export DJANGO_SETTINGS_MODULE=desideliver_backend.settings.local
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

**Note**: This setup uses SQLite and does not include Redis, Celery, or PostgreSQL. Docker setup is highly recommended for full functionality.

</details>

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

### Tickets App
- **Ticket**: Customer support tickets with status tracking
- **TicketComment**: Comments on tickets (customer and staff)
- **TicketHistory**: Audit trail of ticket changes

## Admin Interface

Access the admin panel at `/admin/` after creating a superuser.

### Admin Features
- User management with business information
- Product catalog management
- Cart monitoring
- Order tracking and management
- Category organization

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (JWT)
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Products
- `GET /api/products/` - List all products
- `GET /api/products/<id>/` - Get product details
- `GET /api/categories/` - List all categories

### Cart
- `POST /api/cart/add/` - Add item to cart
- `GET /api/cart/` - View cart
- `PUT /api/cart/update/<id>/` - Update cart item quantity
- `DELETE /api/cart/remove/<id>/` - Remove cart item
- `DELETE /api/cart/clear/` - Clear entire cart

### Orders
- `POST /api/orders/create/` - Create order from cart
- `GET /api/orders/` - List user's orders
- `GET /api/orders/<id>/` - Get order details
- `GET /api/orders/<id>/export-csv/` - Export order as CSV (staff only)

### Tickets
- `POST /api/tickets/` - Create support ticket
- `GET /api/tickets/` - List tickets (user's own or all for staff)
- `GET /api/tickets/<id>/` - Get ticket details
- `POST /api/tickets/<id>/comments/` - Add comment to ticket
- `PATCH /api/tickets/<id>/status/` - Update ticket status (staff only)
- `PATCH /api/tickets/<id>/priority/` - Update ticket priority (staff only)
- `GET /api/tickets/stats/` - Get ticket statistics (staff only)

## Celery Async Tasks

Background tasks processed by Celery workers:

### Order Tasks
- `send_order_confirmation_email` - Send order confirmation to customer
- `send_delivery_notification_email` - Send delivery notification
- `generate_order_csv_async` - Generate CSV export for orders
- `cleanup_old_csv_files` - Periodic cleanup of temporary CSV files

### Monitoring
Access Flower dashboard at http://localhost:5555 to monitor:
- Active tasks
- Task history and status
- Worker status and performance
- Task execution times

## Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=desideliver_backend.settings.local

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=desideliver_dev
DB_USER=desideliver_user
DB_PASSWORD=dev_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Development Notes

- **Docker Compose**: Uses `docker-compose.yml` for development with hot-reloading
- **PostgreSQL**: Production-ready database with persistent volumes
- **Redis**: Used for caching and Celery message broker
- **Celery**: Processes background tasks asynchronously
- **Settings Split**: Separate configurations for local/production environments
- **Static Files**: Served by WhiteNoise in production
- **Health Checks**: All services have health checks for reliability

## Production Deployment

For production deployment, use `docker-compose.prod.yml`:

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Security checks
docker-compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
```

**Production differences:**
- Uses Gunicorn WSGI server (not Django dev server)
- `DEBUG=False`
- Secure PostgreSQL credentials
- Resource limits on containers
- No port exposure for database/redis (internal only)
- Automatic restarts on failure

## Troubleshooting

### Port already in use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Database connection issues
```bash
# Check database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Celery tasks not executing
```bash
# Check worker is running
docker-compose ps celery_worker

# View worker logs
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker
```

### Reset database (⚠️ destroys data)
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

## Documentation

- **Docker Setup**: See `DOCKER_README.md` for comprehensive Docker documentation
- **API Documentation**: Available at `/api/docs/` (coming soon)
- **Feature Docs**: See `/docs/` directory for PRDs and development plans

## Contributing

1. Create feature branch from `main`
2. Make changes with Docker running: `docker-compose up`
3. Run tests: `docker-compose exec backend python manage.py test`
4. Commit with descriptive message
5. Push and create pull request

## Next Steps

- ✅ Docker containerization complete
- ✅ Celery async task processing implemented
- ✅ Customer support ticketing system complete
- ✅ Email notification system functional
- 🔄 Add automated testing suite
- 🔄 Implement API documentation (Swagger/OpenAPI)
- 🔄 Add monitoring and logging (Sentry, ELK)
- 🔄 Implement rate limiting
- 🔄 Add caching strategies for frequently accessed data

## License

Proprietary - DesiDeliver Inc.
