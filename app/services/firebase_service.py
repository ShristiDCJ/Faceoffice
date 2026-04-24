# app/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, db, initialize_app
import os
import logging
from datetime import datetime
import pickle
import base64

logger = logging.getLogger(__name__)

class FirebaseService:
    """Firebase Realtime Database service for all CRUD operations"""
    
    _initialized = False
    
    @staticmethod
    def initialize():
        """Initialize Firebase Admin SDK - call this once on app startup"""
        if FirebaseService._initialized:
            return
        
        try:
            firebase_key_path = os.environ.get('FIREBASE_KEY_PATH', 'firebase-key.json')
            firebase_db_url = os.environ.get('FIREBASE_DB_URL')
            
            if not firebase_db_url:
                raise ValueError("FIREBASE_DB_URL not set in environment variables")
            
            cred = credentials.Certificate(firebase_key_path)
            initialize_app(cred, {'databaseURL': firebase_db_url})
            FirebaseService._initialized = True
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise
    
    # ============= EMPLOYEE OPERATIONS =============
    
    @staticmethod
    def create_employee(name, email, phone, face_encoding):
        """Create new employee in Firebase"""
        try:
            # Encode face_encoding to base64 for storage
            encoding_b64 = base64.b64encode(pickle.dumps(face_encoding)).decode()
            
            employee_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'face_encoding': encoding_b64,
                'created_at': datetime.utcnow().isoformat()
            }
            
            ref = db.reference('employees')
            new_emp = ref.push(employee_data)
            employee_id = new_emp.key
            
            logger.info(f"Employee '{name}' created with ID: {employee_id}")
            return employee_id, None
        
        except Exception as e:
            logger.error(f"Error creating employee: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_employee(employee_id):
        """Get employee by ID"""
        try:
            ref = db.reference(f'employees/{employee_id}')
            employee = ref.get()
            return employee, None
        except Exception as e:
            logger.error(f"Error fetching employee {employee_id}: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_employee_by_email(email):
        """Get employee by email"""
        try:
            ref = db.reference('employees')
            all_employees = ref.get()
            
            if all_employees:
                for emp_id, emp_data in all_employees.items():
                    if emp_data.get('email') == email:
                        return emp_id, emp_data
            
            return None, None
        except Exception as e:
            logger.error(f"Error fetching employee by email: {str(e)}")
            return None, None
    
    @staticmethod
    def get_employee_by_name(name):
        """Get employee by name"""
        try:
            ref = db.reference('employees')
            all_employees = ref.get()
            
            if all_employees:
                for emp_id, emp_data in all_employees.items():
                    if emp_data.get('name') == name:
                        return emp_id, emp_data
            
            return None, None
        except Exception as e:
            logger.error(f"Error fetching employee by name: {str(e)}")
            return None, None
    
    @staticmethod
    def get_all_employees():
        """Get all employees"""
        try:
            ref = db.reference('employees')
            employees = ref.get()
            return employees if employees else {}, None
        except Exception as e:
            logger.error(f"Error fetching all employees: {str(e)}")
            return {}, str(e)
    
    @staticmethod
    def update_employee(employee_id, data):
        """Update employee data"""
        try:
            ref = db.reference(f'employees/{employee_id}')
            ref.update(data)
            logger.info(f"Employee {employee_id} updated")
            return True, None
        except Exception as e:
            logger.error(f"Error updating employee: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def delete_employee(employee_id):
        """Delete employee"""
        try:
            ref = db.reference(f'employees/{employee_id}')
            ref.delete()
            logger.info(f"Employee {employee_id} deleted")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting employee: {str(e)}")
            return False, str(e)
    
    # ============= VISITOR REQUEST OPERATIONS =============
    
    @staticmethod
    def create_visitor_request(visitor_name, visitor_email, visitor_phone, 
                              employee_id, photo_url, face_encoding):
        """Create new visitor request in Firebase"""
        try:
            # Encode face_encoding
            encoding_b64 = base64.b64encode(pickle.dumps(face_encoding)).decode()
            
            request_data = {
                'visitor_name': visitor_name,
                'visitor_email': visitor_email,
                'visitor_phone': visitor_phone,
                'employee_id': employee_id,
                'photo_url': photo_url,
                'face_encoding': encoding_b64,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'responded_at': None,
                'reminder_sent': False
            }
            
            ref = db.reference('visitor_requests')
            new_req = ref.push(request_data)
            request_id = new_req.key
            
            logger.info(f"Visitor request '{visitor_name}' created with ID: {request_id}")
            return request_id, None
        
        except Exception as e:
            logger.error(f"Error creating visitor request: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_visitor_request(request_id):
        """Get visitor request by ID"""
        try:
            ref = db.reference(f'visitor_requests/{request_id}')
            request = ref.get()
            return request, None
        except Exception as e:
            logger.error(f"Error fetching visitor request {request_id}: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_pending_requests_for_employee(employee_email):
        """Get all pending requests for specific employee by EMAIL"""
        try:
            logger.info(f"Searching Firebase for requests with employee_email: {employee_email}")
            ref = db.reference('visitor_requests')
            all_requests = ref.get()
            pending_requests = []
        
            logger.info(f"Total requests in Firebase: {len(all_requests) if all_requests else 0}")
        
            if all_requests:
                for req_id, req_data in all_requests.items():
                    req_employee_id = req_data.get('employee_id')
                    req_status = req_data.get('status')
                
                    logger.info(f"Checking request {req_id}: employee_id={req_employee_id}, status={req_status}")
                
                    # Get employee data to compare email
                    emp_data, _ = FirebaseService.get_employee(req_employee_id)
                
                    if emp_data:
                        emp_email = emp_data.get('email')
                        logger.info(f"  Employee email in Firebase: {emp_email}")
                        logger.info(f"  Comparing: {emp_email} == {employee_email}? {emp_email == employee_email}")
                    
                        if emp_email == employee_email and req_status == 'pending':
                            logger.info(f"  ✓ MATCH! Adding to pending requests")
                            pending_requests.append({'id': req_id, **req_data})
                    else:
                        logger.warning(f"  Employee {req_employee_id} not found in Firebase")
            
            logger.info(f"Total pending requests found: {len(pending_requests)}")
            return pending_requests, None
        
        except Exception as e:
            logger.error(f"✗ Error fetching pending requests: {str(e)}", exc_info=True)
            return [], str(e)
    
    @staticmethod
    def get_all_pending_requests():
        """Get ALL pending visitor requests across all employees"""
        try:
            ref = db.reference('visitor_requests')
            all_requests = ref.get()
            pending_requests = []

            if all_requests:
                for req_id, req_data in all_requests.items():
                    if req_data.get('status') == 'pending':
                        # Fetch employee details to include name/email
                        emp_data, _ = FirebaseService.get_employee(req_data.get('employee_id'))
                        req_data['employee_name'] = emp_data.get('name') if emp_data else 'Unknown'
                        req_data['employee_email'] = emp_data.get('email') if emp_data else 'Unknown'
                        pending_requests.append({'id': req_id, **req_data})

            return pending_requests, None

        except Exception as e:
            logger.error(f"Error fetching all pending requests: {str(e)}")
            return [], str(e)

    @staticmethod
    def get_all_requests_for_employee(employee_id):
        """Get all requests (pending, accepted, rejected) for employee"""
        try:
            ref = db.reference('visitor_requests')
            all_requests = ref.get()
            employee_requests = []
            
            if all_requests:
                for req_id, req_data in all_requests.items():
                    if req_data.get('employee_id') == employee_id:
                        employee_requests.append({'id': req_id, **req_data})
            
            return employee_requests, None
        except Exception as e:
            logger.error(f"Error fetching all employee requests: {str(e)}")
            return [], str(e)
    
    @staticmethod
    def update_request_status(request_id, status):
        """Update visitor request status (pending -> accepted/rejected)"""
        try:
            ref = db.reference(f'visitor_requests/{request_id}')
            ref.update({
                'status': status,
                'responded_at': datetime.utcnow().isoformat()
            })
            logger.info(f"Request {request_id} status updated to {status}")
            return True, None
        except Exception as e:
            logger.error(f"Error updating request status: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def delete_visitor_request(request_id):
        """Delete visitor request"""
        try:
            ref = db.reference(f'visitor_requests/{request_id}')
            ref.delete()
            logger.info(f"Request {request_id} deleted")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting request: {str(e)}")
            return False, str(e)
