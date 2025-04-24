from sqlalchemy.orm import Session

from dependencies.redis_config import redis_manager
from models.models import Corpus
from schemas.Event import CorpusCreate


async def set_heat_task(room_id, event_heat):
    redis_manager.increase_hotness(room_id, event_heat)


async def descrease_heat_task(room_id, event_heat):
    redis_manager.decrease_hotness(room_id, event_heat)


async def create_corpus(db: Session, corpus: CorpusCreate):
    db_corpus = Corpus(
        content=corpus.content,
        speech_type=corpus.speech_type,
        severity=corpus.severity,
        scenario=corpus.scenario,
        notes=corpus.notes,
    )
    db.add(db_corpus)
    db.commit()
    db.refresh(db_corpus)
    return db_corpus


async def get_corpus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Corpus).offset(skip).limit(limit).all()
