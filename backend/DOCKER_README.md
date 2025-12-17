# DesiDeliver Backend - Docker Setup

## 🐳 Docker Architecture

The DesiDeliver backend is fully containerized with Docker and Docker Compose, providing:

- **PostgreSQL 15**: Production database
- **Redis 7**: Cache and message broker
- **Django Backend**: Main API server
- **Celery Worker**: Async task processing
- **Celery Beat**: Scheduled tasks
- **Flower**: Celery monitoring dashboard

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available
- Ports 5432, 6379, 8000, 5555 available

### Start Development Environment

```bash
# Navigate to backend directory
cd backend

# Copy environment file
cp .env.example .env

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

Your application is now running at:
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/
- **Flower (Celery)**: http://localhost:5555

## 📋 Common Docker Commands

### Service Management

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a specific service
docker compose restart backend

# View service status
docker compose ps

# View logs
docker compose logs -f backend          # Backend only
docker compose logs -f celery_worker    # Celery worker only
docker compose logs -f                  # All services
```

### Database Operations

```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Create migrations
docker compose exec backend python manage.py makemigrations

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Access database shell
docker compose exec backend python manage.py dbshell

# Access Django shell
docker compose exec backend python manage.py shell
```

### Testing

```bash
# Run all tests
docker compose exec backend python manage.py test

# Run tests for specific app
docker compose exec backend python manage.py test users
docker compose exec backend python manage.py test orders

# Run with coverage
docker compose exec backend coverage run manage.py test
docker compose exec backend coverage report
```

### Celery Operations

```bash
# View Celery worker logs
docker compose logs -f celery_worker

# View Celery beat logs
docker compose logs -f celery_beat

# Restart Celery worker
docker compose restart celery_worker

# Test Celery task from Django shell
docker compose exec backend python manage.py shell
>>> from orders.tasks import send_order_confirmation_email
>>> result = send_order_confirmation_email.delay(1, 'test@example.com')
>>> result.status
```

### Development Workflow

```bash
# Rebuild after changing requirements.txt
docker compose up --build backend

# Fresh start (removes volumes - WARNING: deletes data!)
docker compose down -v
docker compose up -d

# Execute any Django command
docker compose exec backend python manage.py <command>

# Access bash shell in container
docker compose exec backend bash
```

## 🗄️ Database Access

### Using pgAdmin or DBeaver

Connect with these credentials:

- **Host**: localhost
- **Port**: 5432
- **Database**: desideliver_dev
- **User**: desideliver_user
- **Password**: dev_password_change_in_production

### Backup and Restore

```bash
# Backup database
docker compose exec backend python manage.py dumpdata > backup.json

# Restore database
docker compose exec backend python manage.py loaddata backup.json

# PostgreSQL dump (more complete)
docker compose exec db pg_dump -U desideliver_user desideliver_dev > backup.sql

# PostgreSQL restore
docker compose exec -T db psql -U desideliver_user desideliver_dev < backup.sql
```

## ⚙️ Environment Variables

Key environment variables in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
DJANGO_SETTINGS_MODULE=desideliver_backend.settings.local
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=desideliver_dev
DB_USER=desideliver_user
DB_PASSWORD=dev_password_change_in_production
DB_HOST=db
DB_PORT=5432

# Redis & Celery
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 🔥 Hot Reloading

Code changes are automatically reflected in the running container:

1. Edit any Python file
2. Django dev server auto-reloads
3. Celery workers need manual restart: `docker compose restart celery_worker`

**Note**: Changes to `requirements.txt` require rebuild:
```bash
docker compose up --build backend celery_worker
```

## 🌸 Flower - Celery Monitoring

Access Flower at http://localhost:5555 to:
- Monitor active workers
- View task status (pending, active, completed, failed)
- Inspect task details and results
- Retry failed tasks
- View worker statistics

## 🏭 Production Deployment

### Build Production Images

```bash
# Create production environment file
cp .env.example .env.prod
# Edit .env.prod with production values

# Build production images
docker compose -f docker-compose.prod.yml build

# Start production services
docker compose -f docker-compose.prod.yml up -d

# Check production deployment
docker compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
```

### Production Differences

- Gunicorn instead of Django dev server
- DEBUG=False
- Static files served by WhiteNoise
- Resource limits enforced
- No port exposure for DB/Redis
- Auto-restart on failure
- Health checks enabled

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8000  # Django

# Stop local services
sudo pkill postgres
```

### Container Won't Start

```bash
# Check logs
docker compose logs backend

# Remove and recreate
docker compose down
docker compose up -d

# Full reset (WARNING: deletes data)
docker compose down -v
docker compose up -d
```

### Celery Tasks Not Running

```bash
# Check worker is running
docker compose ps celery_worker

# Check worker logs
docker compose logs celery_worker

# Restart worker
docker compose restart celery_worker

# Check Redis connection
docker compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Database Connection Issues

```bash
# Check DB is healthy
docker compose ps db

# Check logs
docker compose logs db

# Test connection
docker compose exec backend python manage.py dbshell
```

### Migration Issues

```bash
# Show migration status
docker compose exec backend python manage.py showmigrations

# Fake migrations if needed
docker compose exec backend python manage.py migrate --fake

# Roll back migration
docker compose exec backend python manage.py migrate app_name previous_migration
```

## 📦 Docker Images

### Image Sizes (Approximate)

- Development: ~500MB
- Production: ~400MB (optimized)

### Optimize Images

```bash
# Remove unused images
docker image prune -a

# View image sizes
docker images | grep backend

# Multi-stage build already optimizes production images
```

## 🔒 Security Best Practices

### For Production

1. **Change default passwords** in `.env.prod`
2. **Use strong SECRET_KEY**: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
3. **Set ALLOWED_HOSTS** to your domain
4. **Enable HTTPS** (SECURE_SSL_REDIRECT=True)
5. **Use Docker secrets** instead of .env for sensitive data
6. **Limit resource usage** (already configured in prod)
7. **Regular updates**: Update base images and dependencies

### Database Security

```bash
# Never expose database port in production
# In docker-compose.prod.yml, use 'expose' not 'ports'

# Use strong passwords
DB_PASSWORD=$(openssl rand -base64 32)

# Regular backups
# Set up automated backup schedule
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🤝 Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Review this documentation
3. Check project documentation in `/docs`
4. Contact the development team

---

**Happy Dockerizing! 🚀**
