from fastapi import FastAPI
from app.config import settings
from app.routers import audio
app = FastAPI(title=settings.APP_NAME)
app.include_router(audio.router, prefix="/audio", tags=["Audio"])
@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} running 🚀",
        "environment": settings.APP_ENV
    }
