#!/bin/bash

echo "Starting Blaybum FastAPI Production Server..."

cd "$(dirname "$0")/.."

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
fi

echo "Installing/updating dependencies..."
pip3 install -r requirements.txt

mkdir -p logs

pkill -f "uvicorn app.main:app" || true

echo "Starting uvicorn server..."
nohup uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    > logs/app.log 2>&1 &

echo $! > logs/app.pid

echo "Server started with PID: $(cat logs/app.pid)"
echo "Logs: logs/app.log"

sleep 3

if ps -p $(cat logs/app.pid) > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server failed to start"
    exit 1
fi