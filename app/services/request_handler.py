from app.models import db, VisitorRequest, Employee
from app.services.notification import (
    notify_employee_visitor_arrived,
    send_visitor_acceptance_email,
    send_visitor_rejection_email,
    send_employee_pending_reminder_email,
    schedule_2min_reminder,
    cancel_reminder
)
from datetime import datetime

def create_visitor_request(visitor_name, visitor_email, visitor_phone, employee_id, photo_url, face_encoding):
    """Create new visitor request and trigger email notifications"""
    try:
        request_obj = VisitorRequest(
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            employee_id=employee_id,
            photo_url=photo_url
        )
        request_obj.set_face_encoding(face_encoding)
        db.session.add(request_obj)
        db.session.commit()

        employee = request_obj.employee

        # Schedule 2-minute reminder (sends email to employee)
        schedule_2min_reminder(request_obj.id, employee.email, employee.name, visitor_name)

        # Trigger employee email notification
        notify_employee_visitor_arrived(
            employee_email=employee.email,
            visitor_name=visitor_name,
            visitor_photo_url=photo_url
        )

        return request_obj.id, None

    except Exception as e:
        db.session.rollback()
        return None, str(e)

def accept_request(request_id):
    """Accept visitor request and send email confirmations"""
    try:
        request_obj = VisitorRequest.query.get(request_id)
        if not request_obj:
            return False, "Request not found"

        # Cancel reminder if not yet triggered
        cancel_reminder(request_id)

        # Update status
        request_obj.status = 'accepted'
        request_obj.responded_at = datetime.utcnow()
        db.session.commit()

        # Send email confirmations to visitor and employee
        send_visitor_acceptance_email(
            visitor_email=request_obj.visitor_email,
            visitor_name=request_obj.visitor_name,
            employee_name=request_obj.employee.name,
            employee_email=request_obj.employee.email
        )

        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)

def reject_request(request_id):
    """Reject visitor request and send email confirmations"""
    try:
        request_obj = VisitorRequest.query.get(request_id)
        if not request_obj:
            return False, "Request not found"

        # Cancel reminder if not yet triggered
        cancel_reminder(request_id)

        # Update status
        request_obj.status = 'rejected'
        request_obj.responded_at = datetime.utcnow()
        db.session.commit()

        # Send email confirmations to visitor and employee
        send_visitor_rejection_email(
            visitor_email=request_obj.visitor_email,
            visitor_name=request_obj.visitor_name,
            employee_name=request_obj.employee.name,
            employee_email=request_obj.employee.email
        )

        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)
