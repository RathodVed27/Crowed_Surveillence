"""
alert_repository.py
-------------------------------------------------
Enterprise Repository for Emergency & High Alerts
Supports persistence, paginated query, and time-range filter.
-------------------------------------------------
Author : Ved Rathod (Refactored)
"""

from database import CrowdDatabase


class AlertRepository:
    """
    Repository layer for alerts table.
    """

    def __init__(self, db=None):
        self.db = db if db is not None else CrowdDatabase()

    def save(self, level, message):
        self.db.save_alert(level, message)

    def get_recent(self, limit=50):
        result = self.db.query_paginated("alerts", page=1, per_page=limit, time_range="all")
        return [self._row_to_dict(row) for row in result["items"]]

    def get_paginated(self, page=1, per_page=50, time_range="all", level_filter=None):
        result = self.db.query_paginated(
            "alerts",
            page=page,
            per_page=per_page,
            time_range=time_range,
            filter_col="level" if level_filter else None,
            filter_val=level_filter
        )
        result["items"] = [self._row_to_dict(row) for row in result["items"]]
        return result

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "timestamp": row[1],
            "level": row[2],
            "message": row[3]
        }

    def close(self):
        self.db.close()