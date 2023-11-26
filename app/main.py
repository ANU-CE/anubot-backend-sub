from fastapi import FastAPI
from app.api.api import api_router
import sys
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI(title='anubot sub backend', description='anubot sub backend, written by FastAPI', version='1.1')

app.include_router(api_router, prefix="/api/v1")
app.add_middleware(HTTPSRedirectMiddleware)


@app.get('/', description='Hello World')
def default_route():
    return {'Hello':"GET"}
origins = [
    "https://anubot-maryoh2003.vercel.app",
    "http://localhost:5000",
    "http://anubot-maryoh2003.vercel.app",
    "http://localhost",
    "http://localhost:3000",
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
    uvicorn.run("main:app", host='0.0.0.0', port=5000, reload=True, ssl_keyfile="privkey.pem", ssl_certfile="cert.pem")
