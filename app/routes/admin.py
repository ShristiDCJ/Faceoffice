from flask import jsonify, render_template, request
from app.routes import admin_bp
from app.models import db, Employee, EmployeeFaceLogin, VisitorRequest
from app.services import facial_recognition
from app.services.firebase_service import FirebaseService
from app.services.firebase_request_handler import FirebaseRequestHandler
from werkzeug.security import generate_password_hash
import os
import logging

logger = logging.getLogger(__name__)

# Simple admin authentication using environment variable
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin-change-in-production')

@admin_bp.route('/register', methods=['GET'])
def register():
    """Admin employee registration page"""
    return render_template('admin_register.html')

@admin_bp.route('/register', methods=['POST'])
def register_employee():
    """Register new employee with facial encoding"""
    try:
        # For initial implementation, skip auth. Add password protection in production
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        face_image = request.form.get('faceImage')

        # Validate inputs
        if not all([name, email, phone, password, face_image]):
            return jsonify({'error': 'Missing required fields (name, email, phone, password, face)'}), 400

        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        # Check for duplicates in SQLite
        if Employee.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        if Employee.query.filter_by(phone=phone).first():
            return jsonify({'error': 'Phone already registered'}), 409

        # Encode face
        face_encoding, error = facial_recognition.capture_and_encode_face(face_image)
        if error:
            return jsonify({'error': error}), 400

        # Create employee in SQLite
        employee = Employee(
            name=name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password)
        )
        employee.set_face_encoding(face_encoding)

        db.session.add(employee)
        db.session.commit()

        # Create face login entry
        face_login = EmployeeFaceLogin(
            employee_id=employee.id
        )
        face_login.set_face_encoding(face_encoding)

        db.session.add(face_login)
        db.session.commit()

        # ===== FIREBASE SYNC (NEW) =====
        # Also save to Firebase Realtime Database (no password)
        employee_id_firebase, firebase_error = FirebaseService.create_employee(
            name=name,
            email=email,
            phone=phone,
            face_encoding=face_encoding
        )

        if firebase_error:
            logger.warning(f"⚠️ Firebase sync failed but employee was created in SQLite: {firebase_error}")
        else:
            logger.info(f"✓ Employee also saved to Firebase with ID: {employee_id_firebase}")

        logger.info(f"✓ Employee {name} registered with password hash")

        return jsonify({
            'success': True,
            'message': f'Employee {name} registered successfully',
            'employee_id': employee.id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"✗ Error in register_employee: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/employees', methods=['GET'])
def employees_list():
    """List all registered employees"""
    return render_template('admin_employees.html')

@admin_bp.route('/employees/list', methods=['GET'])
def get_employees_list():
    """Get list of employees (API)"""
    try:
        employees = Employee.query.all()

        employees_data = []
        for emp in employees:
            employees_data.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'phone': emp.phone,
                'created_at': emp.created_at.isoformat()
            })

        return jsonify({'employees': employees_data}), 200

    except Exception as e:
        logger.error(f"✗ Error in get_employees_list: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete employee"""
    try:
        employee = Employee.query.get(employee_id)

        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Delete associated records from SQLite
        VisitorRequest.query.filter_by(employee_id=employee_id).delete()
        EmployeeFaceLogin.query.filter_by(employee_id=employee_id).delete()
        db.session.delete(employee)
        db.session.commit()

        # Also delete from Firebase (optional)
        try:
            # Find employee in Firebase by email and delete
            emp_id_firebase, emp_data = FirebaseService.get_employee_by_email(employee.email)
            if emp_id_firebase:
                FirebaseService.delete_employee(emp_id_firebase)
                logger.info(f"✓ Employee also deleted from Firebase")
        except Exception as firebase_error:
            logger.warning(f"⚠️ Firebase deletion failed: {firebase_error}")

        return jsonify({'success': True, 'message': 'Employee deleted'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"✗ Error in delete_employee: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ============= ADMIN REQUEST APPROVAL ROUTES =============

@admin_bp.route('/requests', methods=['GET'])
def admin_requests():
    """Admin page to view and manage all pending visitor requests"""
    return render_template('admin_requests.html')

@admin_bp.route('/requests/list', methods=['GET'])
def get_all_pending_requests_api():
    """Get all pending visitor requests for admin (API)"""
    try:
        logger.info("Admin fetching all pending requests...")
        pending_requests, error = FirebaseService.get_all_pending_requests()

        if error:
            logger.warning(f"⚠️ Firebase fetch error: {error}")
            pending_requests = []

        logger.info(f"Found {len(pending_requests)} total pending requests")

        requests_data = []
        for req in pending_requests:
            request_data = {
                'id': req.get('id'),
                'visitor_name': req.get('visitor_name'),
                'visitor_phone': req.get('visitor_phone'),
                'visitor_email': req.get('visitor_email'),
                'photo_url': req.get('photo_url'),
                'status': req.get('status'),
                'created_at': req.get('created_at'),
                'employee_name': req.get('employee_name'),
                'employee_email': req.get('employee_email')
            }
            requests_data.append(request_data)
            logger.info(f"  - Request {req.get('id')}: {req.get('visitor_name')} -> {req.get('employee_name')} ({req.get('status')})")

        return jsonify({'requests': requests_data}), 200

    except Exception as e:
        logger.error(f"✗ Error in get_all_pending_requests_api: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/requests/<request_id>/accept', methods=['POST'])
def admin_accept_request(request_id):
    """Admin accepts a visitor request on behalf of an employee"""
    try:
        logger.info(f"\n--- ADMIN ACCEPTING REQUEST ---")
        logger.info(f"Request ID: {request_id}")

        # Fetch request from Firebase
        request_data, error = FirebaseService.get_visitor_request(request_id)
        if not request_data:
            logger.error(f"Request {request_id} not found")
            return jsonify({'error': 'Request not found'}), 404

        # Accept request using existing handler (sends emails to visitor & employee)
        success, error = FirebaseRequestHandler.accept_request(request_id)

        if success:
            logger.info(f"✓ Admin accepted request {request_id} successfully")
            return jsonify({'success': True, 'message': 'Request accepted by admin'}), 200
        else:
            logger.error(f"✗ Admin failed to accept request: {error}")
            return jsonify({'error': error}), 500

    except Exception as e:
        logger.error(f"✗ Error in admin_accept_request: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/requests/<request_id>/reject', methods=['POST'])
def admin_reject_request(request_id):
    """Admin rejects a visitor request on behalf of an employee"""
    try:
        logger.info(f"\n--- ADMIN REJECTING REQUEST ---")
        logger.info(f"Request ID: {request_id}")

        # Fetch request from Firebase
        request_data, error = FirebaseService.get_visitor_request(request_id)
        if not request_data:
            logger.error(f"Request {request_id} not found")
            return jsonify({'error': 'Request not found'}), 404

        # Reject request using existing handler (sends emails to visitor & employee)
        success, error = FirebaseRequestHandler.reject_request(request_id)

        if success:
            logger.info(f"✓ Admin rejected request {request_id} successfully")
            return jsonify({'success': True, 'message': 'Request rejected by admin'}), 200
        else:
            logger.error(f"✗ Admin failed to reject request: {error}")
            return jsonify({'error': error}), 500

    except Exception as e:
        logger.error(f"✗ Error in admin_reject_request: {str(e)}", exc_info=True)
        return jsonify({'error': f'Server error: {str(e)}'}), 500

