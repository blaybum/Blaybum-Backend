#!/bin/bash

echo "Starting PostgreSQL with Docker Compose..."

cd "$(dirname "$0")/.."

docker-compose up -d postgres

echo "Waiting for PostgreSQL to start..."
sleep 10

echo "Testing PostgreSQL connection..."
docker exec blaybum_postgres pg_isready -U blaybum_user -d blaybum_db

if [ $? -eq 0 ]; then
    echo "PostgreSQL is ready!"
    echo "Database: blaybum_db"
    echo "User: blaybum_user"
    echo "pgAdmin is also available at http://localhost:5050"
    echo "Email: admin@blaybum.com"
    echo "Password: admin123"
else
    echo "Failed to connect to PostgreSQL"
fi