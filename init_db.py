"""
Initialize the database with the correct schema
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db

def init_database():
    """Create all database tables"""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("[OK] Database initialized successfully!")
        print("[OK] All tables created:")
        print("  - employees")
        print("  - visitor_requests")
        print("  - employee_face_logins (with password support)")
        print("\n[OK] Database ready for use!")
        print("[OK] You can now:")
        print("  1. Start the Flask app: python app.py")
        print("  2. Test visitor request: http://localhost:5000/visitor")
        print("  3. Register an employee first at: http://localhost:5000/auth/register")

if __name__ == '__main__':
    init_database()
