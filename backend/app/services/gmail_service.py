from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
from datetime import datetime
import base64
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)


class GmailService:
    """Gmail API service for email operations"""
    
    def __init__(self, access_token: str, refresh_token: str):
        """Initialize Gmail service with OAuth tokens"""
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,  # Not needed for API calls
            client_secret=None
        )
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def list_emails(self, max_results: int = 5, query: str = "") -> List[Dict[str, Any]]:
        """Fetch emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise Exception(f"Failed to fetch emails: {str(error)}")
    
    def get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract key information
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Parse sender name and email
            sender_name, sender_email = self._parse_sender(sender)
            
            # Get email body
            body = self._get_email_body(message['payload'])
            
            return {
                'id': message_id,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'subject': subject,
                'snippet': message.get('snippet', ''),
                'body': body,
                'date': date,
                'thread_id': message.get('threadId', '')
            }
        
        except HttpError as error:
            logger.error(f"Failed to get email {message_id}: {error}")
            return None
    
    def send_reply(self, to_email: str, subject: str, body: str, 
                   thread_id: Optional[str] = None, message_id: Optional[str] = None) -> bool:
        """Send an email reply"""
        try:
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = {'raw': raw_message}
            
            if thread_id:
                send_message['threadId'] = thread_id
            
            self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        
        except HttpError as error:
            logger.error(f"Failed to send email: {error}")
            raise Exception(f"Failed to send email: {str(error)}")
    
    def delete_email(self, message_id: str) -> bool:
        """Move email to trash"""
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            
            logger.info(f"Email {message_id} moved to trash")
            return True
        
        except HttpError as error:
            logger.error(f"Failed to delete email {message_id}: {error}")
            raise Exception(f"Failed to delete email: {str(error)}")
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails with custom query"""
        return self.list_emails(max_results=max_results, query=query)
    
    def _parse_sender(self, sender: str) -> tuple:
        """Parse sender string to extract name and email"""
        if '<' in sender and '>' in sender:
            # Format: "Name <email@example.com>"
            name = sender.split('<')[0].strip().strip('"')
            email = sender.split('<')[1].split('>')[0].strip()
        else:
            # Format: "email@example.com"
            name = sender.split('@')[0]
            email = sender
        
        return name, email
    
    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        if 'parts' in payload:
            parts = payload['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # If no plain text, try HTML
            for part in parts:
                if part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Simple message
            data = payload['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return ""
    
    def categorize_email(self, subject: str, body: str) -> str:
        """Simple email categorization"""
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # Promotional keywords
        promo_keywords = ['sale', 'offer', 'discount', 'deal', 'promotion', 'unsubscribe']
        if any(keyword in subject_lower or keyword in body_lower for keyword in promo_keywords):
            return "Promotions"
        
        # Work keywords
        work_keywords = ['meeting', 'deadline', 'project', 'report', 'urgent', 'asap']
        if any(keyword in subject_lower or keyword in body_lower for keyword in work_keywords):
            return "Work"
        
        # Finance keywords
        finance_keywords = ['invoice', 'payment', 'receipt', 'transaction', 'bill']
        if any(keyword in subject_lower or keyword in body_lower for keyword in finance_keywords):
            return "Finance"
        
        return "Personal"
