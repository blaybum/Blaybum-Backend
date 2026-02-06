#!/bin/bash

echo "Starting Blaybum FastAPI Development Server..."

cd "$(dirname "$0")/.."

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Starting server with hot reload..."
nohup uvicorn app.main:app --reload --host 127.0.0.1 --port 8000