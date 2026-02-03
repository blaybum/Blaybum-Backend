from app.settings import Colors, settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print(f"{Colors.BLUE} 연결중인 데이터베이스: {settings.database_url}{Colors.RESET}")

try:
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"{Colors.GREEN} 데이터베이스 엔진 생성 성공{Colors.RESET}")
except Exception as e:
    print(f"{Colors.RED} 데이터베이스 엔진 생성 실패: {e}{Colors.RESET}")
    raise

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
