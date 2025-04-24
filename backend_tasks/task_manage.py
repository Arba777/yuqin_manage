import logging
import logging
import random
import time

from backend_tasks.deepseek_tools import create_event_background_ai, authori_release_ai, scoring_news_ai, scoring_comments_ai, \
    comments_effect, replay_source_feeling
from backend_tasks.tran_from import opinion_to_dict
from cruds.Event import EventService
from dependencies.db_session import get_db_direct
from dependencies.redis_config import redis_manager
from tools.str_tools import remove_double_stars
from config.settings import settings

from celery import Celery

celery_app = Celery(
    'tasks',
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend
)

celery_app.conf.update(
    task_serializer=settings.celery.task_serializer,
    accept_content=settings.celery.accept_content,
    result_serializer=settings.celery.result_serializer,
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
)


def get_event_service():
    return EventService(get_db_direct())


@celery_app.task
def set_heat_task(room_id, event_heat):
    redis_manager.increase_hotness(room_id, event_heat)


@celery_app.task
def descrease_heat_task(room_id, event_heat):
    redis_manager.decrease_hotness(room_id, event_heat)


@celery_app.task
def ai_generate_event_background(room_id, content_show):
    back_ground_tasks = create_event_background_ai(content_show)
    event_service = get_event_service()
    background_temp = {'event_bg': back_ground_tasks}
    redis_manager.save_event_bankground_template(room_id, background_temp)
    event_service.update_background_temp(background_temp, room_id)


@celery_app.task
def authori_release_task(room_id, factor, media_type, post_count):
    authori_rele_data = remove_double_stars(authori_release_ai(media_type, factor, post_count))
    print(authori_rele_data, type(authori_rele_data))
    events_service = get_event_service()
    authori_rele_ai = {f"{media_type}@{factor}": authori_rele_data}

    events_service.update_authori_release(authori_rele_ai, room_id)


@celery_app.task
def scoring_news_tasks(room_id, event_content, news_content):
    result_data = scoring_news_ai(event_content, news_content)
    events_service = get_event_service()
    events_service.update_post_rating(room_id, result_data)


@celery_app.task
def init_room_task(marksman_num, room_id, grade, exer_duration, rating_keywords, event_type, create_time, user_id):
    event_service = get_event_service()
    event_db = event_service.get_events_by_event_type(event_type)
    if event_db.event_heat > 50000:
        event_db.event_heat = 50000
    event_map_data = event_service.create_event_temp(event_db, room_id=room_id, create_time=create_time,
                                                     user_id=user_id, exer_duration=exer_duration)

    openion_temp = []
    for i in range(marksman_num):
        logging.info('开始生成评论', i, '\n')
        print(event_db.opinions, "openion_template", '\n')
    minute_task.apply_async(args=[room_id],
                            kwargs={'event_db': event_db.content_show, 'start_minute': 0, 'end_minute': exer_duration})


@celery_app.task
def scoring_comments_tasks(room_id, comment_content, event_content):
    result_data = scoring_comments_ai(comment_content, event_content)
    events_service = get_event_service()
    events_service.update_comment_rating(room_id, result_data)


@celery_app.task
def minute_task(room_id, event_db, start_minute=0, end_minute=60):
    if start_minute < end_minute:
        minute_task.apply_async(args=[room_id], kwargs={"event_db": event_db, 'start_minute': start_minute + 2},
                                countdown=120)

    else:
        print("任务结束")


@celery_app.task
def create_comments_task(room_id, event_data, mid):
    event_service = get_event_service()
    time.sleep(20)
    total_comments, comments_data = event_service.get_comments(mid)
    logging.info(f"total_comments: {total_comments}")
    opinions_temp_dicts = [opinion_to_dict(opinion, room_id) for opinion in comments_data]
    comments_result = comments_effect(event_data, comments_list=opinions_temp_dicts)
    for comments_item in comments_result:
        try:
            sleep_time = random.uniform(10, 15)
            time.sleep(sleep_time)
            data = event_service.create_comments_temp(comments_item, room_id)
            comments_item['id'] = data.id
            redis_manager.rpush_comments(room_id, comments_item)
        except Exception as e:
            print(e)
            logging.error(f"Error saving comments to Redis: {e}")
@celery_app.task
def replay_source_feeling_task(openion_id,replay_content, events_str,comments_str):
    cokments_result = replay_source_feeling(replay_content, events_str,comments_str)
    event_service = get_event_service()
    result = event_service.update_replay_source_feeling(openion_id, cokments_result)


