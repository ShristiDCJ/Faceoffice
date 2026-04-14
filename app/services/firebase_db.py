# app/services/firebase_db.py
import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime
import pickle
import base64
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase
cred_path = os.environ.get('FIREBASE_KEY_PATH', 'firebase-key.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ.get('FIREBASE_DB_URL')
    })

class FirebaseDB:
    """Firebase Realtime Database service"""
    
    @staticmethod
    def create_employee(name, email, phone, face_encoding):
        """Create employee in Firebase"""
        try:
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
            logger.info(f"Employee {name} created with ID: {new_emp.key}")
            return new_emp.key, None
        except Exception as e:
            logger.error(f"Error creating employee: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_employee(employee_id):
        """Get employee by ID"""
        try:
            ref = db.reference(f'employees/{employee_id}')
            data = ref.get()
            return data, None
        except Exception as e:
            logger.error(f"Error getting employee: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_employee_by_name(name):
        """Get employee by name"""
        try:
            ref = db.reference('employees')
            all_employees = ref.get()
            if all_employees:
                for emp_id, emp_data in all_employees.items():
                    if emp_data.get('name') == name:
                        return emp_id, emp_data, None
            return None, None, "Employee not found"
        except Exception as e:
            logger.error(f"Error getting employee by name: {str(e)}")
            return None, None, str(e)
    
    @staticmethod
    def get_all_employees():
        """Get all employees"""
        try:
            ref = db.reference('employees')
            data = ref.get()
            employees = []
            if data:
                for emp_id, emp_data in data.items():
                    employees.append({'id': emp_id, **emp_data})
            return employees, None
        except Exception as e:
            logger.error(f"Error getting all employees: {str(e)}")
            return [], str(e)
    
    @staticmethod
    def update_employee(employee_id, updates):
        """Update employee data"""
        try:
            ref = db.reference(f'employees/{employee_id}')
            ref.update(updates)
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
    
    # ========== VISITOR REQUESTS ==========
    
    @staticmethod
    def create_visitor_request(visitor_name, visitor_email, visitor_phone, employee_id, photo_url, face_encoding):
        """Create visitor request"""
        try:
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
                'responded_at': None
            }
            ref = db.reference('visitor_requests')
            new_req = ref.push(request_data)
            logger.info(f"Visitor request created: {new_req.key}")
            return new_req.key, None
        except Exception as e:
            logger.error(f"Error creating visitor request: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_visitor_request(request_id):
        """Get visitor request by ID"""
        try:
            ref = db.reference(f'visitor_requests/{request_id}')
            data = ref.get()
            return data, None
        except Exception as e:
            logger.error(f"Error getting visitor request: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def get_pending_requests_for_employee(employee_id):
        """Get pending requests for employee"""
        try:
            ref = db.reference('visitor_requests')
            all_requests = ref.get()
            pending = []
            if all_requests:
                for req_id, req_data in all_requests.items():
                    if req_data.get('employee_id') == employee_id and req_data.get('status') == 'pending':
                        pending.append({'id': req_id, **req_data})
            # Sort by created_at descending
            pending.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return pending, None
        except Exception as e:
            logger.error(f"Error getting pending requests: {str(e)}")
            return [], str(e)
    
    @staticmethod
    def update_request_status(request_id, status):
        """Update request status (accepted/rejected)"""
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
    def get_face_encoding(collection, item_id):
        """Retrieve and decode face encoding"""
        try:
            ref = db.reference(f'{collection}/{item_id}')
            data = ref.get()
            if data and 'face_encoding' in data:
                encoding_b64 = data['face_encoding']
                return pickle.loads(base64.b64decode(encoding_b64)), None
            return None, "Face encoding not found"
        except Exception as e:
            logger.error(f"Error decoding face encoding: {str(e)}")
            return None, str(e)
