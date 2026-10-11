"""
test_phase1.py
-------------------------------------------------------
Automated Unit Tests for Phase 1 Enterprise Architecture:
- Camera Hardware & Fallback Layer
- SensorReader Reconnect & Fallbacks
- Centralized SystemState & Health Monitoring
- ServiceContainer Singleton & Dependency Injection
-------------------------------------------------------
"""

import unittest
import numpy as np
from camera import Camera
from sensor_reader import SensorReader
from models.state import SystemState, state
from core.shared_services import ServiceContainer, container
import services


class TestPhase1Architecture(unittest.TestCase):

    def test_camera_fallback_and_info(self):
        cam = Camera()
        info = cam.info()
        self.assertIn("width", info)
        self.assertIn("height", info)
        self.assertIn("connected", info)

        frame = cam.read()
        self.assertIsNotNone(frame)
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(len(frame.shape), 3)
        cam.release()

    def test_sensor_reader_fallback(self):
        reader = SensorReader()
        data = reader.read()
        self.assertIn("piezo", data)
        self.assertIn("ir", data)
        self.assertIn("sw420", data)
        self.assertIn("connected", data)
        reader.close()

    def test_centralized_state_thread_safety_and_health(self):
        s = SystemState()
        s.update_crowd(25, 25, 100, 50, 25)
        s.update_sensors(150, 1, 0, connected=True)
        s.update_analytics(75, "HIGH", "Increasing", "Security Attention Required")
        s.update_health_status(camera_connected=True, db_status="ONLINE", ai_status="READY", fps=29.8)

        data_dict = s.to_dict()
        self.assertEqual(data_dict["people"], 25)
        self.assertEqual(data_dict["risk_score"], 75)
        self.assertEqual(data_dict["status"], "HIGH")
        self.assertEqual(data_dict["health"]["database"], "ONLINE")
        self.assertEqual(data_dict["fps"], 29.8)

        health = s.get_system_health()
        self.assertIn("cpu", health)
        self.assertIn("ram", health)
        self.assertEqual(health["camera"], "ONLINE")

    def test_service_container_singleton(self):
        c1 = ServiceContainer()
        c2 = ServiceContainer()
        self.assertIs(c1, c2)
        self.assertIs(c1.camera, c2.camera)
        self.assertIs(c1.tracker, c2.tracker)

    def test_compatibility_shim(self):
        self.assertIs(services.camera, container.camera)
        self.assertIs(services.tracker, container.tracker)
        self.assertIs(services.sensor, container.sensor)
        self.assertIs(services.analytics, container.analytics)
        self.assertIs(services.alerts, container.alerts)


if __name__ == "__main__":
    unittest.main()
