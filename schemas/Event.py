from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class OpinionResponse(BaseModel):
    id: int
    main_body_mid: Optional[int]
    user_id: int
    parent_comment_id: Optional[int]
    process_content: Optional[str]
    replies_count: int
    star_num: int
    publish_time: datetime

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    room_id: Optional[str] = None
    mid: Optional[int] = None
    uid: Optional[int] = None
    title: Optional[str] = None
    nickname: Optional[str] = None
    personal_href: Optional[str] = None
    event_source: Optional[str] = None
    content_show: Optional[str] = None
    content_html: Optional[str] = None
    event_heat: Optional[int] = None
    publish_time: Optional[datetime] = None
    retweets: Optional[int] = 0
    comment_num: Optional[int] = 0
    star_num: Optional[int] = 0
    event_type: Optional[str] = None
    is_ai: Optional[bool] = None
    is_hot: Optional[bool] = None
    sentiment: Optional[str] = None
    keywords: Optional[list] = None
    color: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    status_code: int
    message: str
    count: int
    data: List[EventBase] = None

    class Config:
        from_attributes = True


class Opinion(BaseModel):
    id: int
    room_id: Optional[str] = None
    nickname: Optional[str] = None
    process_content: Optional[str] = None
    native_content: Optional[str] = None
    comment_location: Optional[str] = None
    comment_heat: Optional[int] = None
    publish_time: Optional[datetime] = None
    comment_rating: Optional[str] = None  # 允许 None 值

    class Config:
        from_attributes = True


class CommentsResponse(BaseModel):
    status_code: int
    message: str
    count: Optional[int] = 0
    data: List[Opinion] = None

    class Config:
        from_attributes = True


class Event_Detail(EventBase):
    opinions_temp: List[Opinion] = []

    class Config:
        from_attributes = True


class Event_Detail_Response(BaseModel):
    status_code: int
    message: str
    data: List[Event_Detail] = None

    class Config:
        from_attributes = True


class Event_back_response(BaseModel):
    status_code: int
    message: str
    data: List[Any]  # 改为接受任意类型的列表
    count: int = 0

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型


class SchoolNameResponse(Event_back_response):
    pass


class Init_Room(BaseModel):
    status_code: int
    message: str
    data: List[dict] = None
    count: int = 0

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    user_id: int
    username: str
    company: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipantsResponse(BaseModel):
    data: List[UserBase]
    message: str
    status_code: int
    count: int


class Event_real_response(BaseModel):
    status_code: int
    message: str
    data: List[dict] = None
    count: int = 0

    class Config:
        from_attributes = True


class Event_release_response(BaseModel):
    status_code: int
    message: str
    data: List[Dict] = None
    count: int = 0

    class Config:
        from_attributes = True


class EvaluateNewsRequest(BaseModel):
    room_id: str
    news_content: str
    evalua_content: str


class ScoringCommentsRequest(BaseModel):
    room_id: str
    event_data: str
    comment_content: str


class OpinionCreate(BaseModel):
    # main_body_mid: Optional[int] = None
    user_id: int = 1
    parent_comment_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    room_id: Optional[str] = None
    main_comment_mid: Optional[int] = None
    nickname: Optional[str] = None
    process_content: Optional[str] = None
    native_content: Optional[str] = None
    reply: Optional[str] = None
    replies_count: int = 0
    comment_heat: int = 0
    publish_time: datetime = datetime.now()
    comment_location: Optional[str] = None
    star_num: int = 0
    sentiment: str = ""
    is_ai: bool = False
    is_deleted: bool = False
    status: int = 0
    comment_rating: Optional[str] = None  # 允许 None 值


class OpinionUpdate(OpinionCreate):
    pass


class Opinion_Response(OpinionCreate):
    id: int
    children: List["Opinion"] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class Opinion_Response_V1(Opinion_Response):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class Comments(BaseModel):
    status_code: int
    message: str
    count: Optional[int] = 0
    data: List[Opinion_Response_V1] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class CorpusBase(BaseModel):
    content: str
    speech_type: str  # 言论类型/情绪化表达
    severity: int
    scenario: str
    notes: Optional[str] = None


class CorpusCreate(CorpusBase):
    pass


class Corpus(CorpusBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CorpusFileResponse(BaseModel):
    id: int
    filename: str
    upload_time: datetime
    file_data: Dict[str, Any]

    class Config:
        from_attributes = True


class CorpusFilesResponse(BaseModel):
    data: List[CorpusFileResponse]
    message: str
    status_code: int
    count: Optional[int] = None
