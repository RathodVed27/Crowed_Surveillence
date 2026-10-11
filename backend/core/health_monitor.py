"""
health_monitor.py
---------------------------------------------------------
AI Crowd Surveillance System — Enterprise System Health Monitor
Implements real-time liveness, readiness, and subsystem metrics
probes for production monitoring (Kubernetes/Docker/Service probers).
---------------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import time
import logging
from typing import Dict, Any
from models.state import state
from database import db
from core.logging_config import get_logger

logger = get_logger("AI_Surveillance.HealthMonitor")

try:
    import psutil
except ImportError:
    psutil = None


class HealthMonitor:
    """
    Centralized health checking engine verifying subsystems:
    - Database responsiveness and query latency
    - Camera hardware connection and FPS
    - ESP8266 COM serial port connection
    - YOLOv8 AI Model inference status
    - System CPU / RAM resource thresholds
    """

    @staticmethod
    def check_database() -> Dict[str, Any]:
        """
        Executes a lightweight query on SQLite to verify write/read responsiveness.
        """
        start_time = time.time()
        try:
            db.execute_query("SELECT 1")
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "ONLINE",
                "latency_ms": latency_ms,
                "healthy": latency_ms < 100.0
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "ERROR",
                "latency_ms": -1,
                "healthy": False,
                "error": str(e)
            }

    @staticmethod
    def check_camera() -> Dict[str, Any]:
        """
        Checks camera stream FPS and connection status.
        """
        fps = state.fps
        status = state.camera_status
        return {
            "status": status,
            "fps": fps,
            "healthy": status == "ONLINE" and fps >= 0.0,
            "is_fallback": status != "ONLINE"
        }

    @staticmethod
    def check_sensors() -> Dict[str, Any]:
        """
        Checks ESP8266 sensor telemetry connection.
        """
        status = state.esp8266_status
        return {
            "status": status,
            "healthy": status in ("CONNECTED", "ONLINE"),
            "fallback_active": status not in ("CONNECTED", "ONLINE")
        }

    @staticmethod
    def check_ai_model() -> Dict[str, Any]:
        """
        Checks YOLOv8 model loading status.
        """
        status = state.ai_model_status
        return {
            "status": status,
            "healthy": status in ("READY", "ACTIVE", "LOADED")
        }

    @staticmethod
    def check_resources() -> Dict[str, Any]:
        """
        Checks host system CPU and RAM usage against safety thresholds.
        """
        cpu_usage = 0.0
        ram_usage = 0.0
        cpu_alert = False
        ram_alert = False

        if psutil:
            try:
                cpu_usage = psutil.cpu_percent(interval=None)
                ram_usage = psutil.virtual_memory().percent
                cpu_alert = cpu_usage >= 85.0
                ram_alert = ram_usage >= 90.0
            except Exception as e:
                logger.warning(f"Failed to read psutil resources: {e}")

        return {
            "cpu_percent": cpu_usage,
            "ram_percent": ram_usage,
            "cpu_alert": cpu_alert,
            "ram_alert": ram_alert,
            "healthy": not (cpu_alert or ram_alert)
        }

    @classmethod
    def get_liveness(cls) -> Dict[str, Any]:
        """
        Kubernetes/Docker liveness probe. Returns immediately if HTTP server is responsive.
        """
        return {
            "status": "ALIVE",
            "service": "AI Crowd Surveillance System",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def get_readiness(cls) -> Dict[str, Any]:
        """
        Kubernetes/Docker readiness probe. Checks database and AI model core readiness.
        """
        db_check = cls.check_database()
        ai_check = cls.check_ai_model()
        cam_check = cls.check_camera()
        sensor_check = cls.check_sensors()
        resource_check = cls.check_resources()

        is_ready = db_check["healthy"] and ai_check["healthy"]

        return {
            "ready": is_ready,
            "status": "READY" if is_ready else "UNAVAILABLE",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "checks": {
                "database": db_check,
                "ai_model": ai_check,
                "camera": cam_check,
                "sensors": sensor_check,
                "resources": resource_check
            }
        }

    @classmethod
    def get_detailed_metrics(cls) -> Dict[str, Any]:
        """
        Comprehensive system health telemetry payload combining state and subsystem probes.
        """
        readiness = cls.get_readiness()
        state_health = state.get_system_health()
        return {
            "status": readiness["status"],
            "ready": readiness["ready"],
            "system_state": state_health,
            "subsystems": readiness["checks"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


# Global singleton monitor
health_monitor = HealthMonitor()
