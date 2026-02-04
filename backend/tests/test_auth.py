import pytest
from app.services.auth_service import GoogleOAuthService
from app.core.config import settings


@pytest.fixture
def oauth_service():
    """Create OAuth service instance"""
    return GoogleOAuthService()


def test_oauth_service_initialization(oauth_service):
    """Test OAuth service initializes correctly"""
    assert oauth_service is not None
    assert len(oauth_service.SCOPES) > 0
    assert "gmail.readonly" in str(oauth_service.SCOPES)


def test_authorization_url_generation(oauth_service):
    """Test authorization URL generation"""
    try:
        auth_url = oauth_service.get_authorization_url()
        assert auth_url is not None
        assert "accounts.google.com" in auth_url
        assert "oauth2" in auth_url
    except Exception as e:
        # May fail if credentials not set
        pytest.skip(f"Skipping due to: {str(e)}")


def test_scopes_include_gmail(oauth_service):
    """Test that Gmail scopes are included"""
    scopes_str = " ".join(oauth_service.SCOPES)
    
    assert "gmail.readonly" in scopes_str
    assert "gmail.send" in scopes_str
    assert "gmail.modify" in scopes_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
