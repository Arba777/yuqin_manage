import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from fastapi import WebSocket, status
from starlette.websockets import WebSocketDisconnect

from dependencies.redis_config import redis_manager
from config.nb_logging import logger
from verify.security import get_websocket_current_user

active_connections: Dict[str, List[WebSocket]] = {}
room_heat_states: Dict[str, Dict[str, Any]] = {}
room_heat_tasks: Dict[str, asyncio.Task] = {}


async def handle_disconnect(room_id: str, heat_incre_dict: dict):
    try:
        if heat_incre_dict:
            redis_manager.save_heat_incre_dict_websocket(room_id, heat_incre_dict)
            last_time = max(heat_incre_dict.keys())
            last_heat = heat_incre_dict[last_time]
            logger.info(f"Last heat state: {heat_incre_dict}")
            redis_manager.save_current_heat_state(room_id, heat_incre_dict)
        logger.info(f"Client disconnected from room {room_id}")
    except Exception as e:
        logger.error(f"Error during handling disconnect: {e}", exc_info=True)


class HeatTrendModel:
    def __init__(
            self, C_max, S_max, L_max, t_c0, k_s, d_s, k_l, t_l0, m,
            w_c=0.4, w_s=0.3, w_l=0.3, drill_duration=3600 * 10,
            init_comments=0, init_shares=0, init_likes=0, water_army_num=1000
    ):
        if C_max < 0 or S_max < 0 or L_max < 0 or t_c0 < 0 or k_s < 0 or d_s < 0 or k_l < 0 or m < 0:
            raise ValueError("Parameters must be non-negative")
        if not (0 <= w_c <= 1 and 0 <= w_s <= 1 and 0 <= w_l <= 1):
            raise ValueError("Weights must be between 0 and 1")
        if not np.isclose(w_c + w_s + w_l, 1):
            raise ValueError("Weights must sum to 1")
        if drill_duration < 0:
            raise ValueError("Drill duration must be non-negative")
        if water_army_num < 0:
            raise ValueError("Water army number must be non-negative")

        self.C_max = C_max
        self.S_max = S_max
        self.L_max = L_max
        self.t_c0 = t_c0
        self.k_s = k_s
        self.d_s = d_s
        self.k_l = k_l
        self.t_l0 = t_l0
        self.m = m
        self.w_c = w_c
        self.w_s = w_s
        self.w_l = w_l
        self.drill_duration = drill_duration
        self.init_comments = init_comments
        self.init_shares = init_shares
        self.init_likes = init_likes
        self.water_army_num = water_army_num

    @property
    def C(self):
        return lambda t: self.C_max * (t ** self.m / (t ** self.m + self.t_c0 ** self.m)) + self.init_comments + (
                self.water_army_num * 0.1)

    @property
    def S(self):
        return lambda t: self.S_max * (1 - np.exp(-self.k_s * t)) * np.exp(-self.d_s * t) + self.init_shares

    @property
    def L(self):
        return lambda t: self.L_max / (1 + np.exp(-self.k_l * (t - self.t_l0))) + self.init_likes

    def get_heat(self, t):
        C_t = max(0, self.C(t))
        S_t = max(0, self.S(t))
        L_t = max(0, self.L(t))
        return self.w_c * C_t + self.w_s * S_t + self.w_l * L_t


async def broadcast_to_room(room_id: str, message: dict):
    """
    """
    if room_id in active_connections:
        disconnected = []
        for connection in active_connections[room_id]:
            logger.info(f"Broadcasting message to client: {message}, client: {connection.client}")
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.append(connection)
        for connection in disconnected:
            if connection in active_connections[room_id]:
                active_connections[room_id].remove(connection)


