// ============================================================
// sensors.js
// Sensor connection/status management
//
// IMPORTANT:
// dashboard.js is responsible for displaying sensor values.
// This file must NOT overwrite:
//     #piezo
//     #ir
//     #sw420
// ============================================================


const Sensors = {

    refreshRate: 2000,
    isUpdating: false

};


// ============================================================
// UPDATE SENSOR CONNECTION BADGE
// ============================================================

function updateSensorBadge(id, isOnline) {

    const badge =
        document.getElementById(id);

    if (!badge) {
        return;
    }


    if (isOnline) {

        badge.innerHTML = "ONLINE";

        badge.className =
            "badge-online";

        badge.style.color =
            "#22C55E";

    } else {

        badge.innerHTML = "OFFLINE";

        badge.className =
            "badge-danger";

        badge.style.color =
            "#EF4444";

    }

}


// ============================================================
// REFRESH SENSOR CONNECTION STATUS
// ============================================================

async function refreshSensors() {

    if (Sensors.isUpdating) {
        return;
    }

    Sensors.isUpdating = true;


    try {

        const data =
            await getStatus();


        if (!data) {
            return;
        }


        let connected = false;


        // ------------------------------------------
        // Health status
        // ------------------------------------------

        if (
            data.health &&
            (
                data.health.esp8266 === "CONNECTED" ||
                data.health.esp8266 === "ONLINE"
            )
        ) {

            connected = true;

        }


        // ------------------------------------------
        // Direct connection flag
        // ------------------------------------------

        if (data.connected === true) {

            connected = true;

        }


        // ------------------------------------------
        // Update ONLY connection badges
        // ------------------------------------------

        updateSensorBadge(
            "piezoBadge",
            connected
        );

        updateSensorBadge(
            "irBadge",
            connected
        );

        updateSensorBadge(
            "sw420Badge",
            connected
        );


    } catch (error) {

        console.warn(
            "Sensor status error:",
            error
        );

    } finally {

        Sensors.isUpdating = false;

    }

}


// ============================================================
// START
// ============================================================

window.addEventListener(
    "load",
    () => {

        refreshSensors();

        setInterval(
            refreshSensors,
            Sensors.refreshRate
        );

    }
);