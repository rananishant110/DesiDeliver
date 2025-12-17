# Development Plan: Backend Dockerization

## Overview
This plan outlines the implementation of Docker containerization for the DesiDeliver backend, including PostgreSQL database, Redis cache, and separate development/production configurations.

**Reference**: [PRD Document](./feat-backend-dockerization.prd.md)

## Project Timeline
**Total Estimated Duration**: 3-4 days (24-32 hours) - Updated to include Celery integration
**Complexity**: Medium-High
**Development Approach**: Infrastructure-first, then configuration split, then testing, then Celery integration

## Implementation Status
- ✅ Milestones 1-7: Completed (Docker setup, PostgreSQL, Redis, Settings split)
- 🔄 Milestone 8: In Progress (Celery Integration)

## Milestones

### Milestone 1: Project Setup & Dependencies
- [x] Status: **COMPLETED**
- Description: Update dependencies and create Docker-related files structure
- Estimated Duration: 1 hour
- Dependencies: None

#### Tasks:
- [x] Task 1.1: Update requirements.txt with production dependencies
  - Add `gunicorn==21.2.0` for WSGI server
  - Add `whitenoise==6.6.0` for static file serving
  - Add `django-environ==0.11.2` for environment variables
  - Verify `psycopg2-binary==2.9.10` is present
  - File: `/backend/requirements.txt`
  - Estimated Time: 15 minutes

- [ ] Task 1.2: Create .dockerignore file
  - Ignore `__pycache__`, `*.pyc`, `.git`
  - Ignore `db.sqlite3`, `.env`, `venv/`
  - Ignore `.DS_Store`, `*.log`, `media/`
  - File: `/backend/.dockerignore`
  - Estimated Time: 10 minutes

- [ ] Task 1.3: Update .gitignore for Docker
  - Add `.env` (but keep `.env.example`)
  - Add Docker volume directories if needed
  - File: `/backend/.gitignore`
  - Estimated Time: 5 minutes

- [ ] Task 1.4: Backup current database (optional)
  - Run: `python manage.py dumpdata > backup_data.json`
  - Store safely for migration to PostgreSQL
  - Estimated Time: 10 minutes

- [ ] Task 1.5: Create .env.example template
  - Define all required environment variables
  - Include comments explaining each variable
  - File: `/backend/.env.example`
  - Estimated Time: 20 minutes

### Milestone 2: Settings Configuration Split
- [ ] Status: Not Started
- Description: Refactor Django settings into base/local/production modules
- Estimated Duration: 3 hours
- Dependencies: Milestone 1 complete

#### Tasks:
- [ ] Task 2.1: Create settings package structure
  - Create directory: `/backend/desideliver_backend/settings/`
  - Ensure proper Python package structure
  - Estimated Time: 5 minutes

- [ ] Task 2.2: Create base.py with shared settings
  - Copy current settings.py content to base.py
  - Remove environment-specific settings (DEBUG, DATABASES, etc.)
  - Keep: INSTALLED_APPS, MIDDLEWARE, TEMPLATES, AUTH_PASSWORD_VALIDATORS
  - Keep: INTERNATIONALIZATION, STATIC_URL, REST_FRAMEWORK, CORS settings
  - Add django-environ setup for loading .env variables
  - File: `/backend/desideliver_backend/settings/base.py`
  - Estimated Time: 1 hour

- [ ] Task 2.3: Create local.py for development settings
  - Import from base: `from .base import *`
  - Set `DEBUG = True`
  - Configure SQLite/PostgreSQL based on environment variable
  - Set `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
  - Configure `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']`
  - Enable verbose logging for development
  - File: `/backend/desideliver_backend/settings/local.py`
  - Estimated Time: 45 minutes

- [ ] Task 2.4: Create production.py for production settings
  - Import from base: `from .base import *`
  - Set `DEBUG = False`
  - Configure PostgreSQL database from environment variables
  - Configure Redis for caching
  - Set secure `ALLOWED_HOSTS` from environment variable
  - Add security settings: SECURE_SSL_REDIRECT, CSRF_COOKIE_SECURE, etc.
  - Configure WhiteNoise for static files
  - Configure proper logging to stdout
  - File: `/backend/desideliver_backend/settings/production.py`
  - Estimated Time: 1 hour

- [ ] Task 2.5: Create settings __init__.py
  - Auto-load appropriate settings based on DJANGO_SETTINGS_MODULE
  - Provide helpful error messages if environment variable missing
  - File: `/backend/desideliver_backend/settings/__init__.py`
  - Estimated Time: 15 minutes

