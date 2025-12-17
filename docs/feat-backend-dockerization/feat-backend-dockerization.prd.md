# Product Requirements Document: Backend Dockerization

## Title
Dockerize DesiDeliver Backend - Containerize Django application with PostgreSQL and Redis for development and production environments

## Overview
Containerize the DesiDeliver backend Django application using Docker and Docker Compose to provide consistent, reproducible development and production environments. This includes PostgreSQL database service, Redis for caching/task queue, and separate configurations for development and production deployments.

## Problem Statement
Currently, the DesiDeliver backend runs directly on the host machine with SQLite, requiring manual setup of Python virtual environments, database configurations, and dependencies. This creates several challenges:
- **Environment Inconsistency**: Different developers may have different Python versions, dependency versions, or OS configurations
- **Deployment Complexity**: Production deployment requires manual server setup and configuration
- **Database Limitations**: SQLite is not suitable for production workloads or concurrent access
- **Scalability**: Difficult to scale horizontally without containerization
- **Onboarding Friction**: New developers spend significant time setting up local environments
- **Testing Gaps**: Development and production environments differ significantly

Dockerization will solve these problems by providing:
- Identical environments across development, testing, and production
- One-command setup for new developers
- PostgreSQL for robust production database
- Redis for caching and background task processing
- Easy deployment to cloud platforms (AWS, GCP, Heroku, DigitalOcean)

## User Stories

### As a Backend Developer
- I want to start the entire backend stack with one command (`docker-compose up`) so that I can begin development quickly
- I want PostgreSQL running locally so that I can develop with the same database engine used in production
- I want hot-reloading to work in Docker so that code changes are reflected immediately without rebuilding
- I want to run migrations and management commands easily inside containers
- I want to access Django shell and database shell without complex setup

### As a DevOps Engineer
- I want separate Docker configurations for development and production so that I can optimize each environment appropriately
- I want environment variables managed securely through .env files
- I want database data persisted in Docker volumes so that data survives container restarts
- I want to easily deploy containers to cloud platforms
- I want logs centralized and accessible from containers

### As a New Team Member
- I want to set up the entire development environment in under 5 minutes
- I want clear documentation on Docker commands and workflows
- I want to avoid installing Python, PostgreSQL, and Redis directly on my machine

### As a System Administrator
- I want containers to restart automatically if they crash
- I want health checks to monitor service availability
- I want resource limits to prevent any single service from consuming all system resources
- I want easy backup and restore procedures for database volumes

## Functional Requirements

### 1. Docker Configuration
- Create `Dockerfile` for Django backend application
- Support multi-stage builds for optimized production images
- Use Python 3.11 or later as base image
- Install all dependencies from `requirements.txt`
- Configure proper file permissions and non-root user
- Set appropriate working directory and environment variables

### 2. Docker Compose Setup
- Create `docker-compose.yml` for development environment
- Create `docker-compose.prod.yml` for production environment
- Define three services:
  - **backend**: Django application
  - **db**: PostgreSQL 15+ database
  - **redis**: Redis 7+ cache/message broker
- Configure service dependencies (backend depends on db and redis)
- Set up internal Docker network for service communication
- Configure restart policies for production

### 3. Database Configuration
- **Development**: 
  - PostgreSQL database with persistent volume
  - Database name: `desideliver_dev`
  - Default credentials for easy local development
  - Accessible on localhost:5432 for external tools (pgAdmin, DBeaver)
- **Production**:
  - PostgreSQL with secure credentials from environment variables
  - Database name from environment variable
  - Not exposed to host (internal Docker network only)
  - Automated backups via volume snapshots

### 4. Redis Configuration
- Redis service for caching and Celery task queue
- Persistent volume for Redis data (optional for dev, required for prod)
- Default Redis port 6379 internally
- No authentication for development
- Authentication required for production

### 5. Settings Configuration Split
- Create `desideliver_backend/settings/` directory
- Create `__init__.py`, `base.py`, `local.py`, `production.py`
- **base.py**: Shared settings for all environments
- **local.py**: Development-specific settings (DEBUG=True, console email, verbose logging)
- **production.py**: Production settings (DEBUG=False, PostgreSQL, Redis cache, security headers)
- Use environment variable `DJANGO_SETTINGS_MODULE` to switch configurations

