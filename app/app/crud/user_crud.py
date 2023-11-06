from app.core.config import settings
from app.db.model import TChats, Chat
from app.schema.user_schema import UserForm, UserToken, UserLoginForm
from app.db.connection import get_db

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from datetime import datetime, timedelta
from typing import Annotated

from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_id(id: str, db: Session = Depends(get_db)):
    return db.query(TChats).filter(TChats.id == id).first()

async def create_user(new_user: UserForm, db: Session = Depends(get_db)):
    db_user = TChats(id=new_user.id, name=new_user.name, password=pwd_context.hash(new_user.password), regdate=datetime.now())
    db.add(db_user)
    db.commit()

def verfiy_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Get recent 3 data(chats) related with user id
def get_recent_chats(id: str, db: Session = Depends(get_db)):
    return db.query(Chat).filter(Chat.id == id).order_by(Chat.datetime.desc()).limit(3).all()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_user(db: Session, username: str):
    return db.query(TChats).filter(TChats.id == username).first()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"payload: {payload}")
        id: str = payload.get("sub")
        print(f"id: {id}")
        if id is None:
            raise credentials_exception
        user = get_user_by_id(id=id, db=db)
        if user is None:
            raise credentials_exception
        return UserForm(**user.__dict__)
    except JWTError:
        raise credentials_exception