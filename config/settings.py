from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import os

class CeleryConfig(BaseModel):
    """Celery配置模型"""
    broker_url: str = Field(
        os.environ.get(
            "CELERY_BROKER_URL",
            f"redis://:{os.environ.get('REDIS_PASSWORD', '')}@{os.environ.get('REDIS_HOST', 'yuqin_redis')}:{os.environ.get('REDIS_PORT', 6379)}/{os.environ.get('REDIS_DB', 0)}"
        ),
        description="Celery消息代理URL"
    )
    result_backend: str = Field(
        os.environ.get(
            "CELERY_RESULT_BACKEND",
            f"redis://:{os.environ.get('REDIS_PASSWORD', '')}@{os.environ.get('REDIS_HOST', 'yuqin_redis')}:{os.environ.get('REDIS_PORT', 6379)}/{os.environ.get('REDIS_DB', 0)}"
        ),
        description="Celery结果后端URL"
    )
    task_serializer: str = Field("json", description="任务序列化格式")
    accept_content: list = Field(["json"], description="接受的内容类型")
    result_serializer: str = Field("json", description="结果序列化格式")
    timezone: str = Field("UTC", description="时区设置")
    enable_utc: bool = Field(True, description="是否启用UTC")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class RedisConfig(BaseModel):
    """Redis配置模型"""
    host: str = Field(os.environ.get("REDIS_HOST", "yuqin_redis"), description="Redis主机地址")
    port: int = Field(int(os.environ.get("REDIS_PORT", 6379)), description="Redis端口")
    db: int = Field(int(os.environ.get("REDIS_DB", 0)), description="Redis数据库索引")
    password: Optional[str] = Field(os.environ.get("REDIS_PASSWORD", None), description="Redis密码")
    decode_responses: bool = Field(os.environ.get("REDIS_DECODE_RESPONSES", "true").lower() == "true", description="是否自动解码响应")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    url: str = Field(
        os.environ.get("DATABASE_URL", "mysql+pymysql://root:m3JdUL48mfLUL@10.245.153.195:3306/yuqin_manage?charset=utf8mb4"),
        description="数据库连接URL"
    )
    autocommit: bool = Field(False, description="是否自动提交事务")
    autoflush: bool = Field(False, description="是否自动刷新会话")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class Settings(BaseModel):
    """应用程序配置模型"""
    base_dir: str = Field(default_factory=lambda: os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局设置实例
settings = Settings()
print(settings)