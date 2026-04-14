from flask import jsonify, render_template, request
from app.routes import visitor_bp
from app.models import db, Employee, VisitorRequest
from app.services import facial_recognition, cloudinary_service
from app.services.firebase_service import FirebaseService
from app.services.firebase_request_handler import FirebaseRequestHandler
import logging

logger = logging.getLogger(__name__)

@visitor_bp.route('/', methods=['GET'])
def kiosk():
    """Visitor kiosk main page"""
    return render_template('visitor.html')

@visitor_bp.route('/submit-request', methods=['POST'])
def submit_request():
    """Submit visitor meeting request with facial photo - PHASE 2"""
    try:
        visitor_name = request.form.get('visitorName')
        employee_name = request.form.get('employeeContact')
        visitor_email = request.form.get('visitorEmail')
        visitor_phone = request.form.get('phoneNumber')
        face_image = request.form.get('faceImage')

        # Validate inputs
        if not all([visitor_name, employee_name, visitor_email, visitor_phone, face_image]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Find employee in Firebase by name
        employee_id, employee = FirebaseService.get_employee_by_name(employee_name)
        if not employee_id:
            return jsonify({'error': f'Employee "{employee_name}" not found'}), 404

        # Encode visitor face
        visitor_encoding, error = facial_recognition.capture_and_encode_face(face_image)
        if error:
            return jsonify({'error': error}), 400

        # Upload photo to Cloudinary
        photo_url, error = cloudinary_service.upload_photo(face_image, folder='visitor_requests')
        if error:
            # Use placeholder if Cloudinary fails
            photo_url = 'data:image/jpeg;base64,' + face_image.split(',')[-1] if ',' in face_image else 'https://via.placeholder.com/300?text=Visitor+Photo'
            logger.warning(f'⚠️ Cloudinary upload failed, using placeholder: {error}')

        # Create visitor request - AUTO-TRIGGERS EMAIL
        request_id, error = FirebaseRequestHandler.create_visitor_request(
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            employee_id=employee_id,
            photo_url=photo_url,
            face_encoding=visitor_encoding
        )

        if error:
            return jsonify({'error': error}), 500

        # Also save to SQLite for backup (optional)
        try:
            emp_obj = Employee.query.filter_by(name=employee_name).first()
            if emp_obj:
                visitor_req = VisitorRequest(
                    visitor_name=visitor_name,
                    visitor_email=visitor_email,
                    visitor_phone=visitor_phone,
                    employee_id=emp_obj.id,
                    photo_url=photo_url
                )
                visitor_req.set_face_encoding(visitor_encoding)
                db.session.add(visitor_req)
                db.session.commit()
        except Exception as e:
            logger.warning(f"⚠️ SQLite backup failed: {str(e)}")

        return jsonify({
            'success': True,
            'message': 'Request submitted successfully. Employee notification sent!',
            'request_id': request_id
        }), 201

    except Exception as e:
        logger.error(f"✗ Error in submit_request: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@visitor_bp.route('/check-status/<request_id>', methods=['GET'])
def check_status(request_id):
    """Check request status from Firebase"""
    try:
        request_data, error = FirebaseService.get_visitor_request(request_id)
        
        if not request_data:
            return jsonify({'error': 'Request not found'}), 404

        employee, _ = FirebaseService.get_employee(request_data.get('employee_id'))
        
        return jsonify({
            'status': request_data.get('status'),
            'visitor_name': request_data.get('visitor_name'),
            'employee_name': employee.get('name') if employee else 'Unknown',
            'responded_at': request_data.get('responded_at')
        }), 200

    except Exception as e:
        logger.error(f"✗ Error in check_status: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
