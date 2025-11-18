from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="VSL Pipeline MVP")


@app.get("/")
def read_root():
    return {
        "message": "VSL Pipeline MVP rodando",
        "environment": settings.app_env,
    }

