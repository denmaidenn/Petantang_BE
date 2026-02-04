from paddleocr import PaddleOCR
import numpy as np

# Initialize PaddleOCR
# use_angle_cls=True enables orientation classification
# lang='en' covers standard Latin characters used in ID cards
ocr = PaddleOCR(use_angle_cls=True, lang='en') 

def extract_text(image_np: np.ndarray) -> list:
    """
    Extracts text from an image using PaddleOCR.
    Returns a list of detected strings.
    """
    if image_np is None or image_np.size == 0:
        return []

    result = ocr.ocr(image_np, cls=True)
    
    detected_texts = []
    if result and result[0]:
        # result structure: [[[[x1,y1],[x2,y2]...], ("text", conf)], ...]
        for line in result[0]:
            text, conf = line[1]
            if conf > 0.5: # Confidence threshold
                detected_texts.append((text, conf))
                
    return detected_texts
