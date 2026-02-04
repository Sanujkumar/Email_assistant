from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Google OAuth2 authentication service"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid'
    ]
    
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return authorization_url
        
        except Exception as e:
            logger.error(f"Failed to generate auth URL: {e}")
            raise Exception(f"OAuth setup failed: {str(e)}")
    
    def exchange_code_for_tokens(self, code: str) -> dict:
        """Exchange authorization code for access and refresh tokens"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Get user info
            user_info = self._get_user_info(credentials.token)
            
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "user_info": user_info,
                "expires_at": credentials.expiry.isoformat() if credentials.expiry else None
            }
        
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            raise Exception(f"Failed to exchange code for tokens: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
            
            request = requests.Request()
            credentials.refresh(request)
            
            return {
                "access_token": credentials.token,
                "expires_at": credentials.expiry.isoformat() if credentials.expiry else None
            }
        
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise Exception(f"Failed to refresh token: {str(e)}")
    
    def _get_user_info(self, access_token: str) -> dict:
        """Get user information from Google"""
        try:
            credentials = Credentials(token=access_token)
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            }
        
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {"email": "", "name": "", "picture": ""}
    
    def revoke_token(self, token: str) -> bool:
        """Revoke access token"""
        try:
            credentials = Credentials(token=token)
            credentials.revoke(requests.Request())
            return True
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
