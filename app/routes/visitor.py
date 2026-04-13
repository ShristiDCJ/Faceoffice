from flask import jsonify, render_template, request
from app.routes import visitor_bp
from app.models import db, VisitorRequest, Employee
from app.services import facial_recognition
from app.services import cloudinary_service
from app.services import request_handler

@visitor_bp.route('/', methods=['GET'])
def kiosk():
    """Visitor kiosk main page"""
    return render_template('visitor.html')

@visitor_bp.route('/submit-request', methods=['POST'])
def submit_request():
    """Submit visitor meeting request with facial photo"""
    try:
        visitor_name = request.form.get('visitorName')
        employee_contact = request.form.get('employeeContact')
        visitor_email = request.form.get('visitorEmail')
        visitor_phone = request.form.get('phoneNumber')
        face_image = request.form.get('faceImage')

        # Validate inputs
        if not all([visitor_name, employee_contact, visitor_email, visitor_phone, face_image]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Find employee by name
        employee = Employee.query.filter_by(name=employee_contact).first()
        if not employee:
            return jsonify({'error': f'Employee "{employee_contact}" not found'}), 404

        # Encode and verify visitor face
        visitor_encoding, error = facial_recognition.capture_and_encode_face(face_image)
        if error:
            return jsonify({'error': error}), 400

        # Upload photo to Cloudinary (optional - use placeholder if fails)
        photo_url, error = cloudinary_service.upload_photo(face_image, folder='visitor_requests')
        if error:
            # Use a placeholder URL if Cloudinary fails
            photo_url = 'data:image/jpeg;base64,' + face_image.split(',')[-1] if ',' in face_image else 'https://via.placeholder.com/300?text=Visitor+Photo'
            print(f'Cloudinary upload failed, using placeholder: {error}')

        # Create visitor request and send notifications
        request_id, error = request_handler.create_visitor_request(
            visitor_name, visitor_email, visitor_phone, employee.id, photo_url, visitor_encoding
        )

        if error:
            return jsonify({'error': error}), 500

        return jsonify({
            'success': True,
            'message': 'Request submitted successfully',
            'request_id': request_id
        }), 201

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@visitor_bp.route('/check-status/<int:request_id>', methods=['GET'])
def check_status(request_id):
    """Check request acceptance status"""
    try:
        visitor_request = VisitorRequest.query.get(request_id)

        if not visitor_request:
            return jsonify({'error': 'Request not found'}), 404

        return jsonify({
            'status': visitor_request.status,
            'visitor_name': visitor_request.visitor_name,
            'employee_name': visitor_request.employee.name,
            'responded_at': visitor_request.responded_at.isoformat() if visitor_request.responded_at else None
        }), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
