from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from app.models.schemas import Token, AuthCallbackRequest, UserInfo
from app.services.auth_service import GoogleOAuthService
from app.core.security import create_access_token
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

oauth_service = GoogleOAuthService()


@router.get("/login")
async def login():
    """Initiate Google OAuth flow"""
    try:
        auth_url = oauth_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def oauth_callback(code: str, state: str = None):
    """Handle OAuth callback from Google"""
    try:
        # Exchange code for tokens
        token_data = oauth_service.exchange_code_for_tokens(code)
        
        # Create JWT token with user info and Google tokens
        jwt_payload = {
            "email": token_data["user_info"]["email"],
            "name": token_data["user_info"]["name"],
            "picture": token_data["user_info"]["picture"],
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"]
        }
        
        jwt_token = create_access_token(jwt_payload)
        
        # Redirect to frontend with token
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        error_url = f"{settings.FRONTEND_URL}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)


@router.post("/callback", response_model=Token)
async def oauth_callback_post(request: AuthCallbackRequest):
    """Alternative POST endpoint for OAuth callback"""
    try:
        token_data = oauth_service.exchange_code_for_tokens(request.code)
        
        jwt_payload = {
            "email": token_data["user_info"]["email"],
            "name": token_data["user_info"]["name"],
            "picture": token_data["user_info"]["picture"],
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"]
        }
        
        jwt_token = create_access_token(jwt_payload)
        
        return Token(access_token=jwt_token)
    
    except Exception as e:
        logger.error(f"OAuth callback POST failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user", response_model=UserInfo)
async def get_current_user(request: Request):
    """Get current authenticated user info"""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = auth_header.split(" ")[1]
        
        from app.core.security import verify_token
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return UserInfo(
            email=payload.get("email"),
            name=payload.get("name"),
            picture=payload.get("picture")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post("/logout")
async def logout(request: Request):
    """Logout user and revoke tokens"""
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            from app.core.security import verify_token
            payload = verify_token(token)
            
            if payload and payload.get("access_token"):
                # Attempt to revoke Google token
                oauth_service.revoke_token(payload["access_token"])
        
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logged out"}


@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = auth_header.split(" ")[1]
        
        from app.core.security import verify_token
        payload = verify_token(token)
        
        if not payload or not payload.get("refresh_token"):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Refresh Google access token
        refreshed = oauth_service.refresh_access_token(payload["refresh_token"])
        
        # Create new JWT with updated access token
        new_payload = payload.copy()
        new_payload["access_token"] = refreshed["access_token"]
        
        new_jwt = create_access_token(new_payload)
        
        return Token(access_token=new_jwt)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=401, detail="Token refresh failed")
