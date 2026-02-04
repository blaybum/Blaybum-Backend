import time
from typing import Generator, Optional

import redis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.settings import Colors, settings


def retry_db_connection(engine, retries: int = 3) -> bool:
    """데이터베이스 연결 재시도"""
    for attempt in range(retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"{Colors.GREEN} 데이터베이스 연결 재시도 성공 (시도 {attempt + 1}/{retries}){Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.YELLOW} 데이터베이스 연결 재시도 {attempt + 1}/{retries} 실패: {e}{Colors.RESET}")
            if attempt < retries - 1:
                time.sleep(2)
    return False


def retry_redis_connection(redis_client, retries: int = 3) -> bool:
    """Redis 연결 재시도"""
    for attempt in range(retries):
        try:
            redis_client.ping()
            print(f"{Colors.GREEN} Redis 연결 재시도 성공 (시도 {attempt + 1}/{retries}){Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.YELLOW} Redis 연결 재시도 {attempt + 1}/{retries} 실패: {e}{Colors.RESET}")
            if attempt < retries - 1:
                time.sleep(2)
    return False


print(f"{Colors.BLUE} 연결중인 데이터베이스: {settings.database_url}{Colors.RESET}")

try:
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print(f"{Colors.GREEN} 데이터베이스 엔진 생성 성공{Colors.RESET}")
except Exception as e:
    print(f"{Colors.RED} 데이터베이스 엔진 생성 실패: {e}{Colors.RESET}")
    print(f"{Colors.YELLOW} 재시도를 통해 연결을 시도합니다...{Colors.RESET}")
    
    if not retry_db_connection(engine):
        print(f"{Colors.RED} 데이터베이스 연결 최종 실패. 수동으로 데이터베이스를 시작해주세요.{Colors.RESET}")
        raise


redis_client: Optional[redis.StrictRedis] = None

print(f"{Colors.BLUE} Redis 서버에 연결 시도: {settings.redis_host}:{settings.redis_port}{Colors.RESET}")

try:
    redis_client = redis.StrictRedis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        max_connections=10,
        decode_responses=True
    )
    redis_client.ping()
    print(f"{Colors.GREEN} Redis 연결 성공{Colors.RESET}")
except Exception as e:
    print(f"{Colors.RED} Redis 연결 실패: {e}{Colors.RESET}")
    print(f"{Colors.YELLOW} Redis 재시도를 시도합니다...{Colors.RESET}")
    
    if redis_client and retry_redis_connection(redis_client):
        print(f"{Colors.GREEN} Redis 재연결 성공{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW} Redis 사용 불가 (캐싱 기능 비활성화){Colors.RESET}")
        redis_client = None


Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Optional[redis.StrictRedis]:
    if redis_client is None:
        print(f"{Colors.YELLOW} Redis가 사용할 수 없습니다{Colors.RESET}")
        return None
    return redis_client


def check_db_health() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except:
        return False


def check_redis_health() -> bool:
    if redis_client is None:
        return False
    try:
        return redis_client.ping()
    except:
        return False