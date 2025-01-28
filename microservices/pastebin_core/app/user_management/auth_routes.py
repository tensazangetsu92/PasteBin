from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.responses import JSONResponse
from .auth_schemas import UserResponse, UserCreate, UserLogin
from .auth_services import register_user_service, login_user_service, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

from .token_utils import decode_access_token, oauth2_scheme
from ..postgresql.database import get_session
from ..schemas import PostResponse

AuthRouter = APIRouter()


@AuthRouter.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        response = await register_user_service(user, session)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@AuthRouter.post("/login")
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    try:
        access_token = await login_user_service(user, session)
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Strict"
        )
        return response
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@AuthRouter.get("/get-current-user", response_model=UserResponse)
async def get_user(session: AsyncSession = Depends(get_session)):
    current_user = await get_current_user(session)
    return current_user