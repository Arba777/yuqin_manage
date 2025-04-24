import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session

from backend_tasks.task_manage import ai_generate_event_background, create_comments_task
from cruds.Event import EventService
from dependencies.db_session import get_db
from schemas.account import TokenData
from schemas.Event import (
    Event_back_response,
    Event_Detail,
    Event_Detail_Response,
    EventBase,
    EventResponse,
)
from services.common_service import get_event_service
from tools.str_tools import get_current_time
from verify.security import get_current_user

news_app = APIRouter()


@news_app.get("/events/", response_model=EventResponse, description="获取事件列表")
async def read_events(
    skip: int = 0,
    limit: int = 10,
    publish_time=None,
    q: str = None,
    field: str = "title",
    event_type: Optional[List[str]] = Query(None),
    event_service: EventService = Depends(get_event_service),
):
    if event_type:
        total_events, events = event_service.get_events_by_event_type(
            event_type, skip=skip, limit=limit
        )
    if publish_time:
        total_events, events = event_service.get_events_by_publish_time(
            publish_time, skip=skip, limit=limit
        )
    if q:
        total_events, events = event_service.get_events_by_keywords(
            q, field, skip=skip, limit=limit, query_set=None
        )
    if not publish_time and not q and event_type == None:
        total_events, events = event_service.get_events(skip=skip, limit=limit)
    events_data = [EventBase.from_orm(event) for event in events]
    if not events:
        return EventResponse(
            data=[], count=0, message="not fund events", status_code=404
        )
    return EventResponse(
        data=events_data, count=total_events, message="success", status_code=200
    )


@news_app.get(
    "/count_event_type", response_model=Event_back_response, description="统计事件类型"
)
async def count_event_type(
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    event_type = event_service.count_event_type()
    return Event_back_response(
        data=event_type,
        message="success",
        status_code=status.HTTP_200_OK,
        count=len(event_type),
    )


@news_app.get(
    "/events/{event_id}",
    response_model=Event_Detail_Response,
    description="获取事件详情",
)
async def read_event(
    event_id: int,
    back_ground_task: BackgroundTasks,
    config_id: str = None,
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
    create_time: datetime = Depends(get_current_time),
    current_user: TokenData = Depends(get_current_user),
):
    expires_at = datetime.now()
    event_db = event_service.get_event_temp_by_mid(event_id, expires_at)
    if not event_db:
        event_db = event_service.get_event_by_id(event_id)
        room_id = str(uuid.uuid4())
        ai_generate_event_background.delay(room_id, event_db.content_show)
        create_comments_task.delay(room_id, event_db.content_show, event_id)
        event_map_data = event_service.create_event_temp(
            event_db,
            room_id=room_id,
            user_id=current_user.user_id,
            create_time=create_time,
        )
        event_detail = Event_Detail.from_orm(event_map_data)
        return Event_Detail_Response(
            data=[event_detail], message="success", status_code=status.HTTP_200_OK
        )
    if event_db:
        # create_comments_task.delay(event_db.room_id,event_db.content_show,event_id)
        event_detail = Event_Detail.from_orm(event_db)
        return Event_Detail_Response(
            data=[event_detail], message="success", status_code=status.HTTP_200_OK
        )