### 6. Environment Variables Management
- Create `.env.example` template file with all required variables
- Create `.env` file for local development (gitignored)
- Support environment variables for:
  - Django SECRET_KEY
  - DEBUG mode
  - Database credentials (host, port, name, user, password)
  - Redis connection string
  - Email configuration (SendGrid API key)
  - ALLOWED_HOSTS
  - CORS_ALLOWED_ORIGINS
- Load environment variables using python-decouple or django-environ

### 7. Volume Management
- **Database Volume**: Persist PostgreSQL data across container restarts
- **Static Files Volume**: Store Django static files for production
- **Media Files Volume**: Store user uploads (if applicable)
- **Redis Volume** (optional): Persist Redis data for production
- Use named Docker volumes (not bind mounts) for data persistence

### 8. Development Workflow
- Hot-reloading: Mount source code as volume for live updates
- Run migrations on container startup (via entrypoint script)
- Collect static files automatically
- Create superuser via management command
- Access Django shell: `docker-compose exec backend python manage.py shell`
- Run tests: `docker-compose exec backend python manage.py test`
- View logs: `docker-compose logs -f backend`

### 9. Production Optimizations
- Multi-stage Docker build to reduce image size
- Use Gunicorn as WSGI server instead of Django dev server
- Configure Gunicorn workers based on CPU cores
- Serve static files via WhiteNoise or separate Nginx container
- Health check endpoints for monitoring
- Resource limits (CPU, memory) for each service
- Security: Run as non-root user, minimal base image

## Technical Requirements

### Backend Changes

#### Django App: Core (`desideliver_backend`)

**New Files to Create**:
1. `/backend/Dockerfile`
2. `/backend/docker-compose.yml`
3. `/backend/docker-compose.prod.yml`
4. `/backend/.env.example`
5. `/backend/.dockerignore`
6. `/backend/entrypoint.sh`
7. `/backend/desideliver_backend/settings/__init__.py`
8. `/backend/desideliver_backend/settings/base.py`
9. `/backend/desideliver_backend/settings/local.py`
10. `/backend/desideliver_backend/settings/production.py`

**Files to Modify**:
1. `/backend/requirements.txt` - Add production dependencies (gunicorn, psycopg2-binary, whitenoise, django-environ)
2. `/backend/.gitignore` - Add Docker-specific ignores (.env, docker volumes)
3. `/backend/README.md` - Update with Docker setup and usage instructions

**Settings Split Structure**:
```
desideliver_backend/
├── settings/
│   ├── __init__.py          # Loads appropriate settings module
│   ├── base.py              # Shared settings
│   ├── local.py             # Development settings (inherits base)
│   └── production.py        # Production settings (inherits base)
├── urls.py
├── wsgi.py
└── asgi.py
```

### Database Schema
No database schema changes required. However:
- Migrate from SQLite to PostgreSQL
- Existing migrations will be run against PostgreSQL
- Database connection will be configured via environment variables

### Infrastructure Requirements

#### Docker Images
- **Base Image**: `python:3.11-slim` or `python:3.11-alpine`
- **PostgreSQL Image**: `postgres:15-alpine`
- **Redis Image**: `redis:7-alpine`

#### System Requirements
- Docker Engine 20.10+
- Docker Compose 2.0+
- Minimum 2GB RAM for all services
- 10GB disk space for images and volumes

## API Specifications

No new API endpoints required. All existing endpoints remain unchanged:
- `POST /api/auth/login/`
- `POST /api/auth/register/`
- `GET /api/products/`
- `POST /api/cart/add/`
- `POST /api/orders/create/`
- etc.

**API Behavior Changes**:
- All endpoints will work identically
- API will be accessible at `http://localhost:8000` (development)
- Production API URL will depend on deployment platform

## Configuration Specifications

