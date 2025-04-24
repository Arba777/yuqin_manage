from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    company: str
    department: str
    is_admin: bool = False
    
    
class User(UserCreate):
    pass


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfoCreate(BaseModel):
    user_id: int
    completions: int
    score: str
    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    user_id: int
    completions: int
    score: str
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = None
    expires_at: Optional[int] = None
