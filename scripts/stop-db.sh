#!/bin/bash

echo "Stopping PostgreSQL..."

cd ..

docker-compose down

echo "PostgreSQL stopped successfully!"