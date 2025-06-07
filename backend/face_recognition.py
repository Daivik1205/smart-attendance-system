# backend/face_recognition.py

import cv2
import face_recognition
import os
import numpy as np
from hardware import lcd_display, success, error, buzzer_beep
import time

FACES_DIR = 'faces/'

# Ensure folder exists
os.makedirs(FACES_DIR, exist_ok=True)

# Capture and save 3 face images
def capture_face_images(student_id):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not detected")
        return None

    angles = ['Front', 'Left Tilt', 'Right Tilt']
    face_images = []

    for i, angle in enumerate(angles):
        lcd_display(f"Look {angle}", f"Photo {i+1}/3 in 3s")
        time.sleep(3)
        ret, frame = cap.read()
        if not ret:
            lcd_display("Camera error", "Try again")
            error()
            cap.release()
            return None

        # Validate face
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) != 1:
            lcd_display("1 face only", "Retry")
            error()
            buzzer_beep()
            cap.release()
            return None

        # Save face image
        path = os.path.join(FACES_DIR, f"{student_id}_{i}.jpg")
        cv2.imwrite(path, frame)
        face_images.append(path)

        lcd_display("Captured", f"{angle} ✓")
        time.sleep(1)

    cap.release()
    success()
    return face_images

# Generate face encodings
def generate_face_encodings(face_image_paths):
    encodings = []
    for img_path in face_image_paths:
        image = face_recognition.load_image_file(img_path)
        enc = face_recognition.face_encodings(image)
        if not enc:
            print(f"Encoding failed for {img_path}")
            continue
        encodings.append(enc[0])

    if len(encodings) != 3:
        return None

    # Return averaged encoding
    return np.mean(encodings, axis=0).tolist()
