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

# Initialize hardware components
fingerprint_sensor = FingerprintSensor()
face_recognizer = FaceRecognizer()
lcd = LCD()
leds = LEDs()
buzzer = Buzzer()
firebase = FirebaseHandler()

# Flask app setup
app = Flask(__name__)
CORS(app)  # Allows frontend to make API calls

@app.route("/register", methods=["POST"])
def register_student():
    data = request.json
    student_id = data.get("student_id")
    name = data.get("name")

    if not student_id or not name:
        return jsonify({"success": False, "error": "Missing student_id or name"}), 400

    with open(PENDING_FILE, "w") as f:
        json.dump({"student_id": student_id, "name": name}, f)

    print(f"[API] Received student registration: {student_id} - {name}")
    return jsonify({"success": True})

def load_pending_student():
    if not os.path.exists(PENDING_FILE):
        return None
    with open(PENDING_FILE, "r") as f:
        data = json.load(f)
    os.remove(PENDING_FILE)
    return data

def button_callback(channel):
    print("Button pressed!")

def biometric_loop():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

    print("[Backend] Biometric main loop started...")

    while True:
        pending = load_pending_student()
        if pending:
            student_id = pending["student_id"]
            name = pending["name"]

            lcd.display("Enroll Finger", "Place finger")
            leds.green_blink_slow()
            success_fp = fingerprint_sensor.enroll(student_id)
            leds.green_off()

            if not success_fp:
                lcd.display("Fingerprint", "Enroll Failed")
                buzzer.error_beep()
                continue

            lcd.display("Enroll Face", "Look at camera")
            leds.green_on()
            success_face, face_encoding = face_recognizer.enroll()
            leds.green_off()

            if not success_face:
                lcd.display("Face Enrollment", "Failed")
                buzzer.error_beep()
                continue

            firebase.add_student(student_id, name, fingerprint_sensor.get_template_id(), face_encoding)

            lcd.display("Registration", "Complete!")
            buzzer.success_beep()
            print(f"[Backend] Enrollment complete for {student_id} - {name}")

        time.sleep(2)

if __name__ == "__main__":
    try:
        # Start biometric loop in a background thread
        biometric_thread = threading.Thread(target=biometric_loop)
        biometric_thread.start()

        # Start Flask API server
        print("[Flask] Starting API server on http://<rpi-ip>:5000")
        app.run(host="0.0.0.0", port=5000)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Clean exit")
