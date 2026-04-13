from flask import jsonify, render_template, request
from app.routes import admin_bp
from app.models import db, Employee, EmployeeFaceLogin, VisitorRequest
from app.services import facial_recognition
import os

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

        # Check for duplicates
        if Employee.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        if Employee.query.filter_by(phone=phone).first():
            return jsonify({'error': 'Phone already registered'}), 409

        # Encode face
        face_encoding, error = facial_recognition.capture_and_encode_face(face_image)
        if error:
            return jsonify({'error': error}), 400

        # Create employee
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

        return jsonify({
            'success': True,
            'message': f'Employee {name} registered successfully',
            'employee_id': employee.id
        }), 201

    except Exception as e:
        db.session.rollback()
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
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete employee"""
    try:
        employee = Employee.query.get(employee_id)

        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Delete associated records
        VisitorRequest.query.filter_by(employee_id=employee_id).delete()
        EmployeeFaceLogin.query.filter_by(employee_id=employee_id).delete()
        db.session.delete(employee)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Employee deleted'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
