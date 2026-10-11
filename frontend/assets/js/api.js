/*=====================================================
AI Crowd Surveillance Dashboard
API Service (Refactored Enterprise Version)
Supports non-blocking fetch with timeouts, paginated queries,
and live stream URLs.
Author : Ved Rathod
=====================================================*/

const API = {
    BASE_URL: "http://127.0.0.1:5000",
    STATUS: "/api/status",
    DASHBOARD: "/api/dashboard",
    HEALTH: "/api/health",
    HISTORY: "/api/history",
    ALERTS: "/api/alerts",
    CAMERA: "/api/camera",
    HEATMAP: "/api/heatmap"
};

//=====================================================
// Helper: Fetch with Timeout & AbortController
//=====================================================
async function fetchWithTimeout(url, timeoutMs = 4000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(id);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        clearTimeout(id);
        console.warn(`API request failed [${url}]:`, error.message || error);
        return null;
    }
}

//=====================================================
// System Status API
//=====================================================
async function getStatus() {
    const data = await fetchWithTimeout(API.BASE_URL + API.STATUS, 3000);
    return data || null;
}

//=====================================================
// Consolidated Dashboard Payload API
//=====================================================
async function getDashboard() {
    const data = await fetchWithTimeout(API.BASE_URL + API.DASHBOARD, 4000);
    return data || null;
}

//=====================================================
// System Health API
//=====================================================
async function getHealth() {
    const data = await fetchWithTimeout(API.BASE_URL + API.HEALTH, 3000);
    return data || null;
}

//=====================================================
// Crowd History API (Supports Pagination & Time Range)
//=====================================================
async function getHistory(page = null, perPage = 50, range = "all") {
    let url = API.BASE_URL + API.HISTORY;
    const params = [];
    if (page !== null) {
        params.push(`page=${encodeURIComponent(page)}`);
        params.push(`per_page=${encodeURIComponent(perPage)}`);
    }
    if (range && range !== "all") {
        params.push(`range=${encodeURIComponent(range)}`);
    }
    if (params.length > 0) {
        url += "?" + params.join("&");
    }

    const data = await fetchWithTimeout(url, 5000);
    return data || [];
}

//=====================================================
// Alerts API
//=====================================================
async function getAlerts() {
    const data = await fetchWithTimeout(API.BASE_URL + API.ALERTS, 3000);
    return data || [];
}

//=====================================================
// Stream URL Helpers
//=====================================================
function cameraURL() {
    return API.BASE_URL + API.CAMERA;
}

function heatmapURL() {
    return API.BASE_URL + API.HEATMAP;
}
