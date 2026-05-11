// Konfigurasi API
const API_URL = 'http://127.0.0.1:5000/analyze';

// Global Variables
let stream = null;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const modal = document.getElementById('captureModal');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');

// --- Fungsi Modal & Kamera ---
function openCaptureModal() {
    modal.classList.remove('hidden');
}

function closeCaptureModal() {
    modal.classList.add('hidden');
    stopCamera();
}

async function startCamera() {
    document.getElementById('cameraContainer').classList.remove('hidden');
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" }
        });
        video.srcObject = stream;
    } catch (err) {
        alert("Akses kamera ditolak atau tidak tersedia.");
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        document.getElementById('cameraContainer').classList.add('hidden');
    }
}

function takeSnapshot() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        imageInput.files = dataTransfer.files;

        previewImage.src = URL.createObjectURL(blob);
        closeCaptureModal();
    }, 'image/jpeg');
}

// --- Fungsi Utama: Analisis AI ---
async function uploadAndAnalyze() {
    const location = document.getElementById('locationInput').value;
    const loading = document.getElementById('loading');

    if (!imageInput.files[0]) {
        alert("Pilih atau ambil foto tanaman dulu ya!");
        return;
    }

    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('location', location);

    loading.classList.remove('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();

        // Update UI
        document.getElementById('diagnosisLabel').innerText = data.primary_diagnosis;
        document.getElementById('riskLabel').innerText = data.risk_assessment;
        document.getElementById('healthScore').innerText = `Score: ${data.health_index}`;
        document.getElementById('healthBar').style.height = `${data.health_index}%`;

        // Update Action Plan
        const actionList = document.getElementById('actionPlan');
        actionList.innerHTML = "";
        data.action_plan.forEach(item => {
            const li = document.createElement('li');
            li.innerText = `• ${item}`;
            actionList.appendChild(li);
        });

    } catch (error) {
        console.error("Error:", error);
        alert("Gagal terhubung ke server AgriMind. Pastikan backend Flask sudah jalan.");
    } finally {
        loading.classList.add('hidden');
    }
}

// --- Event Listeners ---
document.getElementById('analyzeBtn').addEventListener('click', uploadAndAnalyze);
document.getElementById('galleryBtn').addEventListener('click', () => imageInput.click());
document.getElementById('cameraBtn').addEventListener('click', startCamera);
document.getElementById('snapBtn').addEventListener('click', takeSnapshot);
document.getElementById('closeModalBtn').addEventListener('click', closeCaptureModal);

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        previewImage.src = URL.createObjectURL(file);
        closeCaptureModal();
    }
});