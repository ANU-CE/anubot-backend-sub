from typing import Optional
from pydantic import BaseModel, EmailStr, validator

class UserForm(BaseModel):
    user_id: str
    user_name: str
    user_password: str

    @validator('user_id', 'user_name', 'user_password')
    def user_information_must_filled(cls, v):
        if not v.isspace():
            raise HTTPException(status_code=422, detail='항목은 반드시 입력해주세요.')
        return v

    @validator('user_password')
    def user_password_must_8_length(cls, v):
        if len(v) < 8:
            raise HTTPException(status_code=422, detail='비밀번호는 8자리 이상이어야 합니다.')
        return v

class UserToken(BaseModel):
    access_token: str
    token_type: str