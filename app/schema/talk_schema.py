from typing import Optional
from pydantic import BaseModel

class KakaoUser(BaseModel):
    id: str
    properties: dict
    type: str

class KakaoAction(BaseModel):
    clientExtra: Optional[dict]
    detailParams: dict
    id: str
    name: str
    params: dict

class KakaoCallbackRequest(BaseModel):
    callbackUrl: str
    block: dict 
    user: KakaoUser
    utterance: str
    params: dict
    lang: str
    timezone: str

class KakaoAPI(BaseModel):
    action: KakaoAction
    bot: dict
    contexts: Optional[list]
    intent: dict
    userRequest: KakaoCallbackRequest
