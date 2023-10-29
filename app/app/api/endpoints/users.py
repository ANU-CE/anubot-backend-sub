from fastapi import APIRouter, HTTPException, Depends, Response

from app.core.config import settings
from app.schema.user_schema import UserForm, UserToken
from app.crud.user_crud import create_user, get_user_by_id, verfiy_password
from app.db.model import TUsers
from app.db.connection import get_db

from sqlalchemy.orm import Session

router = APIRouter()

@router.post(path="/signup", description="Register form")
async def signup(new_user: UserForm, db: Session = Depends(get_db)):
    user = get_user_by_id(new_user.id, db)

    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    create_user(new_user, db)

    return HTTPException(status_code=200, detail="User created")

@router.post(path="/login", description="Login form")
async def login(response: Response, user: UserForm, db: Session = Depends(get_db)):
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
    access_token = response.cookies.get("access_token")
    response.delete_cookie(key="access_token")

    return HTTPException(status_code=200, detail="Logout success")