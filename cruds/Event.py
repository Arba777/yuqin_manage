import json
from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from models.models import Event, Event_TEMP, Opinion_TEMP, School_name, Opinion


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def get_event_by_id(self, event_id: int):
        events_option = self.db.query(Event).filter(Event.mid == event_id).options(joinedload(Event.opinions)).first()
        return events_option

    def get_event_temp_by_mid(self, event_id: int, expires_at):
        events_option = self.db.query(Event_TEMP).filter(Event_TEMP.mid == event_id,
                                                         Event_TEMP.end_date > expires_at).first()
        return events_option

    def get_event_temp_by_room_id(self, room_id: int, expires_at):
        events_option = self.db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id,
                                                         Event_TEMP.end_date > expires_at).first()
        return events_option

    def get_events(self, skip: int = 0, limit: int = 10):
        total_events = self.db.query(Event).count()
        events = self.db.query(Event).order_by(desc(Event.event_heat)).offset(skip).limit(limit).all()
        return total_events, events

    def get_events_bg(self, room_id):
        event_bg = self.db.query(Event_TEMP.event_bg).filter(Event_TEMP.room_id == room_id).scalar()
        return event_bg

    def get_post_rating(self, room_id):
        post_rating = self.db.query(Event_TEMP.post_rating).filter(Event_TEMP.room_id == room_id).scalar()
        return post_rating

    def update_post_rating(self, room_id, post_rating):
        self.db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id).update({"post_rating": post_rating})
        self.db.commit()

    def get_events_by_release(self, room_id):
        release = self.db.query(Event_TEMP.release).filter(Event_TEMP.room_id == room_id).first()
        return release

    def get_events_by_event_type(self, event_types: list, skip: int = 0, limit: int = 10):
        total_events = self.db.query(Event).filter(Event.event_type.in_(event_types)).count()
        events = self.db.query(Event).filter(Event.event_type.in_(event_types)).offset(skip).limit(limit).all()
        return total_events, events

    def get_events_by_count_show(self, room_id):
        content_show = self.db.query(Event_TEMP.content_show).filter(Event_TEMP.room_id == room_id).scalar()
        return content_show

    def get_events_update_keywords(self, skip, limit):
        events = self.db.query(Event).filter(Event.keywords == None).order_by(desc(Event.event_heat)).offset(
            skip).limit(limit).all()
        return events

    def get_events_by_publish_time(self, publish_time: datetime, skip=0, limit=10):
        total_events = self.db.query(Event).filter(Event.publish_time >= publish_time).count()
        events = self.db.query(Event).filter(Event.publish_time >= publish_time).offset(skip).limit(limit).all()
        return total_events, events

    def get_events_by_keywords(self, keyword: str, field: str, skip: int = 0, limit: int = 10, query_set=None):
        if query_set is not None:
            if field == 'content':
                total_events = query_set.filter(Event.content_all.like(f'%{keyword}%')).count()
                events = query_set.filter(Event.content_all.like(f'%{keyword}%')).offset(skip).limit(limit).all()
                return total_events, events
            else:
                events = query_set.filter(Event.title.like(f'%{keyword}%')).offset(skip).limit(limit).all()
                total_events = len(events)
                return total_events, events
        else:
            if field == 'content':
                total_events = self.db.query(Event).filter(Event.content_all.like(f'%{keyword}%')).count()
                events = self.db.query(Event).filter(Event.content_all.like(f'%{keyword}%')).offset(skip).limit(
                    limit).all()
                return total_events, events
            else:
                total_events = self.db.query(Event).filter(Event.title.like(f'%{keyword}%')).count()
                events = self.db.query(Event).filter(Event.title.like(f'%{keyword}%')).offset(skip).limit(limit).all()
                return total_events, events

    def get_events_count(self):
        return self.db.query(Event).count()

    def create_events(self, events: list[dict]):
        for event in events:
            try:
                new_event = Event(**event)
                self.db.add(new_event)
                self.db.commit()
            except SQLAlchemyError as e:
                print("Error occurred while creating events:", e)
                self.db.rollback()
        return True

    def update_background_temp(self, background_temp, room_id):
        self.db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id).update(background_temp)
        self.db.commit()

    def update_event(self, event_id: int, mid: int = None, uid: int = None, title: str = None, description: str = None,
                     nickname: str = None, keywords: dict = None):
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        event.mid = mid or event.mid
        event.uid = uid or event.uid
        event.title = title or event.title
        event.description = description or event.description
        event.nickname = nickname or event.nickname
        event.keywords = keywords or event.keywords
        self.db.commit()
        return event

    def update_events(self, events):
        for event_id, update in events.items():
            self.db.query(Event).filter(Event.mid == event_id).update(update)
            self.db.commit()

    def delete_event(self, event_id: int):
        event = self.get_event_by_id(event_id)
        if event:
            self.db.delete(event)
            self.db.commit()
            return event
        return None

    def create_event_temp(self, event_db, room_id, user_id, create_time, exer_duration: int = 30):
        start_date = datetime.now()
        event_temp = Event_TEMP(
            user_id=user_id,
            mid=event_db.mid,
            uid=event_db.uid,
            room_id=room_id,
            title=event_db.title,
            nickname=event_db.nickname,
            personal_href=event_db.personal_href,
            event_source=event_db.event_source,
            content_show=event_db.content_show,
            content_all=event_db.content_all,
            content_html=event_db.content_html,
            publish_time=event_db.publish_time,
            keywords=event_db.keywords,
            sentiment=event_db.sentiment,
            event_type=event_db.event_type,
            event_heat=event_db.event_heat,
            is_deleted=event_db.is_deleted,
            is_ai=event_db.is_ai,
            retweets=event_db.retweets,
            comment_num=event_db.comment_num,
            star_num=event_db.star_num,
            is_hot=event_db.is_hot,
            create_time=create_time,
            start_date=start_date,
            end_date=start_date + timedelta(minutes=exer_duration),
        )
        opinions_temp = [
            Opinion_TEMP(
                user_id=user_id,
                main_body_mid=event_temp.mid,
                room_id=room_id,
                main_comment_mid=opinion.main_comment_mid,
                nickname=opinion.nickname,
                process_content=opinion.process_content,
                native_content=opinion.native_content,
                reply=opinion.reply,
                replies_count=opinion.replies_count,
                comment_heat=round(float((opinion.star_num * 25 / (opinion.star_num + 49))), 2),
                comment_location=opinion.comment_location,
                star_num=opinion.star_num,
                publish_time=opinion.publish_time,
                sentiment=opinion.sentiment,
                is_ai=opinion.is_ai,
                is_deleted=opinion.is_deleted
            )
            for opinion in event_db.opinions
        ]

        try:
            self.db.merge(event_temp)

            for opinion_temp in opinions_temp:
                self.db.merge(opinion_temp)

            self.db.commit()

        except SQLAlchemyError as e:
            self.db.rollback()  # Rollback transaction if there's an error
            raise  # Re-raise the exception or handle it as needed
        return event_temp

    # 辅助函数：递归加载子评论
    def load_children_recursively(self, parent_id: int):
        children = self.db.query(Opinion_TEMP).filter(Opinion_TEMP.parent_comment_id == parent_id).order_by(
            desc(Opinion_TEMP.comment_heat)).all()
        for child in children:
            child.children = self.load_children_recursively(child.id)
        return children

    def get_comments_temp(self, room_id: str, skip: int = 0, limit: int = 10):
        total_comments = self.db.query(Opinion_TEMP).filter(Opinion_TEMP.room_id == room_id,
                                                            Opinion_TEMP.is_deleted == False).count()
        comments = (
            self.db.query(Opinion_TEMP)
            .filter(Opinion_TEMP.room_id == room_id, Opinion_TEMP.is_deleted == False)
            .order_by(desc(Opinion_TEMP.comment_heat))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return total_comments, comments

    def get_comments_temp_v1(self, room_id: str, skip: int = 0, limit: int = 10):
        total_comments = self.db.query(Opinion_TEMP).filter(Opinion_TEMP.room_id == room_id,
                                                            Opinion_TEMP.is_deleted == False).count()
        comments = (
            self.db.query(Opinion_TEMP)
            .filter(Opinion_TEMP.room_id == room_id, Opinion_TEMP.is_deleted == False,
                    Opinion_TEMP.parent_comment_id.is_(None))
            .order_by(desc(Opinion_TEMP.comment_heat))
            .offset(skip)
            .limit(limit)
            .all()
        )
        for comment in comments:
            comment.children = self.load_children_recursively(comment.id)
        return total_comments, comments

    def update_authori_release(self, authori_rele_data, room_id):
        print(authori_rele_data)
        try:
            self.db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id).update(
                {
                    Event_TEMP.release: func.json_set(Event_TEMP.release, '$', json.dumps(authori_rele_data))
                },
                synchronize_session=False
            )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    def update_heat_change(self, room_id, heat_change):
        try:
            self.db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id).update(
                {Event_TEMP.heat_change: heat_change},
                synchronize_session=False)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    def delete_opinion(self, opinion_id: int):
        opinion_temp = self.db.query(Opinion_TEMP).filter(Opinion_TEMP.id == opinion_id).first()
        opinion_temp.is_deleted = True
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()

        return opinion_temp

    def get_comments(self, mid: str, skip: int = 0, limit: int = 10):
        total_comments = self.db.query(Opinion).filter(Opinion.main_body_mid == mid,
                                                       Opinion.is_deleted == False).count()
        comments = (
            self.db.query(Opinion)
            .filter(Opinion.main_body_mid == mid, Opinion.is_deleted == False)
            .order_by(desc(Opinion.comment_heat))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return total_comments, comments

    def get_school_name(self):
        schools_name = self.db.query(School_name.name).distinct().all()
        school_name = [school[0] for school in schools_name]
        return school_name

    def count_event_type(self):
        result = self.db.query(Event.event_type, func.count(Event.event_type)).group_by(Event.event_type).all()
        event_types = [row[0] for row in result]
        return event_types

    def update_comment_rating(self, rating, opinion_id):
        self.db.query(Opinion_TEMP).filter(Opinion_TEMP.id == opinion_id).update({"rating": rating})
        self.db.commit()

    def create_comments_temp(self, data, room_id):
        try:
            data['room_id'] = room_id
            new_opinion = Opinion_TEMP(**data)
            self.db.add(new_opinion)
            self.db.commit()
            self.db.refresh(new_opinion)
            return new_opinion
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def update_replay_source_feeling(self, opinion_id, comment_rating):
        self.db.query(Opinion_TEMP).filter(Opinion_TEMP.parent_comment_id == opinion_id).update(
            {"comment_rating": comment_rating})
        self.db.commit()
        return True

    def get_comment_score(self, room_id):
        query = self.db.query(
            Opinion_TEMP.room_id,
            Opinion_TEMP.id,
            Opinion_TEMP.nickname,
            Opinion_TEMP.process_content,
            Opinion_TEMP.comment_rating,
            Opinion_TEMP.publish_time
        ).filter(
            Opinion_TEMP.room_id == room_id,  # 过滤 room_id
            Opinion_TEMP.parent_comment_id.isnot(None)  # 过滤 parent_comment_id 不为空
        )
        results = query.all()
        result_dicts = [
            {
                "nickname": row.nickname,
                "process_content": row.process_content,
                "comment_rating": row.comment_rating,
                'id': row.id,
                'room_id': row.room_id,
                "publish_time":row.publish_time
            }
            for row in results
        ]

        return result_dicts
