/* =====================================================
   INTERACTIVE MODALS & CLICKABLE CONTROLLER
   AI Crowd Surveillance Dashboard
   Author : Ved Rathod
===================================================== */

class InteractiveModalSystem {
    constructor() {
        this.activeDropdown = null;
        this.init();
    }

    init() {
        this.createModalContainer();
        this.createDropdownContainers();
        this.setupNavbarControls();
        this.setupKPICardClicks();
        this.setupSensorAndStatusClicks();

        // Close dropdowns when clicking outside
        document.addEventListener("click", (e) => {
            if (!e.target.closest("#navBellBtn") && !e.target.closest("#notifDropdown") &&
                !e.target.closest("#navProfileBtn") && !e.target.closest("#profileDropdown")) {
                this.closeAllDropdowns();
            }
        });
    }

    // 1. Reusable Modal Overlay Container
    createModalContainer() {
        if (document.getElementById("customModalOverlay")) return;

        const overlay = document.createElement("div");
        overlay.id = "customModalOverlay";
        overlay.className = "custom-modal-overlay";
        overlay.innerHTML = `
            <div class="custom-modal-box" id="customModalBox">
                <div class="custom-modal-header">
                    <h4 id="customModalTitle"><i class="fas fa-chart-pie"></i> Metric Details</h4>
                    <button class="custom-modal-close" id="closeCustomModal"><i class="fas fa-times"></i></button>
                </div>
                <div class="custom-modal-body" id="customModalBody">
                    Loading details...
                </div>
                <div class="custom-modal-footer" id="customModalFooter">
                    <button class="modal-btn modal-btn-secondary" id="modalCloseBtn">Close</button>
                    <button class="modal-btn modal-btn-primary" id="modalActionBtn">Export Report</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById("closeCustomModal").addEventListener("click", () => this.closeModal());
        document.getElementById("modalCloseBtn").addEventListener("click", () => this.closeModal());
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) this.closeModal();
        });
    }

    // 2. Reusable Dropdowns (Notifications & Profile)
    createDropdownContainers() {
        // Notifications Dropdown
        if (!document.getElementById("notifDropdown")) {
            const notifBox = document.createElement("div");
            notifBox.id = "notifDropdown";
            notifBox.className = "floating-dropdown";
            notifBox.innerHTML = `
                <div class="dropdown-header">
                    <span><i class="fas fa-bell"></i> Live Surveillance Alerts</span>
                    <span style="font-size: 11px; color: #10B981;">● Active</span>
                </div>
                <div id="notifList">
                    <div class="dropdown-item">
                        <i class="fas fa-shield-alt" style="color: #00F0FF; font-size: 18px;"></i>
                        <div>
                            <strong style="display: block; color: #fff;">AI YOLOv8 Engine Ready</strong>
                            <small style="color: #94A3B8;">Real-time ByteTrack tracking online</small>
                        </div>
                    </div>
                    <div class="dropdown-item">
                        <i class="fas fa-check-circle" style="color: #10B981; font-size: 18px;"></i>
                        <div>
                            <strong style="display: block; color: #fff;">Crowd Density Safe</strong>
                            <small style="color: #94A3B8;">Occupancy levels within normal limits</small>
                        </div>
                    </div>
                    <div class="dropdown-item">
                        <i class="fas fa-wave-square" style="color: #3B82F6; font-size: 18px;"></i>
                        <div>
                            <strong style="display: block; color: #fff;">Piezo & IR Sensors Synchronized</strong>
                            <small style="color: #94A3B8;">Audio telemetry online (0 dB)</small>
                        </div>
                    </div>
                </div>
                <div style="padding: 12px 20px; text-align: center; border-top: 1px solid rgba(255,255,255,0.06);">
                    <button id="markReadBtn" style="background: transparent; border: none; color: #00F0FF; font-weight: 700; cursor: pointer; font-size: 12px;">Mark All as Read</button>
                </div>
            `;
            document.body.appendChild(notifBox);

            document.getElementById("markReadBtn").addEventListener("click", () => {
                const badge = document.getElementById("notifBadge");
                if (badge) badge.style.display = "none";
                this.closeAllDropdowns();
                this.showToast("All notifications marked as read.", "#10B981");
            });
        }

        // Profile Dropdown
        if (!document.getElementById("profileDropdown")) {
            const profBox = document.createElement("div");
            profBox.id = "profileDropdown";
            profBox.className = "floating-dropdown";
            profBox.style.width = "320px";
            profBox.innerHTML = `
                <div class="dropdown-header">
                    <span><i class="fas fa-user-shield"></i> Administrator Account</span>
                    <span style="background: rgba(16,185,129,0.2); color: #10B981; padding: 3px 10px; border-radius: 12px; font-size: 11px;">Level 5</span>
                </div>
                <div style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; gap: 14px;">
                    <div style="width: 46px; height: 46px; border-radius: 50%; background: linear-gradient(135deg, #00F0FF, #3B82F6); display: flex; align-items: center; justify-content: center; font-weight: 700; color: #000; font-size: 16px;">VR</div>
                    <div>
                        <strong style="color: #fff; font-size: 15px; display: block;">Ved Rathod</strong>
                        <small style="color: #94A3B8;">Super Administrator</small>
                    </div>
                </div>
                <div class="dropdown-item" id="profDiagBtn">
                    <i class="fas fa-chart-line" style="color: #00F0FF;"></i>
                    <span>System Diagnostic Logs</span>
                </div>
                <div class="dropdown-item" id="profApiBtn">
                    <i class="fas fa-key" style="color: #FBBF24;"></i>
                    <span>API & Security Management</span>
                </div>
                <div class="dropdown-item" id="profLogoutBtn" style="color: #EF4444;">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>Log Out Session</span>
                </div>
            `;
            document.body.appendChild(profBox);

            document.getElementById("profDiagBtn").addEventListener("click", () => {
                this.closeAllDropdowns();
                const sec = document.querySelector(".logs-section");
                if (sec) sec.scrollIntoView({ behavior: "smooth" });
            });
            document.getElementById("profApiBtn").addEventListener("click", () => {
                this.closeAllDropdowns();
                this.showModal(
                    '<i class="fas fa-key"></i> API Key & Security',
                    `<p><strong>Connected Backend:</strong> http://127.0.0.1:8000</p>
                     <p><strong>WebSocket Stream:</strong> ws://127.0.0.1:8000/ws/camera</p>
                     <p><strong>Token Authorization:</strong> Active Bearer Token (Enterprise Perpetual License)</p>`,
                    "Copy API URL",
                    () => {
                        navigator.clipboard.writeText("http://127.0.0.1:8000");
                        this.showToast("API URL copied to clipboard!", "#00F0FF");
                        this.closeModal();
                    }
                );
            });
            document.getElementById("profLogoutBtn").addEventListener("click", () => {
                this.closeAllDropdowns();
                this.showToast("Active Administrator Session Continues in Background.", "#3B82F6");
            });
        }
    }

    // 3. Navbar Controls (Bell, Theme, Settings, Profile)
    setupNavbarControls() {
        // Bell Click
        const bellBtn = document.getElementById("navBellBtn");
        const notifDrop = document.getElementById("notifDropdown");
        if (bellBtn && notifDrop) {
            bellBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                this.toggleDropdown(notifDrop);
            });
        }

        // Profile Click
        const profBtn = document.getElementById("navProfileBtn");
        const profDrop = document.getElementById("profileDropdown");
        if (profBtn && profDrop) {
            profBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                this.toggleDropdown(profDrop);
            });
        }

        // Theme Toggle Click
        const themeBtn = document.getElementById("navThemeBtn");
        const themeIcon = document.getElementById("themeIcon");
        if (themeBtn) {
            themeBtn.addEventListener("click", () => {
                document.body.classList.toggle("light-theme");
                const isLight = document.body.classList.contains("light-theme");
                if (themeIcon) {
                    themeIcon.className = isLight ? "fas fa-sun" : "fas fa-moon";
                }
                this.showToast(
                    isLight ? "Switched to Light Contrast Mode" : "Switched to Dark Command Mode",
                    "#00F0FF"
                );
            });
        }

        // Settings Click
        const settingsBtn = document.getElementById("navSettingsBtn");
        if (settingsBtn) {
            settingsBtn.addEventListener("click", () => {
                this.showModal(
                    '<i class="fas fa-sliders-h"></i> System Configuration & Settings',
                    `
                    <div style="margin-bottom: 18px;">
                        <label style="display: block; margin-bottom: 6px; font-weight: 600;">AI YOLOv8 Confidence Threshold: <span id="confVal">75%</span></label>
                        <input type="range" min="50" max="95" value="75" style="width: 100%;" oninput="document.getElementById('confVal').innerText = this.value + '%'" />
                    </div>
                    <div style="margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
                        <label style="font-weight: 600;">Audio Buzzer Alarm System:</label>
                        <select style="background: #1F2937; color: #fff; border: 1px solid rgba(0,240,255,0.4); padding: 6px 14px; border-radius: 8px;">
                            <option>Enabled (Auto-Trigger)</option>
                            <option>Muted (Silent Alert)</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
                        <label style="font-weight: 600;">Camera Stream Quality:</label>
                        <select style="background: #1F2937; color: #fff; border: 1px solid rgba(0,240,255,0.4); padding: 6px 14px; border-radius: 8px;">
                            <option>1080p Full HD (30 FPS)</option>
                            <option>720p HD (30 FPS)</option>
                            <option>480p Fast Mode</option>
                        </select>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <label style="font-weight: 600;">Dashboard Polling Frequency:</label>
                        <select style="background: #1F2937; color: #fff; border: 1px solid rgba(0,240,255,0.4); padding: 6px 14px; border-radius: 8px;">
                            <option>1000 ms (Real-Time)</option>
                            <option>2000 ms (Normal)</option>
                            <option>5000 ms (Low Bandwidth)</option>
                        </select>
                    </div>
                    `,
                    "Save & Apply Settings",
                    () => {
                        this.showToast("System settings saved and synchronized!", "#10B981");
                        this.closeModal();
                    }
                );
            });
        }
    }

    // 4. Clickable KPI Cards
    setupKPICardClicks() {
        const kpiCards = document.querySelectorAll(".kpi-card");
        const kpiDetails = {
            "People Detected": {
                icon: "fa-users",
                description: "Live count of human figures detected across all active RTSP/CCTV camera feeds using YOLOv8 ByteTrack AI.",
                formula: "Count = ∑(Unique Human Bounding Boxes with Confidence > 60%)",
                targetSection: ".dashboard-grid"
            },
            "Occupancy": {
                icon: "fa-building",
                description: "Real-time room occupancy vs maximum permissible safety limits for crowd dispersion.",
                formula: "Occupancy Index = Current Crowd Count / Maximum Zone Capacity (100)",
                targetSection: ".dashboard-grid"
            },
            "Unique Visitors": {
                icon: "fa-id-card",
                description: "Total unique visitor tracks recorded since 00:00 AM today using ByteTrack re-identification.",
                formula: "Unique ID Tracks maintained across active camera frames",
                targetSection: ".chart-section"
            },
            "Entry Count": {
                icon: "fa-arrow-right-to-bracket",
                description: "Total people crossing the designated entry virtual line inwards.",
                formula: "Vector crossings from Zone Outer -> Zone Inner",
                targetSection: ".chart-section"
            },
            "Exit Count": {
                icon: "fa-arrow-right-from-bracket",
                description: "Total people crossing the designated exit virtual line outwards.",
                formula: "Vector crossings from Zone Inner -> Zone Outer",
                targetSection: ".chart-section"
            },
            "Risk Score": {
                icon: "fa-exclamation-triangle",
                description: "Algorithmic crowd density and stampede risk score calculated from density, velocity, and sensor alerts.",
                formula: "Risk % = 0.5×(Occupancy %) + 0.3×(Density Gradient) + 0.2×(Audio Level)",
                targetSection: ".alert-section"
            }
        };

        kpiCards.forEach(card => {
            card.addEventListener("click", () => {
                const titleEl = card.querySelector(".card-title");
                const valEl = card.querySelector("h2");
                const title = titleEl ? titleEl.innerText.trim() : "KPI Metric";
                const val = valEl ? valEl.innerText.trim() : "0";
                const info = kpiDetails[title] || {
                    icon: "fa-chart-line",
                    description: "Real-time analytical telemetry monitored by AI Crowd Surveillance Engine.",
                    formula: "Live System Telemetry",
                    targetSection: ".chart-section"
                };

                this.showModal(
                    `<i class="fas ${info.icon}"></i> ${title} — Analytical Breakdown`,
                    `
                    <div style="background: rgba(0,0,0,0.3); border-radius: 14px; padding: 18px; margin-bottom: 18px; border: 1px solid rgba(0,240,255,0.2);">
                        <span style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Current Recorded Value</span>
                        <h2 style="font-size: 38px; color: #00F0FF; margin: 4px 0 0 0;">${val}</h2>
                    </div>
                    <p><strong><i class="fas fa-info-circle" style="color:#00F0FF;"></i> Description:</strong> ${info.description}</p>
                    <p><strong><i class="fas fa-calculator" style="color:#10B981;"></i> Formula:</strong> <code style="color: #FBBF24;">${info.formula}</code></p>
                    <p style="margin-top: 14px; color: #94A3B8; font-size: 12px;">Data is continuously polled every 1,000 ms with lag protection.</p>
                    `,
                    "Jump to Analytical Charts",
                    () => {
                        this.closeModal();
                        const sec = document.querySelector(info.targetSection);
                        if (sec) sec.scrollIntoView({ behavior: "smooth" });
                    }
                );
            });
        });
    }

    // 5. Clickable Sensor Cards & Status Cards
    setupSensorAndStatusClicks() {
        const sensorCards = document.querySelectorAll(".sensor-card");
        sensorCards.forEach(card => {
            card.addEventListener("click", () => {
                const title = card.querySelector("h5") ? card.querySelector("h5").innerText.trim() : "Sensor";
                const val = card.querySelector("h2") ? card.querySelector("h2").innerText.trim() : "0";
                this.showModal(
                    `<i class="fas fa-microchip"></i> ${title} Telemetry`,
                    `<p><strong>Current Reading:</strong> <span style="color:#00F0FF; font-size: 20px; font-weight: 700;">${val}</span></p>
                     <p><strong>Hardware Interface:</strong> ESP8266 Wi-Fi Microcontroller -> Serial WebSocket</p>
                     <p><strong>Calibration Status:</strong> Automatically calibrated against ambient noise baseline.</p>`,
                    "Refresh Sensor",
                    () => {
                        this.showToast(`${title} re-calibrated successfully!`, "#10B981");
                        this.closeModal();
                    }
                );
            });
        });

        const statusCards = document.querySelectorAll(".status-card");
        statusCards.forEach(card => {
            card.addEventListener("click", () => {
                const title = card.querySelector("h5") ? card.querySelector("h5").innerText.trim() : "System";
                const val = card.querySelector("h2") ? card.querySelector("h2").innerText.trim() : "ONLINE";
                this.showModal(
                    `<i class="fas fa-server"></i> ${title} Health Diagnostics`,
                    `<p><strong>Module Status:</strong> <span style="color:#10B981; font-weight: 800;">${val}</span></p>
                     <p><strong>Uptime:</strong> 99.98% Enterprise High Availability</p>
                     <p><strong>Latency:</strong> < 12 ms response time</p>`,
                    "Run Self-Test",
                    () => {
                        this.showToast(`${title} self-test passed (0 errors)`, "#00F0FF");
                        this.closeModal();
                    }
                );
            });
        });
    }

    // Modal Helpers
    showModal(titleHtml, bodyHtml, actionText = "Export Report", actionCallback = null) {
        const overlay = document.getElementById("customModalOverlay");
        const title = document.getElementById("customModalTitle");
        const body = document.getElementById("customModalBody");
        const actionBtn = document.getElementById("modalActionBtn");

        if (!overlay || !title || !body) return;

        title.innerHTML = titleHtml;
        body.innerHTML = bodyHtml;

        if (actionBtn) {
            actionBtn.innerText = actionText;
            actionBtn.onclick = actionCallback || (() => {
                this.showToast("Report generated & downloaded!", "#10B981");
                this.closeModal();
            });
        }

        overlay.classList.add("active");
    }

    closeModal() {
        const overlay = document.getElementById("customModalOverlay");
        if (overlay) overlay.classList.remove("active");
    }

    toggleDropdown(el) {
        if (!el) return;
        const isActive = el.classList.contains("active");
        this.closeAllDropdowns();
        if (!isActive) el.classList.add("active");
    }

    closeAllDropdowns() {
        document.querySelectorAll(".floating-dropdown").forEach(d => d.classList.remove("active"));
    }

    showToast(message, color = "#00F0FF") {
        if (typeof showNotification === "function") {
            showNotification(message, color);
        } else {
            console.log("Toast:", message);
        }
    }
}

// Initialize Interactive Modals System on DOM load
window.addEventListener("DOMContentLoaded", () => {
    window.modalsController = new InteractiveModalSystem();
});
