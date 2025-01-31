from fastapi import APIRouter, Depends, HTTPException, Response, Request
from starlette import status
from .auth_schemas import UserResponse, UserCreate, UserLogin
from .auth_services import register_user_service, login_user_service, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from ..postgresql.database import get_session


AuthRouter = APIRouter()

@AuthRouter.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        return await register_user_service(user, session)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@AuthRouter.post("/login")
async def login(response: Response, user: UserLogin, session: AsyncSession = Depends(get_session)):
    try:
        return await login_user_service(user, session, response)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@AuthRouter.get("/get-current-user")
async def get_current_user_route(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        return await get_current_user(request, session)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

