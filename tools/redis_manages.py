import json
from config.nb_logging import logger
from redis import RedisError, Redis

from cruds.Event import EventService
from dependencies.db_session import get_db_direct


def get_event_service():
    return EventService(get_db_direct())


class RedisManager:
    """
    """


    def __init__(self, redis_client: Redis):
        self.redis = redis_client

        self.key_prefix = "yuqin"
        self.events_service = get_event_service()

    def get_key(self, key):
        return f"{self.key_prefix}:{key}"


    def save_event_bankground_template(self, room_id, template):
        key = f"event_template:{room_id}"
        self.redis.rpush(key, json.dumps(template))

    def get_event_background_template(self, room_id):
        key = f"event_template:{room_id}"
        event_templates = self.redis.lrange(key, 0, -1)
        self.redis.delete(key)
        event_templates = [json.loads(template) for template in event_templates]
        return event_templates

    def save_heat_incre_dict(self, room_id, heat_incre_dict):
        key = f"heat_incre_dict:{room_id}"
        logger.info(f"保存热度变化字典: {heat_incre_dict}")
        self.redis.rpush(key, json.dumps(heat_incre_dict))

    def save_event_status_dict(self, room_id, heat_status_dict):
        key = f"event_status_dict:{room_id}"
        self.redis.rpush(key, json.dumps(heat_status_dict))

    def get_event_status_dict(self, room_id):
        key = f"event_status_dict:{room_id}"
        event_status_items = self.redis.lrange(key, 0, -1)
        event_status_list = [json.loads(item) for item in event_status_items]
        logger.info(f"获取热度状态get_event_status_dict: {event_status_list}")
        return event_status_list

    def save_current_heat_state(self, room_id: str, heat_state: dict):
        """保存当前的热度状态"""
        key = f"heat_state:{room_id}"
        logger.info(f"保存热度状态save_current_heat_state: {heat_state}")
        self.redis.hset(key, mapping=heat_state)

    def get_current_heat_state(self, room_id: str) -> dict:
        """获取当前的热度状态"""
        key = f"heat_state:{room_id}"
        resul = self.redis.hgetall(key)
        logger.info(f"获取热度状态get_current_heat_state: {resul}")
        return self.redis.hgetall(key)

    def save_heat_incre_dict_websocket(self, room_id: str, heat_incre_dict: dict):
        """保存热度增量字典到 Redis"""
        key = f"heat_incre_dict_websocket:{room_id}"
        self.redis.set(key, json.dumps(heat_incre_dict))



    def set_value(self, key, value, expire=None):
        """
        设置值
        """
        return self.redis.set(name=self.get_key(key), value=value, ex=expire)

    def increase_hotness(self, room_id, increment=0):
        """增加热度值"""
        key = self.get_key(room_id)
        return self.redis.incrbyfloat(key, increment)

    def decrease_hotness(self, room_id, decrement=0):
        """减少热度值"""
        key = self.get_key(room_id)
        return self.redis.incrbyfloat(key, -decrement)

    def get_hotness(self, room_id):
        """获取当前热度值"""
        key = self.get_key(room_id)
        return float(self.redis.get(key) or 0)

    def get_value(self, key):
        """
        获取值
        """
        value = self.redis.get(self.get_key(key))
        if value is None:
            return 0.0
        try:
            return float(value.decode('utf-8'))
        except ValueError:
            return 0.0

    def delete_key(self, key):
        """
        删除key
        """
        return self.redis.delete(self.get_key(key))

    def rpush_comments(self, room_id, comment):
        key = f"comments:{room_id}"
        self.redis.rpush(key, json.dumps(comment))
        return True

    def get_comments(self, room_id):
        key = f"comments:{room_id}"
        comments = self.redis.lpop(key)
        print(comments,'comments')
        if comments is None:
            return None
        comments_list = [json.loads(comments)]
        return comments_list

    def get_heat_incre_dict_websocket(self, room_id: str) -> dict:
        """
        从 Redis 中获取指定 room_id 的热度数据。
        """
        key = f"heat_incre_dict:{room_id}"
        try:
            # 从 Redis 中获取热度数据
            heat_incre_dict = self.redis.hgetall(key)
            if not heat_incre_dict:
                return {}
            return {timestamp: json.loads(data) for timestamp, data in heat_incre_dict.items()}
        except RedisError as e:
            logging.error(f"Error fetching heat increment data from Redis: {e}")
            return {}

    def save_heat_incre_dict_websocket(self, room_id: str, heat_incre_dict: dict):
        """
        将热度数据保存到 Redis。
        """
        key = f"heat_incre_dict:{room_id}"
        try:
            # 将热度数据保存到 Redis
            data_to_save = {timestamp: json.dumps(data) for timestamp, data in heat_incre_dict.items()}
            self.redis.hmset(key, data_to_save)
        except RedisError as e:
            logging.error(f"Error saving heat increment data to Redis: {e}")
            raise

    def get_heat_incre_dict(self, room_id: str) -> dict:
        """        """
        return self.get_heat_incre_dict_websocket(room_id)

    def get_heat_curve(self, room_id: str) -> dict:
        """
        """
        heat_incre_dict = self.get_heat_incre_dict(room_id)
        if not heat_incre_dict:
            return {}
        # 提取 H 字段
        heat_curve = {timestamp: data["H"] for timestamp, data in heat_incre_dict.items()}
        return heat_curve




    def get_keys(self, pattern):
        keys = self.redis.keys(pattern=self.get_key(pattern))
        return [key.decode() for key in keys]

    def get_values(self, keys):
        values = []
        for key in keys:
            value = self.get_value(key)
            if value is not None:
                values.append(value)
        return values
