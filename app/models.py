from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import numpy as np

db = SQLAlchemy()

class Employee(db.Model):
    """Employee model for system users"""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    face_encoding = db.Column(db.LargeBinary, nullable=False)  # Serialized numpy array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    visitor_requests = db.relationship('VisitorRequest', backref='employee', lazy=True)
    face_login = db.relationship('EmployeeFaceLogin', backref='employee', uselist=False, lazy=True)

    def set_face_encoding(self, encoding):
        """Store numpy array as binary"""
        self.face_encoding = pickle.dumps(encoding)

    def get_face_encoding(self):
        """Retrieve numpy array from binary"""
        return pickle.loads(self.face_encoding)

    def __repr__(self):
        return f'<Employee {self.name}>'

class VisitorRequest(db.Model):
    """Visitor meeting request model"""
    __tablename__ = 'visitor_requests'

    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(120), nullable=False)
    visitor_phone = db.Column(db.String(20), nullable=False)
    visitor_email = db.Column(db.String(120), nullable=False)  # Required for email confirmations
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)  # Cloudinary URL
    face_encoding = db.Column(db.LargeBinary, nullable=False)  # Serialized numpy array
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    reminder_sent = db.Column(db.Boolean, default=False)

    def set_face_encoding(self, encoding):
        """Store numpy array as binary"""
        self.face_encoding = pickle.dumps(encoding)

    def get_face_encoding(self):
        """Retrieve numpy array from binary"""
        return pickle.loads(self.face_encoding)

    def __repr__(self):
        return f'<VisitorRequest {self.visitor_name} -> {self.employee.name}>'

class EmployeeFaceLogin(db.Model):
    """Employee facial recognition login encoding"""
    __tablename__ = 'employee_face_logins'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), unique=True, nullable=False)
    face_encoding = db.Column(db.LargeBinary, nullable=False)  # Serialized numpy array
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_face_encoding(self, encoding):
        """Store numpy array as binary"""
        self.face_encoding = pickle.dumps(encoding)

    def get_face_encoding(self):
        """Retrieve numpy array from binary"""
        return pickle.loads(self.face_encoding)

    def __repr__(self):
        return f'<EmployeeFaceLogin {self.employee.name}>'

