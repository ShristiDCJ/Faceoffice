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
        logger.info("=" * 50)
        logger.info("NEW VISITOR REQUEST INCOMING")
        logger.info("=" * 50)
        
        # Get form data
        visitor_name = request.form.get('visitorName', '').strip()
        employee_name = request.form.get('employeeContact', '').strip()
        visitor_email = request.form.get('visitorEmail', '').strip()
        visitor_phone = request.form.get('phoneNumber', '').strip()
        face_image = request.form.get('faceImage', '').strip()

        logger.info(f"Visitor: {visitor_name}")
        logger.info(f"Employee Target: {employee_name}")
        logger.info(f"Visitor Email: {visitor_email}")
        logger.info(f"Visitor Phone: {visitor_phone}")
        logger.info(f"Face Image Present: {bool(face_image)}")

        # Validate inputs
        if not all([visitor_name, employee_name, visitor_email, visitor_phone, face_image]):
            error_msg = "Missing required fields"
            logger.error(f"VALIDATION ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400

        # ===== EMPLOYEE LOOKUP =====
        logger.info(f"\n--- EMPLOYEE LOOKUP ---")
        logger.info(f"Looking for employee: '{employee_name}'")
        
        employee_id = None
        employee_email = None
        
        # Try Firebase first
        logger.info("Checking Firebase...")
        emp_firebase_id, emp_firebase_data = FirebaseService.get_employee_by_name(employee_name)
        
        if emp_firebase_data:
            logger.info(f"✓ Found in Firebase: ID={emp_firebase_id}")
            employee_id = emp_firebase_id
            employee_email = emp_firebase_data.get('email')
        else:
            logger.info("✗ Not in Firebase, checking SQLite...")
            emp_sqlite = Employee.query.filter_by(name=employee_name).first()
            
            if emp_sqlite:
                logger.info(f"✓ Found in SQLite: ID={emp_sqlite.id}")
                
                # Sync this employee to Firebase
                logger.info("Syncing employee to Firebase...")
                sync_id, sync_error = FirebaseService.create_employee(
                    name=emp_sqlite.name,
                    email=emp_sqlite.email,
                    phone=emp_sqlite.phone,
                    face_encoding=emp_sqlite.get_face_encoding()
                )
                
                if not sync_error:
                    logger.info(f"✓ Synced to Firebase: ID={sync_id}")
                    employee_id = sync_id
                    employee_email = emp_sqlite.email
                else:
                    logger.warning(f"⚠️ Firebase sync failed: {sync_error}")
                    # Still use SQLite employee
                    employee_id = str(emp_sqlite.id)  # Use SQLite ID as fallback
                    employee_email = emp_sqlite.email
            else:
                logger.error(f"✗ Employee '{employee_name}' NOT FOUND in either database")
                return jsonify({
                    'error': f'Employee "{employee_name}" not found. Please check the spelling and try again.'
                }), 404

        if not employee_id:
            logger.error("CRITICAL: No employee ID obtained")
            return jsonify({'error': 'Internal error: could not determine employee'}), 500

        logger.info(f"Final Employee ID: {employee_id}")
        logger.info(f"Final Employee Email: {employee_email}")

        # ===== FACE ENCODING =====
        logger.info(f"\n--- FACE ENCODING ---")
        logger.info("Extracting face encoding...")
        visitor_encoding, face_error = facial_recognition.capture_and_encode_face(face_image)
        
        if face_error:
            logger.error(f"✗ Face encoding failed: {face_error}")
            return jsonify({'error': face_error}), 400
        
        logger.info("✓ Face encoded successfully")

        # ===== PHOTO UPLOAD =====
        logger.info(f"\n--- PHOTO UPLOAD ---")
        logger.info("Uploading to Cloudinary...")
        photo_url, upload_error = cloudinary_service.upload_photo(face_image, folder='visitor_requests')
        
        if upload_error:
            logger.warning(f"⚠️ Cloudinary upload failed: {upload_error}")
            # Use base64 as fallback
            photo_url = face_image if face_image.startswith('data:') else f'data:image/jpeg;base64,{face_image}'
            logger.info("Using base64 encoded image as fallback")
        else:
            logger.info(f"✓ Photo uploaded: {photo_url[:80]}...")

        # ===== CREATE REQUEST =====
        logger.info(f"\n--- REQUEST CREATION ---")
        logger.info("Creating visitor request in Firebase...")
        
        request_id, create_error = FirebaseRequestHandler.create_visitor_request(
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            employee_id=employee_id,
            photo_url=photo_url,
            face_encoding=visitor_encoding
        )

        if create_error:
            logger.error(f"✗ Firebase request creation failed: {create_error}")
            return jsonify({'error': f'Failed to create request: {create_error}'}), 500

        logger.info(f"✓ Request created in Firebase: {request_id}")

        # ===== SQLITE BACKUP =====
        logger.info(f"\n--- SQLITE BACKUP ---")
        try:
            emp_sqlite = Employee.query.filter_by(name=employee_name).first()
            if emp_sqlite:
                visitor_req = VisitorRequest(
                    visitor_name=visitor_name,
                    visitor_email=visitor_email,
                    visitor_phone=visitor_phone,
                    employee_id=emp_sqlite.id,
                    photo_url=photo_url
                )
                visitor_req.set_face_encoding(visitor_encoding)
                db.session.add(visitor_req)
                db.session.commit()
                logger.info("✓ Request also saved to SQLite")
            else:
                logger.warning("⚠️ Could not save to SQLite (employee not found)")
        except Exception as e:
            logger.warning(f"⚠️ SQLite backup failed: {str(e)}")
            db.session.rollback()

        logger.info("\n" + "=" * 50)
        logger.info("✓ VISITOR REQUEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)

        return jsonify({
            'success': True,
            'message': 'Request submitted successfully! The employee will be notified via email.',
            'request_id': request_id
        }), 201

    except Exception as e:
        logger.error(f"\n{'=' * 50}")
        logger.error(f"✗ CRITICAL ERROR IN submit_request: {str(e)}")
        logger.error(f"{'=' * 50}")
        logger.exception("Full traceback:")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@visitor_bp.route('/check-status/<request_id>', methods=['GET'])
def check_status(request_id):
    """Check request status from Firebase"""
    try:
        logger.info(f"Checking status for request: {request_id}")
        
        request_data, error = FirebaseService.get_visitor_request(request_id)
        
        if not request_data:
            logger.warning(f"Request {request_id} not found")
            return jsonify({'error': 'Request not found'}), 404

        employee, _ = FirebaseService.get_employee(request_data.get('employee_id'))
        
        response_data = {
            'status': request_data.get('status'),
            'visitor_name': request_data.get('visitor_name'),
            'employee_name': employee.get('name') if employee else 'Unknown',
            'responded_at': request_data.get('responded_at')
        }
        
        logger.info(f"Status: {response_data['status']}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"✗ Error in check_status: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
