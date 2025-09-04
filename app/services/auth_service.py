import os, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status,Depends
from authlib.integrations.starlette_client import OAuth
from app.config import settings
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.user import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class AuthService:
    def __init__(self):
        # Setup Google OAuth
        self.oauth = OAuth()
        self.oauth.register(
            name="google",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    # -------- JWT --------
    def create_token(self, user_id: int) -> str:
        """Generate JWT token for a user"""
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    def verify_token(self, token: str) -> str:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    # -------- Google OAuth --------
    def get_google_oauth(self):
        """Expose Google OAuth client"""
        return self.oauth
# -------- Current User Dependency --------
    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
    ) -> User:
        token = credentials.credentials
        user_id = self.verify_token(token)

        user = db.get(User, int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user


# ✅ make one instance to import everywhere
auth_service = AuthService()