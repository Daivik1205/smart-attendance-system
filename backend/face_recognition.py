# backend/face_recognition.py
import cv2
import face_recognition
import os
import numpy as np
from hardware import lcd_display, success, error, buzzer_beep
import time
from contextlib import contextmanager

FACES_DIR = 'faces/'
MAX_RETRIES = 2
FACE_DETECTION_TIMEOUT = 10  # seconds
MIN_FACE_SIZE = 100  # minimum face size in pixels

# Ensure folder exists
os.makedirs(FACES_DIR, exist_ok=True)

@contextmanager
def camera_context():
    cap = cv2.VideoCapture(0)
    try:
        if not cap.isOpened():
            lcd_display("Camera Error", "Not detected")
            error()
            buzzer_beep(3)
            raise RuntimeError("Camera not detected")
        yield cap
    finally:
        cap.release()

def validate_face_image(frame):
    """Check if frame contains exactly one good quality face"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if len(face_locations) != 1:
        return False, "1 face only"
    
    top, right, bottom, left = face_locations[0]
    face_height = bottom - top
    face_width = right - left
    
    if face_height < MIN_FACE_SIZE or face_width < MIN_FACE_SIZE:
        return False, "Move closer"
    
    # Check image focus (Laplacian variance)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    focus_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if focus_score < 100:
        return False, "Low quality"
    
    return True, ""

def capture_single_face_image(cap, angle, attempt):
    """Capture one face image with specific angle"""
    lcd_display(f"Look {angle}", f"Attempt {attempt+1}/{MAX_RETRIES}")
    time.sleep(3)  # Give user time to position
    
    start_time = time.time()
    while time.time() - start_time < FACE_DETECTION_TIMEOUT:
        ret, frame = cap.read()
        if not ret:
            lcd_display("Camera Error", "Read failed")
            error()
            return None
        
        valid, message = validate_face_image(frame)
        if valid:
            return frame
        
        lcd_display("Adjust Position", message)
        time.sleep(0.5)
    
    lcd_display("Timeout", "Try again")
    return None

def capture_face_images(student_id):
    """Capture 3 face images from different angles"""
    with camera_context() as cap:
        angles = ['Front', 'Left Tilt', 'Right Tilt']
        face_images = []
        
        for i, angle in enumerate(angles):
            frame = None
            for attempt in range(MAX_RETRIES):
                frame = capture_single_face_image(cap, angle, attempt)
                if frame is not None:
                    break
                
                if attempt < MAX_RETRIES - 1:
                    buzzer_beep(1)
                    time.sleep(1)
            
            if frame is None:
                error()
                return None
            
            # Save successful capture
            path = os.path.join(FACES_DIR, f"{student_id}_{i}.jpg")
            cv2.imwrite(path, frame)
            face_images.append(path)
            lcd_display("Captured", f"{angle} ✓")
            buzzer_beep(1)
            time.sleep(1)
        
        success()
        return face_images

def generate_face_encodings(face_image_paths):
    """Generate face encodings from captured images"""
    if len(face_image_paths) != 3:
        return None
    
    encodings = []
    for img_path in face_image_paths:
        try:
            image = face_recognition.load_image_file(img_path)
            enc = face_recognition.face_encodings(image)
            
            if not enc:
                print(f"Encoding failed for {img_path}")
                continue
                
            encodings.append(enc[0])
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
            continue
    
    if len(encodings) != 3:
        return None
    
    # Return averaged encoding with float32 conversion for Firebase
    avg_encoding = np.mean(encodings, axis=0)
    return avg_encoding.astype(np.float32).tolist()