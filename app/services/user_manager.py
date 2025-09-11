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
                password=None,  # never used for Google
                google_id=user_info.get("sub"),
                picture=user_info.get("picture"),
                email_verified=user_info.get("email_verified"),
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        updates = {
        "google_id": user_info.get("sub"),   # attach google_id if matched by email
        "email": user_info["email"],
        "picture": user_info.get("picture"),
        "email_verified": user_info.get("email_verified"),
        "name": user_info.get("name", user.name),
    }

        updated = False
        for field, new_value in updates.items():
         if getattr(user, field) != new_value:
            setattr(user, field, new_value)
            updated = True

        if updated:
         self.db.commit()
         self.db.refresh(user)

    # 5. Return the existing user (after potential updates)
        return user

        
    def login(self, email: str, password: str):

        user = self.db.query(User).filter(User.email == email).first()
        # print("user doesn't exist", user)
        if user is None:
         raise HTTPException(status_code=404, detail="User not found")
        if not user.password:
         raise HTTPException(
          status_code=400,
         detail="This account does not have a password. Please log in using Google OAuth. Create password through settings in app."
         )
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
