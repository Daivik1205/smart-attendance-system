import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import time

class FirebaseHandler:
    def __init__(self):
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})
        self.db_ref = db.reference('/')
        
    def add_student(self, student_id, name, fingerprint_data=None, face_data=None):
        student_ref = self.db_ref.child('students').child(student_id)
        student_ref.set({
            'name': name,
            'fingerprint_data': fingerprint_data,
            'face_data': face_data,
            'registered_at': datetime.now().isoformat()
        })
        
    def log_attendance(self, student_id, status="present"):
        today = datetime.now().strftime('%Y-%m-%d')
        student_ref = self.db_ref.child('students').child(student_id)
        student_data = student_ref.get()
        
        if student_data:
            # Check if already logged today
            today_log = self.db_ref.child('attendance').child(today).child(student_id).get()
            if today_log:
                return False  # Already logged today
            
            log_ref = self.db_ref.child('attendance').child(today).child(student_id)
            log_ref.set({
                'name': student_data['name'],
                'timestamp': datetime.now().isoformat(),
                'status': status
            })
            return True
        return False
    
    def get_student(self, student_id):
        return self.db_ref.child('students').child(student_id).get()
    
    def get_today_attendance(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return self.db_ref.child('attendance').child(today).get()
    
    def get_student_by_fingerprint(self, position):
        students = self.db_ref.child('students').get()
        if students:
            for student_id, data in students.items():
                if data.get('fingerprint_data', {}).get('position') == position:
                    return student_id
        return None