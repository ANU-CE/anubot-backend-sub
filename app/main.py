from fastapi import FastAPI
from app.api.api import api_router
import sys
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='anubot sub backend', description='anubot sub backend, written by FastAPI', version='1.1')

app.include_router(api_router, prefix="/api/v1")

@app.get('/', description='Hello World')
def default_route():
    return {'Hello':"GET"}
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=5000, reload=True)
