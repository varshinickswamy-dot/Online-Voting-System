// ================= CAMERA.JS =================

let videoStream = null;

/* Start Camera */
async function startCamera() {

    const video = document.getElementById("cam");

    if (!video) {
        console.error("Video element with id='cam' not found.");
        return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Camera not supported in this browser.");
        return;
    }

    try {

        // Stop previous stream if running
        if (videoStream) {
            stopCamera();
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 320 },
                height: { ideal: 240 },
                facingMode: "user"
            },
            audio: false
        });

        videoStream = stream;
        video.srcObject = stream;

        await video.play();

    } catch (err) {
        console.error("Camera Error:", err);
        alert("Allow camera permission and ensure webcam is connected.");
    }
}


/* Capture Frame from Webcam */
function captureFrame() {

    const video = document.getElementById("cam");

    if (!video || video.readyState !== 4) {
        console.error("Video not ready.");
        return null;
    }

    const canvas = document.createElement("canvas");

    // FIXED CAPTURE SIZE
    canvas.width = 320;
    canvas.height = 240;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(video, 0, 0, 320, 240);

    return canvas.toDataURL("image/png");
}


/* Send Captured Images to Flask */
async function sendFrames() {

    const img1 = captureFrame();
    const img2 = captureFrame();

    if (!img1 || !img2) {
        alert("Camera not ready.");
        return;
    }

    try {
        const response = await fetch("/upload_temp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                img1: img1,
                img2: img2
            })
        });

        const data = await response.json();
        console.log("Upload response:", data);

    } catch (err) {
        console.error("Upload Error:", err);
    }
}


/* Stop Camera */
function stopCamera() {

    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }

    const video = document.getElementById("cam");
    if (video) {
        video.srcObject = null;
    }
}