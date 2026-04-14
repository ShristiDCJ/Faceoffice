from flask import jsonify, render_template, request
from app.routes import admin_bp
from app.models import db, Employee, EmployeeFaceLogin, VisitorRequest
from app.services import facial_recognition
from app.services.firebase_service import FirebaseService
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
        face_image = request.form.get('faceImage')

        # Validate inputs
        if not all([name, email, phone, face_image]):
            return jsonify({'error': 'Missing required fields'}), 400

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
            phone=phone
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
        # Also save to Firebase Realtime Database
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
