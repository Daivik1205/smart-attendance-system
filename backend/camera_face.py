import cv2
import face_recognition
import pickle
import os
from datetime import datetime

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.load_faces()
        
    def load_faces(self):
        try:
            if os.path.exists('faces.dat'):
                with open('faces.dat', 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_ids = data['ids']
                print(f"Loaded {len(self.known_face_ids)} face encodings")
        except Exception as e:
            print(f"Error loading faces: {str(e)}")
            self.known_face_encodings = []
            self.known_face_ids = []
            
    def save_faces(self):
        with open('faces.dat', 'wb') as f:
            pickle.dump({
                'encodings': self.known_face_encodings,
                'ids': self.known_face_ids
            }, f)
            
    def register_face(self, student_id, image_path=None):
        if image_path:
            image = face_recognition.load_image_file(image_path)
        else:
            camera = cv2.VideoCapture(0)
            print("Look at the camera for face registration...")
            ret, frame = camera.read()
            if not ret:
                return None
            rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB
            camera.release()
            
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            print("No face detected")
            return None
            
        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        
        self.known_face_encodings.append(face_encoding)
        self.known_face_ids.append(student_id)
        self.save_faces()
        
        return face_encoding.tolist()
        
    def recognize_face(self):
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if not ret:
            return None
            
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            camera.release()
            return None
            
        face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        camera.release()
        
        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            return self.known_face_ids[first_match_index]
        return None