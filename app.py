import json
import random
import time

import uvicorn
from fastapi import (
    Body,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from backend_tasks.task_manage import (
    authori_release_task,
    replay_source_feeling_task,
    scoring_news_tasks,
)
from cruds.Event import EventService
from dependencies.db_session import get_db
from dependencies.redis_config import redis_manager
from handle_hotel.heat_model import handle_websocket_test
from models.models import (
    Event_TEMP,
    Opinion_TEMP,
    SessionLocal,
)
from config.nb_logging import logger
from router.comments_route import comments_app
from router.news_router import news_app
from router.room_router import room_app
from router.user_router import user_app
from router.score_router import source_app
from schemas.account import TokenData
from schemas.cust_response import *
from schemas.Event import *
from services.common_service import get_event_service
from tools.search_similar import search_similar_articles
from verify.security import get_current_user

logger.info(" starting server...")
app = FastAPI(
    root_path="/api/v1",
    title="舆情演练项目api",
    description="舆情演练项目",
    version="v1",
)
app.include_router(router=user_app, prefix="", tags=["用户管理"])
app.include_router(router=room_app, prefix="", tags=["演练室管理"])
app.include_router(router=news_app, prefix="", tags=["舆情事件管理"])
app.include_router(router=comments_app, prefix="", tags=["评论管理"])
app.include_router(router=source_app, prefix="", tags=["评分管理"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return custom_http_exception(exc.status_code, exc.detail)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get(
    "/investi_backg/{room_id}",
    response_model=Event_back_response,
    description="事件背景",
)
def investi_background(
    room_id: str,
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    time.sleep(2)
    event_bg = event_service.get_events_bg(room_id)
    if not event_bg:
        return Event_back_response(data=[], message="未找到事件", status_code=200)
    return Event_back_response(data=[event_bg], message="success", status_code=200)


@app.post(
    "/author_release/",
    response_model=Event_release_response,
    description="权威发布接口",
)
def author_release(
    room_id: str = Body(...),
    factor: str = Body(...),
    media_type: str = Body(...),
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    authori_release_data = event_service.get_events_by_release(room_id)

    if authori_release_data[0]:
        return Event_back_response(
            data=[], message="发布成功", status_code=status.HTTP_200_OK
        )

    event_show = event_service.get_events_by_count_show(room_id)
    if not event_show:
        return Event_back_response(
            data=[], message="未找到事件", status_code=status.HTTP_200_OK
        )
    authori_release_task.delay(room_id, factor, media_type, event_show)
    return Event_release_response(data=[], message="发布成功", status_code=200)


@app.get(
    "/author_release/{room_id}",
    response_model=Event_release_response,
    description="获取发布结果",
)
async def get_author_release(
    room_id: str,
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    time.sleep(20)
    authori_release_data = event_service.get_events_by_release(room_id)
    if not authori_release_data:
        return Event_release_response(
            data=[], message="未找到事件", status_code=status.HTTP_200_OK
        )
    if not authori_release_data.release:
        time.sleep(3)
        authori_release_data = event_service.get_events_by_release(room_id)
        if not authori_release_data.release:
            return Event_release_response(
                data=[], message="未找到事件", status_code=status.HTTP_200_OK
            )
        reale_data = json.loads(authori_release_data.release)
        return Event_release_response(
            data=[reale_data], message="发布成功", status_code=200
        )
    reale_data = json.loads(authori_release_data.release)
    return Event_release_response(data=[reale_data], message="success", status_code=200)


@app.get(
    "/get_heat_chang/{room_id}",
    response_model=Event_release_response,
    description="获取热度变化",
)
async def get_heat_chang(room_id: str):
    heat_change = redis_manager.get_heat_curve(room_id)
    if not heat_change:
        return JSONResponse(
            content={
                "data": [],
                "message": "未找到事件",
                "status_code": status.HTTP_200_OK,
            }
        )
    return JSONResponse(
        content={
            "data": [heat_change],
            "message": "success",
            "status_code": status.HTTP_200_OK,
        }
    )


@app.get(
    "/real_events/", response_model=Event_real_response, description="获取相关帖子"
)
async def get_real_events(
    mid: int = Query(..., description="文章id"),
    room_id: str = Query(..., description="room_id"),
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    real_events = search_similar_articles(mid=mid)
    print(real_events, "real_events")
    if not real_events:
        return Event_real_response(
            data=[], message="未找到事件", status_code=status.HTTP_200_OK
        )
    return Event_real_response(
        data=real_events,
        message="success",
        status_code=status.HTTP_200_OK,
        count=len(real_events),
    )


@app.post("/evaluate_news")
async def evaluate_news(
    request_data: EvaluateNewsRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """
    评估新闻，返回新闻内容、事件类型、事件描述、事件相关性、事件可信度、事件可信度原因、事件可信度原因描述、事件可信度原因描述
    """
    room_id = request_data.room_id
    news_content = request_data.news_content
    evalua_content = request_data.evalua_content
    task_id = scoring_news_tasks.delay(room_id, news_content, evalua_content).id
    return Event_back_response(
        data=[task_id], message="发布成功", status_code=status.HTTP_200_OK
    )


@app.get(
    "/get_scoring_result",
    response_model=Event_back_response,
    description="获取发布评估结果",
)
async def get_scoring_news_result(
    room_id: str,
    event_service: EventService = Depends(get_event_service),
):
    post_rating = event_service.get_post_rating(room_id)
    if not post_rating:
        return Event_back_response(
            data=[],
            message="发布结果正在测评中，请稍等",
            status_code=status.HTTP_200_OK,
        )
    return Event_back_response(
        data=[post_rating], message="success", status_code=status.HTTP_200_OK, count=1
    )


# 回复意见（创建子评论）
@app.post("/opinions/{room_id}/reply", response_model=CommentsResponse)
def reply_to_opinion(
    room_id: str,
    reply_content: str = Body(...),
    main_comment_mid: int = Body(...),
    request: Request = Request,
    db: SessionLocal = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    if not (reply_content and main_comment_mid):
        raise HTTPException(status_code=400, detail="Missing required fields")
    db_opinion = (
        db.query(Opinion_TEMP)
        .filter(Opinion_TEMP.id == main_comment_mid, Opinion_TEMP.room_id == room_id)
        .first()
    )
    event_data = db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id).first()
    if db_opinion is None:
        raise HTTPException(status_code=404, detail="Opinion not found")
    replay_source_feeling_task.delay(
        main_comment_mid,
        reply_content,
        db_opinion.process_content,
        event_data.content_show,
    )

    new_reply = Opinion_TEMP(
        room_id=db_opinion.room_id,
        main_body_mid=db_opinion.main_body_mid,
        user_id=current_user.user_id,
        parent_comment_id=db_opinion.id,
        process_content=reply_content,
        comment_location=db_opinion.comment_location,
        nickname=current_user.username,
        main_comment_mid=random.randint(1, 1000000),
        sentiment=Sentiment.NEUTRAL,
    )
    db.add(new_reply)
    db_opinion.replies_count += 1
    db.add(db_opinion)
    db.commit()
    db.refresh(new_reply)
    return CommentsResponse(data=[], message="添加成功", status_code=status.HTTP_200_OK)


@app.get(
    "/comment_score/{room_id}/",
    response_model=CommentsResponse,
    description="获取评论得分",
)
async def get_comment_score(
    room_id: str,
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    comments = event_service.get_comment_score(room_id)
    return CommentsResponse(
        data=comments,
        message="success",
        status_code=status.HTTP_200_OK,
        count=len(comments),
    )


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await handle_websocket_test(websocket, room_id)


#
#
if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=6895, log_level="info")
