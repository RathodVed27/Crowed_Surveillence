"""
test_phase3.py
-------------------------------------------------------
Automated Unit Tests for Phase 3 Enterprise Architecture:
- Database Schema & Indexes (crowd_log, alerts, sensor_log, system_health)
- Repository Pattern (Crowd, Alert, Sensor, Health Repositories)
- Pagination & Time-Range Filtering (1h, 24h, 7d, all)
- Paginated & Filtered Flask API Routes
-------------------------------------------------------
"""

import unittest
import sqlite3
from database import CrowdDatabase
from repositories.crowd_repository import CrowdRepository
from repositories.alert_repository import AlertRepository
from repositories.sensor_repository import SensorRepository
from repositories.health_repository import HealthRepository
from app import app
from config import DATABASE_FILE


class TestPhase3Architecture(unittest.TestCase):

    def setUp(self):
        self.db = CrowdDatabase()
        self.client = app.test_client()

    def test_database_tables_and_indexes_exist(self):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Check all 4 tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("crowd_log", tables)
        self.assertIn("alerts", tables)
        self.assertIn("sensor_log", tables)
        self.assertIn("system_health", tables)

        # Check proper indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        self.assertIn("idx_crowd_log_timestamp", indexes)
        self.assertIn("idx_crowd_log_status", indexes)
        self.assertIn("idx_alerts_timestamp", indexes)
        self.assertIn("idx_alerts_level", indexes)
        self.assertIn("idx_sensor_log_timestamp", indexes)
        self.assertIn("idx_system_health_timestamp", indexes)

        conn.close()

    def test_repositories_pagination_and_range_filter(self):
        # 1. Test CrowdRepository
        crowd_repo = CrowdRepository(self.db)
        crowd_repo.save(45, 10, 1, 0, 80, "HIGH", "Increasing")
        paginated_crowd = crowd_repo.get_paginated(page=1, per_page=10, time_range="1h")
        self.assertIn("items", paginated_crowd)
        self.assertIn("total", paginated_crowd)
        self.assertGreaterEqual(paginated_crowd["total"], 1)

        # 2. Test AlertRepository
        alert_repo = AlertRepository(self.db)
        alert_repo.save("HIGH", "Test Alert Level High")
        paginated_alerts = alert_repo.get_paginated(page=1, per_page=10, time_range="24h")
        self.assertIn("items", paginated_alerts)
        self.assertGreaterEqual(paginated_alerts["total"], 1)

        # 3. Test SensorRepository
        sensor_repo = SensorRepository(self.db)
        sensor_repo.save(200, 1, 1, True)
        paginated_sensor = sensor_repo.get_paginated(page=1, per_page=10, time_range="7d")
        self.assertIn("items", paginated_sensor)
        self.assertGreaterEqual(paginated_sensor["total"], 1)

        # 4. Test HealthRepository
        health_repo = HealthRepository(self.db)
        health_repo.save(12.5, 45.0, "ONLINE", "ONLINE", "ONLINE", "READY", 30.1)
        paginated_health = health_repo.get_paginated(page=1, per_page=10, time_range="all")
        self.assertIn("items", paginated_health)
        self.assertGreaterEqual(paginated_health["total"], 1)

    def test_api_paginated_history_endpoints(self):
        # /api/history?page=1&per_page=5&range=24h
        r_history = self.client.get("/api/history?page=1&per_page=5&range=24h")
        self.assertEqual(r_history.status_code, 200)
        data_history = r_history.get_json()
        self.assertIn("items", data_history)
        self.assertIn("total", data_history)
        self.assertEqual(data_history["page"], 1)

        # /api/alerts/history?page=1&per_page=5
        r_alerts = self.client.get("/api/alerts/history?page=1&per_page=5")
        self.assertEqual(r_alerts.status_code, 200)
        data_alerts = r_alerts.get_json()
        self.assertIn("items", data_alerts)

        # /api/sensors/history?page=1&per_page=5
        r_sensors = self.client.get("/api/sensors/history?page=1&per_page=5")
        self.assertEqual(r_sensors.status_code, 200)
        data_sensors = r_sensors.get_json()
        self.assertIn("items", data_sensors)

        # /api/health/history?page=1&per_page=5
        r_health = self.client.get("/api/health/history?page=1&per_page=5")
        self.assertEqual(r_health.status_code, 200)
        data_health = r_health.get_json()
        self.assertIn("items", data_health)


if __name__ == "__main__":
    unittest.main()
