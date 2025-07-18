from deepface import DeepFace
from PIL import Image
import numpy as np

def analyze_emotion(image_path: str):
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
    except Exception as e:
        return f"Emotion detection failed: {str(e)}"
    