### Milestone 3: Dockerfile Creation
- [ ] Status: Not Started
- Description: Create multi-stage Dockerfile for development and production
- Estimated Duration: 2 hours
- Dependencies: Milestone 1, 2 complete

#### Tasks:
- [ ] Task 3.1: Create development stage in Dockerfile
  - Use `python:3.11-slim` as base image
  - Set working directory to `/app`
  - Install system dependencies (PostgreSQL client libs)
  - Copy requirements.txt and install Python dependencies
  - Copy application code
  - Create non-root user for security
  - Set proper file permissions
  - Expose port 8000
  - File: `/backend/Dockerfile`
  - Estimated Time: 1 hour

- [ ] Task 3.2: Create production stage in Dockerfile
  - Inherit from development stage or create separate optimized stage
  - Install additional production dependencies
  - Run `collectstatic` command
  - Configure Gunicorn as entrypoint
  - Optimize for smaller image size
  - File: `/backend/Dockerfile` (production target)
  - Estimated Time: 45 minutes

- [ ] Task 3.3: Test Dockerfile builds
  - Test: `docker build --target development -t desideliver-backend:dev .`
  - Test: `docker build --target production -t desideliver-backend:prod .`
  - Verify image sizes are reasonable (<500MB)
  - Estimated Time: 15 minutes

### Milestone 4: Entrypoint Script
- [ ] Status: Not Started
- Description: Create entrypoint script for container initialization
- Estimated Duration: 1 hour
- Dependencies: Milestone 3 complete

#### Tasks:
- [ ] Task 4.1: Create entrypoint.sh script
  - Wait for database to be ready (using pg_isready or Python script)
  - Run database migrations automatically
  - Collect static files (production only)
  - Start appropriate server (runserver for dev, gunicorn for prod)
  - Add error handling and logging
  - File: `/backend/entrypoint.sh`
  - Estimated Time: 45 minutes

- [ ] Task 4.2: Make entrypoint.sh executable
  - Run: `chmod +x entrypoint.sh`
  - Ensure line endings are Unix-style (LF, not CRLF)
  - Test script locally if possible
  - Estimated Time: 5 minutes

- [ ] Task 4.3: Update Dockerfile to use entrypoint
  - Copy entrypoint.sh into image
  - Set as ENTRYPOINT in Dockerfile
  - Configure CMD for default command
  - Estimated Time: 10 minutes

### Milestone 5: Docker Compose - Development Configuration
- [ ] Status: Not Started
- Description: Create docker-compose.yml for local development environment
- Estimated Duration: 2 hours
- Dependencies: Milestone 3, 4 complete

#### Tasks:
- [ ] Task 5.1: Create docker-compose.yml file
  - Set version to '3.9'
  - Define services structure
  - Configure networks
  - Define named volumes
  - File: `/backend/docker-compose.yml`
  - Estimated Time: 15 minutes

- [ ] Task 5.2: Configure PostgreSQL service
  - Use `postgres:15-alpine` image
  - Set environment variables: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - Create named volume: `postgres_data`
  - Expose port 5432 to host for debugging
  - Add healthcheck with pg_isready
  - File: `/backend/docker-compose.yml` (db service)
  - Estimated Time: 30 minutes

- [ ] Task 5.3: Configure Redis service
  - Use `redis:7-alpine` image
  - Expose port 6379 to host (optional)
  - Add healthcheck with redis-cli ping
  - Optional: Add named volume for persistence
  - File: `/backend/docker-compose.yml` (redis service)
  - Estimated Time: 20 minutes

- [ ] Task 5.4: Configure Django backend service
  - Build from local Dockerfile (development target)
  - Mount source code as volume for hot-reloading: `.:/app`
  - Set environment variables from .env file
  - Set DJANGO_SETTINGS_MODULE=desideliver_backend.settings.local
  - Expose port 8000
  - Add depends_on with service_healthy conditions
  - Override command to use runserver
  - File: `/backend/docker-compose.yml` (backend service)
  - Estimated Time: 45 minutes

- [ ] Task 5.5: Test docker-compose.yml
  - Create `.env` file from `.env.example`
  - Run: `docker-compose config` to validate syntax
  - Run: `docker-compose up --build`
  - Verify all services start successfully
  - Check health checks pass
  - Estimated Time: 10 minutes

### Milestone 6: Docker Compose - Production Configuration
- [ ] Status: Not Started
- Description: Create docker-compose.prod.yml for production deployment
- Estimated Duration: 1.5 hours
- Dependencies: Milestone 5 complete

#### Tasks:
- [ ] Task 6.1: Create docker-compose.prod.yml
  - Copy structure from docker-compose.yml
  - Remove development-specific configurations
  - File: `/backend/docker-compose.prod.yml`
  - Estimated Time: 15 minutes

