from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatMessage, ChatResponse
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.core.security import verify_token
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


def get_current_user_tokens(request: Request) -> dict:
    """Extract and verify user tokens"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload


@router.post("/message", response_model=ChatResponse)
async def process_message(request: Request, message: ChatMessage):
    """Process natural language chat message"""
    try:
        payload = get_current_user_tokens(request)
        user_message = message.message.lower().strip()
        
        # Initialize services
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        ai = AIService()
        
        # Parse intent using AI
        intent_data = ai.parse_intent(message.message)
        intent = intent_data["intent"]
        
        # Handle different intents
        if "read" in user_message or "show" in user_message or "list" in user_message or "get" in user_message:
            # Read emails
            count = 5
            if "10" in user_message or "ten" in user_message:
                count = 10
            elif "20" in user_message or "twenty" in user_message:
                count = 20
            
            emails = gmail.list_emails(max_results=count)
            email_summaries = []
            
            for i, email in enumerate(emails, 1):
                summary = ai.summarize_email(
                    subject=email['subject'],
                    body=email['body'],
                    sender=email['sender_name']
                )
                email_summaries.append({
                    "number": i,
                    "id": email['id'],
                    "sender_name": email['sender_name'],
                    "sender_email": email['sender_email'],
                    "subject": email['subject'],
                    "summary": summary,
                    "date": email['date']
                })
            
            return ChatResponse(
                response=f"I found {len(emails)} emails in your inbox. Here they are:",
                action="list_emails",
                data={"emails": email_summaries}
            )
        
        elif "delete" in user_message:
            # Delete email
            # Extract email number or identifier
            numbers = re.findall(r'\d+', user_message)
            
            if numbers:
                # Delete by number
                email_num = int(numbers[0])
                return ChatResponse(
                    response=f"Please confirm: Do you want to delete email #{email_num}? Reply 'yes' or 'confirm' to proceed.",
                    action="delete_confirm",
                    data={"email_number": email_num}
                )
            elif "latest" in user_message or "last" in user_message:
                # Delete latest email
                emails = gmail.list_emails(max_results=1)
                if emails:
                    return ChatResponse(
                        response=f"Please confirm: Do you want to delete the latest email from {emails[0]['sender_name']}?",
                        action="delete_confirm",
                        data={"email_id": emails[0]['id']}
                    )
            else:
                # Search for email to delete
                search_query = user_message.replace("delete", "").replace("email", "").strip()
                if search_query:
                    emails = gmail.search_emails(query=search_query, max_results=3)
                    if emails:
                        return ChatResponse(
                            response=f"I found {len(emails)} emails matching '{search_query}'. Which one do you want to delete?",
                            action="delete_select",
                            data={"emails": emails[:3]}
                        )
            
            return ChatResponse(
                response="I couldn't identify which email to delete. Can you be more specific? For example: 'delete email 2' or 'delete latest email from Amazon'",
                action="clarify"
            )
        
        elif "reply" in user_message or "respond" in user_message:
            # Generate reply
            numbers = re.findall(r'\d+', user_message)
            
            if numbers:
                email_num = int(numbers[0])
                return ChatResponse(
                    response=f"I'll generate a reply for email #{email_num}. One moment...",
                    action="generate_reply",
                    data={"email_number": email_num}
                )
            else:
                return ChatResponse(
                    response="Which email would you like to reply to? Please specify the email number.",
                    action="clarify"
                )
        
        elif "digest" in user_message or "summary" in user_message:
            # Daily digest
            emails = gmail.list_emails(max_results=20)
            digest = ai.generate_daily_digest(emails)
            
            return ChatResponse(
                response=digest,
                action="daily_digest",
                data={"email_count": len(emails)}
            )
        
        elif "categorize" in user_message or "organize" in user_message:
            # Categorize emails
            emails = gmail.list_emails(max_results=10)
            categorized = {}
            
            for email in emails:
                category = ai.categorize_email(email['subject'], email['body'])
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append({
                    "subject": email['subject'],
                    "sender": email['sender_name']
                })
            
            return ChatResponse(
                response="I've categorized your recent emails:",
                action="categorize",
                data={"categories": categorized}
            )
        
        elif "search" in user_message or "find" in user_message:
            # Search emails
            search_query = user_message.replace("search", "").replace("find", "").replace("email", "").strip()
            if search_query:
                emails = gmail.search_emails(query=search_query, max_results=5)
                return ChatResponse(
                    response=f"I found {len(emails)} emails matching '{search_query}':",
                    action="search_results",
                    data={"emails": emails, "query": search_query}
                )
            else:
                return ChatResponse(
                    response="What would you like to search for?",
                    action="clarify"
                )
        
        elif "help" in user_message or user_message == "":
            # Help message
            help_text = """I can help you with:
• Read emails: "Show me my latest emails"
• Generate replies: "Reply to email 2"
• Delete emails: "Delete email 3" or "Delete latest email from Amazon"
• Search: "Find emails from John"
• Daily digest: "Give me a daily summary"
• Categorize: "Organize my emails"

What would you like to do?"""
            
            return ChatResponse(
                response=help_text,
                action="help"
            )
        
        else:
            # Default - try AI parsing
            return ChatResponse(
                response="I'm not sure what you'd like to do. Try asking me to 'show emails', 'delete email 2', or 'help' for more options.",
                action="clarify"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-delete")
async def confirm_delete(request: Request, email_id: str):
    """Confirm and execute email deletion"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        
        success = gmail.delete_email(email_id)
        
        if success:
            return ChatResponse(
                response="Email deleted successfully!",
                action="delete_success",
                data={"email_id": email_id}
            )
        else:
            return ChatResponse(
                response="Failed to delete email. Please try again.",
                action="error"
            )
    
    except Exception as e:
        logger.error(f"Delete confirmation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
