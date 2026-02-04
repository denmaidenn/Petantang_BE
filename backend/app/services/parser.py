import re

def parse_ktm_data(ocr_results: list) -> dict:
    """
    Parses OCR text to find Student ID (NIM) and Name.
    Specific for IPB University format.
    Input: list of (text, confidence) tuples.
    """
    data = {
        "nim": None,
        "name": None,
        "faculty_code": None,
        "accuracy": 0.0, # Composite score
        "raw_text": [r[0] for r in ocr_results]
    }
    
    # regex for IPB NIM: 1 Letter + 8 Digits (e.g. G64180001)
    nim_pattern = re.compile(r'\b[A-Za-z]\d{8}\b')
    
    name_candidate = None
    nim_conf = 0.0
    name_conf = 0.0
    
    for i, (text, conf) in enumerate(ocr_results):
        clean_text = text.strip()
        
        # 1. Look for NIM
        if not data["nim"]:
            match = nim_pattern.search(clean_text)
            if match:
                data["nim"] = match.group().upper()
                nim_conf = conf
                if len(data["nim"]) >= 3:
                     data["faculty_code"] = data["nim"][0]

        # 2. Look for Name
        if "NAMA" in clean_text.upper():
            parts = clean_text.split(":")
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                name_candidate = parts[1].strip()
                name_conf = conf
            elif i + 1 < len(ocr_results):
                possible_name, p_conf = ocr_results[i+1]
                if not nim_pattern.search(possible_name):
                    name_candidate = possible_name
                    name_conf = p_conf
                    
    # Fallback for name if specific "Nama" label wasn't found effectively
    # Look for largest text block that isn't the NIM or "KARTU TANDA MAHASISWA" header
    if not name_candidate:
        exclude_terms = ["KARTU", "TANDA", "MAHASISWA", "IPB", "NIM", "BLU", "KEMENTERIAN", "PENDIDIKAN"]
        for text, conf in ocr_results:
            t_upper = text.upper()
            if any(term in t_upper for term in exclude_terms):
                continue
            if data["nim"] and data["nim"] in t_upper:
                continue
            if len(text) > 4 and not re.search(r'\d', text):
                name_candidate = text
                name_conf = conf
                # Boost confidence slightly if it looks like a name (2+ words)
                if " " in name_candidate:
                    name_conf = min(1.0, name_conf + 0.1)
                break
                
    if name_candidate:
        data["name"] = re.sub(r'[^a-zA-Z\s\.]', '', name_candidate).strip()

    # Calculate Accuracy Score
    # 50% weight on NIM existence/format, 30% on NIM OCR confidence, 20% on Name existence
    score = 0.0
    if data["nim"]:
        score += 50 # Base score for valid regex NIM
        score += (nim_conf * 30) # Weighted confidence
    
    if data["name"]:
        score += 10 # Base score for having a name
        score += (name_conf * 10) # Weighted confidence
        
    data["accuracy"] = round(score, 2)
    
    return data
