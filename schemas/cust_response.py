from typing import Optional, Dict, Any, Union, List

from fastapi import status
from pydantic import BaseModel
from starlette.responses import JSONResponse


class CustomResponse(BaseModel):
    message: str
    status_code: Optional[int] = None
    data: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None  # Updated to accept both

    def __init__(self, message: str, data: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
                 status_code=status.HTTP_200_OK) -> None:
        super().__init__(message=message, data=data if data is not None else {}, status_code=status_code)


class ErrorResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    detail: str
    status_code: int = 400

    def __init__(self, error: str, detail: str, status_code: int = 400) -> None:
        super().__init__(error=error, detail=detail, status_code=status_code)


def custom_http_exception(status_code: int, exec: str):
    if status_code == 500:
        return JSONResponse(
            status_code=status_code,
            content={"status_code": status_code, "message": "服务器内部错误",'data':[]},
        )
    elif status_code == 404:
        return JSONResponse(
            status_code=status_code,
            content={"status_code": status_code, "message": "找不到资源",'data':[]},
        )
    elif status_code == 403:
        return JSONResponse(status_code=status_code, content={"status_code": 401, "message": "禁止访问",'data':[]})
    return JSONResponse(
        status_code=status_code,
        content={"status_code": status_code, "message": exec,'data':[]},
    )








