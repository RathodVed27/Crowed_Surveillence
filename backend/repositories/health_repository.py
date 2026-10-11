"""
health_repository.py
-------------------------------------------------
Enterprise Repository for System Health History
Tracks CPU, RAM, database, camera, sensor, AI model status,
and pipeline FPS over time.
-------------------------------------------------
Author : Ved Rathod (Refactored)
"""

from database import CrowdDatabase


class HealthRepository:
    """
    Repository layer for system_health table.
    """

    def __init__(self, db=None):
        self.db = db if db is not None else CrowdDatabase()

    def save(self, cpu, ram, db_status, camera_status, esp_status, ai_status, fps):
        self.db.save_system_health(cpu, ram, db_status, camera_status, esp_status, ai_status, fps)

    def get_recent(self, limit=50):
        result = self.db.query_paginated("system_health", page=1, per_page=limit, time_range="all")
        return [self._row_to_dict(row) for row in result["items"]]

    def get_paginated(self, page=1, per_page=50, time_range="all"):
        result = self.db.query_paginated("system_health", page=page, per_page=per_page, time_range=time_range)
        result["items"] = [self._row_to_dict(row) for row in result["items"]]
        return result

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "timestamp": row[1],
            "cpu": round(float(row[2]), 1),
            "ram": round(float(row[3]), 1),
            "database": row[4],
            "camera": row[5],
            "esp8266": row[6],
            "ai_model": row[7],
            "fps": round(float(row[8]), 1)
        }

    def close(self):
        self.db.close()
