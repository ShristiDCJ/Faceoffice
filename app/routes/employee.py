from flask import jsonify, render_template, request, session
from app.routes import employee_bp
from app.models import db, VisitorRequest, Employee
from app.services import request_handler
from functools import wraps

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
    """Get pending visitor requests for employee (API)"""
    try:
        employee_id = session.get('employee_id')
        requests = VisitorRequest.query.filter_by(
            employee_id=employee_id,
            status='pending'
        ).order_by(VisitorRequest.created_at.desc()).all()

        requests_data = []
        for req in requests:
            requests_data.append({
                'id': req.id,
                'visitor_name': req.visitor_name,
                'visitor_phone': req.visitor_phone,
                'photo_url': req.photo_url,
                'status': req.status,
                'created_at': req.created_at.isoformat()
            })

        return jsonify({'requests': requests_data}), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@employee_bp.route('/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    """Accept visitor request"""
    try:
        employee_id = session.get('employee_id')

        # Verify ownership
        visitor_request = VisitorRequest.query.get(request_id)
        if not visitor_request or visitor_request.employee_id != employee_id:
            return jsonify({'error': 'Request not found or unauthorized'}), 404

        # Accept request
        success, error = request_handler.accept_request(request_id)

        if success:
            return jsonify({'success': True, 'message': 'Request accepted'}), 200
        else:
            return jsonify({'error': error}), 500

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@employee_bp.route('/reject/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    """Reject visitor request"""
    try:
        employee_id = session.get('employee_id')

        # Verify ownership
        visitor_request = VisitorRequest.query.get(request_id)
        if not visitor_request or visitor_request.employee_id != employee_id:
            return jsonify({'error': 'Request not found or unauthorized'}), 404

        # Reject request
        success, error = request_handler.reject_request(request_id)

        if success:
            return jsonify({'success': True, 'message': 'Request rejected'}), 200
        else:
            return jsonify({'error': error}), 500

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@employee_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout employee"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200
