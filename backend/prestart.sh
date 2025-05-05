#!/bin/bash
set -e  # Exit on error

# This script runs before the main application starts
# It's used for tasks like running migrations, checking connections, etc.

echo "Running prestart script..."
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Install required packages for health check - do this quietly
echo "Installing requests package for health checks..."
pip install requests --quiet --no-cache-dir

# Make sure the expected directories exist
mkdir -p cache
mkdir -p logs
echo "Created cache and logs directories"

# Wait for database if needed (for Railway deployments)
if [ ! -z "$DATABASE_URL" ]; then
  echo "Database URL found, attempting database connection..."
  
  # If psycopg2 is missing, install it
  if ! python -c "import psycopg2" 2>/dev/null; then
    echo "psycopg2 not installed, installing..."
    pip install psycopg2-binary --quiet --no-cache-dir
  fi
  
  # Test database connection but don't fail if it doesn't connect
  python -c "
import sys
import psycopg2
import time
try:
    print('Attempting database connection...')
    conn = psycopg2.connect('$DATABASE_URL')
    print('Database connection successful!')
    conn.close()
except Exception as e:
    print(f'DB connection warning: {e}')
    print('Continuing startup anyway...')
"
else
  echo "No DATABASE_URL found, skipping database check"
fi

# Run migrations if MIGRATE is set to true
if [ "$MIGRATE" = "true" ] && [ ! -z "$DATABASE_URL" ]; then
  echo "Running database migrations..."
  alembic upgrade head || echo "Migrations failed, but continuing startup"      
else
  echo "Skipping migrations (MIGRATE not set to true or no DATABASE_URL)"       
fi

# Check if API keys are set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "WARNING: OPENAI_API_KEY not set! Mock data will be used."
fi

# Run deployment health check
echo "Running deployment health check..."
# Set temporary environment variables for the health check if not already set
if [ -z "$ENVIRONMENT" ]; then
  export ENVIRONMENT="production"
  echo "Setting temporary ENVIRONMENT=production for health check"
fi

if [ -z "$PORT" ]; then
  export PORT="8000"
  echo "Setting temporary PORT=8000 for health check"
fi

# Skip health endpoint check during prestart (since server isn't running yet)
python health_check.py --skip-health

echo "Prestart script completed successfully" 