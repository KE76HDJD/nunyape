#!/bin/bash

# Script to generate secrets for the application
set -e

echo "Generating application secrets..."

# Create secrets directory if it doesn't exist
mkdir -p secrets

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 64)
echo "JWT_SECRET=$JWT_SECRET" > secrets/jwt.env

# Generate database passwords
DB_PASSWORD=$(openssl rand -base64 32)
echo "DB_PASSWORD=$DB_PASSWORD" > secrets/database.env

# Generate API keys
STRIPE_SECRET_KEY="sk_test_$(openssl rand -hex 20)"
echo "STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY" >> secrets/api.env

SENDGRID_API_KEY="SG.$(openssl rand -base64 32 | tr -d '=' | tr '+/' '-_')"
echo "SENDGRID_API_KEY=$SENDGRID_API_KEY" >> secrets/api.env

# Generate encryption key for sensitive data
ENCRYPTION_KEY=$(openssl rand -base64 32)
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> secrets/app.env

# Generate OAuth client secrets
GOOGLE_CLIENT_SECRET=$(openssl rand -base64 32 | tr -d '=' | tr '+/' '-_')
echo "GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET" >> secrets/oauth.env

GITHUB_CLIENT_SECRET=$(openssl rand -base64 32 | tr -d '=' | tr '+/' '-_')
echo "GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET" >> secrets/oauth.env

# Set proper permissions
chmod 600 secrets/*.env

echo "Secrets generated successfully in ./secrets/"
echo "Warning: Keep these secrets secure and do not commit to version control!"