async def handle_websocket_test(websocket: WebSocket, room_id: str):
    try:
        logger.warning(f"New WebSocket connection from {websocket.client}")
        current_user = await get_websocket_current_user(websocket)
        if not current_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason='Token expired. Please log in again.')
            return None
        await websocket.accept()
        if room_id not in active_connections:
            active_connections[room_id] = []
            room_heat_states[room_id] = {}

        active_connections[room_id].append(websocket)
        last_heat_state = redis_manager.get_current_heat_state(room_id)
        if last_heat_state:
            init_comments = round(float(last_heat_state.get('C', 0)))
            init_shares = round(float(last_heat_state.get('S', 0)))
            init_likes = round(float(last_heat_state.get('L', 0)))
            model = HeatTrendModel(
                C_max=1000, S_max=2000, L_max=1500, t_c0=2, k_s=0.15, d_s=0.5, k_l=0.1, t_l0=5, m=3,
                init_comments=init_comments,
                init_shares=init_shares,
                init_likes=init_likes
            )
        else:
            model = init_heat_trend_model()

        try:
            if room_id in room_heat_tasks and not room_heat_tasks[room_id].done():
                if room_id in room_heat_states:
                    await websocket.send_json(room_heat_states[room_id])
            else:
                room_heat_tasks[room_id] = asyncio.create_task(
                    handle_room_heat(room_id, model)
                )
            try:
                await websocket.receive()
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected normally")
                await handle_disconnect(room_id, room_heat_states.get(room_id, {}))
        except Exception as e:
            logger.error(f"Error during WebSocket handling: {e}", exc_info=True)
            await handle_disconnect(room_id, room_heat_states.get(room_id, {}))
        finally:
            if websocket in active_connections[room_id]:
                active_connections[room_id].remove(websocket)
            if not active_connections[room_id]:  # 如果房间没有其他连接了
                if room_id in room_heat_tasks:
                    room_heat_tasks[room_id].cancel()  # 取消热度计算任务
                    room_heat_tasks.pop(room_id)
                room_heat_states.pop(room_id, None)
                await handle_disconnect(room_id, room_heat_states.get(room_id, {}))
    except Exception as e:
        logger.error(f"Unexpected error in handle_websocket_test: {e}", exc_info=True)
        if websocket in active_connections.get(room_id, []):
            active_connections[room_id].remove(websocket)


async def handle_room_heat(room_id: str, model: HeatTrendModel):
    """
    处理房间热度，每隔一段时间更新一次热度并广播给所有连接的客户端

    """
    heat_incre_dict = {}
    start_time = time.time()
    start_dt = datetime.now()

    # 初始热度
    heat = model.get_heat(0)
    formatted_start_time = start_dt.strftime('%H:%M:%S')
    heat_incre_dict[formatted_start_time] = {
        "H": heat,
        "C": model.C(0),
        "S": model.S(0),
        "L": model.L(0)
    }

    stage_duration = model.drill_duration / 4
    stage_ends = [stage_duration * i for i in range(1, 5)]

    try:
        while (time.time() - start_time) < model.drill_duration:
            if not active_connections.get(room_id):  # 如果房间没有连接了，停止计算
                break

            elapsed_time = time.time() - start_time
            t = elapsed_time

            event_bank = redis_manager.get_event_background_template(room_id)
            comment_texts = redis_manager.get_comments(room_id)
            heat_increment = max(0, model.get_heat(t) - model.get_heat(t - 3))
            current_dt = start_dt + timedelta(seconds=elapsed_time)
            formatted_current_time = current_dt.strftime('%H:%M:%S')
            current_state = {
                "H": model.get_heat(t),
                "C": model.C(t),
                "S": model.S(t),
                "L": model.L(t)
            }
            heat_incre_dict[formatted_current_time] = current_state

            # 确定当前阶段
            if elapsed_time < stage_ends[0]:
                stage = "1"
            elif elapsed_time < stage_ends[1]:
                stage = "2"
            elif elapsed_time < stage_ends[2]:
                stage = "3"
            else:
                stage = "4"

            # 构建消息
            message = {
                'stage': stage,
                'incre': heat_increment,
                'default_heat': model.get_heat(t),
                'comment_list': comment_texts,
                'event_bank': event_bank,
                'end': stage == '4'
            }
            redis_manager.save_heat_incre_dict_websocket(room_id, heat_incre_dict)
            # 更新房间状态并广播消息
            room_heat_states[room_id] = message
            logger.info(f"Broadcasting message to room {room_id}: {message}")
            await broadcast_to_room(room_id, message)

            await asyncio.sleep(3)

    except Exception as e:
        logger.error(f"Error during heat data handling: {e}", exc_info=True)
        raise
    finally:
        if room_id in room_heat_tasks:
            room_heat_tasks.pop(room_id)
        if room_id in active_connections and not active_connections[room_id]:
            room_heat_states.pop(room_id, None)

    return heat_incre_dict


def init_heat_trend_model():
    return HeatTrendModel(
        C_max=1000, S_max=2000, L_max=1500, t_c0=2, k_s=0.15, d_s=0.5, k_l=0.1, t_l0=5, m=3
    )
