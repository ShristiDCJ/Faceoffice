from flask import Blueprint

visitor_bp = Blueprint('visitor', __name__, url_prefix='/visitor')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
employee_bp = Blueprint('employee', __name__, url_prefix='/employee')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import individual route modules
from app.routes import visitor, auth, employee, admin
