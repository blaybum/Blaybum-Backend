#!/bin/bash

echo "Starting Blaybum FastAPI Production Server..."

cd "$(dirname "$0")/.."

# 가상환경 확인 및 활성화
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment is active: $VIRTUAL_ENV"
else
    echo "Activating virtual environment..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
fi

# 패키지 설치
echo "Installing/updating dependencies..."
pip3 install -r requirements.txt

# 로그 디렉토리 생성
mkdir -p logs

# 기존 프로세스 정리 (선택사항, Pre-deployment Cleanup에서 이미 했다면 불필요)
# pkill -f "uvicorn app.main:app" || true

# 백그라운드로 uvicorn 실행
echo "Starting uvicorn server..."
nohup uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    > logs/app.log 2>&1 &

# PID 저장
echo $! > logs/app.pid

echo "Server started with PID: $(cat logs/app.pid)"
echo "Logs: logs/app.log"

# 서버 시작 대기
sleep 3

# 프로세스 확인
if ps -p $(cat logs/app.pid) > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server failed to start"
    exit 1
fi