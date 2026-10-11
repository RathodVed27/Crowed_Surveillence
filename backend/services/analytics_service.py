"""
analytics_service.py
--------------------------------------------------
Enterprise Crowd Analytics Service

Responsibilities:
- Receive YOLO / ByteTrack tracking data
- Receive ESP8266 sensor data
- Verify physical passage using:
      IR     -> Person passage
      Piezo  -> Footstep
      SW420  -> Vibration
- Calculate crowd analytics
- Update centralized system state
- Save crowd history
- Save system health

Important:
The three sensors are NOT added together as people.

YOLO / ByteTrack:
    Current camera occupancy

IR + Piezo + SW420:
    Physical passage verification

Internal backend sensor values:
    IR    -> 0 / 1
    SW420 -> 0 / 1

Frontend converts these into:
    IR    -> PERSON DETECTED / CLEAR
    SW420 -> VIBRATION DETECTED / CLEAR

Author : Ved Rathod
"""

import logging

from analytics import CrowdAnalytics
from verification import VerificationEngine

from repositories.crowd_repository import CrowdRepository
from repositories.health_repository import HealthRepository

from models.state import state


logger = logging.getLogger(
    "AI_Surveillance.AnalyticsService"
)


class AnalyticsService:

    def __init__(self):

        # ==================================================
        # ANALYTICS ENGINE
        # ==================================================

        self.analytics = CrowdAnalytics()


        # ==================================================
        # VERIFICATION ENGINE
        # ==================================================

        self.verifier = VerificationEngine()


        # ==================================================
        # DATABASE REPOSITORIES
        # ==================================================

        self.crowd_repo = CrowdRepository()

        self.health_repo = HealthRepository()


        logger.info(
            "✅ Analytics Service Started"
        )


    # ======================================================
    # PROCESS TRACKING + SENSOR DATA
    # ======================================================

    def process(
        self,
        tracking_data,
        sensor_data
    ):

        try:

            # ==================================================
            # 1. CAMERA / YOLO DATA
            # ==================================================

            people = int(
                tracking_data.get(
                    "count",
                    0
                ) or 0
            )


            occupancy = tracking_data.get(
                "occupancy",
                0
            )


            unique_people = tracking_data.get(
                "unique",
                0
            )


            entry_count = tracking_data.get(
                "entry",
                0
            )


            exit_count = tracking_data.get(
                "exit",
                0
            )


            people_list = tracking_data.get(
                "people",
                []
            )


            # ==================================================
            # 2. SENSOR RAW VALUES
            # ==================================================

            raw_piezo = sensor_data.get(
                "piezo",
                0
            )

            try:

                raw_piezo = int(
                    raw_piezo
                )

            except (
                ValueError,
                TypeError
            ):

                raw_piezo = 0


            # --------------------------------------------------
            # IR
            #
            # IMPORTANT:
            # Keep numeric internally.
            # Never put "CLEAR" into state.py.
            # --------------------------------------------------

            raw_ir = sensor_data.get(
                "ir",
                0
            )

            try:

                raw_ir = int(
                    raw_ir
                )

            except (
                ValueError,
                TypeError
            ):

                raw_ir = 0


            raw_ir = 1 if raw_ir != 0 else 0


            # --------------------------------------------------
            # SW420
            # --------------------------------------------------

            raw_sw420 = sensor_data.get(
                "sw420",
                0
            )

            try:

                raw_sw420 = int(
                    raw_sw420
                )

            except (
                ValueError,
                TypeError
            ):

                raw_sw420 = 0


            raw_sw420 = 1 if raw_sw420 != 0 else 0


            # ==================================================
            # 3. SENSOR EVENTS
            # ==================================================

            ir_event = bool(
                sensor_data.get(
                    "ir_event",
                    False
                )
            )


            piezo_event = bool(
                sensor_data.get(
                    "piezo_event",
                    False
                )
            )


            sw420_event = bool(
                sensor_data.get(
                    "sw420_event",
                    False
                )
            )


            # ==================================================
            # 4. SENSOR DETECTION STATES
            # ==================================================

            ir_detected = bool(
                sensor_data.get(
                    "ir_detected",
                    raw_ir == 1
                )
            )


            piezo_detected = bool(
                sensor_data.get(
                    "piezo_detected",
                    False
                )
            )


            sw420_detected = bool(
                sensor_data.get(
                    "sw420_detected",
                    raw_sw420 == 1
                )
            )


            # ==================================================
            # 5. SENSOR EVENT COUNTERS
            # ==================================================

            ir_event_count = int(
                sensor_data.get(
                    "ir_event_count",
                    0
                ) or 0
            )


            piezo_event_count = int(
                sensor_data.get(
                    "piezo_event_count",
                    0
                ) or 0
            )


            sw420_event_count = int(
                sensor_data.get(
                    "sw420_event_count",
                    0
                ) or 0
            )


            # ==================================================
            # 6. SENSOR CONNECTION
            # ==================================================

            sensor_connected = bool(
                sensor_data.get(
                    "connected",
                    False
                )
            )


            # ==================================================
            # 7. VERIFY SENSOR + CAMERA
            # ==================================================

            verification_result = self.verifier.verify(

                people=people,

                piezo=raw_piezo,

                ir=raw_ir,

                sw420=raw_sw420,

                ir_event=ir_event,

                piezo_event=piezo_event,

                sw420_event=sw420_event

            )


            # ==================================================
            # 8. VERIFICATION RESULTS
            # ==================================================

            camera_count = int(
                verification_result.get(
                    "camera_count",
                    people
                )
            )


            verified_count = int(
                verification_result.get(
                    "verified_count",
                    camera_count
                )
            )


            sensor_verified = bool(
                verification_result.get(
                    "sensor_verified",
                    False
                )
            )


            sensor_evidence = int(
                verification_result.get(
                    "sensor_evidence",
                    0
                )
            )


            sensor_confidence = int(
                verification_result.get(
                    "sensor_confidence",
                    40
                )
            )


            sensor_passage_count = int(
                verification_result.get(
                    "sensor_passage_count",
                    0
                )
            )


            # ==================================================
            # 9. CROWD ANALYTICS
            # ==================================================
            #
            # IMPORTANT:
            #
            # These numeric sensor values are used internally.
            #
            # They are NOT displayed as 0/1 on the dashboard.
            #
            # ==================================================

            analytics_result = self.analytics.analyze(

                verified_count,

                raw_piezo,

                raw_ir,

                raw_sw420

            )


            # ==================================================
            # 10. ANALYTICS RESULTS
            # ==================================================

            risk_score = analytics_result.get(
                "risk_score",
                0
            )


            status = analytics_result.get(
                "status",
                "SAFE"
            )


            trend = analytics_result.get(
                "trend",
                "Stable"
            )


            alert_message = analytics_result.get(
                "alert",
                "No Action Required"
            )


            # ==================================================
            # 11. UPDATE CENTRAL CROWD STATE
            # ==================================================

            state.update_crowd(

                people_count=verified_count,

                occupancy=occupancy,

                unique_people=unique_people,

                entry_count=entry_count,

                exit_count=exit_count,

                people_list=people_list

            )


            # ==================================================
            # 12. UPDATE CAMERA FRAME
            # ==================================================

            if "frame" in tracking_data:

                state.set_frame(
                    tracking_data["frame"]
                )


            # ==================================================
            # 13. UPDATE SENSOR STATE
            # ==================================================
            #
            # IMPORTANT:
            #
            # state.py expects:
            #
            #     IR    = integer
            #     SW420 = integer
            #
            # Therefore DO NOT send:
            #
            #     "CLEAR"
            #     "PERSON DETECTED"
            #
            # here.
            #
            # Frontend handles the human-readable display.
            #
            # ==================================================

            state.update_sensors(

                piezo=raw_piezo,

                ir=raw_ir,

                sw420=raw_sw420,

                connected=sensor_connected

            )


            # ==================================================
            # 14. SAVE CROWD HISTORY
            # ==================================================

            try:

                self.crowd_repo.save(

                    verified_count,

                    raw_piezo,

                    raw_ir,

                    raw_sw420,

                    risk_score,

                    status,

                    trend

                )

            except Exception as e:

                logger.error(
                    f"Crowd repository error: {e}"
                )


            # ==================================================
            # 15. SAVE SYSTEM HEALTH
            # ==================================================

            try:

                health = state.get_system_health()


                self.health_repo.save(

                    cpu=health.get(
                        "cpu",
                        0.0
                    ),

                    ram=health.get(
                        "ram",
                        0.0
                    ),

                    db_status=health.get(
                        "database",
                        "ONLINE"
                    ),

                    camera_status=health.get(
                        "camera",
                        "OFFLINE"
                    ),

                    esp_status=health.get(
                        "esp8266",
                        "OFFLINE"
                    ),

                    ai_status=health.get(
                        "ai_model",
                        "READY"
                    ),

                    fps=health.get(
                        "fps",
                        0.0
                    )

                )

            except Exception as e:

                logger.error(
                    f"Health repository error: {e}"
                )


            # ==================================================
            # 16. DATABASE HEALTH
            # ==================================================

            try:

                state.update_health_status(
                    db_status="ONLINE"
                )

            except Exception as e:

                logger.error(
                    f"Health state update error: {e}"
                )


            # ==================================================
            # 17. FINAL RESULT
            # ==================================================

            result = {

                # ------------------------------------------------
                # PEOPLE / CAMERA
                # ------------------------------------------------

                "people": verified_count,

                "verified_count": verified_count,

                "camera_count": camera_count,

                "occupancy": occupancy,

                "unique": unique_people,

                "entry": entry_count,

                "exit": exit_count,


                # ------------------------------------------------
                # SENSOR RAW VALUES
                # ------------------------------------------------

                "piezo": raw_piezo,

                "ir": raw_ir,

                "sw420": raw_sw420,


                # ------------------------------------------------
                # SENSOR DETECTION STATES
                # ------------------------------------------------

                "ir_detected": ir_detected,

                "piezo_detected": piezo_detected,

                "sw420_detected": sw420_detected,


                # ------------------------------------------------
                # SENSOR EVENTS
                # ------------------------------------------------

                "ir_event": ir_event,

                "piezo_event": piezo_event,

                "sw420_event": sw420_event,


                # ------------------------------------------------
                # EVENT COUNTERS
                # ------------------------------------------------

                "ir_event_count":
                    ir_event_count,

                "piezo_event_count":
                    piezo_event_count,

                "sw420_event_count":
                    sw420_event_count,


                # ------------------------------------------------
                # SENSOR VERIFICATION
                # ------------------------------------------------

                "sensor_verified":
                    sensor_verified,

                "sensor_evidence":
                    sensor_evidence,

                "sensor_confidence":
                    sensor_confidence,

                "sensor_passage_count":
                    sensor_passage_count,

                "sensor_connected":
                    sensor_connected,


                # ------------------------------------------------
                # CROWD ANALYTICS
                # ------------------------------------------------

                "risk_score":
                    risk_score,

                "status":
                    status,

                "trend":
                    trend,

                "alert":
                    alert_message

            }


            # ==================================================
            # 18. LOG SENSOR VERIFICATION
            # ==================================================

            if sensor_verified:

                logger.info(

                    "✅ SENSOR-CONFIRMED PASSAGE | "

                    f"Camera Count: {camera_count} | "

                    f"Verified Count: {verified_count} | "

                    f"Evidence: "
                    f"{sensor_evidence}/3 | "

                    f"Confidence: "
                    f"{sensor_confidence}%"

                )


            # ==================================================
            # 19. LOG CROWD ANALYTICS
            # ==================================================

            logger.info(

                "Crowd Analytics | "

                f"People: {verified_count} | "

                f"Risk: {risk_score}% | "

                f"Status: {status}"

            )


            return result


        # ==================================================
        # ERROR HANDLING
        # ==================================================

        except Exception as e:

            logger.exception(
                f"❌ Analytics processing error: {e}"
            )


            # Keep the surveillance pipeline alive
            # if one analytics cycle fails.

            fallback_people = 0

            if "people" in locals():

                fallback_people = people


            return {

                "people":
                    fallback_people,

                "verified_count":
                    fallback_people,

                "camera_count":
                    fallback_people,

                "occupancy":
                    0,

                "unique":
                    0,

                "entry":
                    0,

                "exit":
                    0,

                "piezo":
                    0,

                "ir":
                    0,

                "sw420":
                    0,

                "ir_detected":
                    False,

                "piezo_detected":
                    False,

                "sw420_detected":
                    False,

                "ir_event":
                    False,

                "piezo_event":
                    False,

                "sw420_event":
                    False,

                "ir_event_count":
                    0,

                "piezo_event_count":
                    0,

                "sw420_event_count":
                    0,

                "sensor_verified":
                    False,

                "sensor_evidence":
                    0,

                "sensor_confidence":
                    0,

                "sensor_passage_count":
                    0,

                "sensor_connected":
                    False,

                "risk_score":
                    0,

                "status":
                    "SAFE",

                "trend":
                    "Stable",

                "alert":
                    "No Action Required"

            }