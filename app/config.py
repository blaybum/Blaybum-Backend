import logging
import os
from functools import lru_cache
from typing import List

from app.settings import settings


class DatabaseConfig:
    SQLALCHEMY_DATABASE_URL = settings.database_url
    SQLALCHEMY_ECHO = settings.debug
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_PRE_PING = True
    POOL_RECYCLE = 300


class SecurityConfig:
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = False


class CORSConfig:
    ALLOWED_ORIGINS = settings.cors_origins
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS = ["*"]
    ALLOW_CREDENTIALS = True


class LoggingConfig:
    LEVEL = logging.INFO if not settings.debug else logging.DEBUG
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=LoggingConfig.LEVEL,
            format=LoggingConfig.FORMAT,
            datefmt=LoggingConfig.DATE_FORMAT
        )


class APIConfig:
    API_V1_PREFIX = "/api/v1"
    DOCS_URL = "/docs" if settings.debug else None
    REDOC_URL = "/redoc" if settings.debug else None
    OPENAPI_URL = "/openapi.json" if settings.debug else None
    
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class FileConfig:
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt"}
    UPLOAD_FOLDER = "uploads"
    
    @staticmethod
    def get_upload_path():
        upload_path = os.path.join(os.getcwd(), FileConfig.UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        return upload_path


class CacheConfig:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL = 300
    SESSION_TTL = 1800


class EnvironmentConfig:
    @staticmethod
    @lru_cache()
    def is_production():
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    @staticmethod
    @lru_cache() 
    def is_development():
        return not EnvironmentConfig.is_production()
    
    @staticmethod
    @lru_cache()
    def is_testing():
        return os.getenv("ENVIRONMENT", "development").lower() == "testing"


class Config:
    database = DatabaseConfig()
    security = SecurityConfig()
    cors = CORSConfig()
    logging = LoggingConfig()
    api = APIConfig()
    file = FileConfig()
    cache = CacheConfig()
    env = EnvironmentConfig()


config = Config()
