import os
from redis import ConnectionPool, Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7
load_dotenv()

# 导入Pydantic配置模型
from config.settings import settings

# 为了向后兼容，保留这些变量
BASE_DIR = settings.base_dir
DATABASE_URL = settings.database.url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=settings.database.autocommit,
    autoflush=settings.database.autoflush,
    bind=engine
)

# Redis Configuration - 为了向后兼容，保留这个字典
REDIS_CONFIG = settings.redis.model_dump()

# 创建Redis连接
pool = ConnectionPool(**REDIS_CONFIG)
redis_client = Redis(connection_pool=pool)