### Dockerfile Structure
```dockerfile
# Development stage
FROM python:3.11-slim as development
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production stage
FROM python:3.11-slim as production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "desideliver_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml (Development)
```yaml
version: '3.9'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=desideliver_dev
      - POSTGRES_USER=desideliver_user
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U desideliver_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      target: development
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=desideliver_backend.settings.local
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: python manage.py runserver 0.0.0.0:8000

volumes:
  postgres_data:
```

### Environment Variables (.env.example)
```bash
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
DJANGO_SETTINGS_MODULE=desideliver_backend.settings.local
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=desideliver_dev
DB_USER=desideliver_user
DB_PASSWORD=dev_password
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SENDGRID_API_KEY=

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## UI/UX Requirements

No UI changes required. This is a backend infrastructure change only.

## Success Criteria

### Functional Acceptance Criteria
- [ ] Django backend starts successfully in Docker container
- [ ] PostgreSQL database is accessible and migrations run successfully
- [ ] Redis service is accessible from Django backend
- [ ] All existing API endpoints work identically to non-Docker setup
- [ ] Hot-reloading works in development mode (code changes reflect without rebuild)
- [ ] Django admin interface is accessible at `http://localhost:8000/admin/`
- [ ] Database data persists across container restarts
- [ ] Management commands work: `docker-compose exec backend python manage.py {command}`
- [ ] Tests run successfully: `docker-compose exec backend python manage.py test`
- [ ] Production configuration starts with Gunicorn (not dev server)
- [ ] Environment variables are loaded correctly from .env file
- [ ] Settings split works: local.py for dev, production.py for prod

### Performance Requirements
- [ ] Container startup time under 30 seconds (including health checks)
- [ ] API response times unchanged from non-Docker setup
- [ ] Database query performance equivalent to native PostgreSQL
- [ ] Docker image size under 500MB (production image)
- [ ] Memory usage under 1GB for all services combined (development)

### Developer Experience Goals
- [ ] New developer can start entire stack with: `cp .env.example .env && docker-compose up`
- [ ] Documentation includes all common Docker commands
- [ ] Clear error messages if required environment variables are missing
- [ ] Database can be accessed with GUI tools (pgAdmin, DBeaver) for debugging

## Security Considerations

### Authentication & Authorization
- No changes to existing JWT authentication
- All existing permission classes remain functional
- Admin interface protected by Django authentication

### Container Security
- **Non-root User**: Django container runs as non-root user (UID 1000)
- **Minimal Base Image**: Use Alpine or slim variants to reduce attack surface
- **Read-only Filesystem**: Container filesystem is read-only except for necessary writable directories
- **No Unnecessary Packages**: Production image contains only runtime dependencies
- **Security Scanning**: Images should be scanned with tools like Trivy or Snyk

### Environment Variables Security
- **Secret Key**: Never commit actual SECRET_KEY to git
- **Database Credentials**: Use strong passwords in production
- **Environment Files**: `.env` must be in `.gitignore`
- **Docker Secrets**: Consider using Docker secrets for production instead of .env
- **Credential Rotation**: Document process for rotating database and Redis passwords

### Network Security
- **Internal Network**: Database and Redis are not exposed to public internet in production
- **Port Binding**: Only expose necessary ports (8000 for backend)
- **CORS Configuration**: Restrict CORS_ALLOWED_ORIGINS to known frontend domains
- **Database Access**: PostgreSQL accessible only from backend container in production

### Input Validation
- No changes required - existing Django validation remains
- Ensure environment variable validation (fail fast if required vars missing)
- Validate .env file format on startup

## Constraints & Assumptions

### Constraints
- **Docker Required**: All developers must have Docker and Docker Compose installed
- **Resource Availability**: Development machines must have 2GB+ RAM available
- **Port Conflicts**: Ports 8000, 5432, 6379 must be available on host
- **Volume Storage**: Sufficient disk space for Docker volumes (10GB recommended)
- **No Frontend Changes**: Frontend will continue to run separately (not dockerized in this phase)

### Assumptions
- Developers are familiar with basic Docker commands
- PostgreSQL 15+ is compatible with all existing Django models and queries
- Redis will be used for future Celery task queue implementation
- Production deployment will use a container orchestration platform (ECS, Kubernetes, or Heroku)
- Static files will be served by WhiteNoise in production (no separate Nginx container initially)
- Media files (if any) can be stored in Docker volumes or S3 in the future

