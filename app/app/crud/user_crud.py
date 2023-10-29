from app.core.config import settings
from app.db.model import TChats
from app.schema.user_schema import UserForm
from app.db.connection import get_db

from fastapi import Depends

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_id(id: str, db: Session = Depends(get_db)):
    return db.query(TChats).filter(TChats.id == id).first()

def create_user(new_user: UserForm, db: Session = Depends(get_db)):
    db_user = TChats(id=new_user.id, name=new_user.name, password=pwd_context.hash(new_user.password), regdate=datetime.now())
    db.add(db_user)
    db.commit()

def verfiy_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)