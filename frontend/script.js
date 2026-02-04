const video = document.getElementById('videoElement');
const overlay = document.getElementById('overlay');
const offscreenCanvas = document.getElementById('offscreenCanvas');
const toggleScanBtn = document.getElementById('toggleScanBtn');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');

// Modal Elements
const modal = document.getElementById('dataModal');
const rentalForm = document.getElementById('rentalForm');
const nimInput = document.getElementById('nimInput');
const nameInput = document.getElementById('nameInput');
const cancelBtn = document.getElementById('cancelBtn');

const API_URL = "http://localhost:8000/api/v1/scan";
const SUBMIT_URL = "http://localhost:8000/api/v1/submit";

let isScanning = false;
let scanInterval = null;

// Start Camera
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "environment",
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            overlay.width = video.videoWidth;
            overlay.height = video.videoHeight;
        };
    } catch (err) {
        console.error("Error accessing webcam:", err);
        alert("Could not access camera.");
    }
}
startCamera();

// Toggle Scan
toggleScanBtn.addEventListener('click', () => {
    if (isScanning) {
        stopScanning();
    } else {
        startScanning();
    }
});

function startScanning() {
    isScanning = true;
    toggleScanBtn.textContent = "Stop Scanning";
    toggleScanBtn.style.backgroundColor = "#cc0000";

    // Scan every 500ms
    scanInterval = setInterval(processFrame, 500);
}

function stopScanning() {
    isScanning = false;
    clearInterval(scanInterval);
    toggleScanBtn.textContent = "Start Auto-Scan";
    toggleScanBtn.style.backgroundColor = ""; // Reset to default
    clearOverlay();
}

async function processFrame() {
    if (!video.videoWidth) return;

    // Draw to offscreen canvas
    offscreenCanvas.width = video.videoWidth;
    offscreenCanvas.height = video.videoHeight;
    const ctx = offscreenCanvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Send to API
    offscreenCanvas.toBlob(async (blob) => {
        if (!isScanning) return; // double check

        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        try {
            const response = await fetch(API_URL, { method: 'POST', body: formData });
            const result = await response.json();

            if (result.status === 'success') {
                drawOverlay(result.bbox, result.data);

                // If NIM and Name found AND accuracy > Threshold (e.g. 85%), trigger modal
                if (result.data.nim && result.data.name && result.data.accuracy > 85) {
                    stopScanning();
                    showModal(result.data);
                }
            }
        } catch (err) {
            console.error("Scan error:", err);
        }
    }, 'image/jpeg', 0.8);
}

function drawOverlay(bbox, data) {
    const ctx = overlay.getContext('2d');
    ctx.clearRect(0, 0, overlay.width, overlay.height);

    if (!bbox || bbox.length < 4) return;

    const [x1, y1, x2, y2] = bbox;

    // Draw Box
    ctx.strokeStyle = "#00ff00";
    ctx.lineWidth = 4;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    // Draw Status Background
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(x1, y1 - 60, Math.max(200, x2 - x1), 60);

    // Draw Text
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 16px Segoe UI";

    if (data && data.nim) {
        ctx.fillText(`NIM: ${data.nim}`, x1 + 10, y1 - 35);
        ctx.fillText(`Name: ${data.name || '?'}`, x1 + 10, y1 - 15);

        // Draw Accuracy
        const acc = data.accuracy || 0;
        ctx.fillStyle = acc > 85 ? "#00ff00" : "#ffcc00";
        ctx.fillText(`${acc}%`, x1 + 160, y1 - 35);
    } else {
        ctx.fillText("Scanning for KTM...", x1 + 10, y1 - 25);
    }
}

function clearOverlay() {
    const ctx = overlay.getContext('2d');
    ctx.clearRect(0, 0, overlay.width, overlay.height);
}

function showModal(data) {
    nimInput.value = data.nim || "";
    nameInput.value = data.name || "";
    modal.classList.remove('hidden');
}

// Modal Actions
cancelBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    // Don't auto-restart scan immediately to prevent annoying loop, or do?
    // User can restart manually.
});

rentalForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
        nim: nimInput.value,
        name: nameInput.value,
        lab: document.getElementById('labSelect').value,
        computer_no: document.getElementById('pcInput').value
    };

    try {
        const res = await fetch(SUBMIT_URL, {
            headers: { 'Content-Type': 'application/json' },
            method: 'POST',
            body: JSON.stringify(payload)
        });

        const json = await res.json();
        if (json.status === 'success') {
            alert("Rental Successful! Enjoy your session.");
            modal.classList.add('hidden');
            rentalForm.reset();
        } else {
            alert("Error: " + json.detail);
        }
    } catch (err) {
        alert("Submission failed: " + err.message);
    }
});

// Create a fallback for manual upload if needed
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', async (e) => {
    if (e.target.files.length > 0) {
        // Manual upload flow could share logic, but for now simple one-shot
        loading.classList.remove('hidden');
        const formData = new FormData();
        formData.append('file', e.target.files[0]);
        const res = await fetch(API_URL, { method: 'POST', body: formData });
        const json = await res.json();
        loading.classList.add('hidden');

        if (json.data) {
            showModal(json.data);
        }
    }
});
