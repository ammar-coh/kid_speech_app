from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.services.base_service import BaseService
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager(BaseService):
    def __init__(self, db: Session, pwd_context: CryptContext = pwd_context):
        super().__init__(db)
        self.pwd_context = pwd_context
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)

    def register(self, name: str, email: str, password: str, age: int | None = None):
        try:
            
            user = User(
                name=name,
                email=email,
                password=self.hash_password(password),
                age=age,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    def register_google_user(self, user_info: dict):
        """Create or fetch a user from Google OAuth info"""
        user = self.db.query(User).filter_by(google_id=user_info["sub"]).first()

        if not user:
            user = self.db.query(User).filter_by(email=user_info["email"]).first()

        if not user:
            user = User(
                name=user_info.get("name", "Google User"),
                email=user_info["email"],
                password="oauth_dummy_password",  # never used for Google
                google_id=user_info.get("sub"),
                picture=user_info.get("picture"),
                email_verified=user_info.get("email_verified"),
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def login(self, email: str, password: str):

        user = self.db.query(User).filter(User.email == email).first()
        if user.google_id:
         raise HTTPException(
            status_code=400,
            detail="This account was created with Google. Please log in using Google OAuth."
        )
       
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
