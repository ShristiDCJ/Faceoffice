from flask import jsonify, render_template, request, session
from app.routes import employee_bp
from app.models import db, VisitorRequest
from app.services.firebase_service import FirebaseService
from app.services.firebase_request_handler import FirebaseRequestHandler
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """Decorator to check if employee is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            return jsonify({'error': 'Unauthorized. Please login first.'}), 401
        return f(*args, **kwargs)
    return decorated_function

@employee_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Employee dashboard - view pending requests"""
    return render_template('employee_dashboard.html')

@employee_bp.route('/dashboard/requests', methods=['GET'])
@login_required
def get_requests():
    """Get pending visitor requests for employee (API) - PHASE 3"""
    try:
        employee_id = session.get('employee_id')
        
        # Fetch pending requests from Firebase
        pending_requests, error = FirebaseService.get_pending_requests_for_employee(employee_id)
        
        if error:
            logger.error(f"✗ Error fetching requests: {error}")
            return jsonify({'error': error}), 500

        requests_data = []
        for req in pending_requests:
            requests_data.append({
                'id': req.get('id'),
                'visitor_name': req.get('visitor_name'),
                'visitor_phone': req.get('visitor_phone'),
                'photo_url': req.get('photo_url'),
                'status': req.get('status'),
                'created_at': req.get('created_at')
            })

        return jsonify({'requests': requests_data}), 200

    except Exception as e:
        logger.error(f"✗ Error in get_requests: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@employee_bp.route('/accept/<request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    """Accept visitor request - PHASE 4"""
    try:
        employee_id = session.get('employee_id')

        # Fetch request from Firebase
        request_data, error = FirebaseService.get_visitor_request(request_id)
        if not request_data or request_data.get('employee_id') != employee_id:
            return jsonify({'error': 'Request not found or unauthorized'}), 404

        # Accept request and send emails
        success, error = FirebaseRequestHandler.accept_request(request_id)

        if success:
            return jsonify({'success': True, 'message': 'Request accepted'}), 200
        else:
            return jsonify({'error': error}), 500

    except Exception as e:
        logger.error(f"✗ Error in accept_request: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@employee_bp.route('/reject/<request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    """Reject visitor request - PHASE 4"""
    try:
        employee_id = session.get('employee_id')

        # Fetch request from Firebase
        request_data, error = FirebaseService.get_visitor_request(request_id)
        if not request_data or request_data.get('employee_id') != employee_id:
            return jsonify({'error': 'Request not found or unauthorized'}), 404

        # Reject request and send emails
        success, error = FirebaseRequestHandler.reject_request(request_id)

        if success:
            return jsonify({'success': True, 'message': 'Request rejected'}), 200
        else:
            return jsonify({'error': error}), 500

    except Exception as e:
        logger.error(f"✗ Error in reject_request: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@employee_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout employee"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200
