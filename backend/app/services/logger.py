import csv
import os
from datetime import datetime

LOG_FILE = "activity_log.csv"

def log_activity(data: dict):
    """
    Logs the student activity to a CSV file.
    """
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(["Timestamp", "NIM", "Name", "Lab", "Computer_No"])
            
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("nim", ""),
            data.get("name", ""),
            data.get("lab", ""),
            data.get("computer_no", "")
        ])

    return True
