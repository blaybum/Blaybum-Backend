#!/bin/bash

echo "Starting Blaybum FastAPI Production Server..."

cd "$(dirname "$0")/.."

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Starting production server with 4 workers..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

echo "✨ Production server started at http://0.0.0.0:8000"