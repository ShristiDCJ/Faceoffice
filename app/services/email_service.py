import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from flask import current_app

import sys

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EmailService:
    """Send emails via Gmail SMTP (no external service needed)"""
    
    @staticmethod
    def send_visitor_notification(employee_email, employee_name, visitor_name, visitor_photo_url):
        """
        PHASE 2.1: Send notification to employee when visitor request is created
        Triggered automatically when visitor submits request
        """
        try:
            logger.info("=" * 60)
            logger.info("SENDING VISITOR NOTIFICATION EMAIL")
            logger.info("=" * 60)
        
            sender_email = os.environ.get('MAIL_USERNAME')
            sender_password = os.environ.get('MAIL_PASSWORD')
            smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        
            logger.info(f"SMTP Configuration:")
            logger.info(f"  Server: {smtp_server}")
            logger.info(f"  Port: 465 (SSL)")
            logger.info(f"  Username: {sender_email}")
            logger.info(f"  Password set: {bool(sender_password)}")
            logger.info(f"  Recipient: {employee_email}")
        
            if not sender_email or not sender_password:
                logger.error("SMTP credentials not configured")
                return False, "SMTP credentials missing"
        
            # HTML email template
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
        
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"New Visitor Request: {visitor_name}"
            msg['From'] = sender_email
            msg['To'] = employee_email
            msg.attach(MIMEText(html_body, 'html'))
        
            logger.info(f"Connecting to {smtp_server}:465 with SSL...")
            # Use SMTP_SSL on port 465
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                logger.info("Connected to SMTP server with SSL")
            
                logger.info(f"Logging in as {sender_email}...")
                server.login(sender_email, sender_password)
                logger.info("Logged in successfully")
            
                logger.info("Sending email...")
                server.sendmail(sender_email, employee_email, msg.as_string())
                logger.info("Email sent successfully")
        
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Visitor notification email sent to {employee_email}")
            logger.info("=" * 60)
            return True, None
    
        except smtplib.SMTPAuthenticationError as e:
            logger.error("=" * 60)
            logger.error(f"SMTP AUTHENTICATION FAILED")
            logger.error(f"  Error: {str(e)}")
            logger.error("=" * 60)
            return False, f"Authentication failed: {str(e)}"
    
        except TimeoutError as e:
            logger.error("=" * 60)
            logger.error(f"SMTP CONNECTION TIMEOUT")
            logger.error(f"  Error: {str(e)}")
            logger.error("=" * 60)
            return False, f"Timeout: {str(e)}"
    
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"Failed to send visitor notification")
            logger.error(f"  Error: {str(e)}")
            logger.error("=" * 60)
            logger.exception("Full traceback:")
            return False, str(e)
    
    @staticmethod
    def send_approval_email(visitor_email, visitor_name, employee_name):
        """
        PHASE 4.1: Send approval email to VISITOR
        """
        try:
            logger.info("=" * 60)
            logger.info("SENDING APPROVAL EMAIL TO VISITOR")
            logger.info("=" * 60)
            
            sender_email = os.environ.get('MAIL_USERNAME')
            sender_password = os.environ.get('MAIL_PASSWORD')
            smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            
            if not sender_email or not sender_password:
                logger.error("SMTP credentials not configured")
                return False, "SMTP credentials missing"
            
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
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Visit Approved by {employee_name}"
            msg['From'] = sender_email
            msg['To'] = visitor_email
            msg.attach(MIMEText(html_body, 'html'))
            
            logger.info(f"Connecting to {smtp_server}:465 with SSL...")
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                logger.info("Connected to SMTP server with SSL")
                logger.info(f"Logging in as {sender_email}...")
                server.login(sender_email, sender_password)
                logger.info("Logged in successfully")
                logger.info("Sending email...")
                server.sendmail(sender_email, visitor_email, msg.as_string())
                logger.info("Email sent successfully")
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Approval email sent to visitor {visitor_email}")
            logger.info("=" * 60)
            return True, None
        
        except Exception as e:
            logger.error(f"Failed to send approval email: {str(e)}")
            logger.exception("Full traceback:")
            return False, str(e)
    
    @staticmethod
    def send_approval_confirmation_to_employee(employee_email, employee_name, visitor_name):
        """
        PHASE 4.2: Send confirmation email to EMPLOYEE after approval
        """
        try:
            logger.info("=" * 60)
            logger.info("SENDING APPROVAL CONFIRMATION TO EMPLOYEE")
            logger.info("=" * 60)
            
            sender_email = os.environ.get('MAIL_USERNAME')
            sender_password = os.environ.get('MAIL_PASSWORD')
            smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            
            if not sender_email or not sender_password:
                logger.error("SMTP credentials not configured")
                return False, "SMTP credentials missing"
            
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
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Confirmation: Visitor Request Approved - {visitor_name}"
            msg['From'] = sender_email
            msg['To'] = employee_email
            msg.attach(MIMEText(html_body, 'html'))
            
            logger.info(f"Connecting to {smtp_server}:465 with SSL...")
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                logger.info("Connected to SMTP server with SSL")
                logger.info(f"Logging in as {sender_email}...")
                server.login(sender_email, sender_password)
                logger.info("Logged in successfully")
                logger.info("Sending email...")
                server.sendmail(sender_email, employee_email, msg.as_string())
                logger.info("Email sent successfully")
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Employee confirmation email sent to {employee_email}")
            logger.info("=" * 60)
            return True, None
        
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}")
            logger.exception("Full traceback:")
            return False, str(e)
    
    @staticmethod
    def send_rejection_email(visitor_email, visitor_name, employee_name):
        """
        PHASE 4.3: Send rejection email to VISITOR
        """
        try:
            logger.info("=" * 60)
            logger.info("SENDING REJECTION EMAIL TO VISITOR")
            logger.info("=" * 60)
            
            sender_email = os.environ.get('MAIL_USERNAME')
            sender_password = os.environ.get('MAIL_PASSWORD')
            smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            
            if not sender_email or not sender_password:
                logger.error("SMTP credentials not configured")
                return False, "SMTP credentials missing"
            
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
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Visit Request Declined"
            msg['From'] = sender_email
            msg['To'] = visitor_email
            msg.attach(MIMEText(html_body, 'html'))
            
            logger.info(f"Connecting to {smtp_server}:465 with SSL...")
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                logger.info("Connected to SMTP server with SSL")
                logger.info(f"Logging in as {sender_email}...")
                server.login(sender_email, sender_password)
                logger.info("Logged in successfully")
                logger.info("Sending email...")
                server.sendmail(sender_email, visitor_email, msg.as_string())
                logger.info("Email sent successfully")
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Rejection email sent to visitor {visitor_email}")
            logger.info("=" * 60)
            return True, None
        
        except Exception as e:
            logger.error(f"Failed to send rejection email: {str(e)}")
            logger.exception("Full traceback:")
            return False, str(e)
    
    @staticmethod
    def send_rejection_confirmation_to_employee(employee_email, employee_name, visitor_name):
        """
        PHASE 4.4: Send rejection confirmation email to EMPLOYEE
        """
        try:
            logger.info("=" * 60)
            logger.info("SENDING REJECTION CONFIRMATION TO EMPLOYEE")
            logger.info("=" * 60)
            
            sender_email = os.environ.get('MAIL_USERNAME')
            sender_password = os.environ.get('MAIL_PASSWORD')
            smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            
            if not sender_email or not sender_password:
                logger.error("SMTP credentials not configured")
                return False, "SMTP credentials missing"
            
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
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Confirmation: Visitor Request Declined - {visitor_name}"
            msg['From'] = sender_email
            msg['To'] = employee_email
            msg.attach(MIMEText(html_body, 'html'))
            
            logger.info(f"Connecting to {smtp_server}:465 with SSL...")
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                logger.info("Connected to SMTP server with SSL")
                logger.info(f"Logging in as {sender_email}...")
                server.login(sender_email, sender_password)
                logger.info("Logged in successfully")
                logger.info("Sending email...")
                server.sendmail(sender_email, employee_email, msg.as_string())
                logger.info("Email sent successfully")
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Employee rejection confirmation sent to {employee_email}")
            logger.info("=" * 60)
            return True, None
        
        except Exception as e:
            logger.error(f"Failed to send rejection confirmation: {str(e)}")
            logger.exception("Full traceback:")
            return False, str(e)
