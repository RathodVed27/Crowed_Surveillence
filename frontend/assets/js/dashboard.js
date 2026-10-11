/*=====================================================
AI Crowd Surveillance Dashboard
Dashboard Controller (Enterprise Refactored Version)
Synchronizes real-time KPIs, sensors, and system health badges
without resetting the MJPEG camera stream or causing polling lag.
Author : Ved Rathod
=====================================================*/

const Dashboard = {
    data: {},
    refreshRate: 1000,
    isUpdating: false
};

//=====================================================
// Update KPI Cards
//=====================================================
function updateKPICards(data) {

    if (!data) {
        return;
    }


    // ==================================================
    // DIRECT KPI UPDATE
    // ==================================================
    //
    // We intentionally do NOT use animateCounter()
    // here because the dashboard refreshes every 1 second.
    //
    // Direct values guarantee that the dashboard always
    // matches the backend API.
    //
    // ==================================================


    const people =
        document.getElementById("people");

    const occupancy =
        document.getElementById("occupancy");

    const unique =
        document.getElementById("unique");

    const entry =
        document.getElementById("entry");

    const exit =
        document.getElementById("exit");

    const riskScore =
        document.getElementById("risk_score");


    // ==================================================
    // PEOPLE
    // ==================================================

    if (people) {

        people.innerText =
            Number(data.people) || 0;

    }


    // ==================================================
    // OCCUPANCY
    // ==================================================

    if (occupancy) {

        occupancy.innerText =
            Number(data.occupancy) || 0;

    }


    // ==================================================
    // UNIQUE VISITORS
    // ==================================================

    if (unique) {

        unique.innerText =
            Number(data.unique) || 0;

    }


    // ==================================================
    // ENTRY
    // ==================================================

    if (entry) {

        entry.innerText =
            Number(data.entry) || 0;

    }


    // ==================================================
    // EXIT
    // ==================================================

    if (exit) {

        exit.innerText =
            Number(data.exit) || 0;

    }


    // ==================================================
    // RISK SCORE
    // ==================================================

    if (riskScore) {

        riskScore.innerText =
            Number(data.risk_score) || 0;

    }


    // ==================================================
    // PROGRESS BARS
    // ==================================================

    if (typeof updateProgress === "function") {

        updateProgress(
            "peopleProgress",
            Number(data.people) || 0,
            100
        );


        updateProgress(
            "occupancyProgress",
            Number(data.occupancy) || 0,
            100
        );


        updateProgress(
            "uniqueProgress",
            Number(data.unique) || 0,
            100
        );


        updateProgress(
            "entryProgress",
            Number(data.entry) || 0,
            100
        );


        updateProgress(
            "exitProgress",
            Number(data.exit) || 0,
            100
        );


        updateProgress(
            "riskProgress",
            Number(data.risk_score) || 0,
            100
        );

    }

}

//=====================================================
// Update Crowd Status
//=====================================================
function updateStatus(data) {
    const status = document.getElementById("status");
    if (!status) return;

    // Backend may return status as an object
    // Example:
    // { status: "SAFE", alert: "No Action Required", ... }

    const statusValue =
        typeof data.status === "object"
            ? (data.status.status || "SAFE")
            : (data.status || "SAFE");

    status.innerHTML = statusValue;

    if (typeof statusClass === "function") {
        status.className = statusClass(statusValue);
    } else {
        status.style.color =
            statusValue === "EMERGENCY" ? "#EF4444" :
            statusValue === "HIGH" ? "#F97316" :
            "#22C55E";
    }
}
//=====================================================
// Update Sensors
//=====================================================
// ============================================================
// SENSOR DISPLAY
// ============================================================

function updateSensors(data) {

    if (!data) {
        return;
    }


    const piezo =
        document.getElementById("piezo");

    const ir =
        document.getElementById("ir");

    const sw420 =
        document.getElementById("sw420");


    // ========================================================
    // PIEZO
    // ========================================================

    if (piezo) {

        const piezoValue =
            Number(data.piezo) || 0;

        piezo.innerText =
            piezoValue;

    }


    // ========================================================
    // IR
    // ========================================================

    if (ir) {

        if (Number(data.ir) === 1) {

            ir.innerText =
                "PERSON DETECTED";

        } else {

            ir.innerText =
                "CLEAR";

        }

    }


    // ========================================================
    // SW420
    // ========================================================

    if (sw420) {

        if (Number(data.sw420) === 1) {

            sw420.innerText =
                "VIBRATION DETECTED";

        } else {

            sw420.innerText =
                "CLEAR";

        }

    }

}

//=====================================================
// Update Right Panel (System Health Badges)
//=====================================================
function updateSystemPanel(data) {
    const health = data.health || {};

    const updateBadge = (id, statusText, isOnline) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.innerHTML = statusText;
        el.style.color = isOnline ? "#22C55E" : "#EF4444";
    };

    const camStatus = health.camera || (data.fps > 0 ? "ONLINE" : "OFFLINE");
    const aiStatus = health.ai_model || "READY";
    const dbStatus = health.database || "ONLINE";
    const espStatus = health.esp8266 || "CONNECTED";

    updateBadge("systemCameraStatus", camStatus, camStatus === "ONLINE");
    updateBadge("aiStatus", aiStatus, aiStatus === "READY" || aiStatus === "ACTIVE");
    updateBadge("databaseStatus", dbStatus, dbStatus === "ONLINE" || dbStatus === "CONNECTED");
    updateBadge("espStatus", espStatus, espStatus === "CONNECTED" || espStatus === "ONLINE");
}

//=====================================================
// Update Time
//=====================================================
function updateDateTime() {
    const time = document.getElementById("currentTime");
    const date = document.getElementById("currentDate");

    if (time && typeof currentTime === "function") {
        time.innerHTML = currentTime();
    }
    if (date && typeof currentDate === "function") {
        date.innerHTML = currentDate();
    }
}

//=====================================================
// Update Dashboard Loop (Lag-Protected)
//=====================================================
async function updateDashboard() {
    if (Dashboard.isUpdating) return;
    Dashboard.isUpdating = true;

    try {
        const data = await getDashboard();
        if (!data) {
            console.warn("No Dashboard Data Received");
            return;
        }

        Dashboard.data = data;
        updateKPICards(data);
        updateStatus(data);
        updateSensors(data);
        updateSystemPanel(data);
    } catch (error) {
        console.error("Dashboard update error:", error);
    } finally {
        Dashboard.isUpdating = false;
    }
}

//=====================================================
// Start Dashboard
//=====================================================
function startDashboard() {
    console.info("✅ Enterprise Dashboard Started");
    updateDashboard();
    updateDateTime();

    setInterval(updateDashboard, Dashboard.refreshRate);
    setInterval(updateDateTime, 1000);
}



//=====================================================
// Window Load
//=====================================================
window.addEventListener("load", () => {
    if (typeof hideLoader === "function") {
        hideLoader();
    }
    startDashboard();
});