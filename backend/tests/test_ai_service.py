import pytest
from app.services.ai_service import AIService
from app.core.config import settings


@pytest.fixture
def ai_service():
    """Create AI service instance"""
    return AIService()


def test_ai_service_initialization(ai_service):
    """Test AI service initializes correctly"""
    assert ai_service is not None
    assert ai_service.provider in ["anthropic", "openai"]


def test_summarize_email(ai_service):
    """Test email summarization"""
    subject = "Project Update Meeting"
    body = "Hi team, we need to discuss the Q4 project timeline. Please review the attached documents before our meeting next week."
    sender = "John Doe"
    
    summary = ai_service.summarize_email(subject, body, sender)
    
    assert summary is not None
    assert len(summary) > 0
    assert isinstance(summary, str)


def test_generate_reply(ai_service):
    """Test reply generation"""
    subject = "Request for Information"
    body = "Could you please send me the latest report?"
    sender = "Jane Smith"
    
    reply = ai_service.generate_reply(subject, body, sender)
    
    assert reply is not None
    assert len(reply) > 0
    assert isinstance(reply, str)


def test_parse_intent(ai_service):
    """Test intent parsing"""
    message = "Show me my latest emails"
    
    result = ai_service.parse_intent(message)
    
    assert result is not None
    assert "intent" in result
    assert "params" in result
    assert "confidence" in result


def test_categorize_email(ai_service):
    """Test email categorization"""
    subject = "25% OFF Sale - Limited Time!"
    body = "Shop now and save on all items. Click here to unsubscribe."
    
    category = ai_service.categorize_email(subject, body)
    
    assert category is not None
    assert isinstance(category, str)
    assert len(category) > 0


@pytest.mark.asyncio
async def test_daily_digest_generation(ai_service):
    """Test daily digest generation"""
    emails = [
        {"sender_name": "John", "subject": "Meeting Tomorrow"},
        {"sender_name": "Jane", "subject": "Project Update"},
    ]
    
    digest = ai_service.generate_daily_digest(emails)
    
    assert digest is not None
    assert isinstance(digest, str)
    assert len(digest) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
