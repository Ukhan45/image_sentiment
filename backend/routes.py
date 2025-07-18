import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, UploadFile, File
from utils.emotion import analyze_emotion
from utils.object import detect_objects

import shutil

router = APIRouter()

@router.post("/analyze/")
async def analyze_image(file: UploadFile = File(...)):
    img_path = f"temp_{file.filename}"
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    emotion = analyze_emotion(img_path)
    objects = detect_objects(img_path)

    os.remove(img_path)
    return {
        "emotion": emotion,
        "objects_detected": objects
    }
