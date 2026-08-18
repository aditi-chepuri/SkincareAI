/* =========================================================
   SkincareAI - analyze.js
   Camera + Upload + Flask Result
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("✅ SkincareAI Analyze JS Loaded");

    const cameraMode = document.getElementById("cameraMode");
    const uploadMode = document.getElementById("uploadMode");
    const cameraSection = document.getElementById("cameraSection");
    const uploadSection = document.getElementById("uploadSection");
    const video = document.getElementById("camera");
    const canvas = document.getElementById("snapshot");
    const captureBtn = document.getElementById("captureBtn");
    const retakeBtn = document.getElementById("retakeBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const cameraStatus = document.getElementById("cameraStatus");
    const imageInput = document.getElementById("imageInput");
    const uploadArea = document.getElementById("uploadArea");
    const previewContainer = document.getElementById("previewContainer");
    const previewImage = document.getElementById("previewImage");
    const hiddenImage = document.getElementById("capturedImage");
    const analysisForm = document.getElementById("analysisForm");
    const loadingSection = document.getElementById("loadingSection");
    const progressBar = document.getElementById("progressBar");
    const progressText = document.getElementById("progressText");

    let stream = null;

    if (cameraSection) cameraSection.style.display = "block";
    if (uploadSection) uploadSection.style.display = "none";
    if (cameraMode) cameraMode.classList.add("active");
    if (uploadMode) uploadMode.classList.remove("active");
    if (retakeBtn) retakeBtn.style.display = "none";
    if (analyzeBtn) analyzeBtn.disabled = true;

    startCamera();

    if (cameraMode) {
        cameraMode.addEventListener("click", async function () {
            cameraMode.classList.add("active");
            if (uploadMode) uploadMode.classList.remove("active");
            if (cameraSection) cameraSection.style.display = "block";
            if (uploadSection) uploadSection.style.display = "none";
            clearUpload();
            clearImage();
            await startCamera();
        });
    }

    if (uploadMode) {
        uploadMode.addEventListener("click", function () {
            uploadMode.classList.add("active");
            if (cameraMode) cameraMode.classList.remove("active");
            if (uploadSection) uploadSection.style.display = "block";
            if (cameraSection) cameraSection.style.display = "none";
            stopCamera();
            clearImage();
            setStatus("🖼️ Select an Image", "Choose a facial image to continue.");
        });
    }

    async function startCamera() {
        if (!video) return;
        stopCamera();

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setStatus("🔴 Camera Not Supported", "Please use Chrome or Edge.");
            return;
        }

        try {
            setStatus("🟡 Starting Camera...", "Please allow camera permission.");
            stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
                audio: false
            });
            video.srcObject = stream;
            video.muted = true;
            video.autoplay = true;
            video.playsInline = true;

            await new Promise(function (resolve) {
                if (video.readyState >= 1) resolve();
                else video.onloadedmetadata = function () { resolve(); };
            });

            await video.play();
            setStatus("🟢 Camera Ready", "Click Capture when you are ready.");
        } catch (error) {
            console.error("❌ Camera Error:", error);
            setStatus("🔴 Camera Access Failed", "Please allow camera permission and try again.");
        }
    }

    function setStatus(title, message) {
        if (!cameraStatus) return;
        cameraStatus.innerHTML = `${title}<br><br>${message}`;
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(function (track) { track.stop(); });
            stream = null;
        }
        if (video) {
            video.pause();
            video.srcObject = null;
        }
    }

    if (captureBtn) {
        captureBtn.addEventListener("click", function () {
            if (!stream || !video.srcObject) {
                setStatus("🔴 Camera Not Ready", "Please wait for the camera to start.");
                return;
            }
            if (video.videoWidth === 0 || video.videoHeight === 0) {
                setStatus("🟡 Camera Loading", "Please wait a moment and try again.");
                return;
            }
            captureImage();
        });
    }

    function captureImage() {
        if (!video || !canvas || !hiddenImage) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL("image/jpeg", 0.90);
        hiddenImage.value = imageData;

        video.pause();
        setStatus("✅ Face Captured Successfully", "Your image is ready for AI Analysis.");

        if (captureBtn) captureBtn.style.display = "none";
        if (retakeBtn) retakeBtn.style.display = "inline-block";
        if (analyzeBtn) analyzeBtn.disabled = false;
    }

    if (retakeBtn) {
        retakeBtn.addEventListener("click", async function () {
            clearImage();
            await startCamera();
        });
    }

    function clearImage() {
        if (hiddenImage) hiddenImage.value = "";
        if (captureBtn) {
            captureBtn.style.display = "inline-block";
            captureBtn.disabled = false;
        }
        if (retakeBtn) retakeBtn.style.display = "none";
        if (analyzeBtn) analyzeBtn.disabled = true;
    }

    if (uploadArea) {
        uploadArea.addEventListener("dragover", function (event) {
            event.preventDefault();
            uploadArea.classList.add("drag-active");
        });
        uploadArea.addEventListener("dragleave", function () {
            uploadArea.classList.remove("drag-active");
        });
        uploadArea.addEventListener("drop", function (event) {
            event.preventDefault();
            uploadArea.classList.remove("drag-active");
            const file = event.dataTransfer.files[0];
            if (file) processUploadedFile(file);
        });
    }

    if (imageInput) {
        imageInput.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;
            processUploadedFile(file);
        });
    }

    function processUploadedFile(file) {
        if (!file.type || !file.type.startsWith("image/")) {
            setStatus("❌ Invalid File", "Please select a JPG, JPEG or PNG image.");
            return;
        }

        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            setStatus("❌ File Too Large", "Please select an image smaller than 10 MB.");
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            const imageData = event.target.result;
            if (hiddenImage) hiddenImage.value = imageData;

            if (previewImage) previewImage.src = imageData;
            if (previewContainer) previewContainer.style.display = "block";
            if (analyzeBtn) analyzeBtn.disabled = false;

            setStatus("✅ Image Uploaded Successfully", "Your image is ready for AI Analysis.");
        };
        reader.onerror = function () {
            setStatus("❌ Unable to Read Image", "Please select another image.");
        };
        reader.readAsDataURL(file);
    }

    function clearUpload() {
        if (imageInput) imageInput.value = "";
        if (previewContainer) previewContainer.style.display = "none";
        if (previewImage) previewImage.src = "";
    }

    if (analysisForm) {
        analysisForm.addEventListener("submit", function (event) {
            if (!hiddenImage || !hiddenImage.value || hiddenImage.value.length < 100) {
                event.preventDefault();
                setStatus("⚠️ No Image Selected", "Please capture or upload an image first.");
                return;
            }

            if (analyzeBtn) analyzeBtn.disabled = true;
            if (loadingSection) loadingSection.style.display = "block";
            if (progressBar) progressBar.style.width = "60%";
            if (progressText) progressText.innerHTML = "Analyzing your skin...";
        });
    }

    window.addEventListener("beforeunload", function () {
        stopCamera();
    });
});