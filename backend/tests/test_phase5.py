"""
test_phase5.py
-------------------------------------------------------
Automated Unit Tests for Phase 5 Enterprise Architecture:
- Production Liveness & Readiness Probes (/api/health/live, /api/health/ready)
- Deep Subsystem Metrics Probe (/api/health/metrics)
- HealthMonitor Singleton functionality & Database latency checks
- Enterprise Rotating Logging setup (logging_config.py)
- Requirements dependencies verification
-------------------------------------------------------
"""

import os
import unittest
import logging
from app import app
from core.health_monitor import health_monitor
from core.logging_config import setup_logging, get_logger


class TestPhase5Architecture(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_logging_config_and_rotating_handler(self):
        log_file = "logs/test_surveillance.log"
        logger = setup_logging(log_file=log_file, level=logging.INFO)
        self.assertIsInstance(logger, logging.Logger)
        logger.info("Test logging message for Phase 5 verification.")
        
        # Verify log file created
        self.assertTrue(os.path.exists(log_file))

    def test_health_monitor_probes(self):
        liveness = health_monitor.get_liveness()
        self.assertEqual(liveness["status"], "ALIVE")
        self.assertIn("timestamp", liveness)

        readiness = health_monitor.get_readiness()
        self.assertIn("ready", readiness)
        self.assertIn("status", readiness)
        self.assertIn("checks", readiness)
        
        checks = readiness["checks"]
        for sub in ("database", "ai_model", "camera", "sensors", "resources"):
            self.assertIn(sub, checks)

        # Check DB latency metric present
        self.assertIn("latency_ms", checks["database"])

    def test_kubernetes_probes_endpoints(self):
        # 1. Liveness
        resp_live = self.client.get("/api/health/live")
        self.assertEqual(resp_live.status_code, 200)
        self.assertEqual(resp_live.get_json()["status"], "ALIVE")

        # 2. Readiness
        resp_ready = self.client.get("/api/health/ready")
        self.assertIn(resp_ready.status_code, [200, 503])
        data_ready = resp_ready.get_json()
        self.assertIn("ready", data_ready)

        # 3. Deep metrics
        resp_metrics = self.client.get("/api/health/metrics")
        self.assertEqual(resp_metrics.status_code, 200)
        data_metrics = resp_metrics.get_json()
        self.assertIn("subsystems", data_metrics)
        self.assertIn("system_state", data_metrics)

    def test_requirements_files_exist_and_complete(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        root_req = os.path.join(base_dir, "requirements.txt")
        backend_req = os.path.join(base_dir, "backend/requirements.txt")

        self.assertTrue(os.path.exists(root_req), "Root requirements.txt missing")
        self.assertTrue(os.path.exists(backend_req), "backend/requirements.txt missing")

        with open(root_req, "r", encoding="utf-8") as f:
            content = f.read().lower()
            for pkg in ("flask", "waitress", "opencv-python", "ultralytics", "psutil", "pyserial"):
                self.assertIn(pkg, content, f"Missing dependency {pkg} in requirements.txt")


if __name__ == "__main__":
    unittest.main()
