from fastapi import APIRouter, Depends, BackgroundTasks

from cruds.Event import EventService
from config.nb_logging import logger
from schemas.account import TokenData
from schemas.cust_response import *
from schemas.Event import *
from services.common_service import get_event_service
from services.heat_incret import descrease_heat_task
from verify.security import get_current_user

comments_app = APIRouter()


@comments_app.get(
    "/comments/{room_id}", response_model=Comments, description="获取评论列表"
)
async def get_comments(
    room_id: str,
    skip: int = 0,
    limit: int = 10,
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    # total_comments, comments_data = event_service.get_comments_temp(room_id, skip=skip, limit=limit)
    total_comments, comments_data = event_service.get_comments_temp_v1(
        room_id, skip=skip, limit=limit
    )
    if not comments_data:
        return Comments(
            data=[], message="已加载全部评论", status_code=status.HTTP_200_OK
        )
    print(comments_data, len(comments_data))
    comments_db = [Opinion_Response_V1.from_orm(comment) for comment in comments_data]
    return Comments(
        data=comments_db,
        message="success",
        status_code=status.HTTP_200_OK,
        count=total_comments,
    )


@comments_app.post(
    "/delete/comment/", response_model=CommentsResponse, description="评论降温"
)
async def delete_comment(
    comment_id: int,
    back_ground_task: BackgroundTasks,
    event_service: EventService = Depends(get_event_service),
    current_user: TokenData = Depends(get_current_user),
):
    comment = event_service.delete_opinion(comment_id)
    if not comment:
        logger.error(f"未找到评论{comment_id}")
        return CommentsResponse(
            data=[], message="未找到评论", status_code=status.HTTP_200_OK
        )
    comment = Opinion.from_orm(comment)
    await descrease_heat_task(comment.room_id, comment.comment_heat)
    return CommentsResponse(
        data=[comment],
        message=f"成功降温{comment.comment_heat}",
        status_code=status.HTTP_200_OK,
    )