### Technical Assumptions
- Python 3.11+ is compatible with all dependencies
- SQLite to PostgreSQL migration will not require model changes
- Existing migrations will work with PostgreSQL without modifications
- Docker host networking is available for development
- Build context size is reasonable (under 100MB excluding node_modules, venv)

## Dependencies

### External Services
- **Docker Hub**: For pulling base images (python, postgres, redis)
- **PyPI**: For installing Python packages during build
- **SendGrid** (optional): Email service (existing dependency)

### Existing Features
- All existing Django apps: users, products, cart, orders, tickets
- All existing models, serializers, views, and URLs
- Django REST Framework configuration
- JWT authentication system
- CORS configuration
- Email notification system

### Third-Party Libraries
**New Production Dependencies** (to add to requirements.txt):
- `gunicorn==21.2.0` - WSGI HTTP server for production
- `whitenoise==6.6.0` - Serve static files in production
- `django-environ==0.11.2` - Simplified environment variable parsing

**Already Installed**:
- `psycopg2-binary==2.9.10` - PostgreSQL adapter (already in requirements.txt)
- `python-decouple==3.8` - Environment variable management (already in requirements.txt)

### Infrastructure Dependencies
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (for version control)
- PostgreSQL client tools (optional, for debugging)

## Testing Requirements

### Backend Testing

#### Docker Build Testing
```bash
# Test development build
docker build --target development -t desideliver-backend:dev .

# Test production build
docker build --target production -t desideliver-backend:prod .

# Verify image size
docker images desideliver-backend

# Test container startup
docker run --rm -p 8000:8000 desideliver-backend:dev
```

#### Docker Compose Testing
```bash
# Test development stack
docker-compose up -d
docker-compose ps
docker-compose logs backend

# Test health checks
docker-compose ps | grep healthy

# Test database connectivity
docker-compose exec backend python manage.py dbshell

# Test Redis connectivity
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

#### Django Application Testing
```bash
# Run all tests in Docker
docker-compose exec backend python manage.py test

# Run specific app tests
docker-compose exec backend python manage.py test users
docker-compose exec backend python manage.py test products
docker-compose exec backend python manage.py test orders

# Test migrations
docker-compose exec backend python manage.py makemigrations --check
docker-compose exec backend python manage.py migrate --check
```

#### Settings Configuration Testing
```bash
# Test local settings
docker-compose exec backend python manage.py diffsettings

# Test production settings
docker-compose -f docker-compose.prod.yml exec backend python manage.py check --deploy

# Verify SECRET_KEY is loaded
docker-compose exec backend python manage.py shell
>>> from django.conf import settings
>>> print(settings.SECRET_KEY)
```

### Integration Testing

#### API Endpoint Testing
- Test all existing API endpoints work identically in Docker
- Test JWT authentication with Docker-hosted backend
- Test CORS with frontend (if running)
- Test file uploads (if applicable)
- Test email sending (console backend for dev)

#### Database Testing
- Verify all migrations run successfully
- Test data persistence across container restarts
- Test database backup and restore
- Verify foreign key relationships work correctly
- Test concurrent database access

#### Performance Testing
- Benchmark API response times (should be within 10% of non-Docker)
- Test concurrent requests (100+ simultaneous users)
- Monitor memory usage under load
- Test container restart time

### Manual Testing Checklist

#### Development Environment
- [ ] `docker-compose up` starts all services without errors
- [ ] Backend accessible at `http://localhost:8000`
- [ ] Django admin accessible at `http://localhost:8000/admin/`
- [ ] Database accessible with pgAdmin on localhost:5432
- [ ] Code changes reflect immediately (hot-reload)
- [ ] Logs visible with `docker-compose logs -f`
- [ ] Can create superuser: `docker-compose exec backend python manage.py createsuperuser`
- [ ] Can run migrations: `docker-compose exec backend python manage.py migrate`
- [ ] Can access Django shell: `docker-compose exec backend python manage.py shell`
- [ ] Data persists after `docker-compose down && docker-compose up`

