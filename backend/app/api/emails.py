from fastapi import APIRouter, HTTPException, Request, Depends
from app.models.schemas import (
    EmailListResponse, EmailSummary, GenerateReplyRequest, 
    GenerateReplyResponse, DeleteEmailRequest
)
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.core.security import verify_token
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/emails", tags=["emails"])


def get_current_user_tokens(request: Request) -> dict:
    """Extract and verify user tokens from request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload


@router.get("/list", response_model=EmailListResponse)
async def list_emails(
    request: Request,
    max_results: int = 5,
    query: str = ""
):
    """List emails from inbox with AI summaries"""
    try:
        payload = get_current_user_tokens(request)
        
        # Initialize services
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        ai = AIService()
        
        # Fetch emails
        emails = gmail.list_emails(max_results=max_results, query=query)
        
        # Generate AI summaries
        email_summaries = []
        for email in emails:
            summary = ai.summarize_email(
                subject=email['subject'],
                body=email['body'],
                sender=email['sender_name']
            )
            
            email_summaries.append(EmailSummary(
                id=email['id'],
                sender_name=email['sender_name'],
                sender_email=email['sender_email'],
                subject=email['subject'],
                summary=summary,
                snippet=email['snippet'],
                date=email['date']
            ))
        
        return EmailListResponse(
            emails=email_summaries,
            total=len(email_summaries)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List emails failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{email_id}")
async def get_email(email_id: str, request: Request):
    """Get detailed email information"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        
        email = gmail.get_email_details(email_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return email
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get email failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-reply", response_model=GenerateReplyResponse)
async def generate_reply(
    request: Request,
    body: GenerateReplyRequest
):
    """Generate AI reply for an email"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        ai = AIService()
        
        # Get email details
        email = gmail.get_email_details(body.email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Generate reply
        reply = ai.generate_reply(
            subject=email['subject'],
            body=email['body'],
            sender=email['sender_name'],
            context=body.context
        )
        
        return GenerateReplyResponse(
            reply=reply,
            email_id=body.email_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-reply")
async def send_reply(
    request: Request,
    email_id: str,
    reply_content: str
):
    """Send email reply"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        
        # Get original email
        email = gmail.get_email_details(email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Send reply
        success = gmail.send_reply(
            to_email=email['sender_email'],
            subject=email['subject'],
            body=reply_content,
            thread_id=email.get('thread_id')
        )
        
        if success:
            return {"message": "Reply sent successfully", "email_id": email_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to send reply")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    request: Request
):
    """Delete (trash) an email"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        
        success = gmail.delete_email(email_id)
        
        if success:
            return {"message": "Email deleted successfully", "email_id": email_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete email")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete email failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{query}")
async def search_emails(
    query: str,
    request: Request,
    max_results: int = 10
):
    """Search emails with natural language query"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        
        emails = gmail.search_emails(query=query, max_results=max_results)
        
        return {"emails": emails, "total": len(emails), "query": query}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search emails failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categorize")
async def categorize_emails(request: Request):
    """Categorize recent emails using AI"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        ai = AIService()
        
        emails = gmail.list_emails(max_results=10)
        
        categorized = {}
        for email in emails:
            category = ai.categorize_email(email['subject'], email['body'])
            if category not in categorized:
                categorized[category] = []
            categorized[category].append({
                "id": email['id'],
                "subject": email['subject'],
                "sender": email['sender_name']
            })
        
        return {"categories": categorized}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Categorize emails failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/digest/daily")
async def daily_digest(request: Request):
    """Generate daily email digest"""
    try:
        payload = get_current_user_tokens(request)
        
        gmail = GmailService(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"]
        )
        ai = AIService()
        
        emails = gmail.list_emails(max_results=20)
        digest = ai.generate_daily_digest(emails)
        
        return {
            "digest": digest,
            "email_count": len(emails),
            "timestamp": "today"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily digest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
