import sys
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent))

from database import Base, engine, get_db
from models.models import Post, User
from settings import Colors, settings
from config import config

config.logging.setup_logging()

try:
    Base.metadata.create_all(bind=engine)
    print(f"{Colors.GREEN}데이터베이스 연결 성공{Colors.RESET}")
except Exception as e:
    print(f"{Colors.RED}데이터베이스 연결 오류 발생: {e}{Colors.RESET}")
    print(
        f"{Colors.YELLOW}PostgreSQL이 실행 중인지 확인하세요: ./scripts/start-db.sh{Colors.RESET}"
    )

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for Blaybum application with PostgreSQL",
    docs_url=config.api.DOCS_URL,
    redoc_url=config.api.REDOC_URL,
    openapi_url=config.api.OPENAPI_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=config.cors.ALLOWED_METHODS,
    allow_headers=config.cors.ALLOWED_HEADERS,
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}


@app.get("/db-test")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT version()"))
        db_version = result.fetchone()[0]
        return {"status": "connected", "db_version": db_version}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
