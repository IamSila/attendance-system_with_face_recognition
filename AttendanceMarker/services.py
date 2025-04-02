import face_recognition
from geopy.distance import geodesic
import numpy as np
import base64
from PIL import Image
from io import BytesIO

class FaceRecognitionService:
    @staticmethod
    def get_face_encoding(image_data):
        # Convert base64 image data to numpy array
        image = Image.open(BytesIO(base64.b64decode(image_data.split(',')[1])))
        image_np = np.array(image)
        
        # Get face encodings
        face_locations = face_recognition.face_locations(image_np)
        if not face_locations:
            return None
        face_encodings = face_recognition.face_encodings(image_np, face_locations)
        
        if face_encodings:
            return face_encodings[0].tobytes().hex()  # Convert to hex string for storage
        return None
    
    @staticmethod
    def verify_face(image_data, employee):
        # Get face encoding from image
        current_encoding = FaceRecognitionService.get_face_encoding(image_data)
        if not current_encoding:
            return False
            
        # Compare with stored encoding
        stored_encoding = np.frombuffer(bytes.fromhex(employee.face_encoding), dtype=np.float64)
        current_encoding = np.frombuffer(bytes.fromhex(current_encoding), dtype=np.float64)
        
        # Calculate face distance
        face_distance = face_recognition.face_distance([stored_encoding], current_encoding)[0]
        return face_distance < 0.6  # Threshold for match



class LocationService:
    @staticmethod
    def is_within_radius(user_lat, user_long, target_lat, target_long, radius_km=0.1):
        """
        Check if user is within radius (default 100 meters) of target location
        """
        user_location = (user_lat, user_long)
        target_location = (target_lat, target_long)
        distance = geodesic(user_location, target_location).kilometers
        return distance <= radius_km