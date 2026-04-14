import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class FirebaseService:
    def __init__(self, database_url):
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
        firebase_admin.initialize_app(cred, {'databaseURL': database_url})

    def create_employee(self, employee_data):
        ref = db.reference('employees')
        return ref.push(employee_data)

    def read_employee(self, employee_id):
        ref = db.reference(f'employees/{employee_id}')
        return ref.get()

    def update_employee(self, employee_id, updated_data):
        ref = db.reference(f'employees/{employee_id}')
        ref.update(updated_data)

    def delete_employee(self, employee_id):
        ref = db.reference(f'employees/{employee_id}')
        ref.delete()

    def create_visitor(self, visitor_data):
        ref = db.reference('visitors')
        return ref.push(visitor_data)

    def read_visitor(self, visitor_id):
        ref = db.reference(f'visitors/{visitor_id}')
        return ref.get()

    def update_visitor(self, visitor_id, updated_data):
        ref = db.reference(f'visitors/{visitor_id}')
        ref.update(updated_data)

    def delete_visitor(self, visitor_id):
        ref = db.reference(f'visitors/{visitor_id}')
        ref.delete()
