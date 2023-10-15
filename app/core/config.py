import os
from dotenv import load_dotenv

load_dotenv(verbose=True)
class Settings:
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

    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

    DB_URL = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

settings = Settings()
