# app/services/firebase_request_handler.py
from app.services.firebase_service import FirebaseService
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class FirebaseRequestHandler:
    """Handle visitor request lifecycle and trigger emails"""
    
    @staticmethod
    def create_visitor_request(visitor_name, visitor_email, visitor_phone, 
                              employee_id, photo_url, face_encoding):
        """
        PHASE 2: Create visitor request and AUTO-TRIGGER employee email
        
        Flow:
        1. Store request in Firebase
        2. Fetch employee details from Firebase
        3. Send notification email to employee
        """
        try:
            # Step 1: Create request in Firebase
            request_id, error = FirebaseService.create_visitor_request(
                visitor_name=visitor_name,
                visitor_email=visitor_email,
                visitor_phone=visitor_phone,
                employee_id=employee_id,
                photo_url=photo_url,
                face_encoding=face_encoding
            )
            
            if error:
                logger.error(f"Failed to create visitor request: {error}")
                return None, error
            
            # Step 2: Fetch employee details from Firebase
            employee, error = FirebaseService.get_employee(employee_id)
            if not employee:
                logger.error(f"Employee {employee_id} not found")
                return request_id, "Employee not found"
            
            # Step 3: Send email notification to employee (AUTO-TRIGGER)
            success, email_error = EmailService.send_visitor_notification(
                employee_email=employee.get('email'),
                employee_name=employee.get('name'),
                visitor_name=visitor_name,
                visitor_photo_url=photo_url
            )
            
            if not success:
                logger.warning(f"Email notification failed but request was created: {email_error}")
            
            logger.info(f"✓ Visitor request created with ID: {request_id}")
            return request_id, None
        
        except Exception as e:
            logger.error(f"Error in create_visitor_request: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def accept_request(request_id):
        """
        PHASE 4: Accept request and send 2 emails
        
        Flow:
        1. Fetch request from Firebase
        2. Update status to "accepted"
        3. Send acceptance email to VISITOR
        4. Send confirmation email to EMPLOYEE
        """
        try:
            # Step 1: Fetch request
            request_data, error = FirebaseService.get_visitor_request(request_id)
            if not request_data:
                return False, "Request not found"
            
            # Step 2: Update status
            success, error = FirebaseService.update_request_status(request_id, 'accepted')
            if not success:
                return False, error
            
            # Step 3: Fetch employee details
            employee, _ = FirebaseService.get_employee(request_data.get('employee_id'))
            if not employee:
                return False, "Employee not found"
            
            # Step 4a: Send acceptance email to VISITOR
            success1, error1 = EmailService.send_approval_email(
                visitor_email=request_data.get('visitor_email'),
                visitor_name=request_data.get('visitor_name'),
                employee_name=employee.get('name'),
                employee_email=employee.get('email')
            )
            
            # Step 4b: Send confirmation email to EMPLOYEE
            success2, error2 = EmailService.send_approval_confirmation_to_employee(
                employee_email=employee.get('email'),
                employee_name=employee.get('name'),
                visitor_name=request_data.get('visitor_name')
            )
            
            if success1 and success2:
                logger.info(f"✓ Request {request_id} accepted and both emails sent")
                return True, None
            else:
                logger.warning(f"Request accepted but email sending had issues: {error1}, {error2}")
                return True, None
        
        except Exception as e:
            logger.error(f"Error in accept_request: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def reject_request(request_id):
        """
        PHASE 4: Reject request and send 2 emails
        
        Flow:
        1. Fetch request from Firebase
        2. Update status to "rejected"
        3. Send rejection email to VISITOR
        4. Send confirmation email to EMPLOYEE
        """
        try:
            # Step 1: Fetch request
            request_data, error = FirebaseService.get_visitor_request(request_id)
            if not request_data:
                return False, "Request not found"
            
            # Step 2: Update status
            success, error = FirebaseService.update_request_status(request_id, 'rejected')
            if not success:
                return False, error
            
            # Step 3: Fetch employee details
            employee, _ = FirebaseService.get_employee(request_data.get('employee_id'))
            if not employee:
                return False, "Employee not found"
            
            # Step 4a: Send rejection email to VISITOR
            success1, error1 = EmailService.send_rejection_email(
                visitor_email=request_data.get('visitor_email'),
                visitor_name=request_data.get('visitor_name'),
                employee_name=employee.get('name'),
                employee_email=employee.get('email')
            )
            
            # Step 4b: Send confirmation email to EMPLOYEE
            success2, error2 = EmailService.send_rejection_confirmation_to_employee(
                employee_email=employee.get('email'),
                employee_name=employee.get('name'),
                visitor_name=request_data.get('visitor_name')
            )
            
            if success1 and success2:
                logger.info(f"✓ Request {request_id} rejected and both emails sent")
                return True, None
            else:
                logger.warning(f"Request rejected but email sending had issues: {error1}, {error2}")
                return True, None
        
        except Exception as e:
            logger.error(f"Error in reject_request: {str(e)}")
            return False, str(e)
