import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import exceptions, decode
from starlette.websockets import WebSocket
from schemas.account import TokenData
from config.nb_logging import logger

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("username")
        if username is None:
            logger.error("token 错误，请重新登录")
            raise HTTPException(
                status_code=status.http.HTTP_401_UNAUTHORIZED,
                detail="token 错误，请重新登录",
            )
        return TokenData(username=username,user_id=payload.get("user_id"),expires_at =payload.get("exp"))
    except jwt.ExpiredSignatureError:
        logger.error("token 过期，请重新登录")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token 过期，请重新登录",
        )
    except jwt.PyJWTError:
        logger.error("token，格式错误，请重新登录")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token，格式错误，请重新登录",
        )


async def get_websocket_current_user(websocket: WebSocket):
    token = websocket.query_params.get('token')
    if not token:
        return None
    try:
        payload = decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
            return None
        return payload
    except exceptions.PyJWTError:
        return None
