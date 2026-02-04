from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.detector import detect_card
from app.services.ocr import extract_text
from app.services.parser import parse_ktm_data
from app.services.logger import log_activity
from pydantic import BaseModel
import io
from PIL import Image
import numpy as np

app = FastAPI(title="Student ID OCR System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/scan")
async def scan_ktm(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image_np = np.array(image)
    
    # 1. Detect and Crop Card (YOLO)
    bbox = []
    try:
        cropped_image_np, bbox = detect_card(image_np)
    except Exception as e:
        print(f"Detection failed: {e}")
        cropped_image_np = image_np
        h, w, _ = image_np.shape
        bbox = [0, 0, w, h]
    
    # 2. Extract Text (PaddleOCR)
    try:
        raw_text_list = extract_text(cropped_image_np)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
    
    # 3. Parse Data (IPB NIM Logic)
    parsed_data = parse_ktm_data(raw_text_list)
    
    return {
        "status": "success",
        "data": parsed_data,
        "bbox": bbox, # Return bbox for frontend overlay
        "debug_raw_text": raw_text_list
    }

class SubmitRequest(BaseModel):
    nim: str
    name: str
    lab: str
    computer_no: str

@app.post("/api/v1/submit")
async def submit_log(request: SubmitRequest):
    try:
        log_activity(request.dict())
        return {"status": "success", "message": "Logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    return {"message": "Student ID OCR API is running"}
