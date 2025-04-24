import pymysql
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

from models.models import Event

Base = declarative_base()

import pymysql
from datetime import datetime
from sqlalchemy import create_engine, Column, BigInteger, String, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

Base = declarative_base()

def process_time(publish_time):
    # 示例处理逻辑，根据实际需求修改
    return int(datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S').timestamp())


def process_event_list(event_list):
    processed_events = []
    seen_mids = set()
    for event in event_list:
        if event['mid'] not in seen_mids:
            seen_mids.add(event['mid'])
            event['personal_href'] = 'https:' + event['personal_href']
            event['publish_time'] = process_time(event['publish_time'])
            processed_events.append(event)
        else:
            print(f"Duplicate mid found and ignored: {event['mid']}")
    return processed_events


def save_to_database(event_list):
    # 数据库连接配置
    db_url = "mysql+pymysql://root:123456789@localhost/one_data?charset=utf8mb4"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for event in event_list:
            existing_event = session.query(Event).filter_by(mid=event['mid']).first()
            if existing_event:
                existing_event.uid = event['uid']
                existing_event.title = event['title']
                existing_event.nickname = event['nickname']
                existing_event.personal_href = event['personal_href']
                existing_event.event_source = event['event_source']
                existing_event.content_show = event['content_show']
                existing_event.publish_time = event['publish_time']
            else:
                new_event = Event(
                    mid=event['mid'],
                    uid=event['uid'],
                    title=event['title'],
                    nickname=event['nickname'],
                    personal_href=event['personal_href'],
                    event_source=event['event_source'],
                    content_show=event['content_show'],
                    publish_time=event['publish_time']
                )
                session.add(new_event)

        session.commit()
        print("数据已成功保存到数据库！")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()
