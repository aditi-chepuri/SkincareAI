/* ===========================================
   SkincareAI - script.js
   Complete Frontend JavaScript
   =========================================== */


/* ===========================================
   GLOBAL ELEMENTS
   =========================================== */

const cameraMode = document.getElementById("cameraMode");
const uploadMode = document.getElementById("uploadMode");

const cameraSection = document.getElementById("cameraSection");
const uploadSection = document.getElementById("uploadSection");

const video = document.getElementById("camera");
const canvas = document.getElementById("snapshot");

const captureBtn = document.getElementById("captureBtn");
const retakeBtn = document.getElementById("retakeBtn");
const analyzeBtn = document.getElementById("analyzeBtn");

const countdown = document.getElementById("countdown");
const cameraStatus = document.getElementById("cameraStatus");

const imageInput = document.getElementById("imageInput");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");

const capturedImage = document.getElementById("capturedImage");

const analysisForm = document.getElementById("analysisForm");

const loadingSection = document.getElementById("loadingSection");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");

const uploadArea = document.querySelector(".upload-area");


/* ===========================================
   VARIABLES
   =========================================== */

let stream = null;
let captured = false;
let capturedBlob = null;


/* ===========================================
   CAMERA START
   =========================================== */

async function startCamera() {

    if (!video) {
        return;
    }

    if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
    ) {

        if (cameraStatus) {

            cameraStatus.innerHTML = `
                🔴 Camera Not Supported
                <br><br>
                Please use a modern browser.
            `;

        }

        return;
    }


    try {

        if (cameraStatus) {

            cameraStatus.innerHTML = `
                🔄 Starting Camera...
            `;

        }


        stream = await navigator.mediaDevices.getUserMedia({

            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: "user"
            },

            audio: false

        });


        video.srcObject = stream;

        video.muted = true;
        video.autoplay = true;
        video.playsInline = true;


        /* Important */
        await video.play();


        if (cameraStatus) {

            cameraStatus.innerHTML = `
                🟢 Camera Ready
                <br><br>
                Position your face inside the frame.
            `;

        }


        if (captureBtn) {
            captureBtn.disabled = false;
        }


        console.log("✅ Camera started successfully");

    }


    catch (error) {

        console.error("Camera Error:", error);


        if (cameraStatus) {

            cameraStatus.innerHTML = `
                🔴 Camera Access Failed
                <br><br>
                Please allow camera permission and try again.
            `;

        }

    }

}


/* ===========================================
   STOP CAMERA
   =========================================== */

function stopCamera() {

    if (stream) {

        stream.getTracks().forEach(function(track) {

            track.stop();

        });

        stream = null;

    }

}


/* ===========================================
   START CAMERA WHEN PAGE LOADS
   =========================================== */

if (video) {

    startCamera();

}


/* ===========================================
   CAMERA MODE
   =========================================== */

if (cameraMode) {

    cameraMode.addEventListener("click", function() {


        cameraMode.classList.add("active");


        if (uploadMode) {
            uploadMode.classList.remove("active");
        }


        if (cameraSection) {
            cameraSection.style.display = "block";
        }


        if (uploadSection) {
            uploadSection.style.display = "none";
        }


        /* Reset camera state */

        captured = false;
        capturedBlob = null;


        if (analyzeBtn) {
            analyzeBtn.disabled = true;
        }


        if (captureBtn) {

            captureBtn.style.display = "inline-block";
            captureBtn.disabled = false;

        }


        if (retakeBtn) {

            retakeBtn.style.display = "none";

        }


        /* Start camera again */

        if (!stream) {

            startCamera();

        }

    });

}


/* ===========================================
   UPLOAD MODE
   =========================================== */

if (uploadMode) {

    uploadMode.addEventListener("click", function() {


        uploadMode.classList.add("active");


        if (cameraMode) {
            cameraMode.classList.remove("active");
        }


        if (uploadSection) {
            uploadSection.style.display = "block";
        }


        if (cameraSection) {
            cameraSection.style.display = "none";
        }


        /* Stop camera */

        stopCamera();


        if (analyzeBtn) {
            analyzeBtn.disabled = true;
        }


        if (cameraStatus) {

            cameraStatus.innerHTML = `
                🖼️ Select a facial image
                <br><br>
                JPG, JPEG or PNG
            `;

        }

    });

}


/* ===========================================
   CAPTURE FACE
   =========================================== */