- [ ] Task 6.2: Configure production PostgreSQL service
  - Do NOT expose port to host (security)
  - Use environment variables for credentials (no defaults)
  - Add resource limits (memory, CPU)
  - Configure restart policy: `restart: always`
  - Add production-grade healthcheck
  - File: `/backend/docker-compose.prod.yml` (db service)
  - Estimated Time: 30 minutes

- [ ] Task 6.3: Configure production Redis service
  - Do NOT expose port to host
  - Add persistence volume
  - Configure restart policy: `restart: always`
  - Add resource limits
  - File: `/backend/docker-compose.prod.yml` (redis service)
  - Estimated Time: 15 minutes

- [ ] Task 6.4: Configure production backend service
  - Build production target from Dockerfile
  - Do NOT mount source code (use image code)
  - Set DJANGO_SETTINGS_MODULE=desideliver_backend.settings.production
  - Use Gunicorn instead of runserver
  - Add resource limits
  - Configure restart policy: `restart: always`
  - Add healthcheck endpoint
  - File: `/backend/docker-compose.prod.yml` (backend service)
  - Estimated Time: 30 minutes

### Milestone 7: Environment Variables Configuration
- [ ] Status: Not Started
- Description: Complete .env.example and create local .env file
- Estimated Duration: 45 minutes
- Dependencies: Milestone 2 complete

#### Tasks:
- [ ] Task 7.1: Complete .env.example file
  - Document all required variables with comments
  - Provide example values for development
  - Group by category (Django, Database, Redis, Email, CORS)
  - Include security notes for production
  - File: `/backend/.env.example`
  - Estimated Time: 30 minutes

- [ ] Task 7.2: Create .env file for local development
  - Copy from .env.example: `cp .env.example .env`
  - Set appropriate development values
  - Generate new SECRET_KEY for development
  - Ensure .env is in .gitignore
  - File: `/backend/.env` (not committed to git)
  - Estimated Time: 15 minutes

### Milestone 8: Database Migration & Testing
- [ ] Status: Not Started
- Description: Migrate from SQLite to PostgreSQL and verify all data/models work
- Estimated Duration: 2 hours
- Dependencies: Milestone 5, 7 complete

#### Tasks:
- [ ] Task 8.1: Start Docker stack and verify services
  - Run: `docker-compose up -d`
  - Check: `docker-compose ps` (all services should be healthy)
  - View logs: `docker-compose logs -f`
  - Estimated Time: 15 minutes

- [ ] Task 8.2: Run migrations in PostgreSQL
  - Run: `docker-compose exec backend python manage.py migrate`
  - Verify all migrations apply successfully
  - Check for any migration errors
  - Estimated Time: 15 minutes

- [ ] Task 8.3: Create superuser in Docker
  - Run: `docker-compose exec backend python manage.py createsuperuser`
  - Create test superuser account
  - Estimated Time: 5 minutes

- [ ] Task 8.4: Load existing data (if applicable)
  - If backup exists: `docker-compose exec backend python manage.py loaddata backup_data.json`
  - Verify data loaded correctly
  - Check foreign key relationships
  - Estimated Time: 20 minutes

- [ ] Task 8.5: Test database connectivity
  - Access Django shell: `docker-compose exec backend python manage.py shell`
  - Test ORM queries: `CustomUser.objects.all()`, `Product.objects.all()`
  - Test creating and saving models
  - Verify relationships work (ForeignKey, ManyToMany)
  - Estimated Time: 20 minutes

- [ ] Task 8.6: Test Redis connectivity
  - Django shell: `docker-compose exec backend python manage.py shell`
  - Test cache: `from django.core.cache import cache`
  - Set value: `cache.set('test_key', 'test_value', 300)`
  - Get value: `cache.get('test_key')`
  - Estimated Time: 10 minutes

- [ ] Task 8.7: Test data persistence
  - Stop containers: `docker-compose down`
  - Start again: `docker-compose up -d`
  - Verify data still exists in database
  - Verify volumes were persisted
  - Estimated Time: 15 minutes

- [ ] Task 8.8: Connect with external database tool
  - Use pgAdmin, DBeaver, or psql
  - Connect to localhost:5432
  - Verify can browse database schema
  - Verify can run queries
  - Estimated Time: 20 minutes

### Milestone 9: API Testing & Verification
- [ ] Status: Not Started
- Description: Test all existing API endpoints work in Docker environment
- Estimated Duration: 2 hours
- Dependencies: Milestone 8 complete

