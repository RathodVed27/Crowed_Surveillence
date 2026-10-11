/*=====================================================
AI Crowd Surveillance Dashboard
Main Application Controller (Enterprise Refactored Version)
Coordinates module initialization, real-time telemetry polling,
and live system health reporting.
Author : Ved Rathod
=====================================================*/

"use strict";

const App = {
    name: "AI Crowd Surveillance",
    version: "2.0 (Enterprise)",
    refreshRate: 1000,
    initialized: false
};

//=====================================================
// Loader & Clock Helpers
//=====================================================
function initializeLoader() {
    if (typeof hideLoader === "function") hideLoader();
}

function initializeClock() {
    if (typeof startClock === "function") startClock();
}

//=====================================================
// Module Initializers
//=====================================================
function initializeCameraModule() {
    if (typeof initializeCamera === "function") initializeCamera();
}

function initializeChartsModule() {
    if (typeof initializeCharts === "function") initializeCharts();
}

function initializeDashboardModule() {
    if (typeof startDashboard === "function") startDashboard();
}

function initializeSensorsModule() {
    if (typeof refreshSensors === "function") refreshSensors();
}

function initializeAlertsModule() {
    if (typeof refreshAlerts === "function") refreshAlerts();
}

//=====================================================
// Sidebar Toggle
//=====================================================
function sidebarToggle() {
    const sidebar = document.querySelector(".sidebar");
    const main = document.querySelector(".main-content");
    if (!sidebar) return;

    sidebar.classList.toggle("collapsed");
    if (main) {
        main.classList.toggle("expanded");
    }
}

//=====================================================
// Master Polling Coordinator (Prevents Lag / Duplicate Fetch)
//=====================================================
async function refreshDashboard() {
    if (typeof updateDashboard === "function") {
        await updateDashboard();
    }
    if (typeof refreshCharts === "function") {
        await refreshCharts();
    }
    if (typeof refreshSensors === "function") {
        refreshSensors();
    }
}

//=====================================================
// Keyboard Shortcuts
//=====================================================
document.addEventListener("keydown", (event) => {
    switch (event.key.toLowerCase()) {
        case "f":
            if (typeof fullscreenCamera === "function") fullscreenCamera();
            break;
        case "s":
            if (typeof captureSnapshot === "function") captureSnapshot();
            break;
        case "r":
            refreshDashboard();
            break;
    }
});

//=====================================================
// Network Connection Monitor
//=====================================================
window.addEventListener("offline", () => {
    if (typeof showNotification === "function") {
        showNotification("Internet Connection Lost", "#EF4444");
    }
});

window.addEventListener("online", () => {
    if (typeof showNotification === "function") {
        showNotification("Connection Restored", "#22C55E");
    }
});

//=====================================================
// System Health (Real Backend Telemetry)
//=====================================================
async function updateSystemHealth() {
    try {
        const health = await getHealth();
        if (!health) return;

        const cpu = document.getElementById("cpuUsage");
        const ram = document.getElementById("ramUsage");
        const network = document.getElementById("networkUsage");

        if (cpu && health.cpu !== undefined) {
            cpu.innerHTML = `${health.cpu}%`;
        }
        if (ram && health.ram !== undefined) {
            ram.innerHTML = `${health.ram}%`;
        }
        if (network) {
            network.innerHTML = health.network || "Online";
        }
    } catch (error) {
        console.warn("System Health Telemetry Error:", error);
    }
}

//=====================================================
// Weather Placeholder
//=====================================================
function updateWeather() {
    const weather = document.getElementById("weatherTemp");
    if (weather) {
        weather.innerHTML = "32°C";
    }
}

//=====================================================
// Start Application Loop
//=====================================================
function startSystem() {
    refreshDashboard();
    updateSystemHealth();
    updateWeather();

    setInterval(refreshDashboard, App.refreshRate);
    setInterval(updateSystemHealth, 3000);
}