if (captureBtn) {

    captureBtn.addEventListener("click", function() {


        if (!video) {
            return;
        }


        if (
            video.videoWidth === 0 ||
            video.videoHeight === 0
        ) {

            if (cameraStatus) {

                cameraStatus.innerHTML = `
                    🔄 Camera is still starting...
                    <br><br>
                    Please wait a moment.
                `;

            }

            return;

        }


        captureBtn.disabled = true;


        let count = 3;


        if (countdown) {

            countdown.style.display = "block";
            countdown.innerHTML = count;

        }


        if (cameraStatus) {

            cameraStatus.innerHTML = `
                📸 Preparing Capture...
                <br><br>
                Keep your face steady.
            `;

        }


        const timer = setInterval(function() {


            count--;


            if (count > 0) {

                if (countdown) {
                    countdown.innerHTML = count;
                }

            }


            else {

                clearInterval(timer);


                if (countdown) {

                    countdown.innerHTML = "";
                    countdown.style.display = "none";

                }


                captureImage();

            }


        }, 1000);

    });

}


/* ===========================================
   CAPTURE IMAGE
   =========================================== */

function captureImage() {

    if (!video || !canvas) {
        return;
    }


    if (
        video.videoWidth === 0 ||
        video.videoHeight === 0
    ) {

        if (captureBtn) {
            captureBtn.disabled = false;
        }

        return;

    }


    /* Set canvas dimensions */

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;


    /* Draw camera frame */

    const context = canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    /* Convert canvas to image */

    const imageData =
        canvas.toDataURL("image/png");


    /* Store Base64 */

    if (capturedImage) {

        capturedImage.value = imageData;

    }


    /* Create Blob for Flask */

    canvas.toBlob(function(blob) {

        capturedBlob = blob;

    }, "image/png");


    captured = true;


    /* Status */

    if (cameraStatus) {

        cameraStatus.innerHTML = `
            ✅ Face Captured Successfully
            <br><br>
            Ready for AI Analysis.
        `;

    }


    /* Buttons */

    if (captureBtn) {

        captureBtn.style.display = "none";

    }


    if (retakeBtn) {

        retakeBtn.style.display = "inline-block";

    }


    if (analyzeBtn) {

        analyzeBtn.disabled = false;

    }


    /* Freeze video */

    video.pause();

}


/* ===========================================
   RETAKE
   =========================================== */

if (retakeBtn) {

    retakeBtn.addEventListener("click", async function() {


        captured = false;
        capturedBlob = null;


        if (capturedImage) {

            capturedImage.value = "";

        }


        if (captureBtn) {

            captureBtn.style.display = "inline-block";
            captureBtn.disabled = false;

        }


        retakeBtn.style.display = "none";


        if (analyzeBtn) {

            analyzeBtn.disabled = true;

        }


        if (countdown) {

            countdown.innerHTML = "";

        }


        /* Restart video */

        try {

            await video.play();

        }

        catch (error) {

            console.error(error);

        }


        if (cameraStatus) {

            cameraStatus.innerHTML = `
                🟢 Camera Ready
                <br><br>
                Position your face inside the frame.
            `;

        }

    });

}


/* ===========================================
   UPLOAD AREA CLICK
   =========================================== */

if (uploadArea && imageInput) {

    uploadArea.addEventListener("click", function() {

        imageInput.click();

    });

}


/* ===========================================
   IMAGE UPLOAD
   =========================================== */

if (imageInput) {

    imageInput.addEventListener("change", function() {


        const file = this.files[0];


        if (!file) {
            return;
        }


        /* Validate image */

        if (!file.type.startsWith("image/")) {

            alert("Please select a valid image file.");

            imageInput.value = "";

            return;

        }


        /* Show preview */

        const reader = new FileReader();


        reader.onload = function(event) {


            if (previewImage) {

                previewImage.src =
                    event.target.result;

            }


            if (previewContainer) {

                previewContainer.style.display =
                    "block";

            }


            if (analyzeBtn) {

                analyzeBtn.disabled = false;

            }


            if (cameraStatus) {

                cameraStatus.innerHTML = `
                    🖼️ Image Selected Successfully
                    <br><br>
                    Ready for AI Analysis.
                `;

            }

        };


        reader.readAsDataURL(file);

    });

}


/* ===========================================
   DRAG AND DROP
   =========================================== */

if (uploadArea) {


    uploadArea.addEventListener(
        "dragover",
        function(event) {

            event.preventDefault();

            uploadArea.classList.add("drag-active");

        }
    );


    uploadArea.addEventListener(
        "dragleave",
        function() {

            uploadArea.classList.remove(
                "drag-active"
            );

        }
    );


    uploadArea.addEventListener(
        "drop",
        function(event) {


            event.preventDefault();


            uploadArea.classList.remove(
                "drag-active"
            );


            const file =
                event.dataTransfer.files[0];


            if (!file) {
                return;
            }


            if (!file.type.startsWith("image/")) {

                alert("Please drop a valid image.");

                return;

            }


            /* Put dropped file into input */

            try {

                const dataTransfer =
                    new DataTransfer();

                dataTransfer.items.add(file);

                imageInput.files =
                    dataTransfer.files;

            }

            catch(error) {

                console.error(error);

            }


            /* Show preview */

            const reader = new FileReader();


            reader.onload = function(event) {


                if (previewImage) {

                    previewImage.src =
                        event.target.result;

                }


                if (previewContainer) {

                    previewContainer.style.display =
                        "block";

                }


                if (analyzeBtn) {

                    analyzeBtn.disabled = false;

                }


                if (cameraStatus) {

                    cameraStatus.innerHTML = `
                        🖼️ Image Selected Successfully
                        <br><br>
                        Ready for AI Analysis.
                    `;

                }

            };


            reader.readAsDataURL(file);

        }
    );

}