#### Tasks:
- [ ] Task 9.1: Access Django admin interface
  - Navigate to: `http://localhost:8000/admin/`
  - Log in with superuser credentials
  - Verify admin interface loads correctly
  - Test CRUD operations on a model
  - Estimated Time: 15 minutes

- [ ] Task 9.2: Test authentication endpoints
  - POST to `/api/auth/register/` with test user data
  - POST to `/api/auth/login/` to get JWT tokens
  - Verify tokens are returned correctly
  - Test token refresh endpoint
  - Use Postman or curl for testing
  - Estimated Time: 30 minutes

- [ ] Task 9.3: Test products API endpoints
  - GET `/api/products/` to list products
  - GET `/api/products/{id}/` for detail view
  - Test filtering and search if implemented
  - Verify response format matches expectations
  - Estimated Time: 20 minutes

- [ ] Task 9.4: Test cart API endpoints
  - POST `/api/cart/add/` to add items
  - GET `/api/cart/` to view cart
  - PUT `/api/cart/update/{id}/` to update quantities
  - DELETE `/api/cart/remove/{id}/` to remove items
  - Test authentication requirement
  - Estimated Time: 30 minutes

- [ ] Task 9.5: Test orders API endpoints
  - POST `/api/orders/create/` to create order
  - GET `/api/orders/` to list user orders
  - GET `/api/orders/{id}/` for order detail
  - Test CSV generation if implemented
  - Verify email notifications (console backend)
  - Estimated Time: 25 minutes

### Milestone 10: Hot-Reloading & Development Workflow
- [ ] Status: Not Started
- Description: Verify development workflow with hot-reloading works correctly
- Estimated Duration: 1 hour
- Dependencies: Milestone 9 complete

#### Tasks:
- [ ] Task 10.1: Test code hot-reloading
  - With containers running, edit a view file
  - Make a small change (e.g., add print statement)
  - Verify Django dev server reloads automatically
  - Test API endpoint reflects the change
  - No need to rebuild containers
  - Estimated Time: 15 minutes

- [ ] Task 10.2: Test adding new dependencies
  - Add a new package to requirements.txt
  - Rebuild backend service: `docker-compose up --build backend`
  - Verify new package is available
  - Test import in Django shell
  - Estimated Time: 20 minutes

- [ ] Task 10.3: Test management commands
  - Create test data: `docker-compose exec backend python manage.py shell`
  - Run migrations: `docker-compose exec backend python manage.py migrate`
  - Create superuser: `docker-compose exec backend python manage.py createsuperuser`
  - Run custom commands if any exist
  - Estimated Time: 15 minutes

- [ ] Task 10.4: Test log viewing
  - View all logs: `docker-compose logs`
  - Follow logs: `docker-compose logs -f backend`
  - View specific service: `docker-compose logs db`
  - Verify logs are readable and helpful
  - Estimated Time: 10 minutes

### Milestone 11: Unit Tests Execution
- [ ] Status: Not Started
- Description: Run all existing Django tests in Docker environment
- Estimated Duration: 1.5 hours
- Dependencies: Milestone 8 complete

#### Tasks:
- [ ] Task 11.1: Run all tests
  - Execute: `docker-compose exec backend python manage.py test`
  - Verify all tests pass
  - Note any failing tests (may need fixes for PostgreSQL)
  - Estimated Time: 30 minutes

- [ ] Task 11.2: Run tests for individual apps
  - Test users app: `docker-compose exec backend python manage.py test users`
  - Test products app: `docker-compose exec backend python manage.py test products`
  - Test cart app: `docker-compose exec backend python manage.py test cart`
  - Test orders app: `docker-compose exec backend python manage.py test orders`
  - Test tickets app: `docker-compose exec backend python manage.py test tickets`
  - Estimated Time: 40 minutes

- [ ] Task 11.3: Fix any PostgreSQL-specific test issues
  - Address any SQLite vs PostgreSQL compatibility issues
  - Update test fixtures if needed
  - Rerun tests to verify fixes
  - Estimated Time: 20 minutes

### Milestone 12: Production Configuration Testing
- [ ] Status: Not Started
- Description: Test production Docker configuration locally
- Estimated Duration: 1.5 hours
- Dependencies: Milestone 6 complete

#### Tasks:
- [ ] Task 12.1: Create production .env file
  - Copy .env.example to .env.prod
  - Set production-appropriate values
  - Set DEBUG=False
  - Set strong SECRET_KEY
  - Set secure database password
  - File: `/backend/.env.prod` (not committed)
  - Estimated Time: 15 minutes

