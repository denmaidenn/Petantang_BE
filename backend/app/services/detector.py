from ultralytics import YOLO
import numpy as np
import cv2

# Initialize YOLO model
# This will download yolov8n.pt if not present
try:
    model = YOLO("yolov8n.pt") 
except Exception as e:
    print(f"Failed to load YOLO model: {e}")
    model = None

def detect_card(image_np: np.ndarray) -> np.ndarray:
    """
    Detects a card/document in the image and crops it.
    If no detection, returns the original image.
    """
    if model is None:
        return image_np

    # Run inference
    # classes=None will detect all COCO classes. 
    # Ideal: train custom model for 'id_card'.
    # Fallback: Look for large objects.
    results = model(image_np, verbose=False)
    
    if not results:
        return image_np

    # Get boxes
    boxes = results[0].boxes
    if len(boxes) == 0:
        return image_np

    # Naive usage: Get the largest bounding box (assuming card is the main subject)
    # box format: xyxy
    largest_area = 0
    best_box = None
    
    for box in boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        w = xyxy[2] - xyxy[0]
        h = xyxy[3] - xyxy[1]
        area = w * h
        if area > largest_area:
            largest_area = area
            best_box = xyxy
            
    if best_box is not None:
        x1, y1, x2, y2 = map(int, best_box)
        # Add some padding
        h_img, w_img, _ = image_np.shape
        pad = 10
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w_img, x2 + pad)
        y2 = min(h_img, y2 + pad)
        
        # Return crop AND the box coordinates [x1, y1, x2, y2]
        return image_np[y1:y2, x1:x2], [x1, y1, x2, y2]

    # If no detection, return original and full frame box
    h, w, _ = image_np.shape
    return image_np, [0, 0, w, h]
