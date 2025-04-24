from passlib.context import CryptContext
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from models.models import UserDB

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.db = db

    # 创建用户时，密码应加密
    def create_user(self, username: str, password: str, company: str,department: str,is_admin: bool):
        hashed_password = hash_password(password)  # Encrypt password
        new_user = UserDB(username=username, password=hashed_password, company=company,department=department,is_admin=is_admin)
        self.db.add(new_user)
        try:
            self.db.commit()
            self.db.refresh(new_user)
        except Exception as e:
            self.db.rollback()  # Rollback if there's any error
            raise e  # Log or handle the error appropriately
        return new_user

    # 通过 ID 获取用户
    def get_user_by_id(self, user_id: int):
        try:
            return self.db.query(UserDB).filter(UserDB.user_id == user_id).first()
        except NoResultFound:
            return None

    # 通过用户名获取用户
    def get_user_by_username(self, username: str):
        try:
            return self.db.query(UserDB).filter(UserDB.username == username).first()
        except NoResultFound:
            return None

    # 更新用户时，密码也需要加密
    def update_user(self, user_id: int, username: str = None, password: str = None, is_active: bool = None):
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if username:
            user.username = username
        if password:
            user.password = hash_password(password)  # Hash the new password
        if is_active is not None:
            user.is_active = is_active
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()  # Rollback if there's any error
            raise e  # Log or handle the error appropriately
        return user

    # 删除用户
    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        try:
            self.db.delete(user)
            self.db.commit()
        except Exception as e:
            self.db.rollback()  # Rollback if there's any error
            raise e  # Log or handle the error appropriately
        return True


# 密码处理函数
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