#### Production Environment
- [ ] Production build completes successfully
- [ ] Gunicorn starts and serves requests
- [ ] Static files served correctly
- [ ] DEBUG=False in production settings
- [ ] Security checks pass: `python manage.py check --deploy`
- [ ] Environment variables loaded from .env
- [ ] Database credentials secured
- [ ] Health checks work
- [ ] Containers restart automatically on failure

#### Cross-Environment Testing
- [ ] Can switch between local and production settings
- [ ] Database migrations work in both environments
- [ ] Tests pass in both environments
- [ ] Environment-specific settings applied correctly

## Documentation Requirements

### README.md Updates
Add comprehensive Docker setup section:
- Prerequisites (Docker, Docker Compose installation)
- Quick start guide (3 steps: clone, configure, run)
- Environment variables explanation
- Common Docker commands cheat sheet
- Troubleshooting guide
- Migration guide from non-Docker setup

### New Documentation Files
Create `/backend/docs/DOCKER.md`:
- Detailed Docker architecture explanation
- Development workflow with Docker
- Production deployment guide
- Volume management and backups
- Scaling and performance tuning
- Security best practices

### Code Comments
- Document Dockerfile stages and commands
- Explain docker-compose service configurations
- Comment entrypoint.sh script logic
- Document settings split rationale

## Migration Strategy

### From Existing Non-Docker Setup

#### For Current Developers
1. **Export SQLite Data** (if preserving data):
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Install Docker**:
   - macOS: Docker Desktop
   - Linux: Docker Engine + Docker Compose plugin
   - Windows: Docker Desktop with WSL2

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with appropriate values
   ```

4. **Start Docker Stack**:
   ```bash
   docker-compose up -d
   ```

5. **Import Data** (if needed):
   ```bash
   docker-compose exec backend python manage.py loaddata data.json
   ```

6. **Verify Setup**:
   ```bash
   docker-compose exec backend python manage.py test
   ```

#### For New Developers
1. Clone repository
2. Copy `.env.example` to `.env`
3. Run `docker-compose up`
4. Access application at `http://localhost:8000`

### Data Migration from SQLite to PostgreSQL
- SQLite data dump will work with PostgreSQL
- Use `dumpdata` and `loaddata` commands
- Test migration on sample data first
- Verify all models and relationships after migration

### Rollback Plan
If Docker setup fails:
1. Keep existing non-Docker setup intact initially
2. Document known issues and solutions
3. Provide non-Docker instructions as fallback
4. Fix Docker issues before removing non-Docker support

## Timeline Estimate

**Total Estimated Duration**: 2-3 days

**Complexity**: Medium

**Breakdown**:
- Docker configuration: 4-6 hours
- Settings split: 2-3 hours
- Environment variable setup: 1-2 hours
- Testing and debugging: 4-6 hours
- Documentation: 2-3 hours

## Future Enhancements

### Phase 2 (Future Scope)
- Dockerize frontend React application
- Single docker-compose.yml for full-stack development
- Nginx reverse proxy container

### Phase 3 (Future Scope)
- Celery worker container for background tasks
- Celery beat container for scheduled tasks
- Flower container for Celery monitoring

### Phase 4 (Future Scope)
- Kubernetes deployment manifests
- CI/CD pipeline with Docker builds
- Multi-stage deployments (staging, production)
- Container registry setup (ECR, GCR, DockerHub)

### Potential Improvements
- Redis caching for API responses
- Database connection pooling (PgBouncer)
- Separate Nginx container for static files
- Monitoring stack (Prometheus, Grafana)
- Centralized logging (ELK stack)
- Automated database backups

---

## Approval Checklist

Before proceeding to development plan:
- [ ] Docker architecture approved (PostgreSQL + Redis + Django)
- [ ] Settings split approach confirmed (base/local/production)
- [ ] Environment variable strategy approved (.env files)
- [ ] Volume management strategy confirmed
- [ ] Development and production separation clear
- [ ] Testing strategy acceptable
- [ ] Documentation requirements understood
- [ ] Timeline and complexity estimate reasonable

**Next Steps**: Upon approval, create detailed development plan with milestones and tasks.
