import uuid
from datetime import datetime
from enum import Enum as Pyenum

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm._orm_constructors import backref
from config.env import SessionLocal

Base = declarative_base()


class Sentiment(Pyenum):
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1


class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)  # 公司名称
    department = Column(String(255), nullable=True)  # 部门
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    user_infos = relationship(
        "UserInfo", back_populates="user"
    )  # Relationship with UserInfo
    history = relationship(
        "History_info", back_populates="user"
    )  # Relationship with History_info
    opinions_temp = relationship("Opinion_TEMP", back_populates="user")  # 修改这里
    event_temp = relationship("Event_TEMP", back_populates="user")  # 修改这里
    corpora = relationship("Corpus", back_populates="user")

    joined_rooms = relationship(
        "ExerciseRoom", secondary="room_participants", back_populates="participants"
    )


class ExerciseRoom(Base):
    __tablename__ = "exercise_rooms"
    room_id = Column(String(255), primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    grade = Column(Integer, nullable=False, default=1)  # 演练等级
    marksman_num = Column(Integer, nullable=False)  # 水军数量
    event_mid = Column(BigInteger,ForeignKey("events.mid"),default=0, nullable=True)
    person_num = Column(Integer, nullable=True)  # 人次
    status = Column(String(255), default="active")
    corpus_file_id = Column(Integer, ForeignKey("corpus.id"), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    invite_code = Column(String(255), unique=True, index=True, nullable=False)
    # direction = Column(JSON, nullable=True)
    participants = relationship(
        "UserDB", secondary="room_participants", back_populates="joined_rooms"
    )
    event = relationship("Event", back_populates="event_real")
    corpus = relationship("Corpus", back_populates="room")  # Ensure this line is correct
    creator = relationship("UserDB", foreign_keys=[creator_id])


class RoomParticipants(Base):
    __tablename__ = "room_participants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    room_id = Column(String(255), ForeignKey("exercise_rooms.room_id"), nullable=False)


class School_name(Base):
    __tablename__ = "school_name"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)


class UserInfo(Base):
    __tablename__ = "userinfo"
    id = Column(Integer, primary_key=True, index=True)  # 使用自增ID作为主键
    user_id = Column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )  # ForeignKey linking to UserDB
    completions = Column(Integer, nullable=False)
    score = Column(String(100), nullable=False)
    user = relationship(
        "UserDB", back_populates="user_infos"
    )  # Back reference to UserDB


class TokenDB(Base):
    __tablename__ = "tokens"
    token_id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, index=True)  # 存储token哈希值
    user_id = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=True)  # 根据是否过期或使用确定有效性


class Event(Base):
    __tablename__ = "events"
    mid = Column(
        BigInteger,
        primary_key=True,
        index=True,
        nullable=False,
        default=lambda: uuid.uuid4().int & 0x7FFFFFFFFFFFFFFF,
    )
    uid = Column(
        BigInteger,
        index=True,
        nullable=True,
        default=lambda: uuid.uuid4().int & 0x7FFFFFFFFFFFFFFF,
    )
    title = Column(String(255), index=True, nullable=True)  # 事件标题
    nickname = Column(String(255), index=True, nullable=True)  # 事件发起
    personal_href = Column(Text, nullable=True)  # 个人主页链接
    event_source = Column(String(255), index=True, nullable=True)  # 事件来源
    content_show = Column(Text, nullable=True)  # 事件简单介绍
    content_all = Column(Text, nullable=True)  # 事件全部内容
    content_html = Column(Text, nullable=True)  # 事件页面格式
    publish_time = Column(DateTime, index=True, default=datetime.utcnow)  # 发布时间
    # save_time = Column(DateTime, index=True, default=datetime.utcnow)  #入库时间
    color = Column(String(255), nullable=True)  # 情感属性颜色颜色
    keywords = Column(JSON, nullable=True)  # 事件关键词，以 JSON 形式存储
    sentiment = Column(String(255), nullable=True)  # 情感属性
    event_heat = Column(Integer, default=0)  # 事件热度
    original_heat = Column(Integer, default=0)  # 事件原始热度
    is_deleted = Column(Boolean, default=False)  # 是否逻辑删除
    is_ai = Column(Boolean, default=False)  # 是否为AI生成
    retweets = Column(Integer, default=0)  # 转发次数
    comment_num = Column(Integer, default=0)  # 评论数
    star_num = Column(Integer, default=0)  # 点赞数
    is_hot = Column(Boolean, default=False)  # 是否为热点事件
    event_type = Column(String(255), index=True, nullable=True)  # 事件类型
    opinions = relationship("Opinion", back_populates="event")
    event_real = relationship("ExerciseRoom", back_populates="event")  # Add this line


