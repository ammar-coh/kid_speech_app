from fastapi import APIRouter, UploadFile, File, status, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.deps import get_db
from app.models.user import User
from pydantic import BaseModel, EmailStr
from app.services.user_manager import UserManager
from sqlalchemy.orm import Session
from app.services.auth_service import auth_service

load_dotenv()
router = APIRouter()


class UserRegister(BaseModel):
    name: str | None = None
    email: EmailStr
    password: str
    age: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register_user(user_signup: UserRegister, db: Session = Depends(get_db)):
    manager = UserManager(db)
    user = manager.register(
        name=user_signup.name,
        email=user_signup.email,
        password=user_signup.password,
        age=user_signup.age,
    )
    return {"status": status.HTTP_200_OK, "message": "Registration Successful"}


@router.post("/login")
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    # print("Login", login_in)
    manager = UserManager(db)
    user = manager.login(login_in.email, login_in.password)
    token = auth_service.create_token(user.id)
    return {"id": user.id, "email": user.email, "access_token": token}
