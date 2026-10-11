"""
sensor_reader.py
--------------------------------------------
ESP8266 Serial Communication Layer

Sensors:
1. Piezo
2. IR
3. SW420

ESP8266 telemetry format:
    DATA,piezo,ir,sw420

Example:
    DATA,433,1,0

Also supports:
    FOOTSTEP DETECTED | Strength: 559

Features:
- Live sensor telemetry
- Piezo event detection
- Automatic serial reconnection
- Backend-compatible sensor fields
- Safe fallback values
--------------------------------------------
Author : Ved Rathod
"""

import time
import serial
import logging

from config import SERIAL_PORT, BAUD_RATE, SERIAL_TIMEOUT


logger = logging.getLogger("AI_Surveillance.SensorReader")


class SensorReader:

    def __init__(self):

        self.serial_port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
        self.timeout = SERIAL_TIMEOUT

        self.serial = None
        self.connected = False

        self.last_reconnect_try = 0
        self.reconnect_interval = 5.0

        # -----------------------------------------------------
        # CURRENT SENSOR VALUES
        # -----------------------------------------------------

        self.piezo = 0
        self.ir = 0
        self.sw420 = 0

        # -----------------------------------------------------
        # SENSOR DETECTION STATES
        # -----------------------------------------------------

        self.piezo_detected = False
        self.ir_detected = False
        self.sw420_detected = False

        # -----------------------------------------------------
        # SENSOR EVENTS
        # -----------------------------------------------------

        self.piezo_event = False
        self.ir_event = False
        self.sw420_event = False

        # -----------------------------------------------------
        # EVENT COUNTERS
        # -----------------------------------------------------

        self.piezo_event_count = 0
        self.ir_event_count = 0
        self.sw420_event_count = 0

        # Connect automatically
        self._connect()

    # =========================================================
    # SERIAL CONNECTION
    # =========================================================

    def _connect(self):

        try:

            if self.serial is not None and self.serial.is_open:
                self.serial.close()

            self.serial = serial.Serial(
                self.serial_port,
                self.baud_rate,
                timeout=self.timeout
            )

            time.sleep(1)

            self.connected = True

            logger.info(
                f"ESP8266 Sensor connected on port {self.serial_port}"
            )

        except Exception as e:

            self.connected = False

            logger.warning(
                f"ESP8266 Sensor port {self.serial_port} unavailable "
                f"({e}). Using fallback sensor values."
            )

    # =========================================================
    # READ SENSOR DATA
    # =========================================================

    def read(self):

        # -----------------------------------------------------
        # RESET ONE-CYCLE EVENTS
        # -----------------------------------------------------

        self.piezo_event = False
        self.ir_event = False
        self.sw420_event = False

        # -----------------------------------------------------
        # CHECK CONNECTION
        # -----------------------------------------------------

        if (
            not self.connected
            or self.serial is None
            or not self.serial.is_open
        ):

            current_time = time.time()

            if (
                current_time - self.last_reconnect_try
                > self.reconnect_interval
            ):

                self.last_reconnect_try = current_time

                self._connect()

            return self._build_data()

        # -----------------------------------------------------
        # READ SERIAL DATA
        # -----------------------------------------------------

        try:

            # Prevent huge serial backlog
            if self.serial.in_waiting > 1000:
                self.serial.reset_input_buffer()

            while self.serial.in_waiting:

                line = self.serial.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                # =================================================
                # FORMAT 1
                # LIVE TELEMETRY
                #
                # DATA,433,1,0
                # =================================================

                if line.startswith("DATA,"):

                    parts = line.split(",")

                    if len(parts) >= 4:

                        try:

                            piezo_value = int(parts[1])
                            ir_value = int(parts[2])
                            sw420_value = int(parts[3])

                            # -------------------------------
                            # UPDATE CURRENT VALUES
                            # -------------------------------

                            self.piezo = piezo_value
                            self.ir = 1 if ir_value else 0
                            self.sw420 = 1 if sw420_value else 0

                            # -------------------------------
                            # UPDATE DETECTION STATES
                            # -------------------------------

                            self.ir_detected = self.ir == 1
                            self.sw420_detected = self.sw420 == 1

                            # Piezo is considered detected
                            # when its current value crosses
                            # the threshold.
                            self.piezo_detected = self.piezo >= 80

                            # -------------------------------
                            # Detect state transitions
                            # -------------------------------

                            if self.ir_detected:
                                self.ir_event = True
                                self.ir_event_count += 1

                            if self.sw420_detected:
                                self.sw420_event = True
                                self.sw420_event_count += 1

                            logger.debug(
                                f"Telemetry | "
                                f"Piezo={self.piezo} | "
                                f"IR={self.ir} | "
                                f"SW420={self.sw420}"
                            )

                        except ValueError:

                            logger.warning(
                                f"Invalid telemetry received: {line}"
                            )

                    continue

                # =================================================
                # FORMAT 2
                # PIEZO EVENT
                #
                # FOOTSTEP DETECTED | Strength: 559
                # =================================================

                if (
                    "FOOTSTEP DETECTED" in line
                    and "Strength:" in line
                ):

                    try:

                        value = line.split(
                            "Strength:"
                        )[-1].strip()

                        self.piezo = int(value)

                        self.piezo_detected = True
                        self.piezo_event = True
                        self.piezo_event_count += 1

                        logger.info(
                            f"Footstep detected | "
                            f"Piezo={self.piezo}"
                        )

                    except ValueError:

                        logger.warning(
                            f"Invalid Piezo event: {line}"
                        )

                    continue

                # =================================================
                # FORMAT 3
                # OLD MULTI-SENSOR FORMAT
                #
                # 433,1,0
                # =================================================

                parts = line.split(",")

                if len(parts) >= 3:

                    try:

                        self.piezo = int(parts[0])
                        self.ir = int(parts[1])
                        self.sw420 = int(parts[2])

                        self.ir_detected = self.ir == 1
                        self.sw420_detected = self.sw420 == 1
                        self.piezo_detected = self.piezo >= 80

                    except ValueError:

                        # Ignore unrelated startup/debug messages
                        pass

        # -----------------------------------------------------
        # SERIAL ERROR
        # -----------------------------------------------------

        except Exception as e:

            logger.error(
                f"Error reading serial sensor data: {e}"
            )

            self.connected = False

        # -----------------------------------------------------
        # RETURN DATA
        # -----------------------------------------------------

        return self._build_data()

    # =========================================================
    # BUILD SENSOR DATA
    # =========================================================

    def _build_data(self):

        return {

            # Raw/current values
            "piezo": self.piezo,
            "ir": self.ir,
            "sw420": self.sw420,

            # Detection states
            "piezo_detected": self.piezo_detected,
            "ir_detected": self.ir_detected,
            "sw420_detected": self.sw420_detected,

            # One-cycle events
            "piezo_event": self.piezo_event,
            "ir_event": self.ir_event,
            "sw420_event": self.sw420_event,

            # Event counters
            "piezo_event_count": self.piezo_event_count,
            "ir_event_count": self.ir_event_count,
            "sw420_event_count": self.sw420_event_count,

            # Connection
            "connected": self.connected
        }

    # =========================================================
    # CLOSE CONNECTION
    # =========================================================

    def close(self):

        if (
            self.serial is not None
            and self.serial.is_open
        ):

            try:
                self.serial.close()

            except Exception:
                pass

        self.connected = False

        logger.info(
            "ESP8266 Sensor connection closed."
        )


# =============================================================
# DIRECT TEST
# =============================================================

if __name__ == "__main__":

    reader = SensorReader()

    print()
    print("========================================")
    print(" ESP8266 SENSOR READER TEST")
    print("========================================")
    print("Waiting for sensor telemetry...")
    print("Press CTRL+C to stop.")
    print()

    try:

        while True:

            data = reader.read()

            print(
                f"Piezo: {data['piezo']} | "
                f"IR: {data['ir']} | "
                f"SW420: {data['sw420']} | "
                f"Connected: {data['connected']}"
            )

            time.sleep(0.5)

    except KeyboardInterrupt:

        print()
        print("Stopping sensor reader...")

    finally:

        reader.close()

        print("Sensor connection closed.")