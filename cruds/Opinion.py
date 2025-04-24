from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models.models import Opinion, Opinion_TEMP, Sentiment
import logging

from schemas.Event import OpinionCreate

logger = logging.getLogger(__name__)

class OpinionService:
    def __init__(self, db: Session):
        self.db = db

    def create_opinions(self,opinion_list : list[dict]):
        for opinion in opinion_list:
            try:
                new_opinion = Opinion(**opinion)
                self.db.add(new_opinion)
                self.db.commit()
            except IntegrityError as e:
                self.db.rollback()
                logger.error(f"插入失败: {e}，意见: {opinion}")

    def get_opinion_by_id(self, opinion_id: int):
        return self.db.query(Opinion).filter(Opinion.id == opinion_id).first()

    def update_opinion(self, opinion_id: int, content: str = None, sentiment: Sentiment = None):
        opinion = self.get_opinion_by_id(opinion_id)
        if not opinion:
            return None
        if content:
            opinion.content = content
        if sentiment is not None:
            opinion.sentiment = sentiment
        self.db.commit()
        self.db.refresh(opinion)
        return opinion

    def delete_opinion(self, opinion_id: int):
        opinion = self.get_opinion_by_id(opinion_id)
        if not opinion:
            return None
        self.db.delete(opinion)
        self.db.commit()
        return True
