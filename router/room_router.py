import json
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session
from starlette import status

from corpus.corpus_file_analysis import process_corpus_file
from cruds.Event import EventService
from dependencies.db_session import get_db
from models.models import Corpus, ExerciseRoom, RoomParticipants, UserDB
from config.nb_logging import logger
from schemas.account import TokenData
from schemas.Event import Event_back_response, Init_Room, ParticipantsResponse, UserBase
from services.common_service import get_event_service
from tools.str_tools import get_current_time, invite_code
from verify.security import get_current_user

room_app = APIRouter()


@room_app.post("/init_room", response_model=Init_Room, description="初始化演练室")
async def init_room(
    marksman_num: int = Query(..., description="水军数量"),
    grade: int = Query(..., description="演练等级"),
    exer_duration: int = Query(..., description="演练时长"),
    create_time_str: datetime = Depends(get_current_time),
    corpus_file_id: Optional[str] = Query(default=None, description="语料文件id"),
    topic_direction: Optional[List[str]] = Query(default=None, description="话题方向"),
    event_mid : Optional[List] = Query(default = None, description="事件id"),
    invite_code: str = Depends(invite_code),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if marksman_num < 1 or marksman_num > 1000:
        logger.error("水军数量必须在1到1000之间")
        return Event_back_response(
            data=[],
            message="水军数量必须在1到1000之间",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if grade < 1 or grade > 6:
        return Event_back_response(
            data=[],
            message="演练等级必须在1到6之间",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if exer_duration < 1 or exer_duration > 100:
        return Event_back_response(
            data=[],
            message="演练时长必须在1到100之间",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    configure_id = str(uuid.uuid4())
    create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
    new_room = ExerciseRoom(
        room_id=configure_id,
        # corpus_file_id = corpus_file_id,
        creator_id=current_user.user_id,
        grade=grade,
        marksman_num=marksman_num,
        person_num=0,
        event_mid=event_mid,
        invite_code=invite_code,
        start_time=create_time,
        end_time=create_time + timedelta(minutes=exer_duration),
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    resp_data = {
        "configure_id": configure_id,
        "invite_code": invite_code,
    }
    time.sleep(8)
    return Init_Room(
        data=[resp_data],
        message=f"初始化成功，您的演练邀请码为:{invite_code}",
        status_code=status.HTTP_200_OK,
        count=1,
    )


@room_app.post("/join_room", response_model=Init_Room, description="加入演练室")
async def join_room(
    invite_code: str,
    current_user: TokenData = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    room = (
        db.query(ExerciseRoom).filter(ExerciseRoom.invite_code == invite_code).first()
    )
    if not room:
        return Event_back_response(
            data=[], message="邀请码无效", status_code=status.HTTP_400_BAD_REQUEST
        )
    is_joined = (
        db.query(RoomParticipants)
        .filter(
            RoomParticipants.user_id == current_user.user_id,
            RoomParticipants.room_id == room.room_id,
        )
        .first()
    )
    # if is_joined:
    #     return Event_back_response(data=[], message="您已加入该演练室", status_code=status.HTTP_400_BAD_REQUEST)

    # 将用户加入演练室
    participant = RoomParticipants(user_id=current_user.user_id, room_id=room.room_id)
    db.add(participant)
    db.commit()
    return Init_Room(
        data=[{"configure_id": room.room_id, "invite_code": invite_code}],
        message="success",
        status_code=status.HTTP_200_OK,
    )


@room_app.post(
    "/leave_room", response_model=Event_back_response, description="离开演练室"
)
async def leave_room(
    room_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 检查用户是否已经加入了该演练室
    participant = (
        db.query(RoomParticipants)
        .filter(
            RoomParticipants.user_id == current_user.user_id,
            RoomParticipants.room_id == room_id,
        )
        .first()
    )
    if not participant:
        return Event_back_response(
            data=[], message="您尚未加入该演练室", status_code=status.HTTP_200_OK
        )
    db.delete(participant)
    db.commit()
    return Event_back_response(
        data=[room_id], message="退出演练室成功", status_code=status.HTTP_200_OK
    )


@room_app.get(
    "/participants/{room_id}",
    response_model=ParticipantsResponse,
    description="获取演练室参与者信息",
)
async def get_participants(
    room_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = db.query(ExerciseRoom).filter(ExerciseRoom.room_id == room_id).first()
    if not room:
        return ParticipantsResponse(
            data=[], message="演练室不存在", status_code=status.HTTP_404_NOT_FOUND
        )

    if room.creator_id != current_user.user_id:
        participant = (
            db.query(RoomParticipants)
            .filter(
                RoomParticipants.user_id == current_user.user_id,
                RoomParticipants.room_id == room_id,
            )
            .first()
        )
        if not participant:
            return ParticipantsResponse(
                data=[], message="无权限访问", status_code=status.HTTP_403_FORBIDDEN
            )

    participants = (
        db.query(UserDB)
        .join(RoomParticipants, UserDB.user_id == RoomParticipants.user_id)
        .filter(RoomParticipants.room_id == room_id)
        .all()
    )
    participants_data = [UserBase.from_orm(user) for user in participants]
    return ParticipantsResponse(
        data=participants_data,
        message="success",
        status_code=status.HTTP_200_OK,
        count=len(participants_data),
    )


@room_app.post(
    "/upload_corpus", response_model=Event_back_response, description="上传语料库文件"
)
async def upload_corpus(
    corpus_file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    上传并解析语料库文件
    """
    try:
        # 处理文件
        corpus_data = await process_corpus_file(corpus_file)
        if not corpus_data:
            return Event_back_response(data=[], message="文件解析失败", status_code=400)

        # 保存文件信息到数据库
        corpus_record = Corpus(
            file_name=corpus_file.filename,
            upload_id=current_user.user_id,
            file_data=json.dumps(corpus_data),
        )
        db.add(corpus_record)
        db.commit()
        db.refresh(corpus_record)

        # 返回处理结果，包含文件ID和文件名
        response_data = {
            "file_id": corpus_record.id,
            "file_name": corpus_record.file_name,
            "upload_time": corpus_record.created_at,
            "parsed_data": corpus_data,
        }

        return Event_back_response(
            data=[response_data],  # 将文件信息和解析数据一起返回
            message="文件解析成功",
            status_code=200,
            count=len(corpus_data),
        )
    except Exception as e:
        logger.error(f"Error processing corpus file: {e}")
        return Event_back_response(
            data=[], message=f"文件处理失败: {str(e)}", status_code=500
        )


@room_app.get(
    "/corpus_files",
    response_model=Event_back_response,
    description="获取已上传的语料库文件列表",
)
async def get_corpus_files(
    current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    获取已上传的语料库文件列表
    """
    try:
        corpus_files = (
            db.query(Corpus).filter(Corpus.upload_id == current_user.user_id).all()
        )
        files_data = [
            {
                "file_id": file.id,
                "file_name": file.file_name,
                "upload_time": file.updated_at,
                "file_data": json.loads(file.file_data),
            }
            for file in corpus_files
        ]

        return Event_back_response(
            data=files_data,
            message="文件解析成功",
            status_code=200,
            count=len(files_data),
        )
    except Exception as e:
        logger.error(f"Error retrieving corpus files: {e}")
        raise Event_back_response(
            status_code=500, message="文件解析失败，服务器出错", data=[]
        )
