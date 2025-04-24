from fastapi import Depends
from sqlalchemy.orm import Session

from models.models import Event_TEMP


class Heat_Manager():
    def __init__(self, db: Session):
        self.db = db

    def select_heat(self, room_id: str):
        return self.db.query(Event_TEMP.event_heat).filter(Event_TEMP.room_id == room_id).first()

    def update_heat(self, room_id: str, heat: int):
        self.db.query(Event_TEMP).filter(Event_TEMP.room_id == room_id).update({'event_heat': heat})
        self.db.commit()