/* ===========================================
   ANALYSIS FORM
   =========================================== */

if (analysisForm) {

    analysisForm.addEventListener(
        "submit",
        async function(event) {


            event.preventDefault();


            let imageBlob = null;


            /* =================================
               CAMERA IMAGE
               ================================= */

            if (captured && capturedBlob) {

                imageBlob = capturedBlob;

            }


            /* =================================
               UPLOADED IMAGE
               ================================= */

            else if (
                imageInput &&
                imageInput.files &&
                imageInput.files.length > 0
            ) {

                imageBlob =
                    imageInput.files[0];

            }


            /* =================================
               NO IMAGE
               ================================= */

            if (!imageBlob) {

                alert(
                    "Please capture your face or upload an image before starting AI analysis."
                );

                return;

            }


            /* =================================
               SHOW LOADING
               ================================= */

            if (loadingSection) {

                loadingSection.style.display =
                    "block";

            }


            if (cameraSection) {

                cameraSection.style.display =
                    "none";

            }


            if (uploadSection) {

                uploadSection.style.display =
                    "none";

            }


            if (analyzeBtn) {

                analyzeBtn.disabled = true;

            }


            startAIProgress();


            /* =================================
               PREPARE IMAGE FOR FLASK
               ================================= */

            const formData = new FormData();


            formData.append(
                "image",
                imageBlob,
                "skincare_image.png"
            );


            try {


                const response =
                    await fetch(
                        analysisForm.action,
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                /* =================================
                   LOGIN REDIRECT
                   ================================= */

                if (response.redirected) {

                    window.location.href =
                        response.url;

                    return;

                }


                /* =================================
                   RESULT PAGE
                   ================================= */

                const resultHTML =
                    await response.text();


                document.open();

                document.write(resultHTML);

                document.close();


            }


            catch(error) {


                console.error(
                    "Analysis Error:",
                    error
                );


                alert(
                    "Something went wrong while analyzing the image. Please try again."
                );


                if (loadingSection) {

                    loadingSection.style.display =
                        "none";

                }


                if (cameraSection) {

                    cameraSection.style.display =
                        "block";

                }


                if (analyzeBtn) {

                    analyzeBtn.disabled = false;

                }

            }

        }
    );

}
document.addEventListener("DOMContentLoaded", function () {

    const confidenceBar =
        document.querySelector(".confidence-fill");

    if (confidenceBar) {

        const confidence =
            parseFloat(
                confidenceBar.dataset.confidence
            );

        confidenceBar.style.width =
            confidence + "%";
    }

});


/* ===========================================
   AI PROGRESS
   =========================================== */

function startAIProgress() {


    if (!progressBar || !progressText) {
        return;
    }


    progressBar.style.width = "0%";


    const stages = [

        {
            percent: 20,
            text: "🔍 Detecting facial features..."
        },

        {
            percent: 40,
            text: "🧴 Analyzing skin texture..."
        },

        {
            percent: 60,
            text: "💧 Checking hydration level..."
        },

        {
            percent: 80,
            text: "⚕ Detecting skin sensitivity..."
        },

        {
            percent: 100,
            text: "🤖 Generating personalized recommendations..."
        }

    ];


    let stage = 0;


    const progressTimer =
        setInterval(function() {


            if (stage < stages.length) {


                progressBar.style.width =
                    stages[stage].percent + "%";


                progressText.innerHTML =
                    stages[stage].text;


                stage++;


            }


            else {

                clearInterval(progressTimer);

            }


        }, 700);

}


/* ===========================================
   CONTACT FORM
   =========================================== */

const contactForm =
    document.querySelector(
        ".form-container form"
    );


if (
    contactForm &&
    window.location.pathname.includes("contact")
) {


    contactForm.addEventListener(
        "submit",
        function(event) {


            event.preventDefault();


            alert(
                "Thank you! Your message has been sent successfully."
            );


            contactForm.reset();

        }
    );

}


/* ===========================================
   SMOOTH SCROLL
   =========================================== */

document
    .querySelectorAll('a[href^="#"]')
    .forEach(function(anchor) {


        anchor.addEventListener(
            "click",
            function(event) {


                const target =
                    document.querySelector(
                        this.getAttribute("href")
                    );


                if (target) {

                    event.preventDefault();


                    target.scrollIntoView({

                        behavior: "smooth"

                    });

                }

            }
        );

    });


/* ===========================================
   PAGE LOADED
   =========================================== */

console.log(
    "✅ SkincareAI JavaScript Loaded Successfully"
);