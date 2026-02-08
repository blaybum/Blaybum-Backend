#!/bin/bash

echo "Stopping PostgreSQL..."

cd "$(dirname "$0")/.."

docker-compose down

echo "PostgreSQL stopped successfully!"