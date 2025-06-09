# main.py
import time
import json
import os
import threading
import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from fingerprint import FingerprintSensor
from face_recognition import FaceRecognizer
from hardware import LCD, LEDs, Buzzer
from firebase_handler import FirebaseHandler

# Constants
PENDING_FILE = "pending_student.json"
BUTTON_PIN = 17  # GPIO pin connected to physical button
ENROLLMENT_TIMEOUT = 300  # 5 minutes timeout for enrollment

# Initialize components
fingerprint_sensor = FingerprintSensor()
face_recognizer = FaceRecognizer()
lcd = LCD()
leds = LEDs()
buzzer = Buzzer()
firebase = FirebaseHandler()

app = Flask(__name__)
CORS(app)

class EnrollmentManager:
    def __init__(self):
        self.current_student = None
        self.enrollment_start_time = 0
        self.enrollment_active = False

    def start_enrollment(self, student_id, name):
        self.current_student = {
            "student_id": student_id,
            "name": name,
            "fingerprint_id": None,
            "face_encoding": None,
            "status": "pending"
        }
        self.enrollment_start_time = time.time()
        self.enrollment_active = True
        lcd.display("Enrollment", "Ready to start")
        leds.green_blink_slow()
        print(f"[Enrollment] Started for {student_id} - {name}")

    def complete_enrollment(self):
        if not self.current_student:
            return False

        # Save to Firebase
        firebase.add_student(
            self.current_student["student_id"],
            self.current_student["name"],
            self.current_student["fingerprint_id"],
            self.current_student["face_encoding"]
        )

        lcd.display("Enrollment", "Complete!")
        buzzer.success_beep()
        print(f"[Enrollment] Completed for {self.current_student['student_id']}")
        
        self.current_student = None
        self.enrollment_active = False
        return True

    def check_timeout(self):
        if (self.enrollment_active and 
            time.time() - self.enrollment_start_time > ENROLLMENT_TIMEOUT):
            lcd.display("Enrollment", "Timed out")
            buzzer.error_beep()
            self.current_student = None
            self.enrollment_active = False
            return True
        return False

enrollment_manager = EnrollmentManager()

@app.route("/register", methods=["POST"])
def register_student():
    data = request.json
    student_id = data.get("student_id")
    name = data.get("name")

    if not student_id or not name:
        return jsonify({"success": False, "error": "Missing student_id or name"}), 400

    # Check if enrollment is already in progress
    if enrollment_manager.enrollment_active:
        return jsonify({
            "success": False,
            "error": "Another enrollment in progress"
        }), 423  # 423 Locked

    enrollment_manager.start_enrollment(student_id, name)
    return jsonify({"success": True})

@app.route("/enrollment/status", methods=["GET"])
def get_enrollment_status():
    status = {
        "active": enrollment_manager.enrollment_active,
        "student": enrollment_manager.current_student,
        "timeout": ENROLLMENT_TIMEOUT - (time.time() - enrollment_manager.enrollment_start_time) 
                   if enrollment_manager.enrollment_active else 0
    }
    return jsonify(status)

def button_callback(channel):
    if not enrollment_manager.enrollment_active:
        return

    print("Button pressed - starting enrollment")
    lcd.display("Place finger", "on sensor")
    leds.green_on()

    try:
        # Fingerprint enrollment
        fingerprint_id = fingerprint_sensor.enroll()
        if fingerprint_id is None:
            lcd.display("Fingerprint", "Failed")
            buzzer.error_beep()
            return

        enrollment_manager.current_student["fingerprint_id"] = fingerprint_id
        lcd.display("Fingerprint OK", "Now face")
        buzzer.success_beep()

        # Face enrollment
        success, face_encoding = face_recognizer.enroll()
        if not success:
            lcd.display("Face enroll", "Failed")
            buzzer.error_beep()
            return

        enrollment_manager.current_student["face_encoding"] = face_encoding
        enrollment_manager.complete_enrollment()

    except Exception as e:
        print(f"Enrollment error: {str(e)}")
        lcd.display("Error", str(e))
        buzzer.error_beep()

def biometric_loop():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

    print("[Backend] Biometric main loop started...")

    while True:
        # Check for enrollment timeout
        if enrollment_manager.check_timeout():
            print("[Enrollment] Timed out")

        time.sleep(1)

if __name__ == "__main__":
    try:
        # Start biometric loop in a background thread
        biometric_thread = threading.Thread(target=biometric_loop)
        biometric_thread.daemon = True
        biometric_thread.start()

        # Start Flask API server
        print("[Flask] Starting API server on http://<rpi-ip>:5000")
        app.run(host="0.0.0.0", port=5000)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Clean exit")