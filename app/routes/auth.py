from flask import jsonify, render_template, request, session
from app.routes import auth_bp
from app.models import db, Employee, EmployeeFaceLogin
from app.services import facial_recognition
from app import create_app

@auth_bp.route('/login', methods=['GET'])
def login():
    """Employee facial login page"""
    return render_template('employee_login.html')

@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Verify employee face and create session"""
    try:
        data = request.get_json()
        face_image = data.get('faceImage')

        if not face_image:
            return jsonify({'error': 'No face image provided'}), 400

        # Encode captured face
        captured_encoding, error = facial_recognition.capture_and_encode_face(face_image)
        if error:
            return jsonify({'error': error}), 400

        # Find matching employee
        employees = Employee.query.all()
        matched_employee = None
        app = create_app()
        threshold = app.config.get('FACE_RECOGNITION_THRESHOLD', 0.6)

        for employee in employees:
            employee_encoding = employee.get_face_encoding()
            if facial_recognition.verify_faces(captured_encoding, employee_encoding, threshold):
                matched_employee = employee
                break

        if not matched_employee:
            return jsonify({'error': 'Face not recognized. Please try again.'}), 401

        # Create session
        session['employee_id'] = matched_employee.id
        session['employee_name'] = matched_employee.name
        session['employee_email'] = matched_employee.email

        return jsonify({
            'success': True,
            'message': f'Welcome {matched_employee.name}',
            'employee_id': matched_employee.id
        }), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout employee"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200
