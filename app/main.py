from fastapi import FastAPI
from app.api.routes import router
from db.db import db

app = FastAPI()

app.include_router(router)

@app.get('/')
async def root():
    return {
        'message': 'Welcome to Lingua'
    }