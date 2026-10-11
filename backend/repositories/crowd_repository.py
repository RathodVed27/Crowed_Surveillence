"""
crowd_repository.py
-------------------------------------------------
Enterprise Repository for Crowd Surveillance Logs
Supports clean OOP persistence, recent query, and
paginated & time-filtered analytical query.
-------------------------------------------------
Author : Ved Rathod (Refactored)
"""

from database import CrowdDatabase


class CrowdRepository:
    """
    Repository layer for crowd_log table.
    """

    def __init__(self, db=None):
        self.db = db if db is not None else CrowdDatabase()

    def save(
        self,
        people,
        piezo,
        ir,
        sw420,
        risk_score,
        crowd_status,
        trend
    ):
        self.db.save_crowd_data(
            people,
            piezo,
            ir,
            sw420,
            risk_score,
            crowd_status,
            trend
        )

    def latest(self):
        row = self.db.latest_data()
        if not row:
            return None
        return self._row_to_dict(row)

    def get_recent(self, limit=50):
        """
        Returns a list of recent crowd history records as dictionaries.
        """
        records = self.db.get_recent_data(limit=limit)
        return [self._row_to_dict(row) for row in records]

    def get_paginated(self, page=1, per_page=50, time_range="all"):
        """
        Returns paginated dictionary payload with timestamp range filtering.
        """
        result = self.db.query_paginated("crowd_log", page=page, per_page=per_page, time_range=time_range)
        result["items"] = [self._row_to_dict(row) for row in result["items"]]
        return result

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "timestamp": row[1],
            "people": row[2],
            "piezo": row[3],
            "ir": row[4],
            "sw420": row[5],
            "risk_score": row[6],
            "status": row[7],
            "trend": row[8]
        }

    def close(self):
        self.db.close()