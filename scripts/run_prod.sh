#!/bin/bash

echo "Starting Blaybum FastAPI Production Server..."

cd "$(dirname "$0")/.."

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

pip3 install -r requirements.txt

nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4