#!/bin/bash

# Exit on error
set -e

echo "🔧 Starting entrypoint script..."

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL to be ready..."
    
    while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-desideliver_user}" > /dev/null 2>&1; do
        echo "⏳ PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    
    echo "✅ PostgreSQL is ready!"
}

# Function to wait for Redis
wait_for_redis() {
    echo "⏳ Waiting for Redis to be ready..."
    
    # Extract redis host from REDIS_URL or use default
    REDIS_HOST=$(echo "${REDIS_URL:-redis://redis:6379/0}" | sed -e 's|redis://||' -e 's|:[0-9]*.*||')
    
    while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/${REDIS_HOST}/6379" 2>/dev/null; do
        echo "⏳ Redis is unavailable - sleeping"
        sleep 2
    done
    
    echo "✅ Redis is ready!"
}

# Wait for database and redis
wait_for_postgres
wait_for_redis

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files (only in production)
if [ "$DJANGO_SETTINGS_MODULE" = "desideliver_backend.settings.production" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "✅ Entrypoint script completed successfully!"
echo "🚀 Starting application..."

# Execute the main container command
exec "$@"
