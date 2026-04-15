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
        # Log incoming data
        logger.info(f"Form data received: {request.form.keys()}")
        
        visitor_name = request.form.get('visitorName')
        employee_name = request.form.get('employeeContact')
        visitor_email = request.form.get('visitorEmail')
        visitor_phone = request.form.get('phoneNumber')
        face_image = request.form.get('faceImage')

        # Validate inputs
        if not all([visitor_name, employee_name, visitor_email, visitor_phone, face_image]):
            missing = []
            if not visitor_name: missing.append('visitorName')
            if not employee_name: missing.append('employeeContact')
            if not visitor_email: missing.append('visitorEmail')
            if not visitor_phone: missing.append('phoneNumber')
            if not face_image: missing.append('faceImage')
            
            logger.error(f"Missing fields: {missing}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        logger.info(f"Looking for employee: {employee_name}")

        # Try to find employee in Firebase first
        employee_id, employee = FirebaseService.get_employee_by_name(employee_name)
        
        # If not in Firebase, try SQLite
        if not employee_id:
            logger.info(f"Employee not in Firebase, checking SQLite...")
            emp_obj = Employee.query.filter_by(name=employee_name).first()
            if not emp_obj:
                logger.error(f"Employee '{employee_name}' not found in either database")
                return jsonify({'error': f'Employee "{employee_name}" not found. Please check the name and try again.'}), 404
            
            # Create Firebase entry for this employee if it doesn't exist
            employee_id, firebase_error = FirebaseService.create_employee(
                name=emp_obj.name,
                email=emp_obj.email,
                phone=emp_obj.phone,
                face_encoding=emp_obj.get_face_encoding()
            )
            if firebase_error:
                logger.warning(f"Failed to sync employee to Firebase: {firebase_error}")
            employee = {'name': emp_obj.name, 'email': emp_obj.email}

        logger.info(f"Found employee: {employee_id}")

        # Encode visitor face
        visitor_encoding, error = facial_recognition.capture_and_encode_face(face_image)
        if error:
            logger.error(f"Face encoding failed: {error}")
            return jsonify({'error': error}), 400

        # Upload photo to Cloudinary
        photo_url, error = cloudinary_service.upload_photo(face_image, folder='visitor_requests')
        if error:
            # Use placeholder if Cloudinary fails
            photo_url = 'data:image/jpeg;base64,' + face_image.split(',')[-1] if ',' in face_image else 'https://via.placeholder.com/300?text=Visitor+Photo'
            logger.warning(f'⚠️ Cloudinary upload failed, using placeholder: {error}')

        # Create visitor request - AUTO-TRIGGERS EMAIL
        logger.info(f"Creating visitor request for {visitor_name} to meet {employee_name}")
        request_id, error = FirebaseRequestHandler.create_visitor_request(
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            employee_id=employee_id,
            photo_url=photo_url,
            face_encoding=visitor_encoding
        )

        if error:
            logger.error(f"Failed to create request: {error}")
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
                logger.info(f"Request also saved to SQLite")
        except Exception as e:
            logger.warning(f"⚠️ SQLite backup failed: {str(e)}")

        logger.info(f"✓ Request created successfully: {request_id}")
        return jsonify({
            'success': True,
            'message': 'Request submitted successfully. Employee notification sent!',
            'request_id': request_id
        }), 201

    except Exception as e:
        logger.error(f"✗ Error in submit_request: {str(e)}", exc_info=True)
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