class Real_Event(Base):
    __tablename__ = "real_events"
    room_id = Column(String(255), index=True, nullable=False)
    real_mid = Column(
        BigInteger,
        index=True,
        nullable=False,
        default=lambda: uuid.uuid4().int & 0x7FFFFFFFFFFFFFFF,
        primary_key=True,
    )
    title = Column(String(255), index=True, nullable=True)  # 事件标题
    nickname = Column(String(255), index=True, nullable=True)  # 事件发起
    content_show = Column(Text, nullable=True)  # 事件简单介绍
    publish_time = Column(DateTime, index=True, default=datetime.utcnow)  # 发布时间
    event_heat = Column(Integer, default=0)  # 事件热度
    is_deleted = Column(Boolean, default=False)  # 是否逻辑删除
    is_ai = Column(Boolean, default=False)  # 是否为AI生成
    retweets = Column(Integer, default=0)  # 转发次数
    comment_num = Column(Integer, default=0)  # 评论数
    star_num = Column(Integer, default=0)  # 点赞数
    is_hot = Column(Boolean, default=False)  # 是否为热点事件
    event_type = Column(String(255), index=True, nullable=True)  # 事件类型


class Event_TEMP(Base):
    __tablename__ = "events_temp"
    room_id = Column(String(255), index=True, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), default=1)  # 添加外键
    mid = Column(
        BigInteger, index=True, nullable=True, default=lambda: uuid.uuid4().int
    )
    uid = Column(
        BigInteger, index=True, nullable=True, default=lambda: uuid.uuid4().int
    )
    title = Column(String(255), index=True, nullable=False)  # 事件标题
    nickname = Column(String(255), index=True, nullable=True)  # 事件发起
    personal_href = Column(Text, nullable=True)  # 个人主页链接
    event_source = Column(String(255), index=True, nullable=True)  # 事件来源
    content_show = Column(Text, nullable=True)  # 事件简单介绍
    content_all = Column(Text, nullable=True)  # 事件全部内容
    content_html = Column(Text, nullable=True)  # 事件页面格式
    publish_time = Column(DateTime, index=True, default=datetime.utcnow)  # 发布时间
    keywords = Column(JSON, nullable=True)  # 事件关键词，以 JSON 形式存储
    sentiment = Column(String(255), nullable=True)  # 情感属性
    event_heat = Column(Integer, default=0)  # 事件热度
    is_deleted = Column(Boolean, default=False)  # 是否逻辑删除
    is_ai = Column(Boolean, default=False)  # 是否为AI生成
    retweets = Column(Integer, default=0)  # 转发次数
    heat_change = Column(JSON, nullable=True)  # 事件热度变化
    comment_num = Column(Integer, default=0)  # 评论数
    star_num = Column(Integer, default=0)  # 点赞数
    is_hot = Column(Boolean, default=False)  # 是否为热点事件
    create_time = Column(String(255), nullable=True, index=True)  # 创建时间
    start_date = Column(DateTime, default=datetime.utcnow)  # 开始时间
    end_date = Column(DateTime, nullable=True)  # 结束时间
    event_bg = Column(JSON, nullable=True)  # 事件背景
    event_type = Column(String(255), index=True, nullable=True)  # 事件类型
    release = Column(JSON, default={})  # 发布模版
    post_rating = Column(Text, nullable=True)  # 发布评分
    opinions_temp = relationship("Opinion_TEMP", back_populates="events_temp")
    history = relationship("History_info", back_populates="event")  # 确保这里正确
    user = relationship("UserDB", back_populates="event_temp")  # 添加 user 关系


