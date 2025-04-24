from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from services.common_service import get_user_service
from cruds.UserDB import UserService, verify_password
from schemas import UserCreate, UserLogin
from schemas.Event import SchoolNameResponse
from schemas.cust_response import CustomResponse
from verify.security import create_jwt_token
from services.common_service import get_event_service
from cruds.Event import EventService
from config.env import ACCESS_TOKEN_EXPIRE_MINUTES

user_app = APIRouter()



# 注册用户
@user_app.post("/register", status_code=status.HTTP_201_CREATED, response_model=CustomResponse, description='用户注册')
def register_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    # 检查用户是否已存在
    existing_user = user_service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已经被使用"
        )

    new_user = user_service.create_user(user.username, user.password, user.company, user.company, user.is_admin)
    data = {"user_name": new_user.username}
    return CustomResponse(status_code=200, message="注册成功", data=data)


# 用户登录
@user_app.post("/login", response_model=CustomResponse, description='用户登录')
async def login_user(user: UserLogin, user_service: UserService = Depends(get_user_service)):
    # 查找用户
    db_user = user_service.get_user_by_username(user.username)
    if not db_user:
        return CustomResponse(status_code=400, message="用户不存在", data=[])

    # 验证密码
    if not verify_password(user.password, db_user.password):
        return CustomResponse(status_code=status.HTTP_400_BAD_REQUEST, message="账号或密码错误", data=[])

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"username": db_user.username, "user_id": db_user.user_id}, expires_delta=access_token_expires
    )
    data = {"access_token": access_token, "token_type": "bearer", "user_name": db_user.username,
            'is_admin': db_user.is_admin}
    return CustomResponse(status_code=200, message="登录成功", data=[data])






@user_app.get('/school_name/', response_model=SchoolNameResponse, description='学校名称')
def get_school_name(event_service: EventService = Depends(get_event_service)):
    school_name = event_service.get_school_name()
    count = len(school_name)
    return SchoolNameResponse(data=school_name, message="success", status_code=status.HTTP_200_OK, count=count)


