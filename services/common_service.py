from fastapi import Depends
from sqlalchemy.orm import Session

from cruds.Event import EventService
from cruds.UserDB import UserService
from dependencies.db_session import get_db


async def get_event_service(db: Session = Depends(get_db)):
    return EventService(db)



def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)