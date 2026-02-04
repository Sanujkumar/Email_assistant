from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI service for email summarization and reply generation"""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        
        if self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = "claude-sonnet-4-20250514"
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Invalid AI provider: {self.provider}")
    
    def summarize_email(self, subject: str, body: str, sender: str) -> str:
        """Generate AI summary of email content"""
        try:
            prompt = f"""Summarize this email in 2-3 concise sentences. Focus on the main point and any actions needed.

From: {sender}
Subject: {subject}

Email content:
{body[:1000]}

Provide a clear, professional summary."""

            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
            # Fallback to snippet
            return body[:200] + "..." if len(body) > 200 else body
    
    def generate_reply(self, subject: str, body: str, sender: str, context: Optional[str] = None) -> str:
        """Generate professional email reply"""
        try:
            context_text = f"\nAdditional context: {context}" if context else ""
            
            prompt = f"""Generate a professional, helpful email reply to this email. Keep it concise but warm.

From: {sender}
Subject: {subject}

Email content:
{body[:1500]}{context_text}

Generate a complete email reply. Do not include subject line or salutation - just the body of the reply."""

            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"AI reply generation failed: {e}")
            return f"Thank you for your email. I've received your message regarding '{subject}' and will respond shortly."
    
    def parse_intent(self, user_message: str) -> Dict[str, Any]:
        """Parse user intent from natural language"""
        try:
            prompt = f"""Analyze this user command and extract the intent and parameters.

User message: "{user_message}"

Respond in this exact format:
INTENT: [read_emails | generate_reply | send_reply | delete_email | search_emails | help]
PARAMS: [any relevant parameters like email_id, query, number, etc.]
CONFIDENCE: [high | medium | low]

Examples:
"Show me my latest emails" -> INTENT: read_emails, PARAMS: count=5, CONFIDENCE: high
"Delete email 2" -> INTENT: delete_email, PARAMS: email_id=2, CONFIDENCE: high
"Reply to the Amazon email" -> INTENT: generate_reply, PARAMS: query=Amazon, CONFIDENCE: medium"""

            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.choices[0].message.content
            
            # Parse the response
            lines = result.strip().split('\n')
            intent = "help"
            params = {}
            confidence = "medium"
            
            for line in lines:
                if line.startswith("INTENT:"):
                    intent = line.split("INTENT:")[1].strip().split(',')[0].strip()
                elif line.startswith("PARAMS:"):
                    params_str = line.split("PARAMS:")[1].strip()
                    if params_str and params_str != "none":
                        # Simple parsing
                        for param in params_str.split(','):
                            if '=' in param:
                                k, v = param.split('=', 1)
                                params[k.strip()] = v.strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence = line.split("CONFIDENCE:")[1].strip()
            
            return {
                "intent": intent,
                "params": params,
                "confidence": confidence,
                "original_message": user_message
            }
        
        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            return {
                "intent": "help",
                "params": {},
                "confidence": "low",
                "original_message": user_message
            }
    
    def categorize_email(self, subject: str, body: str) -> str:
        """AI-based email categorization"""
        try:
            prompt = f"""Categorize this email into ONE of these categories: Work, Personal, Promotions, Finance, Urgent, Social

Subject: {subject}
Body: {body[:500]}

Respond with only the category name."""

            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=20,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=20,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            return "Personal"
    
    def generate_daily_digest(self, emails: List[Dict[str, Any]]) -> str:
        """Generate a daily email digest summary"""
        try:
            email_summaries = []
            for email in emails[:10]:  # Limit to 10 emails
                email_summaries.append(
                    f"- From {email['sender_name']}: {email['subject']}"
                )
            
            emails_text = "\n".join(email_summaries)
            
            prompt = f"""Create a brief daily digest of these emails. Highlight important ones and suggest priorities.

Emails received:
{emails_text}

Provide a concise executive summary."""

            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Digest generation failed: {e}")
            return f"You have {len(emails)} emails. Please review them at your convenience."
