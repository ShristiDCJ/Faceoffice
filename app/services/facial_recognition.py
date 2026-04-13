import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import base64

def capture_and_encode_face(image_data):
    """
    Detect face in image and return simple encoding (face region hash)
    image_data: base64 encoded image string from browser
    Returns: face_encoding (numpy array) or None if no face detected
    """
    try:
        # Decode base64 image
        img_data = base64.b64decode(image_data.split(',')[1])
        image = Image.open(BytesIO(img_data))
        image_array = np.array(image)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

        # Load Haar Cascade classifier
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None, "No face detected. Please try again."

        if len(faces) > 1:
            return None, "Multiple faces detected. Please ensure only one face is visible."

        # Extract face region and create encoding (simple hash of pixel values)
        x, y, w, h = faces[0]
        face_region = image_array[y:y+h, x:x+w]

        # Create a simple encoding by resizing and flattening face region
        face_resized = cv2.resize(face_region, (50, 50))
        face_encoding = face_resized.flatten().astype(np.float32)

        return face_encoding, None

    except Exception as e:
        return None, f"Error processing image: {str(e)}"

def verify_faces(face_encoding1, face_encoding2, threshold=0.6):
    """
    Compare two face encodings using simple cosine distance
    Returns: True if faces match, False otherwise
    """
    try:
        # Normalize encodings
        enc1 = face_encoding1 / (np.linalg.norm(face_encoding1) + 1e-7)
        enc2 = face_encoding2 / (np.linalg.norm(face_encoding2) + 1e-7)

        # Calculate cosine distance
        distance = 1.0 - np.dot(enc1, enc2)

        return distance < threshold

    except Exception as e:
        print(f"Error verifying faces: {str(e)}")
        return False

def encode_face_from_image(image_path):
    """
    Load image and encode face from file path
    Returns: face_encoding or None
    """
    try:
        image_array = np.array(Image.open(image_path))
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None

        x, y, w, h = faces[0]
        face_region = image_array[y:y+h, x:x+w]
        face_resized = cv2.resize(face_region, (50, 50))
        face_encoding = face_resized.flatten().astype(np.float32)

        return face_encoding

    except Exception as e:
        print(f"Error encoding face: {str(e)}")
        return None
