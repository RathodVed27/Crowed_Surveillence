"""
state.py
-------------------------------------------------------
Enterprise Centralized State Manager (SystemState)
Stores real-time data shared by all services with thread-safe
locking, real-time System Health metrics, and Heatmap Frame buffer.
-------------------------------------------------------
Author : Ved Rathod (Refactored)
"""

import threading
import time
from datetime import datetime
import json
import os

try:
    import psutil
except ImportError:
    psutil = None


class SystemState:
    """
    Thread-safe Centralized State Manager for AI Crowd Surveillance System.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # -------------------------------
        # Camera & Pipeline Metadata
        # -------------------------------
        self.camera_connected = False
        self.fps = 0.0

        # -------------------------------
        # Crowd Information
        # -------------------------------
        self.people_count = 0
        self.unique_people = 0
        self.current_occupancy = 0
        self.entry_count = 0
        self.exit_count = 0

        # -------------------------------
        # Detection & Frames
        # -------------------------------
        self.people = []
        self._frame = None
        self._heatmap_frame = None

        # -------------------------------
        # Sensor Values
        # -------------------------------
        self.piezo = 0
        self.ir = 0
        self.sw420 = 0

        # -------------------------------
        # AI Analytics
        # -------------------------------
        self.risk_score = 0
        self.crowd_status = "SAFE"
        self.trend = "Stable"
        self.alert_message = "No Action Required"

        # -------------------------------
        # Alerts History (In-Memory Buffer)
        # -------------------------------
        self.alerts = []

        # -------------------------------
        # System Health
        # -------------------------------
        self.database_status = "ONLINE"
        self.camera_status = "OFFLINE"
        self.esp8266_status = "OFFLINE"
        self.ai_model_status = "READY"
        self.network_status = "ONLINE"

    # ------------------------------------
    # Thread-Safe Setters / Updaters
    # ------------------------------------

    def update_crowd(self, people_count, occupancy, unique_people, entry_count, exit_count, people_list=None):
        with self._lock:
            self.people_count = int(people_count)
            self.current_occupancy = int(occupancy)
            self.unique_people = int(unique_people)
            self.entry_count = int(entry_count)
            self.exit_count = int(exit_count)
            if people_list is not None:
                self.people = people_list

    def update_sensors(self, piezo, ir, sw420, connected=False):
        with self._lock:
            self.piezo = int(piezo)
            self.ir = int(ir)
            self.sw420 = int(sw420)
            self.esp8266_status = "ONLINE" if connected else "OFFLINE"

    def update_analytics(self, risk_score, status, trend, alert_message=""):
        with self._lock:
            self.risk_score = int(risk_score)
            self.crowd_status = str(status)
            self.trend = str(trend)
            if alert_message:
                self.alert_message = str(alert_message)

    def set_frame(self, frame):
        with self._lock:
            self._frame = frame

    def get_frame(self):
        with self._lock:
            return self._frame

    def set_heatmap_frame(self, frame):
        with self._lock:
            self._heatmap_frame = frame

    def get_heatmap_frame(self):
        with self._lock:
            return self._heatmap_frame

    def add_alert(self, level, message):
        with self._lock:
            alert_entry = {
                "id": len(self.alerts) + 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "level": level,
                "message": message
            }
            self.alerts.insert(0, alert_entry)
            # keep max 100 alerts in memory
            if len(self.alerts) > 100:
                self.alerts.pop()

    def update_health_status(self, camera_connected=None, db_status=None, ai_status=None, fps=None):
        with self._lock:
            if camera_connected is not None:
                self.camera_connected = camera_connected
                self.camera_status = "ONLINE" if camera_connected else "OFFLINE"
            if db_status is not None:
                self.database_status = db_status
            if ai_status is not None:
                self.ai_model_status = ai_status
            if fps is not None:
                self.fps = round(float(fps), 1)

    # ------------------------------------
    # System Health Metrics Calculation
    # ------------------------------------

    def get_system_health(self):
        cpu_usage = 0.0
        ram_usage = 0.0
        if psutil:
            try:
                cpu_usage = psutil.cpu_percent(interval=None)
                ram_usage = psutil.virtual_memory().percent
            except Exception:
                pass

        with self._lock:
            return {
                "cpu": cpu_usage,
                "ram": ram_usage,
                "database": self.database_status,
                "camera": self.camera_status,
                "esp8266": self.esp8266_status,
                "ai_model": self.ai_model_status,
                "network": self.network_status,
                "fps": self.fps,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    # ------------------------------------
    # Serialization (Clean JSON for API)
    # ------------------------------------

    def to_dict(self):
        """
        Returns clean, standardized JSON-serializable dictionary for /api/status.
        Consistent naming: people, occupancy, unique, entry, exit, risk_score,
        status, trend, piezo, ir, sw420.
        """
        with self._lock:
            return {
                "people": self.people_count,
                "occupancy": self.current_occupancy,
                "unique": self.unique_people,
                "entry": self.entry_count,
                "exit": self.exit_count,
                "piezo": self.piezo,
                "ir": self.ir,
                "sw420": self.sw420,
                "risk_score": self.risk_score,
                "status": self.crowd_status,
                "trend": self.trend,
                "alert": self.alert_message,
                "fps": self.fps,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "health": {
                    "database": self.database_status,
                    "camera": self.camera_status,
                    "esp8266": self.esp8266_status,
                    "ai_model": self.ai_model_status,
                    "network": self.network_status
                }
            }

    def get_dashboard_payload(self):
        """
        Consolidated clean JSON payload for /api/dashboard.
        Includes top-level KPIs and nested status/health/alerts.
        """
        status_dict = self.to_dict()
        health_dict = self.get_system_health()
        with self._lock:
            alerts_copy = list(self.alerts[:15])

        payload = dict(status_dict)
        payload.update({
            "status": status_dict,
            "health": health_dict,
            "alerts": alerts_copy,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return payload

    def get_alerts(self):
        with self._lock:
            return list(self.alerts)

    # ------------------------------------
    # Reset State
    # ------------------------------------

    def reset(self):
        with self._lock:
            self.people_count = 0
            self.unique_people = 0
            self.current_occupancy = 0
            self.entry_count = 0
            self.exit_count = 0
            self.people = []
            self._frame = None
            self._heatmap_frame = None
            self.piezo = 0
            self.ir = 0
            self.sw420 = 0
            self.risk_score = 0
            self.crowd_status = "SAFE"
            self.trend = "Stable"
            self.alerts.clear()


# -------------------------------------------------
# Global Shared State Instance
# -------------------------------------------------

state = SystemState()