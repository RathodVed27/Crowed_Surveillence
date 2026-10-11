"""
sensor_reader.py
--------------------------------------------
ESP8266 Sensor Communication Layer

Sensors:
1. Piezo
2. IR
3. SW420

The reader converts raw ESP8266 messages into
meaningful sensor events.

No raw 0/1 sensor values are exposed to the
dashboard as detection information.
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

        # Latest raw values
        self.piezo = 0

        # Human-readable sensor states
        self.ir_detected = False
        self.piezo_detected = False
        self.sw420_detected = False

        # One-shot events
        self.ir_event = False
        self.piezo_event = False
        self.sw420_event = False

        # Event counters
        self.ir_event_count = 0
        self.piezo_event_count = 0
        self.sw420_event_count = 0

        self._connect()


    # =====================================================
    # SERIAL CONNECTION
    # =====================================================

    def _connect(self):

        try:

            if self.serial is not None and self.serial.is_open:
                self.serial.close()

            self.serial = serial.Serial(
                self.serial_port,
                self.baud_rate,
                timeout=self.timeout
            )

            self.connected = True

            logger.info(
                f"ESP8266 Sensor connected on port "
                f"{self.serial_port}"
            )

        except Exception as e:

            self.connected = False

            logger.warning(
                f"ESP8266 Sensor unavailable on "
                f"{self.serial_port}: {e}"
            )


    # =====================================================
    # SERIAL READER
    # =====================================================

    def read(self):

        # Reset one-shot events
        self.ir_event = False
        self.piezo_event = False
        self.sw420_event = False

        # -------------------------------------------------
        # Reconnect if disconnected
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Read incoming ESP8266 messages
        # -------------------------------------------------

        try:

            if self.serial.in_waiting > 500:
                self.serial.reset_input_buffer()


            while self.serial.in_waiting:

                line = self.serial.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line:
                    continue


                # =========================================
                # PIEZO EVENT
                # =========================================

                if "FOOTSTEP DETECTED" in line:

                    self.piezo_event = True
                    self.piezo_detected = True

                    self.piezo_event_count += 1

                    if "Strength:" in line:

                        try:

                            value = (
                                line.split("Strength:")
                                [-1]
                                .strip()
                            )

                            self.piezo = int(value)

                        except ValueError:

                            pass

                    logger.info(
                        f"Piezo footstep detected "
                        f"(strength={self.piezo})"
                    )


                # =========================================
                # IR EVENT
                # =========================================

                elif "IR PERSON DETECTED" in line:

                    self.ir_event = True
                    self.ir_detected = True

                    self.ir_event_count += 1

                    logger.info(
                        "IR person passage detected"
                    )


                # =========================================
                # SW420 EVENT
                # =========================================

                elif "VIBRATION DETECTED" in line:

                    self.sw420_event = True
                    self.sw420_detected = True

                    self.sw420_event_count += 1

                    logger.info(
                        "SW420 vibration detected"
                    )


                # =========================================
                # OLD CSV FORMAT SUPPORT
                # =========================================

                else:

                    parts = line.split(",")

                    if len(parts) >= 3:

                        try:

                            self.piezo = int(parts[0])

                            ir_raw = int(parts[1])
                            sw420_raw = int(parts[2])

                            # We don't expose these raw values
                            # as dashboard detection states.

                            if ir_raw != 0:

                                self.ir_detected = True

                            if sw420_raw != 0:

                                self.sw420_detected = True

                        except ValueError:

                            pass


        except Exception as e:

            logger.error(
                f"Error reading ESP8266 serial data: {e}"
            )

            self.connected = False


        return self._build_data()


    # =====================================================
    # BUILD SENSOR DATA
    # =====================================================

    def _build_data(self):

        return {

            # Raw piezo strength
            "piezo": self.piezo,

            # Human-readable states
            "ir_detected": self.ir_detected,
            "piezo_detected": self.piezo_detected,
            "sw420_detected": self.sw420_detected,

            # One-shot events
            "ir_event": self.ir_event,
            "piezo_event": self.piezo_event,
            "sw420_event": self.sw420_event,

            # Event counters
            "ir_event_count": self.ir_event_count,
            "piezo_event_count": self.piezo_event_count,
            "sw420_event_count": self.sw420_event_count,

            # Connection
            "connected": self.connected
        }


    # =====================================================
    # CLOSE SERIAL
    # =====================================================

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


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    reader = SensorReader()

    print()
    print("========================================")
    print(" ESP8266 SENSOR READER")
    print("========================================")
    print("Waiting for sensor events...")
    print("Press CTRL+C to stop.")
    print()

    try:

        while True:

            data = reader.read()

            print(
                f"IR: "
                f"{'PERSON DETECTED' if data['ir_detected'] else 'CLEAR'}"
            )

            print(
                f"Piezo: "
                f"{'FOOTSTEP DETECTED' if data['piezo_detected'] else 'CLEAR'}"
            )

            print(
                f"SW420: "
                f"{'VIBRATION DETECTED' if data['sw420_detected'] else 'CLEAR'}"
            )

            print(
                f"Verified Events: "
                f"IR={data['ir_event_count']} | "
                f"Piezo={data['piezo_event_count']} | "
                f"SW420={data['sw420_event_count']}"
            )

            print("----------------------------------------")

            time.sleep(1)

    except KeyboardInterrupt:

        print("\nStopping sensor reader...")

    finally:

        reader.close()