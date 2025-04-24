import asyncio
import logging
import random
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from starlette import status

from models.models import RoomParticipants
from tools.redis_manages import RedisManager
from verify.security import get_current_user, get_websocket_current_user

HEAT_DECREMENT_PER_DELETE = 5
STAGE_1_END = 120
STAGE_2_END = 240
STAGE_3_END = 360


def calculate_heat_increment(heat):
    heat_increments = heat / 50
    return round(random.uniform(heat_increments / 50, heat_increments), 2)


async def handle_websocket_status(websocket: WebSocket, room_id: str, redis_manager: RedisManager):

    current_user = await get_websocket_current_user(websocket)
    if not current_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason='token 过期，请重新登录')
        return None
    await websocket.accept()
    heat_incre_dict = {}
    heat = redis_manager.get_hotness(room_id)
    start_time = asyncio.get_event_loop().time()
    formatted_start_time = datetime.now().strftime('%H:%M:%S')
    heat_incre_dict[formatted_start_time] = heat
    message = {'stage': '1', 'incre': 0, 'default_heat': heat, 'end': False}
    await websocket.send_json(message)
    try:
        while True:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            heat_increment = calculate_heat_increment(heat)
            heat_data = redis_manager.increase_hotness(room_id, heat_increment)
            formatted_start_time = datetime.now().strftime('%H:%M:%S')
            heat_incre_dict[formatted_start_time] = heat_data
            if elapsed_time < STAGE_1_END:
                message = {'stage': '1', 'incre': heat_increment, 'default_heat': heat_data, 'end': False,
                           'elapsed_time': elapsed_time}
                redis_manager.save_heat_incre_dict(room_id, heat_incre_dict)
            elif elapsed_time < STAGE_2_END:
                redis_manager.save_heat_incre_dict(room_id, heat_incre_dict)
                message = {'stage': '2', 'incre': heat_increment, 'default_heat': heat_data, 'end': False,
                           'elapsed_time': elapsed_time}
            elif elapsed_time < STAGE_3_END:
                redis_manager.save_heat_incre_dict(room_id, heat_incre_dict)
                message = {'stage': '3', 'incre': heat_increment, 'default_heat': heat_data, 'end': False,
                           'elapsed_time': elapsed_time}
            else:
                message = {'stage': '4', 'incre': 0, 'default_heat': heat_data, 'end': True}
                redis_manager.save_heat_incre_dict(room_id, heat_incre_dict)
            await asyncio.sleep(1)
            await websocket.send_json(message)
    except WebSocketDisconnect:
        redis_manager.save_heat_incre_dict(room_id, heat_incre_dict)
        redis_manager.save_event_status_dict(room_id, heat_incre_dict)
        logging.info(f"Client disconnected from room {room_id}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