- [ ] Task 12.2: Build and start production stack
  - Build: `docker-compose -f docker-compose.prod.yml build`
  - Start: `docker-compose -f docker-compose.prod.yml up -d`
  - Verify services start successfully
  - Estimated Time: 15 minutes

- [ ] Task 12.3: Test production settings
  - Verify Gunicorn is running (not runserver)
  - Check logs: `docker-compose -f docker-compose.prod.yml logs backend`
  - Verify static files are served correctly
  - Test API endpoints work
  - Estimated Time: 20 minutes

- [ ] Task 12.4: Run Django security checks
  - Execute: `docker-compose -f docker-compose.prod.yml exec backend python manage.py check --deploy`
  - Address any security warnings
  - Fix settings as needed
  - Rerun checks until all pass
  - Estimated Time: 30 minutes

- [ ] Task 12.5: Test production health and restart
  - Stop one service: `docker-compose -f docker-compose.prod.yml stop backend`
  - Verify it restarts automatically (restart: always policy)
  - Check that health checks work
  - Estimated Time: 10 minutes

### Milestone 13: Documentation
- [ ] Status: Not Started
- Description: Create comprehensive documentation for Docker setup
- Estimated Duration: 2 hours
- Dependencies: All previous milestones complete

#### Tasks:
- [ ] Task 13.1: Update main README.md
  - Add "Docker Setup" section at the top
  - Include prerequisites (Docker, Docker Compose)
  - Add quick start guide (3-4 commands)
  - Add common commands cheat sheet
  - Link to detailed Docker documentation
  - File: `/backend/README.md`
  - Estimated Time: 45 minutes

- [ ] Task 13.2: Create detailed DOCKER.md guide
  - Architecture overview with diagram
  - Detailed setup instructions
  - Development workflow guide
  - Production deployment guide
  - Troubleshooting common issues
  - Volume management and backups
  - Environment variables reference
  - Scaling and performance tips
  - File: `/backend/docs/DOCKER.md` (create docs folder if needed)
  - Estimated Time: 1 hour

- [ ] Task 13.3: Add inline documentation
  - Add comments to Dockerfile explaining each step
  - Comment docker-compose.yml services and configurations
  - Document entrypoint.sh script logic
  - Add comments to settings files explaining differences
  - Estimated Time: 15 minutes

### Milestone 14: Performance Benchmarking
- [ ] Status: Not Started
- Description: Benchmark and compare Docker vs non-Docker performance
- Estimated Duration: 1 hour
- Dependencies: Milestone 9 complete

#### Tasks:
- [ ] Task 14.1: Benchmark API response times
  - Use Apache Bench or similar tool
  - Test key endpoints: products list, order creation
  - Run 100 requests: `ab -n 100 -c 10 http://localhost:8000/api/products/`
  - Record average response time
  - Estimated Time: 20 minutes

- [ ] Task 14.2: Monitor resource usage
  - Check memory usage: `docker stats`
  - Monitor CPU usage during load
  - Verify resource limits are appropriate
  - Adjust if needed
  - Estimated Time: 20 minutes

- [ ] Task 14.3: Test concurrent requests
  - Simulate multiple users (50-100 concurrent)
  - Verify no connection errors
  - Check database connection pool
  - Estimated Time: 20 minutes

### Milestone 15: Cleanup & Final Verification
- [ ] Status: Not Started
- Description: Final cleanup, verification, and preparation for team rollout
- Estimated Duration: 1 hour
- Dependencies: All previous milestones complete

#### Tasks:
- [ ] Task 15.1: Clean up old files
  - Remove or archive db.sqlite3
  - Remove old virtual environment folders (venv, env)
  - Clean up any temporary files
  - Ensure .gitignore is comprehensive
  - Estimated Time: 15 minutes

- [ ] Task 15.2: Final checklist verification
  - ✅ All services start successfully
  - ✅ All tests pass
  - ✅ Hot-reloading works
  - ✅ Data persists across restarts
  - ✅ Production config tested
  - ✅ Documentation complete
  - ✅ .env.example provided
  - ✅ Security checks pass
  - Estimated Time: 20 minutes

- [ ] Task 15.3: Create developer onboarding checklist
  - Document step-by-step setup for new developers
  - Test instructions on a clean machine (if possible)
  - Include troubleshooting for common issues
  - Add to README.md or DOCKER.md
  - Estimated Time: 25 minutes

## Technical Considerations

### Architecture Decisions

#### Docker Multi-Stage Builds
- Use multi-stage Dockerfile to separate development and production builds
- Development stage optimized for fast rebuilds with hot-reloading
- Production stage optimized for small image size and security
- Shared base to reduce redundancy

