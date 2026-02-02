# Blaybum Backend

FastAPI와 uvicorn을 사용한 백엔드 API 서버

## 🚀 빠른 시작

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
또는
```bash
cd app
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### 프로덕션 서버
```bash
./scripts/run_prod.sh
```

## 🐘 PostgreSQL 관리

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

## 📋 API 엔드포인트

- **GET /** - 루트 페이지
- **GET /health** - 헬스체크
- **GET /db-test** - 데이터베이스 연결 테스트
- **GET /api/v1/hello** - 테스트 API
- **GET /docs** - Swagger UI (API 문서)
- **GET /redoc** - ReDoc (API 문서)

## 🌐 접속 주소

- **API 서버**: http://127.0.0.1:8000
- **API 문서**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **pgAdmin**: http://localhost:5050 (관리자 도구)

## 📁 프로젝트 구조

```
blaybum-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # 메인 FastAPI 애플리케이션
│   ├── database.py      # 데이터베이스 연결 설정
│   ├── models/          # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   └── models.py
│   └── schemas/         # Pydantic 스키마
│       ├── __init__.py
│       └── schemas.py
├── scripts/            # 실행 스크립트들
│   ├── run_dev.sh      # 개발 서버 실행
│   ├── run_prod.sh     # 프로덕션 서버 실행
│   ├── start-db.sh     # PostgreSQL 시작
│   ├── stop-db.sh      # PostgreSQL 중지
│   └── db-status.sh    # 데이터베이스 상태 확인
├── docker/             # Docker 설정
│   └── postgres/
│       └── init/       # 데이터베이스 초기화 스크립트
├── .venv/              # Python 가상환경
├── .env                # 환경변수 설정
├── .gitignore          # Git 무시 파일
├── docker-compose.yml  # PostgreSQL Docker 구성
└── requirements.txt    # Python 의존성
├── requirements.txt    # Python 의존성
├── run_dev.sh         # 개발 서버 실행 스크립트
├── run_prod.sh        # 프로덕션 서버 실행 스크립트
└── README.md          # 프로젝트 설명서
```

## 🛠 개발 도구

### 코드 포맷팅 및 린팅 설치
```bash
pip install black isort flake8 pytest
```

### 코드 포맷팅
```bash
black app/
isort app/
```