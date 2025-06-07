# backend/firebase_handler.py

import firebase_admin
from firebase_admin import credentials, db
import datetime
import json

# --- Initialize Firebase App (do this once globally) ---
def init_firebase():
    cred = credentials.Certificate('smart_attendance.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://smart-attendance-rv-default-rtdb.firebaseio.com'
    })

# --- Add new student data ---
def add_student(student_id, name, fingerprint_id, face_encoding):
    ref = db.reference(f'students/{student_id}')
    ref.set({
        'name': name,
        'fingerprint_id': fingerprint_id,
        'face_encoding': face_encoding
    })
    print(f"Student {student_id} registered")

# --- Mark attendance ---
def mark_attendance(student_id):
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')

    ref = db.reference(f'attendance/{student_id}/{date}')
    ref.set({
        'time': time_str,
        'status': 'Present'
    })
    print(f"Marked attendance for {student_id} at {time_str}")

# --- Fetch all students (for dashboard) ---
def get_all_students():
    ref = db.reference('students')
    return ref.get()

# --- Fetch attendance for a student ---
def get_attendance(student_id):
    ref = db.reference(f'attendance/{student_id}')
    return ref.get()