#### Settings Configuration Pattern
- **base.py**: Contains all shared settings (90% of configuration)
- **local.py**: Development overrides (DEBUG=True, console email, SQLite option)
- **production.py**: Production overrides (DEBUG=False, PostgreSQL, Redis, security)
- Easily extensible for staging, testing environments

#### Volume Strategy
- **Named Volumes**: For database data (postgres_data) - Docker-managed, better for production
- **Bind Mounts**: For source code in development - enables hot-reloading
- **No Volumes**: For production backend service - code is in image, not mounted

#### Network Configuration
- Default bridge network for development (simple, exposes ports)
- Internal networks for production (security, isolation)
- Services communicate via service names (DNS resolution)

### Technology Choices

#### Base Images
- **python:3.11-slim**: Balance of size and compatibility
- **postgres:15-alpine**: Latest stable PostgreSQL in minimal size
- **redis:7-alpine**: Latest Redis in minimal size
- Alpine variants save 50-70% image size

#### WSGI Server
- **Gunicorn**: Industry-standard, production-ready
- Configured with 4 workers (adjust based on CPU cores: `2 * cores + 1`)
- Timeout of 120 seconds for long-running requests
- Proper signal handling for graceful shutdowns

#### Static Files
- **WhiteNoise**: Serves static files efficiently from Django
- Eliminates need for separate Nginx container (simpler architecture)
- Supports compression and caching headers
- Can be upgraded to Nginx later if needed

### Integration Points

#### Django ORM → PostgreSQL
- All existing models work identically with PostgreSQL
- Migrations apply cleanly
- Use psycopg2-binary for PostgreSQL adapter
- Connection pooling handled by Django CONN_MAX_AGE setting

#### Django Cache → Redis
- Configure Redis as cache backend in production settings
- Use for session storage (optional)
- Prepared for Celery integration in future
- Fast in-memory storage for frequently accessed data

#### Environment Variables → Settings
- python-decouple or django-environ to load .env files
- Type conversion handled automatically (bool, int, list)
- Sensible defaults for non-critical settings
- Fail fast if critical variables missing

### Database Schema Changes
No schema changes required. However:
```python
# production.py - Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

### API Contract Definitions
No API changes. All endpoints remain identical:
```
# Authentication
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/

# Products
GET /api/products/
GET /api/products/{id}/

# Cart
POST /api/cart/add/
GET /api/cart/
PUT /api/cart/update/{id}/
DELETE /api/cart/remove/{id}/

# Orders
POST /api/orders/create/
GET /api/orders/
GET /api/orders/{id}/
```

## Testing Strategy

### Backend Testing

#### Docker Build Tests
```bash
# Test development build
docker build --target development -t desideliver-backend:dev .

# Test production build  
docker build --target production -t desideliver-backend:prod .

# Verify image sizes
docker images | grep desideliver-backend
# dev should be ~400-600MB, prod should be ~300-500MB
```

#### Docker Compose Tests
```bash
# Validate compose file syntax
docker-compose config
docker-compose -f docker-compose.prod.yml config

# Start services
docker-compose up -d

# Check service health
docker-compose ps
# All services should show "healthy"

# Check logs for errors
docker-compose logs backend | grep -i error
docker-compose logs db | grep -i error
```

#### Django Application Tests
```bash
# Run all tests
docker-compose exec backend python manage.py test

# Run with coverage (if installed)
docker-compose exec backend coverage run manage.py test
docker-compose exec backend coverage report

# Run specific test
docker-compose exec backend python manage.py test users.tests.UserAuthenticationTest
```

#### Settings Tests
```bash
# Verify development settings loaded
docker-compose exec backend python manage.py diffsettings | grep DEBUG
# Should show DEBUG = True

# Verify production settings
docker-compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
# Should pass all security checks
```

### Integration Testing

#### Database Connectivity
```bash
# Test from Django shell
docker-compose exec backend python manage.py shell
>>> from users.models import CustomUser
>>> CustomUser.objects.count()
>>> # Create test object
>>> user = CustomUser.objects.create_user(email='test@test.com', password='test123')
>>> user.save()
>>> CustomUser.objects.filter(email='test@test.com').exists()

# Test from pgAdmin
# Connect to localhost:5432
# Database: desideliver_dev
# User: desideliver_user
```

#### Redis Connectivity
```bash
# Test from Django shell
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test_key', 'hello', 300)
>>> cache.get('test_key')
'hello'

# Test with redis-cli
docker-compose exec redis redis-cli
> PING
PONG
> SET test "value"
OK
> GET test
"value"
```

#### API Integration Tests
```bash
# Test with curl
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get products (with JWT token)
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

