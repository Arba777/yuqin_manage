
from fastapi import APIRouter, Depends, status, BackgroundTasks
from cruds.Event import EventService
from schemas.Event import Event_back_response, ScoringCommentsRequest
from verify.security import get_current_user, TokenData
from backend_tasks.task_manage import scoring_comments_tasks


source_app = APIRouter()




# 对评论内容进行评分
@source_app.post(
    "/scoring_comments",
    response_model=Event_back_response,
    description="对评论内容进行评分",
)
async def scoring_comments(
    request_data: ScoringCommentsRequest,
    current_user: TokenData = Depends(get_current_user),
):
    room_id = request_data.room_id
    comment_content = request_data.comment_content
    event_data = request_data.event_data
    task_id = scoring_comments_tasks.delay(room_id, comment_content, event_data).id
    return Event_back_response(
        data=[task_id], message="发布成功", status_code=status.HTTP_200_OK
    )

