import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import threading
from config import *
from fingerprint import FingerprintSensor
from camera_face import FaceRecognizer
from firebase_handler import FirebaseHandler
from lcd_display import LCDDisplay
from led_buzzer import LEDBuzzer

class AttendanceSystem:
    def __init__(self):
        # Initialize components
        self.lcd = LCDDisplay()
        self.led_buzzer = LEDBuzzer()
        self.fingerprint = FingerprintSensor()
        self.face_recognizer = FaceRecognizer()
        self.firebase = FirebaseHandler()
        
        # System state
        self.running = False
        self.session_start_time = None
        self.last_press_time = 0
        
        # Setup button
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                            callback=self.button_callback, 
                            bouncetime=300)
        
        # Initial display
        self.lcd.display_string("Attendance System", 1)
        self.lcd.display_string("Press to start", 2)
        
    def button_callback(self, channel):
        current_time = time.time()
        if (current_time - self.last_press_time) >= DEBOUNCE_DELAY:
            self.last_press_time = current_time
            self.toggle_system()
            
    def toggle_system(self):
        if self.running:
            self.stop_attendance()
        else:
            self.start_attendance()
            
    def start_attendance(self):
        self.running = True
        self.session_start_time = datetime.now()
        self.lcd.display_string("System Running", 1)
        self.lcd.display_string("Scan Fingerprint", 2)
        self.led_buzzer.success()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_attendance)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_attendance(self):
        self.running = False
        self.lcd.display_string("System Stopped", 1)
        self.lcd.display_string("Press to start", 2)
        self.led_buzzer.failure()
        
    def check_session_timeout(self):
        if self.session_start_time and self.running:
            elapsed = datetime.now() - self.session_start_time
            if elapsed > timedelta(hours=MAX_SESSION_HOURS):
                self.stop_attendance()
                return True
        return False
        
    def monitor_attendance(self):
        while self.running and not self.check_session_timeout():
            # Step 1: Fingerprint scan
            fingerprint_pos = self.fingerprint.search_finger()
            if fingerprint_pos is None:
                time.sleep(0.1)
                continue
                
            # Get student ID from fingerprint position
            student_id = self.firebase.get_student_by_fingerprint(fingerprint_pos)
            if not student_id:
                self.lcd.display_string("Fingerprint not", 1)
                self.lcd.display_string("registered", 2)
                self.led_buzzer.failure()
                time.sleep(2)
                self.lcd.display_string("Scan Fingerprint", 2)
                continue
                
            # Step 2: Face recognition
            self.lcd.display_string("Look at camera", 2)
            face_id = self.face_recognizer.recognize_face()
            
            if face_id != student_id:
                self.lcd.display_string("Face mismatch", 1)
                self.lcd.display_string("Try again", 2)
                self.led_buzzer.failure()
                time.sleep(2)
                self.lcd.display_string("Scan Fingerprint", 2)
                continue
                
            # Both authentications successful
            student = self.firebase.get_student(student_id)
            if student:
                self.lcd.display_string(f"Welcome {student['name']}", 1)
                self.lcd.display_string("Attendance logged", 2)
                if self.firebase.log_attendance(student_id):
                    self.led_buzzer.success()
                else:
                    self.lcd.display_string("Already logged", 2)
                    self.led_buzzer.failure()
                time.sleep(3)
                self.lcd.display_string("System Running", 1)
                self.lcd.display_string("Scan Fingerprint", 2)
                
    def cleanup(self):
        self.running = False
        self.lcd.clear()
        self.led_buzzer.off()
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        system = AttendanceSystem()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        system.cleanup()