import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Send emails using Gmail SMTP + Python native SMTP (no Flask-Mail needed)"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.sender_email = os.environ.get('SMTP_EMAIL')
        self.sender_password = os.environ.get('SMTP_PASSWORD')
        
        if not self.sender_email or not self.sender_password:
            logger.warning("SMTP credentials not configured")
    
    def send_email(self, recipient_email, subject, html_body):
        """Send email via Gmail SMTP"""
        try:
            if not self.sender_email or not self.sender_password:
                logger.error("SMTP credentials not configured")
                return False, "SMTP credentials not configured"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Attach HTML
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            
            logger.info(f"✓ Email sent to {recipient_email}")
            return True, None
            
        except Exception as e:
            logger.error(f"✗ Failed to send email to {recipient_email}: {str(e)}")
            return False, str(e)


# Initialize global email service
email_service = EmailService()