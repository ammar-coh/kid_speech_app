from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.deps import get_db
from app.models.user import User
from pydantic import BaseModel, EmailStr
from app.services.user_manager import UserManager
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService

load_dotenv()
router = APIRouter()
auth_service = AuthService()

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    manager = UserManager(db)
    user = manager.register(
        name=user_in.name,
        email=user_in.email,
        password=user_in.password,
        age=user_in.age,
    )
    token = auth_service.create_token(user.id)
    return {"id": user.id, "email": user.email, "access_token": token}


@router.post("/login")
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    manager = UserManager(db)
    user = manager.login(login_in.email, login_in.password)
    token = auth_service.create_token(user.id)
    return {"id": user.id, "email": user.email, "access_token": token}
