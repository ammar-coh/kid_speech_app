import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from authlib.integrations.starlette_client import OAuth
from app.config import settings


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
        print("Client ID:", settings.GOOGLE_CLIENT_ID)

        return self.oauth