//=====================================================
// Interactive Sidebar Navigation
//=====================================================
function setupSidebarNavigation() {
    const menuItems = document.querySelectorAll(".sidebar-menu li");
    if (!menuItems.length) return;

    const sectionMap = {
        "Dashboard": "top",
        "Live Monitoring": ".dashboard-grid",
        "Media Analysis": ".media-section",
        "Analytics": ".chart-section",
        "Sensors": ".sensor-section",
        "Alerts": ".alert-section",
        "Reports": ".logs-section",
        "History": ".table-section",
        "Settings": ".status-section",
        "Logout": "logout"
    };

    menuItems.forEach(item => {
        item.style.cursor = "pointer";
        item.addEventListener("click", () => {
            const textEl = item.querySelector("span");
            const text = textEl ? textEl.innerText.trim() : "";

            // Set active class
            menuItems.forEach(li => li.classList.remove("active"));
            item.classList.add("active");

            const target = sectionMap[text];
            if (target === "top") {
                window.scrollTo({ top: 0, behavior: "smooth" });
            } else if (target === "logout") {
                if (typeof showNotification === "function") {
                    showNotification("Admin Session Active — Continuous Background Surveillance", "#3B82F6");
                }
            } else if (target) {
                const sec = document.querySelector(target);
                if (sec) {
                    sec.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            }
        });
    });
}

//=====================================================
// 3D Interactive Cyber-Command Parallax Card Tilt
//=====================================================
function init3DCardParallax() {
    const cards = document.querySelectorAll(".kpi-card, .sensor-card, .chart-card, .camera-wrapper, .heatmap-box, .media-panel");
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -6; // max 6 degrees tilt
            const rotateY = ((x - centerX) / centerX) * 6;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02) translateY(-6px)`;
            card.style.transition = "transform 0.1s ease-out, border-color 0.3s";
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1) translateY(0px)";
            card.style.transition = "all 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
        });
    });
}

//=====================================================
// Initialize Application
//=====================================================
function initializeApp() {
    console.clear();
    console.log(
        "%cAI Crowd Surveillance System",
        "color:#3B82F6;font-size:24px;font-weight:bold;"
    );
    console.log("Version : " + App.version);

    initializeLoader();
    initializeClock();
    initializeCameraModule();
    initializeChartsModule();
    initializeDashboardModule();
    initializeSensorsModule();
    initializeAlertsModule();
    setupSidebarNavigation();
    init3DCardParallax();

    startSystem();
    App.initialized = true;

    if (typeof showNotification === "function") {
        showNotification("AI Crowd Surveillance 3D Cyber-Command System Online", "#00F0FF");
    }
}

//=====================================================
// Window Load Event
//=====================================================
window.addEventListener("load", () => {
    initializeApp();
});

//=====================================================
// AI Media Crowd Analyzer (Image & Video Upload)
//=====================================================
let selectedMediaFile = null;

function handleMediaSelect(event) {
    const files = event.target.files;
    if (!files || !files.length) return;

    selectedMediaFile = files[0];
    const infoEl = document.getElementById("mediaFileInfo");
    const btnEl = document.getElementById("mediaAnalyzeBtn");

    if (infoEl) {
        infoEl.innerHTML = `<i class="fas fa-check-circle" style="color:#10B981;"></i> Selected: <strong>${selectedMediaFile.name}</strong> (${(selectedMediaFile.size / 1024 / 1024).toFixed(2)} MB)`;
        infoEl.style.display = "block";
    }

    if (btnEl) {
        btnEl.style.display = "inline-block";
    }
}

async function analyzeSelectedMedia() {
    if (!selectedMediaFile) return;

    const btnEl = document.getElementById("mediaAnalyzeBtn");
    const infoEl = document.getElementById("mediaFileInfo");
    const placeholder = document.getElementById("mediaPlaceholder");
    const resultImg = document.getElementById("mediaResultImg");
    const countVal = document.getElementById("mediaCountVal");
    const riskVal = document.getElementById("mediaRiskVal");
    const statusBadge = document.getElementById("mediaStatusBadge");

    if (btnEl) {
        btnEl.disabled = true;
        btnEl.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Analyzing with YOLOv8...`;
    }

    const formData = new FormData();
    formData.append("file", selectedMediaFile);

    try {
        const response = await fetch("http://127.0.0.1:5000/api/analyze_media", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (data && data.success) {
            if (placeholder) placeholder.style.display = "none";
            if (resultImg) {
                resultImg.src = data.image_base64;
                resultImg.style.display = "block";
            }
            if (countVal) countVal.innerText = data.count;
            if (riskVal) riskVal.innerText = data.risk_score + "%";
            
            const accuracyVal = document.getElementById("mediaAccuracyVal");
            if (accuracyVal) accuracyVal.innerText = data.accuracy ? data.accuracy + "%" : "N/A";
            
            if (statusBadge) {
                statusBadge.innerText = data.status;
                statusBadge.style.background = (data.status === "HIGH" || data.status === "EMERGENCY") ?
                    "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)";
                statusBadge.style.color = (data.status === "HIGH" || data.status === "EMERGENCY") ?
                    "#EF4444" : "#34D399";
            }
            if (typeof showNotification === "function") {
                showNotification(`AI Media Analysis Complete: Detected ${data.count} people (${data.status})`, "#10B981");
            }
        } else {
            alert("Error analyzing media: " + (data.error || "Unknown error"));
        }
    } catch (error) {
        console.error("Media analysis error:", error);
        alert("Failed to connect to backend AI analyzer.");
    } finally {
        if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = `<i class="fas fa-bolt"></i> Run AI Crowd Detection`;
        }
    }
}

window.handleMediaSelect = handleMediaSelect;
window.analyzeSelectedMedia = analyzeSelectedMedia;