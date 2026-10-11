"""
sensor_repository.py
-------------------------------------------------
Enterprise Repository for ESP8266 Hardware Sensor Logs
Supports persistence, paginated query, and time-range filtering.
-------------------------------------------------
Author : Ved Rathod (Refactored)
"""

from database import CrowdDatabase


class SensorRepository:
    """
    Repository layer for sensor_log table.
    """

    def __init__(self, db=None):
        self.db = db if db is not None else CrowdDatabase()

    def save(self, piezo, ir, sw420, connected):
        self.db.save_sensor_data(piezo, ir, sw420, connected)

    def get_recent(self, limit=50):
        result = self.db.query_paginated("sensor_log", page=1, per_page=limit, time_range="all")
        return [self._row_to_dict(row) for row in result["items"]]

    def get_paginated(self, page=1, per_page=50, time_range="all"):
        result = self.db.query_paginated("sensor_log", page=page, per_page=per_page, time_range=time_range)
        result["items"] = [self._row_to_dict(row) for row in result["items"]]
        return result

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "timestamp": row[1],
            "piezo": row[2],
            "ir": row[3],
            "sw420": row[4],
            "connected": bool(row[5])
        }

    def close(self):
        self.db.close()
