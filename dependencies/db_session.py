from models.models import SessionLocal

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_direct():
    return SessionLocal()

def get_db_session_direct():
    return SessionLocal()


