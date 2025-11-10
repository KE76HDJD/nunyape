#!/bin/bash

# Database migration script
set -e

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-appdb}
DB_USER=${DB_USER:-appuser}

echo "Running database migrations..."

# Check if required environment variables are set
if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD environment variable is not set"
    exit 1
fi

# Wait for database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready, running migrations..."

# Run migrations based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    # Production migrations
    for migration_file in migrations/prod/*.sql; do
        if [ -f "$migration_file" ]; then
            echo "Running migration: $migration_file"
            PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file"
        fi
    done
else
    # Development migrations
    for migration_file in migrations/dev/*.sql; do
        if [ -f "$migration_file" ]; then
            echo "Running migration: $migration_file"
            PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file"
        fi
    done
fi

# Run seed data if in development
if [ "$ENVIRONMENT" = "development" ] && [ -f "migrations/seed/seed_data.sql" ]; then
    echo "Seeding database with sample data..."
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "migrations/seed/seed_data.sql"
fi

echo "Migrations completed successfully!"