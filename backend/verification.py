"""
verification.py
--------------------------------------------
Sensor + Camera Verification Engine

Camera:
    YOLO / ByteTrack people count

Sensors:
    IR       -> passage
    Piezo    -> footstep
    SW420    -> vibration

Important:
The three sensors are NOT added together.

One person can trigger all three sensors.
Therefore they act as corroborating evidence.
"""

import time
import logging

logger = logging.getLogger(
    "AI_Surveillance.VerificationEngine"
)


class VerificationEngine:

    def __init__(self):

        self.last_ir_time = 0
        self.last_piezo_time = 0
        self.last_sw420_time = 0

        self.sensor_verified_passages = 0

        # Sensor correlation window
        # Events occurring within this time
        # are treated as belonging to the same passage.
        self.correlation_window = 1.5


    def verify(
        self,
        people,
        piezo=0,
        ir=False,
        sw420=False,
        ir_event=False,
        piezo_event=False,
        sw420_event=False
    ):

        current_time = time.time()


        # ==========================================
        # RECORD SENSOR EVENTS
        # ==========================================

        if ir_event:

            self.last_ir_time = current_time

        if piezo_event:

            self.last_piezo_time = current_time

        if sw420_event:

            self.last_sw420_time = current_time


        # ==========================================
        # CHECK RECENT SENSOR EVENTS
        # ==========================================

        ir_recent = (
            current_time - self.last_ir_time
            <= self.correlation_window
        )

        piezo_recent = (
            current_time - self.last_piezo_time
            <= self.correlation_window
        )

        sw420_recent = (
            current_time - self.last_sw420_time
            <= self.correlation_window
        )


        # ==========================================
        # SENSOR EVIDENCE SCORE
        # ==========================================

        evidence = 0

        if ir_recent:
            evidence += 1

        if piezo_recent:
            evidence += 1

        if sw420_recent:
            evidence += 1


        # ==========================================
        # SENSOR VERIFICATION
        # ==========================================

        sensor_verified = (
            ir_recent
            and (
                piezo_recent
                or sw420_recent
            )
        )


        # ==========================================
        # COUNT SENSOR-CONFIRMED PASSAGE
        # ==========================================

        if sensor_verified and ir_event:

            self.sensor_verified_passages += 1

            logger.info(
                "Sensor-confirmed person passage detected"
            )


        # ==========================================
        # CONFIDENCE
        # ==========================================

        if evidence == 3:

            confidence = 100

        elif evidence == 2:

            confidence = 85

        elif evidence == 1:

            confidence = 65

        else:

            confidence = 40


        # Camera count remains the actual
        # current occupancy count.

        camera_count = max(0, int(people))


        # ==========================================
        # VERIFIED COUNT
        # ==========================================
        #
        # IMPORTANT:
        #
        # We do NOT add sensor events to
        # camera count.
        #
        # The camera is responsible for
        # current occupancy.
        #
        # Sensors verify physical activity.
        #
        # ==========================================

        verified_count = camera_count


        return {

            "verified_count":
                verified_count,

            "camera_count":
                camera_count,

            "sensor_verified":
                sensor_verified,

            "sensor_evidence":
                evidence,

            "sensor_confidence":
                confidence,

            "sensor_passage_count":
                self.sensor_verified_passages,

            "ir_recent":
                ir_recent,

            "piezo_recent":
                piezo_recent,

            "sw420_recent":
                sw420_recent
        }