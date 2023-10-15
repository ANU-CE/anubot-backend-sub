from fastapi import APIRouter

from app.core.config import settings
from app.schema.user_schema import User
from app.crud.user_crud import create_user, get_user_by_id, verfiy_password
from app.db.model import model
from app.db.connection import get_db

router = APIRouter()

@router.post(path="/signup", description="Register form")
async def signup(new_user: User, db: Session = Depends(get_db)):
    user = get_user_by_id(new_user.id, db)

    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    create_user(new_user, db)

    return HTTPException(status_code=200, detail="User created")

@router.post(path="/login", description="Login form")
async def login(user: User, db: Session = Depends(get_db)):
    db_user = get_user_by_id(user.id, db)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verfiy_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

        
    
    return HTTPException(status_code=200, detail="Login success")