/*=====================================================
AI Crowd Surveillance Dashboard
Alert Controller (Enterprise Refactored Version)
Synchronizes alerts and historical logs with support for
paginated responses and consistent timestamp formatting.
Author : Ved Rathod
=====================================================*/

const AlertSystem = {
    refreshRate: 2000,
    alerts: [],
    isUpdating: false
};

//=====================================================
// Create Alert Card
//=====================================================
function createAlertCard(alert) {
    const level = (alert.status || alert.level || "SAFE").toLowerCase();
    const timeStr = alert.time || alert.timestamp || "Just Now";
    const statusText = alert.status || alert.level || "SAFE";
    const peopleCount = alert.people !== undefined ? alert.people : 0;
    const riskScore = alert.risk_score !== undefined ? alert.risk_score : 0;

    return `
    <div class="alert-card alert-${level}">
        <div class="alert-top">
            <div class="alert-title">
                <i class="fas fa-triangle-exclamation"></i>
                <div>
                    <h5>${statusText}</h5>
                    <small>${timeStr}</small>
                </div>
            </div>
            <span class="alert-badge badge-${level}">
                ${statusText}
            </span>
        </div>
        <div class="alert-body">
            ${alert.message || "Crowd Surveillance Monitoring Event"}
        </div>
        <div class="alert-footer">
            <div class="alert-info">
                <span>
                    <i class="fas fa-users"></i>
                    ${peopleCount}
                </span>
                <span>
                    <i class="fas fa-chart-line"></i>
                    ${riskScore}%
                </span>
            </div>
        </div>
    </div>
    `;
}

//=====================================================
// Update Alert Panel
//=====================================================
function updateAlertPanel(alerts) {
    const container = document.getElementById("alertList");
    if (!container) return;

    const list = Array.isArray(alerts) ? alerts : (alerts.items || []);

    if (list.length === 0) {
        container.innerHTML = `
        <div class="no-alert">
            <i class="fas fa-check-circle"></i>
            <h4>No Active Emergency Alerts</h4>
        </div>
        `;
        return;
    }

    container.innerHTML = list.map(createAlertCard).join("");
}

//=====================================================
// History Table
//=====================================================
function updateHistoryTable(history) {
    const table = document.getElementById("historyTable");
    if (!table) return;

    const list = Array.isArray(history) ? history : (history.items || []);
    table.innerHTML = "";

    list.slice(0, 15).forEach(item => {
        const timeStr = item.time || item.timestamp || "-";
        const statusStr = item.status || "SAFE";
        const riskStr = item.risk_score !== undefined ? item.risk_score : 0;
        const peopleStr = item.people !== undefined ? item.people : 0;
        const piezo = item.piezo || 0;
        const ir = item.ir || 0;
        const sw = item.sw420 || 0;

        table.innerHTML += `
        <tr>
            <td>${timeStr}</td>
            <td><span class="badge ${statusStr === 'EMERGENCY' ? 'bg-danger' : (statusStr === 'HIGH' ? 'bg-warning' : 'bg-success')}">${statusStr}</span></td>
            <td>${riskStr}%</td>
            <td>${peopleStr}</td>
            <td>Piezo: ${piezo} | IR: ${ir} | SW: ${sw}</td>
        </tr>
        `;
    });
}

//=====================================================
// Alert Notification
//=====================================================
function notify(alert) {
    if (!alert || typeof showNotification !== "function") return;
    showNotification(
        alert.message || "High Crowd Alert Detected",
        "#EF4444"
    );
}

//=====================================================
// System Logs Box
//=====================================================
function updateSystemLogs(history) {
    const logsContainer = document.getElementById("logs");
    if (!logsContainer) return;

    const list = Array.isArray(history) ? history : (history.items || []);
    if (list.length === 0) {
        logsContainer.innerHTML = `
        <div class="log-item" style="padding: 12px; color: #94A3B8; font-family: monospace;">
            [SYSTEM] AI Surveillance Daemon initialized. Monitoring crowd telemetry...
        </div>`;
        return;
    }

    logsContainer.innerHTML = list.slice(0, 15).map(item => {
        const timeStr = item.time || item.timestamp || "Just Now";
        const statusStr = item.status || "SAFE";
        const riskStr = item.risk_score !== undefined ? item.risk_score : 0;
        const peopleStr = item.people !== undefined ? item.people : 0;
        const color = statusStr === 'EMERGENCY' ? '#EF4444' : (statusStr === 'HIGH' ? '#F97316' : '#22C55E');

        return `
        <div class="log-item" style="padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: monospace; font-size: 13px;">
            <span style="color: #64748B;">[${timeStr}]</span>
            <strong style="color: ${color}; margin: 0 8px;">[${statusStr}]</strong>
            <span style="color: #E2E8F0;">Crowd: ${peopleStr} people detected | Risk Score: ${riskStr}% | Sensor Telemetry Verified</span>
        </div>`;
    }).join("");
}

//=====================================================
// Refresh Alerts & History (Lag-Protected)
//=====================================================
async function refreshAlerts() {
    if (AlertSystem.isUpdating) return;
    AlertSystem.isUpdating = true;

    try {
        const [alerts, history] = await Promise.all([
            getAlerts(),
            getHistory(null, 30, "all")
        ]);

        if (alerts) {
            updateAlertPanel(alerts);
        }
        if (history) {
            updateHistoryTable(history);
            updateSystemLogs(history);
        }
    } catch (error) {
        console.error("Alerts refresh error:", error);
    } finally {
        AlertSystem.isUpdating = false;
    }
}

//=====================================================
// Start
//=====================================================
window.addEventListener("load", () => {
    refreshAlerts();
    setInterval(refreshAlerts, AlertSystem.refreshRate);
});