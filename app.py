import requests

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from typing import Optional
from pydantic import BaseModel

#for vector database   
from qdrant_client import QdrantClient
import openai

import asyncio

#for Dev
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_PORT = os.getenv('QDRANT_PORT')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = 'cl100k_base'

openai.api_key = OPENAI_API_KEY

COLLECTION_NAME = 'anubot-unified'

qdrant_client = QdrantClient(
    url = QDRANT_URL,
    port= QDRANT_PORT, 
)

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

def build_prompt(question: str, references: list) -> tuple[str, str]:
    prompt = f"""
    당신은 안동대학교의 궁금한 점을 답변해 주는 챗봇, 아누봇입니다.
    사용자의 질문은 다음과 같습니다.: '{question}'
    질문과 관련된 것으로 추정되는 자료를 몇개 첨부하겠씁니다.
    만약 자료가 질문과 관련이 없다면 아예 인용하지 마세요.
    링크가 있다면 링크의 원문을 그대로 이용하세요.

    참고자료:
    """.strip()

    references_text = ""

    for i, reference in enumerate(references, start=1):
        text = reference.payload["plain_text"].strip()
        references_text += f"\n[{i}]: {text}"

    prompt += (
        references_text
        + ""
    )
    return prompt, references_text


async def prompt_ask(question: str, callback_url: str):
    similar_docs = qdrant_client.search(
        collection_name='anubot-unified',
        query_vector=openai.Embedding.create(input=question, model=EMBEDDING_MODEL)["data"][0]["embedding"],
        limit=3,
        append_payload=True,
    )
    print('생성중')
    prompt, references = build_prompt(question, similar_docs)

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
    print('반환중 3/3')

app = FastAPI()

@app.get('/')
def default_route():
    return {'Hello':"GET"}

@app.post(path='/api/v1/ask', response_model=KakaoAPI)
async def ask(item: KakaoAPI):
    try:
        task = asyncio.create_task(prompt_ask(item.userRequest.utterance, item.userRequest.callbackUrl))
    except requests.exceptions.ReadTimeout:
        pass
    print('반환중')
    return ORJSONResponse({
        "version" : "2.0",
        "useCallback" : True
    })

