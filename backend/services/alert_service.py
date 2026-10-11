"""
alert_service.py
-------------------------------------------------------
Enterprise Alert Service
Monitors analytics crowd status, saves alerts to database,
and manages global alert notifications in SystemState.
-------------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import logging
from repositories.alert_repository import AlertRepository
from models.state import state

logger = logging.getLogger("AI_Surveillance.AlertService")


class AlertService:
    """
    Evaluates crowd status changes and logs alerts for HIGH and EMERGENCY levels.
    """

    def __init__(self):
        self.repository = AlertRepository()
        self.last_status = None
        logger.info("✅ Alert Service Started")

    def process(self, analytics_result):
        status = analytics_result.get("status", "SAFE")
        message = analytics_result.get("alert", "No Action Required")

        # Avoid spamming duplicate alerts for same status level unless EMERGENCY
        if status == self.last_status and status != "EMERGENCY":
            return

        self.last_status = status

        if status in ["HIGH", "EMERGENCY"]:
            try:
                self.repository.save(status, message)
                state.update_health_status(db_status="ONLINE")
            except Exception as e:
                state.update_health_status(db_status="ERROR")
                logger.error(f"❌ Error saving alert to database: {e}")

            state.add_alert(status, message)
            logger.warning(f"🚨 ALERT REGISTERED : {status} - {message}")

    def get_alerts(self):
        return state.get_alerts()

    def clear(self):
        state.reset()

    def stop(self):
        try:
            self.repository.close()
        except Exception:
            pass
        logger.info("✅ Alert Service Stopped")