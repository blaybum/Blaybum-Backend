#!/bin/bash

echo "PostgreSQL Status Check..."

cd ..

echo "Docker containers:"
docker-compose ps

echo ""
echo "PostgreSQL connection test:"
docker exec blaybum_postgres pg_isready -U blaybum_user -d blaybum_db 2>/dev/null

if [ $? -eq 0 ]; then
    echo "PostgreSQL is running and accepting connections"
    
    echo ""
    echo "Database information:"
    docker exec blaybum_postgres psql -U blaybum_user -d blaybum_db -c "SELECT version();" 2>/dev/null | head -3
    
    echo ""
    echo "Tables in database:"
    docker exec blaybum_postgres psql -U blaybum_user -d blaybum_db -c "\dt" 2>/dev/null
else
    echo "PostgreSQL is not running or not accessible"
fi