from app.core.config import settings
from app.db.model import User
from app.schema.user_schema import User
from app.db.connection import get_db

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_id(id: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == id).first()

def create_user(new_user: User, db: Session = Depends(get_db)):
    db_user = TUsers(id=new_user.id, name=new_user.name, password=pwd_context.hash(new_user.password), regdate=datetime.now())
    db.add(db_user)
    db.commit()

def verfiy_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)