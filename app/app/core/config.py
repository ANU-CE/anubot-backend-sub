import os
import sys
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings

load_dotenv(verbose=True)
class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    QDRANT_URL: str = os.getenv('QDRANT_URL')
    QDRANT_PORT: str = os.getenv('QDRANT_PORT')
    QDRANT_API_KEY: str = os.getenv('QDRANT_API_KEY')

    EMBEDDING_MODEL: str = 'text-embedding-ada-002'
    EMBEDDING_CTX_LENGTH:int = 8191
    EMBEDDING_ENCODING:str = 'cl100k_base'

    DB_USERNAME:str = os.getenv('DB_USERNAME')
    DB_PASSWORD:str = os.getenv('DB_PASSWORD')
    DB_HOST:str = os.getenv('DB_HOST')
    DB_PORT:str = os.getenv('DB_PORT')
    DB_DATABASE:str = os.getenv('DB_DATABASE')

    SECRET_KEY:str = os.getenv('SECRET_KEY')
    ALGORITHM:str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30

    DB_URL:str = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

settings = Settings()
