from fastapi import FastAPI

app = FastAPI(title='anubot sub backend', description='anubot sub backend, written by FastAPI', version='1.1')

from app.api.api import api_router

app.include_router(api_router, prefix="API_V1")

@app.get('/', description='Hello World')
def default_route():
    return {'Hello':"GET"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, reload=True)
