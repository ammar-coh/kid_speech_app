from fastapi import APIRouter, Request, Depends,HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.services.auth_service import AuthService
from app.services.user_manager import UserManager
from app.models.user import User
from app.config import settings
router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()

# Step 1: redirect user to Google
@router.get("/google")
async def google_login(request: Request):
    try:
        redirect_uri = request.url_for("google_callback")
        return await auth_service.get_google_oauth().google.authorize_redirect(
            request, redirect_uri
        )
    except Exception as e:
        import traceback
        print("Google Auth Error:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Google Auth Error: {str(e)}")

# Step 2: handle callback from Google
# @router.get("/google/callback")
# async def google_callback(request: Request, db: Session = Depends(get_db)):
#     token = await auth_service.get_google_oauth().google.authorize_access_token(request)
#     user_info = token["userinfo"]

#     manager = UserManager(db)
#     user = db.query(manager.model).filter_by(email=user_info["email"]).first()
#     if not user:
#         user = manager.register(
#             name=user_info.get("name", "Google User"),
#             email=user_info["email"],
#             password="oauth_dummy_password",  # never used for Google accounts
#         )

#     jwt_token = auth_service.create_token(user.id)
#     return {"access_token": jwt_token, "user": {"id": user.id, "email": user.email}}

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await auth_service.get_google_oauth().google.authorize_access_token(request)

        user_info = token.get("userinfo")
        if not user_info:
            user_info = await auth_service.get_google_oauth().google.parse_id_token(request, token)

        # Persist in DB
        manager = UserManager(db)
        user = manager.register_google_user(user_info)

        # Issue your own JWT
        jwt_token = auth_service.create_token(user.id)

        return {
            "access_token": jwt_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "email_verified": user.email_verified
            }
        }

    except Exception as e:
        import traceback
        print("🔥 Google callback error:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Google callback error: {str(e)}")
