from typing import Dict, Any
from tools.redis_manages import RedisManager
from config.nb_logging import logger
from config.env import redis_client

try:
    result = redis_client.ping()
    logger.info(f"redis 连接成功: {result}")
    redis_manager = RedisManager(redis_client)
except Exception as e:
    logger.error(f"redis 连接失败 : {e}")

def get_heat_config(self, room_id: str) -> Dict[str, Any]:
    """获取热度模型配置"""
    config = self.redis_client.hgetall(f"heat_config:{room_id}")
    if not config:
        return None
    return {k: float(v) for k, v in config.items()}

def get_heat_boost_config(self, room_id: str) -> Dict[str, float]:
    """获取热度提升配置"""
    config = self.redis_client.hgetall(f"heat_boost:{room_id}")
    if not config:
        return None
    return {k: float(v) for k, v in config.items()}