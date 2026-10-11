/*=====================================================
AI Crowd Surveillance Dashboard
Camera & Heatmap Controller (Enterprise Version)
Manages live MJPEG feeds for YOLO Camera and Crowd Density Heatmap,
with automatic reconnects and FPS monitoring.
Author : Ved Rathod
=====================================================*/

const Camera = {
    image: null,
    heatmap: null,
    connected: false,
    heatmapConnected: false,
    fps: 0,
    lastFrame: performance.now(),
    frameCount: 0,
    reconnectTimer: null,
    heatmapReconnectTimer: null,
    isStopped: false
};

//=====================================================
// Initialize Camera & Heatmap
//=====================================================
function initializeCamera() {
    Camera.image = document.getElementById("liveCamera");
    Camera.heatmap = document.getElementById("heatmapImage");

    if (!Camera.image) {
        console.error("Camera element not found.");
        return;
    }

    connectCamera();

    if (Camera.heatmap) {
        connectHeatmap();
    }
}

//=====================================================
// Connect Camera Feed
//=====================================================
function connectCamera() {
    if (!Camera.image) return;
    Camera.connected = true;
    updateCameraStatus(true);
    Camera.image.src = cameraURL() + "?t=" + Date.now();

    Camera.image.onload = function() {
        Camera.connected = true;
        updateCameraStatus(true);
        updateFPS();
    };

    Camera.image.onerror = function() {
        Camera.connected = false;
        updateCameraStatus(false);
        reconnectCamera();
    };
}

//=====================================================
// Connect Heatmap Feed
//=====================================================
function connectHeatmap() {
    if (!Camera.heatmap) return;
    Camera.heatmapConnected = true;
    Camera.heatmap.src = heatmapURL() + "?t=" + Date.now();

    Camera.heatmap.onload = function() {
        Camera.heatmapConnected = true;
    };

    Camera.heatmap.onerror = function() {
        Camera.heatmapConnected = false;
        reconnectHeatmap();
    };
}

//=====================================================
// Reconnect Camera Feed
//=====================================================
function reconnectCamera() {
    if (Camera.reconnectTimer) return;
    console.warn("Reconnecting Camera Stream...");

    Camera.reconnectTimer = setTimeout(() => {
        Camera.reconnectTimer = null;
        connectCamera();
    }, 3000);
}

//=====================================================
// Reconnect Heatmap Feed
//=====================================================
function reconnectHeatmap() {
    if (Camera.heatmapReconnectTimer) return;
    Camera.heatmapReconnectTimer = setTimeout(() => {
        Camera.heatmapReconnectTimer = null;
        connectHeatmap();
    }, 4000);
}

//=====================================================
// Camera Status Badge
//=====================================================
function updateCameraStatus(status) {
    const element = document.getElementById("cameraStatus");
    if (!element) return;

    if (status) {
        element.innerHTML = "ONLINE";
        element.style.color = "#22C55E";
    } else {
        element.innerHTML = "OFFLINE";
        element.style.color = "#EF4444";
    }
}

//=====================================================
// FPS Calculation
//=====================================================
function updateFPS() {
    Camera.frameCount++;
    const now = performance.now();
    const elapsed = now - Camera.lastFrame;

    if (elapsed >= 1000) {
        Camera.fps = Camera.frameCount;
        Camera.frameCount = 0;
        Camera.lastFrame = now;

        const fpsEl = document.getElementById("fps");
        if (fpsEl) {
            fpsEl.innerHTML = Camera.fps + " FPS";
        }
    }
}

//=====================================================
// Fullscreen Toggle
//=====================================================
function fullscreenCamera() {
    const camera = document.getElementById("cameraContainer");
    if (!camera) return;

    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        camera.requestFullscreen();
    }
}

//=====================================================
// Toggle Camera Power
//=====================================================
async function toggleCamera() {
    const btn = document.getElementById("toggleCameraBtn");
    const icon = btn ? btn.querySelector("i") : null;
    
    if (!Camera.isStopped) {
        try {
            await fetch(API.BASE_URL + "/api/camera/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action: "stop" })
            });
            Camera.isStopped = true;
            if (icon) icon.style.color = "#EF4444";
            if (typeof showNotification === "function") showNotification("Camera Off", "#EF4444");
        } catch(e) { console.error(e); }
    } else {
        try {
            await fetch(API.BASE_URL + "/api/camera/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action: "start" })
            });
            Camera.isStopped = false;
            if (icon) icon.style.color = "";
            if (typeof showNotification === "function") showNotification("Camera On", "#22C55E");
        } catch(e) { console.error(e); }
    }
}

//=====================================================
// Snapshot Capture
//=====================================================
function captureSnapshot() {
    const image = document.getElementById("liveCamera");
    if (!image || !Camera.connected) {
        if (typeof showNotification === "function") {
            showNotification("Camera Stream Not Available", "#EF4444");
        }
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = image.naturalWidth || image.width || 1280;
    canvas.height = image.naturalHeight || image.height || 720;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0);

    const link = document.createElement("a");
    link.download = "snapshot_" + Date.now() + ".png";
    link.href = canvas.toDataURL("image/png");
    link.click();

    if (typeof showNotification === "function") {
        showNotification("Snapshot Captured", "#22C55E");
    }
}

//=====================================================
// Recording Indicator
//=====================================================
function startRecordingIndicator() {
    const recording = document.getElementById("recordingStatus");
    if (recording) {
        recording.innerHTML = "● REC";
    }
}

function stopRecordingIndicator() {
    const recording = document.getElementById("recordingStatus");
    if (recording) {
        recording.innerHTML = "● LIVE";
    }
}

//=====================================================
// Camera Health Object
//=====================================================
function cameraHealth() {
    return {
        connected: Camera.connected,
        heatmapConnected: Camera.heatmapConnected,
        fps: Camera.fps
    };
}

//=====================================================
// Auto Refresh FPS Counter
//=====================================================
setInterval(() => {
    if (Camera.connected) {
        updateFPS();
    }
}, 100);

//=====================================================
// Initialize on Window Load
//=====================================================
window.addEventListener("load", () => {
    initializeCamera();
});