from fastapi import FastAPI
from app.config import settings
from app.routers import audio
from app.routers import google_OAuth  # 👈 add this
from app.routers import user
from starlette.middleware.sessions import SessionMiddleware



app = FastAPI(title=settings.APP_NAME)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

app.include_router(audio.router, prefix="/audio", tags=["Audio"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(google_OAuth.router)

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} running 🚀",
        "environment": settings.APP_ENV
    }
