import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class EmailService:
    """Send emails via Brevo SMTP"""
    
    @staticmethod
    def _send_email(to_email, subject, html_body):
        """Helper method to send email via Brevo"""
        try:
            logger.info("=" * 60)
            logger.info(f"SENDING EMAIL: {subject}")
            logger.info("=" * 60)
            
            api_key = os.environ.get('BREVO_API_KEY')
            from_email = os.environ.get('MAIL_FROM_EMAIL', 'noreply@faceoffice.com')
            smtp_server = os.environ.get('MAIL_SERVER', 'smtp-relay.brevo.com')
            smtp_port = int(os.environ.get('MAIL_PORT', 587))
            
            logger.info(f"SMTP Server: {smtp_server}:{smtp_port}")
            logger.info(f"From: {from_email}")
            logger.info(f"To: {to_email}")
            logger.info(f"Subject: {subject}")
            
            if not api_key:
                logger.error("BREVO_API_KEY not configured")
                return False, "Brevo API key missing"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            msg.attach(MIMEText(html_body, 'html'))
            
            logger.info(f"Connecting to {smtp_server}:{smtp_port}...")
            
            # Connect and send via Brevo SMTP
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                logger.info("Connected to Brevo SMTP")
                logger.info("Starting TLS...")
                server.starttls()
                logger.info("TLS started")
                
                logger.info("Logging in with API key...")
                # Brevo uses 'apikey' as username and the API key as password
                server.login('apikey', api_key)
                logger.info("Logged in successfully")
                
                logger.info("Sending email...")
                server.sendmail(from_email, to_email, msg.as_string())
                logger.info("Email sent successfully")
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Email sent to {to_email}")
            logger.info("=" * 60)
            return True, None
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error("=" * 60)
            logger.error(f"AUTHENTICATION FAILED: {str(e)}")
            logger.error("Check your BREVO_API_KEY")
            logger.error("=" * 60)
            return False, f"Auth failed: {str(e)}"
        
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"Failed to send email: {str(e)}")
            logger.error("=" * 60)
            logger.exception("Full traceback:")
            return False, str(e)
    
    @staticmethod
    def send_visitor_notification(employee_email, employee_name, visitor_name, visitor_photo_url):
        """Send notification to employee"""
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                    .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                    .photo-section {{ margin: 20px 0; text-align: center; }}
                    .photo-section img {{ max-width: 250px; border-radius: 8px; border: 2px solid #ddd; }}
                    .button {{ background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px; }}
                    .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>New Visitor Request</h2>
                    </div>
                    <div class="content">
                        <p>Hi <strong>{employee_name}</strong>,</p>
                        <p><strong>{visitor_name}</strong> is requesting to meet you.</p>
                    
                        <div class="photo-section">
                            <p><strong>Visitor Photo:</strong></p>
                            <img src="{visitor_photo_url}" alt="Visitor photo">
                        </div>
                    
                        <p style="margin-top: 20px;">
                            <a href="{current_app.config.get('APP_URL', 'http://localhost:5000')}/employee/dashboard" class="button">
                                View Full Request in Dashboard
                            </a>
                        </p>
                    
                        <p style="color: #ff6b6b; font-weight: bold; margin-top: 20px;">
                            Please respond within 2 minutes.
                        </p>
                    </div>
                    <div class="footer">
                        <p>Faceoffice Visitor Management System</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            employee_email,
            f"New Visitor Request: {visitor_name}",
            html_body
        )
    
    @staticmethod
    def send_approval_email(visitor_email, visitor_name, employee_name):
        """Send approval email to visitor"""
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #28a745; color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                    .success-box {{ background-color: #d4edda; border: 1px solid #28a745; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Your Visit Has Been Approved</h2>
                    </div>
                    <div class="content">
                        <p>Hi <strong>{visitor_name}</strong>,</p>
                        
                        <div class="success-box">
                            <p><strong>{employee_name}</strong> has approved your visitor request.</p>
                            <p>You may now proceed to meet them.</p>
                        </div>
                        
                        <p>Thank you for using Faceoffice Visitor Management System.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated confirmation from Faceoffice.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            visitor_email,
            f"Visit Approved by {employee_name}",
            html_body
        )
    
    @staticmethod
    def send_approval_confirmation_to_employee(employee_email, employee_name, visitor_name):
        """Send confirmation to employee"""
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #28a745; color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                    .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Confirmation: Request Approved</h2>
                    </div>
                    <div class="content">
                        <p>Hi <strong>{employee_name}</strong>,</p>
                        <p>You have successfully approved the visitor request from <strong>{visitor_name}</strong>.</p>
                        <p>A confirmation email has been sent to the visitor.</p>
                    </div>
                    <div class="footer">
                        <p>Faceoffice Visitor Management System</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            employee_email,
            f"Confirmation: Visitor Request Approved - {visitor_name}",
            html_body
        )
    
    @staticmethod
    def send_rejection_email(visitor_email, visitor_name, employee_name):
        """Send rejection email to visitor"""
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                    .info-box {{ background-color: #f8d7da; border: 1px solid #dc3545; color: #721c24; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Request Declined</h2>
                    </div>
                    <div class="content">
                        <p>Hi <strong>{visitor_name}</strong>,</p>
                        
                        <div class="info-box">
                            <p><strong>{employee_name}</strong> has declined your visitor request.</p>
                            <p>Unfortunately, you will not be able to meet at this time.</p>
                        </div>
                        
                        <p>If you believe this is an error, please contact building security.</p>
                    </div>
                    <div class="footer">
                        <p>Faceoffice Visitor Management System</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            visitor_email,
            f"Visit Request Declined",
            html_body
        )
    
    @staticmethod
    def send_rejection_confirmation_to_employee(employee_email, employee_name, visitor_name):
        """Send rejection confirmation to employee"""
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 5px 5px 0 0; text-align: center; }}
                    .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                    .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Confirmation: Request Declined</h2>
                    </div>
                    <div class="content">
                        <p>Hi <strong>{employee_name}</strong>,</p>
                        <p>You have declined the visitor request from <strong>{visitor_name}</strong>.</p>
                        <p>A notification has been sent to the visitor.</p>
                    </div>
                    <div class="footer">
                        <p>Faceoffice Visitor Management System</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return EmailService._send_email(
            employee_email,
            f"Confirmation: Visitor Request Declined - {visitor_name}",
            html_body
        )
