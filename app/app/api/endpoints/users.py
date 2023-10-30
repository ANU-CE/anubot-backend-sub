from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.schema.user_schema import UserForm, UserToken, UserLoginForm
from app.crud.user_crud import create_user, get_user_by_id, verfiy_password, create_access_token, get_current_user, get_user
from app.db.model import TChats
from app.db.connection import get_db

from datetime import timedelta, datetime
from typing import Annotated

from sqlalchemy.orm import Session

from jose import jwt

router = APIRouter()

@router.post(path="/signup", description="Register form")
async def signup(new_user: UserForm, db: Session = Depends(get_db)):
    user = get_user_by_id(new_user.id, db)

    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    create_user(new_user, db)

    return HTTPException(status_code=200, detail="User created")

@router.post(path="/login", description="Login form")
async def login(response: Response, user: UserLoginForm, db: Session = Depends(get_db)):
    db_user = get_user_by_id(user.id, db)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verfiy_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token_expoires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expoires
    )

    response.set_cookie(key="access_token", value=access_token, expires=access_token_expoires, httponly=True)

    return UserToken(access_token=access_token, token_type="bearer")

@router.get(path="/logout", description="Logout form")
async def logout(response: Response):

    response.delete_cookie(key="access_token")

    return HTTPException(status_code=200, detail="Logout success")

@router.get(path="/fetch", description="Fetch user info, recent 3 chats")
async def fetch_user(response: Response, db: Session = Depends(get_db)):
    user = get_current_user(response.cookies.get("access_token"))

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    recent_chats = get_recent_chats(user.id, db)
    
    return ORJSONResponse(content={"user": user, "recent_chats": recent_chats})

@router.get(path="/chat", description="Chat with AnuBot")
async def web_chat(response: Response, db: Session = Depedns(get_db)):
    user = get_current_user(response.cookies.get("access_token"))

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    recent_chats = get_recent_chats(user.id, db)
    