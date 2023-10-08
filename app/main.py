import requests

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

import asyncio
import uvicorn

from typing import Optional
from pydantic import BaseModel

#for vector database   
from qdrant_client import QdrantClient
import openai

#for Dev
from dotenv import load_dotenv
import os

#for DB
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta


load_dotenv(verbose=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_PORT = os.getenv('QDRANT_PORT')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = 'cl100k_base'

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')

openai.api_key = OPENAI_API_KEY

COLLECTION_NAME = 'anubot-unified'

qdrant_client = QdrantClient(
    url = QDRANT_URL,
    port= QDRANT_PORT, 
)

engine = create_engine('mysql+pymysql://'+DB_USERNAME+':'+DB_PASSWORD+'@'+DB_HOST+':'+DB_PORT+'/'+DB_DATABASE, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Chat(Base):
    __tablename__ = 'Talks'
    id = Column(String(255), primary_key=True)
    chat = Column(String(255))
    reply = Column(String(255))
    datetime = Column(DateTime, server_default=func.now())

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

def get_recent_chats(id):
    session = Session()
    chats = session.query(Chat).filter(Chat.id == id).order_by(Chat.datetime.desc()).limit(3).all()
    session.close()
    return '\n\n'.join([f'{chat.chat}\n{chat.reply}' for chat in chats]) if chats else ''

def save_ask(question, final_response, id):
    session = Session()
    chat = Chat(chat=question, reply=final_response, id=id)
    session.add(chat)
    session.commit()
    session.close()

def build_prompt(question: str, references: list, saved_ask: str) -> str:
    prompt = f"""
    당신은 안동대학교의 궁금한 점을 답변해 주는 챗봇, 아누봇입니다.
    사용자의 질문은 다음과 같습니다.: '{question}'
    당신은 현재 안동대 주변 식당가, 기숙사식, 사무실이나 부서의 전화번호, 장학금에 대한 정보만 알고있으므로, 그 외의 질문은 답변의 정확도가 떨어진다고 통보하세요.
    링크가 있다면 링크의 원문을 그대로 이용하세요.

    자료:
    """.strip()

    references_text = ""

    for i, reference in enumerate(references, start=1):
        text = reference.payload["plain_text"].strip()
        references_text += f"\n{text}"

    prompt += (
        references_text
        + """\n 
        만약 내용이 없다면 첫 대화이니 절대 질문과 답변을 지어내지 마세요! 
        그리고 '사용자:', '아누봇:' 과 같은 표현은 절대 하지 마세요. 매우 중요합니다. 꼭 지키세요.
        또, 다음은 최근에 사용자와 당신이 주고받은 3개의 질문-답변 쌍이며 답변에 이를 참고할 수 있습니다.
        """
    )
    
    print(saved_ask)

    for i, chat in enumerate(saved_ask.split('\n\n'), start=1):
        prompt += f"\n\n{i}. {chat}"

    return prompt


async def prompt_ask(question: str, callback_url: str, id: str):
    similar_docs = qdrant_client.search(
        collection_name='anubot-unified',
        query_vector=openai.Embedding.create(input=question, model=EMBEDDING_MODEL)["data"][0]["embedding"],
        limit=3,
        append_payload=True,
    )
    saved_ask = get_recent_chats(id)

    print('생성중')
    prompt= build_prompt(question, similar_docs, saved_ask)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.2,
    )
    final_response = response["choices"][0]["message"]["content"]
    responseBody = {
        "version" : "2.0",
        "template" : {
            "outputs" : [
                {
                    "simpleText" : {
                        "text" : final_response
                    }
                }
            ]
        }
    }
    responseCode = requests.post(callback_url, json=responseBody)
    print(final_response)
    print('반환 완료!')
    save_ask(question, final_response, id)
    print('저장 완료!')

app = FastAPI(title='anubot sub backend', description='anubot sub backend, written by FastAPI', version='1.0')

@app.get('/', description='Hello World')
def default_route():
    return {'Hello':"GET"}

@app.post(path='/api/v1/ask', response_model=KakaoAPI, description='API for KakaoTalk Chatbot, with Callback Function')
async def ask(item: KakaoAPI):
    try:
        task = asyncio.create_task(prompt_ask(item.userRequest.utterance, item.userRequest.callbackUrl, item.userRequest.user.id))
    except requests.exceptions.ReadTimeout:
        pass
    print('반환중')
    return ORJSONResponse({
        "version" : "2.0",
        "useCallback" : True
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)