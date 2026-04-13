from flask_mail import Message
from app import mail
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()
scheduler_started = False

def send_email(recipient_email, subject, html_body):
    """Send email notification to employee"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html_body
        )
        mail.send(msg)
        logger.info(f"Email sent to {recipient_email}")
        return True, None
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False, str(e)

def send_visitor_acceptance_email(visitor_email, visitor_name, employee_name, employee_email):
    """Send email confirming visitor request was accepted to BOTH visitor and employee"""
    # Email to visitor
    visitor_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #28a745;">Request Accepted ✓</h2>
            <p style="font-size: 16px;">Hi {visitor_name},</p>
            <p><strong>{employee_name}</strong> has accepted your visitor request!</p>
            <p style="margin: 20px 0; padding: 15px; background: #e8f5e9; border-left: 4px solid #28a745;">
                You may now proceed to meet them.
            </p>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated message. If you have questions, contact building security.
            </p>
        </body>
    </html>
    """
    send_email(visitor_email, f"Visitor Request Accepted - {employee_name}", visitor_html)

    # Email to employee
    employee_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #28a745;">Confirmation: Request Accepted</h2>
            <p>You have accepted the visitor request from <strong>{visitor_name}</strong>.</p>
            <p style="margin: 20px 0; padding: 15px; background: #e8f5e9; border-left: 4px solid #28a745;">
                A confirmation email has been sent to: {visitor_email}
            </p>
        </body>
    </html>
    """
    send_email(employee_email, f"Confirmation: Visitor Request Accepted - {visitor_name}", employee_html)

def send_visitor_rejection_email(visitor_email, visitor_name, employee_name, employee_email):
    """Send email confirming visitor request was rejected to BOTH visitor and employee"""
    # Email to visitor
    visitor_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #dc3545;">Request Declined</h2>
            <p style="font-size: 16px;">Hi {visitor_name},</p>
            <p><strong>{employee_name}</strong> has declined your visitor request.</p>
            <p style="margin: 20px 0; padding: 15px; background: #fadbd8; border-left: 4px solid #dc3545;">
                Unfortunately, you will not be able to proceed at this time.
            </p>
            <p>If you believe this is an error, please contact building security.</p>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated message.
            </p>
        </body>
    </html>
    """
    send_email(visitor_email, f"Visitor Request Declined - {employee_name}", visitor_html)

    # Email to employee
    employee_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #dc3545;">Confirmation: Request Declined</h2>
            <p>You have declined the visitor request from <strong>{visitor_name}</strong>.</p>
            <p style="margin: 20px 0; padding: 15px; background: #fadbd8; border-left: 4px solid #dc3545;">
                A confirmation email has been sent to: {visitor_email}
            </p>
        </body>
    </html>
    """
    send_email(employee_email, f"Confirmation: Visitor Request Declined - {visitor_name}", employee_html)

def send_employee_pending_reminder_email(employee_email, employee_name, visitor_name):
    """Send reminder email to employee if request not answered in 2 minutes"""
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #ff9800;">Reminder: Pending Visitor Request</h2>
            <p style="font-size: 16px;">Hi {employee_name},</p>
            <p>This is a reminder that visitor <strong>{visitor_name}</strong> is still waiting for your response.</p>
            <p style="margin: 20px 0; padding: 15px; background: #fff3cd; border-left: 4px solid #ff9800;">
                It has been 2 minutes since their request was submitted.
                Please log in to the dashboard to accept or decline their request.
            </p>
            <p style="margin-top: 20px;">
                <a href="{current_app.config.get('APP_URL', 'http://localhost:5000')}/employee/dashboard"
                   style="background:#ff9800; color:white; padding:12px 24px; text-decoration:none; border-radius:5px; font-weight:bold;">
                    Go to Dashboard
                </a>
            </p>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated reminder message.
            </p>
        </body>
    </html>
    """
    send_email(employee_email, f"Reminder: Pending Visitor Request - {visitor_name}", html_body)

def notify_employee_visitor_arrived(employee_email, visitor_name, visitor_photo_url):
    """
    Notify employee that a visitor has arrived via email
    """
    # Send email with photo
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #007bff;">New Visitor Alert</h2>
            <p><strong style="font-size: 18px;">{visitor_name}</strong> has arrived and is requesting to meet you.</p>
            <img src="{visitor_photo_url}" alt="Visitor photo" style="width:300px; max-width:100%; border-radius:8px; margin:15px 0; border: 2px solid #ddd;">
            <p style="margin-top: 20px;">
                <a href="{current_app.config.get('APP_URL', 'http://localhost:5000')}/employee/dashboard"
                   style="background:#007bff; color:white; padding:12px 24px; text-decoration:none; border-radius:5px; font-weight:bold;">
                    View Full Request
                </a>
            </p>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                You have 2 minutes to respond. If you don't respond, a reminder will be sent.
            </p>
        </body>
    </html>
    """

    send_email(
        recipient_email=employee_email,
        subject=f"New Visitor: {visitor_name}",
        html_body=html_body
    )

def schedule_2min_reminder(request_id, employee_email, employee_name, visitor_name):
    """Schedule email reminder 2 minutes after request creation"""
    from datetime import datetime, timedelta

    run_time = datetime.utcnow() + timedelta(minutes=2)

    try:
        scheduler.add_job(
            send_employee_pending_reminder_email,
            'date',
            run_date=run_time,
            args=[employee_email, employee_name, visitor_name],
            id=f'reminder_{request_id}',
            replace_existing=True
        )
        logger.info(f"Reminder scheduled for request {request_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to schedule reminder: {str(e)}")
        return False

def cancel_reminder(request_id):
    """Cancel scheduled reminder"""
    try:
        scheduler.remove_job(f'reminder_{request_id}')
        logger.info(f"Reminder cancelled for request {request_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to cancel reminder: {str(e)}")
        return False

def start_scheduler():
    """Start background scheduler for reminders"""
    global scheduler_started
    if not scheduler_started and not scheduler.running:
        scheduler.start()
        scheduler_started = True
        logger.info("APScheduler started for reminder tasks")
