# Blaybum Backend

FastAPI와 uvicorn을 사용한 백엔드 API 서버

## 빠른 시작

### 1. 가상환경 활성화
```bash
source .venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. PostgreSQL 시작
```bash
./scripts/start-db.sh
```

### 4. 서버 실행

#### 개발 서버 (Hot Reload)
```bash
./scripts/run_dev.sh
```

#### 프로덕션 서버
```bash
./scripts/run_prod.sh
```

## PostgreSQL 관리

### 데이터베이스 시작
```bash
./scripts/start-db.sh
```

### 데이터베이스 중지
```bash
./scripts/stop-db.sh
```

### 데이터베이스 상태 확인
```bash
./scripts/db-status.sh
```

## API 엔드포인트

- **GET /** - 루트 페이지
- **GET /health** - 헬스체크
- **GET /db-test** - 데이터베이스 연결 테스트
- **GET /api/v1/hello** - 테스트 API
- **GET /docs** - Swagger UI (API 문서)
- **GET /redoc** - ReDoc (API 문서)

## 접속 주소

- **API 서버**: http://127.0.0.1:8000
- **API 문서**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **pgAdmin**: http://localhost:5050
