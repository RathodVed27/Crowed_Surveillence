"""
sensor_service.py
--------------------------------------------------
Enterprise Sensor Service

Manages:
- ESP8266 serial sensor reader
- Piezo sensor
- IR sensor
- SW420 vibration sensor
- SensorRepository
- Centralized SystemState

Internal representation:
    IR    -> 0 / 1
    SW420 -> 0 / 1

Dashboard representation is handled by frontend.

Author : Ved Rathod
"""

import logging

from sensor_reader import SensorReader
from repositories.sensor_repository import SensorRepository
from models.state import state


logger = logging.getLogger(
    "AI_Surveillance.SensorService"
)


class SensorService:

    def __init__(self):

        self.sensor = None

        self.repository = SensorRepository()


    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.sensor is None:

            self.sensor = SensorReader()

            logger.info(
                "✅ Sensor Service Started"
            )


    # =====================================================
    # READ
    # =====================================================

    def read(self):

        if self.sensor is None:

            raise Exception(
                "Sensor Service Not Started"
            )


        # -------------------------------------------------
        # Read ESP8266
        # -------------------------------------------------

        data = self.sensor.read()


        # -------------------------------------------------
        # Piezo
        # -------------------------------------------------

        piezo = data.get(
            "piezo",
            0
        )

        try:

            piezo = int(piezo)

        except (ValueError, TypeError):

            piezo = 0


        # -------------------------------------------------
        # Sensor detection states
        #
        # INTERNAL VALUES MUST REMAIN NUMERIC
        # because state.py expects int().
        # -------------------------------------------------

        ir_detected = bool(
            data.get(
                "ir_detected",
                False
            )
        )


        piezo_detected = bool(
            data.get(
                "piezo_detected",
                False
            )
        )


        sw420_detected = bool(
            data.get(
                "sw420_detected",
                False
            )
        )


        # -------------------------------------------------
        # Convert detection states to internal 0/1
        # -------------------------------------------------

        ir_value = 1 if ir_detected else 0

        sw420_value = 1 if sw420_detected else 0


        # -------------------------------------------------
        # Connection
        # -------------------------------------------------

        connected = bool(
            data.get(
                "connected",
                False
            )
        )


        # -------------------------------------------------
        # Events
        # -------------------------------------------------

        ir_event = bool(
            data.get(
                "ir_event",
                False
            )
        )


        piezo_event = bool(
            data.get(
                "piezo_event",
                False
            )
        )


        sw420_event = bool(
            data.get(
                "sw420_event",
                False
            )
        )


        # -------------------------------------------------
        # Event counters
        # -------------------------------------------------

        ir_event_count = data.get(
            "ir_event_count",
            0
        )

        piezo_event_count = data.get(
            "piezo_event_count",
            0
        )

        sw420_event_count = data.get(
            "sw420_event_count",
            0
        )


        # =================================================
        # UPDATE CENTRAL STATE
        # =================================================

        try:

            state.update_sensors(

                piezo=piezo,

                # IMPORTANT:
                # state.py expects integers
                ir=ir_value,

                sw420=sw420_value,

                connected=connected

            )

        except Exception as e:

            logger.error(
                f"State sensor update error: {e}"
            )


        # =================================================
        # DATABASE
        # =================================================

        try:

            self.repository.save(

                piezo,

                ir_value,

                sw420_value,

                connected

            )

            state.update_health_status(
                db_status="ONLINE"
            )


        except Exception as e:

            state.update_health_status(
                db_status="ERROR"
            )

            logger.error(
                f"Sensor repository error: {e}"
            )


        # =================================================
        # RETURN DATA
        # =================================================
        #
        # Keep BOTH:
        #
        # Numeric values -> backend compatibility
        #
        # Detection states -> meaningful frontend display
        #
        # =================================================

        return {

            # ---------------------------------------------
            # Numeric backend values
            # ---------------------------------------------

            "piezo": piezo,

            "ir": ir_value,

            "sw420": sw420_value,


            # ---------------------------------------------
            # Human-readable detection states
            # ---------------------------------------------

            "ir_detected": ir_detected,

            "piezo_detected": piezo_detected,

            "sw420_detected": sw420_detected,


            # ---------------------------------------------
            # One-shot events
            # ---------------------------------------------

            "ir_event": ir_event,

            "piezo_event": piezo_event,

            "sw420_event": sw420_event,


            # ---------------------------------------------
            # Event counters
            # ---------------------------------------------

            "ir_event_count":
                ir_event_count,

            "piezo_event_count":
                piezo_event_count,

            "sw420_event_count":
                sw420_event_count,


            # ---------------------------------------------
            # Connection
            # ---------------------------------------------

            "connected": connected

        }


    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        if self.sensor is not None:

            try:

                self.sensor.close()

            except Exception as e:

                logger.warning(
                    f"Sensor close error: {e}"
                )

            finally:

                self.sensor = None

                logger.info(
                    "🛑 Sensor Service Stopped"
                )