class Opinion(Base):
    __tablename__ = "opinions"
    main_body_mid = Column(BigInteger, ForeignKey("events.mid"), nullable=True)
    main_comment_mid = Column(BigInteger, primary_key=True, index=True, nullable=False)
    parent_comment_id = Column(
        BigInteger, ForeignKey("opinions.main_comment_mid"), nullable=True
    )  # 父级评论id
    nickname = Column(String(255), index=True, nullable=True)  # 事件发起
    process_content = Column(Text, nullable=True)  # 评论内容
    native_content = Column(Text, nullable=True)  # 原始内容
    reply = Column(Text, nullable=True)  # 回复内容
    replies_count = Column(Integer, default=0)  # 回复数
    comment_heat = Column(Integer, default=0)
    comment_original_heat = Column(Integer, default=0)
    comment_location = Column(String(255), index=True, nullable=True)  # 评论位置
    star_num = Column(Integer, default=0)  # 点赞数
    publish_time = Column(DateTime, default=datetime.utcnow)  # 创建时间
    sentiment = Column(Enum(Sentiment), default=Sentiment.NEUTRAL)  # 情感属性
    is_ai = Column(Boolean, default=False)  # 是否为AI生成
    is_deleted = Column(Boolean, default=False)  # 是否逻辑删除
    event = relationship("Event", back_populates="opinions")
    children = relationship(
        "Opinion", backref=backref("parent", remote_side=[main_comment_mid])
    )  # 新增：子评论关系


class Opinion_TEMP(Base):
    __tablename__ = "opinions_temp"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    main_body_mid = Column(BigInteger, ForeignKey("events_temp.mid"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), default=1)
    expires_at = Column(DateTime, nullable=True)
    room_id = Column(String(255), nullable=True)
    main_comment_mid = Column(BigInteger, nullable=True)
    nickname = Column(String(255), index=True, nullable=True)
    process_content = Column(Text, nullable=True)
    native_content = Column(Text, nullable=True)
    reply = Column(Text, nullable=True)
    comment_rating = Column(Text, nullable=True)  # 评论评分
    replies_count = Column(Integer, default=0)
    comment_heat = Column(Integer, default=0)
    comment_location = Column(String(255), index=True, nullable=True)
    star_num = Column(Integer, default=0)
    publish_time = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String(255), default=Sentiment.NEUTRAL)
    status = Column(
        Integer, default=0, nullable=True
    )  # 0: 未处理，1: 已处理，2: 已忽略
    is_ai = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    # 指向父评论的外键
    parent_comment_id = Column(Integer, ForeignKey("opinions_temp.id"), nullable=True)
    user = relationship("UserDB", back_populates="opinions_temp")
    events_temp = relationship("Event_TEMP", back_populates="opinions_temp")
    # 多级评论关系
    children = relationship(
        "Opinion_TEMP",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        foreign_keys=[parent_comment_id],
    )


class History_info(Base):
    __tablename__ = "history_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    room_id = Column(
        String(255), ForeignKey("events_temp.room_id"), nullable=True
    )  # 修改这里
    title = Column(String(255), nullable=False)
    source = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    event = relationship("Event_TEMP", back_populates="history")  # 事件关系
    user = relationship(
        "UserDB", back_populates="history"
    )  # Add this line for the relationship
    __table_args__ = (UniqueConstraint("user_id", "room_id"),)


class Corpus(Base):
    __tablename__ = "corpus"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    upload_id = Column(String(255), index=True, nullable=False)
    file_data = Column(Text, comment="语料内容")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user = relationship("UserDB", back_populates="corpora")
    room = relationship("ExerciseRoom", back_populates="corpus")  # Add this line

