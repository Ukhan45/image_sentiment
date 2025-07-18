from ultralytics import YOLO
import cv2

model = YOLO("yolov5s.pt")  

def detect_objects(image_path: str) -> list:
    results = model(image_path)  
    objects = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])
            objects.append({"label": label, "confidence": round(confidence, 2)})
    return objects
