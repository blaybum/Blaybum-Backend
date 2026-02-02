#!/bin/bash

echo "Starting Blaybum FastAPI Development Server..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Starting server with hot reload..."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

echo "Server started at http://127.0.0.1:8000"
echo "API Docs available at http://127.0.0.1:8000/docs"