### Performance Testing

#### Load Testing
```bash
# Install Apache Bench
# macOS: brew install httpd
# Linux: apt-get install apache2-utils

# Test product list endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/api/products/

# Test with authentication
ab -n 100 -c 10 -H "Authorization: Bearer <token>" http://localhost:8000/api/products/

# Monitor during load test
docker stats
```

#### Resource Monitoring
```bash
# Real-time resource usage
docker stats

# Specific service
docker stats desideliver_backend_1

# Check logs during load
docker-compose logs -f --tail=100 backend
```

### Manual Testing Checklist

#### Development Environment Setup
- [ ] Clone repository
- [ ] Copy `.env.example` to `.env`
- [ ] Run `docker-compose up --build`
- [ ] All services show "healthy" status
- [ ] Backend accessible at `http://localhost:8000`
- [ ] Admin interface accessible at `http://localhost:8000/admin/`
- [ ] Database accessible with pgAdmin (localhost:5432)

#### Development Workflow
- [ ] Code changes trigger automatic reload
- [ ] Can create migrations: `docker-compose exec backend python manage.py makemigrations`
- [ ] Can run migrations: `docker-compose exec backend python manage.py migrate`
- [ ] Can create superuser: `docker-compose exec backend python manage.py createsuperuser`
- [ ] Can access Django shell: `docker-compose exec backend python manage.py shell`
- [ ] Can view logs: `docker-compose logs -f backend`
- [ ] Tests run successfully: `docker-compose exec backend python manage.py test`

#### Data Persistence
- [ ] Create test data in database
- [ ] Stop containers: `docker-compose down`
- [ ] Start containers: `docker-compose up -d`
- [ ] Test data still exists
- [ ] Volumes show data: `docker volume ls`

#### API Functionality
- [ ] Can register new user
- [ ] Can log in and receive JWT tokens
- [ ] Can access protected endpoints with token
- [ ] Token refresh works
- [ ] CRUD operations work on all models
- [ ] Email notifications appear in console

#### Production Environment
- [ ] Production build completes: `docker-compose -f docker-compose.prod.yml build`
- [ ] Production stack starts: `docker-compose -f docker-compose.prod.yml up -d`
- [ ] Gunicorn is running (check logs)
- [ ] DEBUG is False (check via Django shell)
- [ ] Security checks pass: `python manage.py check --deploy`
- [ ] Static files served correctly
- [ ] Health checks pass
- [ ] Services restart on failure

## Risk Assessment

### Potential Blockers

#### 1. Docker Installation Issues
**Risk**: Developers may struggle with Docker Desktop installation or configuration
**Impact**: High - prevents entire setup
**Mitigation**:
- Provide detailed installation guides for macOS, Linux, Windows
- Include troubleshooting section in documentation
- Offer alternative: Docker Toolbox for older systems
- Have fallback: Keep non-Docker instructions available temporarily

#### 2. Port Conflicts
**Risk**: Ports 8000, 5432, 6379 may be in use by existing services
**Impact**: Medium - prevents services from starting
**Mitigation**:
- Document how to check for port conflicts: `lsof -i :8000`
- Provide instructions to change ports in docker-compose.yml
- Use non-standard ports by default (e.g., 8001, 5433, 6380)
- Add port conflict detection to documentation

#### 3. SQLite to PostgreSQL Migration Issues
**Risk**: Data migration may fail or lose data
**Impact**: High - data loss
**Mitigation**:
- Always create backup before migration: `dumpdata > backup.json`
- Test migration with sample data first
- Provide step-by-step migration guide
- Keep SQLite option available in local.py for fallback
- Document known SQLite-specific features that don't work in PostgreSQL

#### 4. File Permission Issues
**Risk**: Docker volume permissions may cause read/write errors (especially on Linux)
**Impact**: Medium - app won't start or can't write files
**Mitigation**:
- Run container as non-root user with matching host UID
- Document permission fix: `chown -R 1000:1000 /path/to/volume`
- Use proper WORKDIR and USER directives in Dockerfile
- Test on Linux environment before rollout

#### 5. Memory Constraints
**Risk**: Running 3+ services may exceed available RAM on developer machines
**Impact**: Medium - poor performance or crashes
**Mitigation**:
- Set memory limits in docker-compose.yml
- Monitor with `docker stats` during development
- Provide minimum system requirements (4GB RAM recommended)
- Allow running services individually (e.g., just backend + db, skip Redis initially)

