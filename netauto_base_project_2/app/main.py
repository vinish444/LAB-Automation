from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="NetAuto Platform",
    version="0.1.0",
    description="Base network automation platform with FastAPI, Celery, Redis, and Nornir",
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "NetAuto Platform is running"}
