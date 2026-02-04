from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None


class AuthCallbackRequest(BaseModel):
    code: str


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[Any] = None


class EmailSummary(BaseModel):
    id: str
    sender_name: str
    sender_email: str
    subject: str
    summary: str
    snippet: str
    date: str


class EmailReply(BaseModel):
    email_id: str
    reply_content: str


class EmailAction(BaseModel):
    email_id: str
    action: str  # delete, reply, etc.
    confirmation: bool = False


class EmailListResponse(BaseModel):
    emails: List[EmailSummary]
    total: int


class GenerateReplyRequest(BaseModel):
    email_id: str
    context: Optional[str] = None


class GenerateReplyResponse(BaseModel):
    reply: str
    email_id: str


class DeleteEmailRequest(BaseModel):
    email_id: str
    confirmation: bool = True