#### 6. Hot-Reload Not Working
**Risk**: Code changes may not reflect without rebuilding containers
**Impact**: Medium - poor developer experience
**Mitigation**:
- Ensure proper volume mounting: `.:/app`
- Use `runserver` with `0.0.0.0:8000` binding
- Document that requirements.txt changes need rebuild
- Provide quick rebuild command: `docker-compose up --build backend`

#### 7. Environment Variable Confusion
**Risk**: Developers may use wrong environment variables or forget to create .env
**Impact**: Medium - services won't start or misconfigure
**Mitigation**:
- Provide clear .env.example with all variables documented
- Add environment variable validation in settings
- Fail fast with clear error messages if variables missing
- Include .env setup in quick start guide

### Mitigation Strategies

#### Comprehensive Documentation
- Step-by-step setup guide with screenshots
- Troubleshooting section addressing common issues
- Quick reference cheat sheet for common commands
- Video walkthrough for initial setup (optional)

#### Gradual Rollout
- Implement on development machine first
- Test with one other developer before full team rollout
- Offer Docker and non-Docker options in parallel initially
- Gather feedback and fix issues before mandating Docker

#### Health Checks & Monitoring
- Implement health checks for all services
- Add startup dependency management (depends_on with conditions)
- Monitor resource usage during development
- Set up alerts for service failures in production

#### Automated Testing
- Add Docker build to CI/CD pipeline
- Run integration tests in Docker environment
- Verify migrations work in PostgreSQL
- Test production configuration in staging environment

### Rollback Procedures

#### If Docker Setup Fails Completely
```bash
# Stop all Docker containers
docker-compose down -v

# Remove Docker images (optional)
docker rmi desideliver-backend:dev
docker rmi desideliver-backend:prod

# Fall back to traditional setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

#### If Database Migration Fails
```bash
# Restore from backup
docker-compose exec backend python manage.py flush --noinput
docker-compose exec backend python manage.py loaddata backup_data.json

# Or switch back to SQLite temporarily
# Edit .env: DB_ENGINE=django.db.backends.sqlite3
docker-compose restart backend
```

#### If Production Build Has Issues
```bash
# Roll back to previous working build
docker-compose -f docker-compose.prod.yml down
docker pull <registry>/desideliver-backend:<previous-tag>
docker-compose -f docker-compose.prod.yml up -d

# Or switch to development mode temporarily
docker-compose up -d
```

## Implementation Checklist

Before starting implementation:
- [ ] Team has reviewed and approved PRD
- [ ] All developers have Docker Desktop installed
- [ ] System requirements verified (RAM, disk space)
- [ ] Backup of current database created
- [ ] Development branch created: `git checkout -b feat/backend-dockerization`

During implementation:
- [ ] Follow milestones in order
- [ ] Test each milestone before proceeding
- [ ] Commit after each completed milestone
- [ ] Update documentation as you go
- [ ] Ask for help if blocked for more than 30 minutes

After implementation:
- [ ] All manual testing checklist items pass
- [ ] Documentation reviewed by another developer
- [ ] Changes merged to main branch
- [ ] Team notified of new Docker workflow
- [ ] Quick start guide shared with team
- [ ] Schedule onboarding session for team

## Success Metrics

Implementation is successful when:
1. ✅ New developer can set up entire environment in under 5 minutes
2. ✅ All existing tests pass in Docker environment
3. ✅ API performance is within 10% of non-Docker setup
4. ✅ All 5 developers have successfully migrated to Docker
5. ✅ No critical bugs reported in first week
6. ✅ Documentation is clear and complete (no questions asked more than twice)
7. ✅ Production deployment tested successfully
8. ✅ Data persistence verified across multiple restarts
9. ✅ Zero data loss during migration
10. ✅ Team productivity not impacted negatively

## Next Steps After Completion

1. **Frontend Dockerization** (Future milestone)
   - Dockerize React frontend
   - Create unified docker-compose.yml for full stack
   - Add Nginx reverse proxy

2. **CI/CD Integration**
   - Add Docker build to GitHub Actions
   - Automated testing in Docker environment
   - Push images to container registry

3. **Production Deployment**
   - Deploy to AWS ECS, Google Cloud Run, or DigitalOcean
   - Set up environment-specific configurations
   - Configure monitoring and logging

4. **Celery Integration**
   - Add Celery worker container
   - Add Celery beat for scheduled tasks
   - Add Flower for monitoring

5. **Database Optimizations**
   - Add PgBouncer for connection pooling
   - Configure automated backups
   - Set up read replicas if needed

---

**Ready to start implementation?** Begin with Milestone 1!

**Estimated completion**: 2-3 days of focused work, or 1 week if done incrementally alongside other tasks.

**Questions or blockers?** Refer to Risk Assessment section or ask for help.
