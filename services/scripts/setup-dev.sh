#!/bin/bash

# Development environment setup script
set -e

echo "Setting up development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is installed (if needed)
if ! command -v node &> /dev/null; then
    echo "Warning: Node.js is not installed (optional for some services)"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-dev.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p logs
mkdir -p data
mkdir -p secrets
mkdir -p migrations/dev
mkdir -p migrations/prod
mkdir -p migrations/seed

# Generate default environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env << EOL
# Development Environment Configuration
ENVIRONMENT=development
DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=devpassword

# JWT Configuration
JWT_SECRET=dev_jwt_secret_change_in_production
JWT_EXPIRATION=3600

# Service URLs
AUTH_SERVICE_URL=http://localhost:8000
PAYMENT_SERVICE_URL=http://localhost:8080
PRESENTATION_SERVICE_URL=http://localhost:8001
QA_SERVICE_URL=http://localhost:8081

# External APIs
STRIPE_SECRET_KEY=sk_test_example
SENDGRID_API_KEY=SG.example

# Feature Flags
ENABLE_EMAILS=False
ENABLE_PAYMENTS=True
ENABLE_ANALYTICS=False
EOL
    echo "Created .env file. Please review and update the values."
fi

# Set up pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "Setting up pre-commit hooks..."
    pre-commit install
else
    echo "pre-commit not installed, skipping hook setup"
fi

# Create docker-compose for development
if [ ! -f "docker-compose.dev.yml" ]; then
    echo "Creating docker-compose.dev.yml..."
    cat > docker-compose.dev.yml << EOL
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations/dev:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

volumes:
  postgres_data:
EOL
fi

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and update the .env file with your configuration"
echo "2. Start services: docker-compose -f docker-compose.dev.yml up -d"
echo "3. Run migrations: ./scripts/run-migrations.sh"
echo "4. Seed database: python scripts/seed-database.py"
echo "5. Start the application services"
echo ""