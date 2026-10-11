"""
test_phase2.py
-------------------------------------------------------
Automated Unit Tests for Phase 2 Enterprise Architecture:
- HeatmapService YOLO spatial density generation & MJPEG stream
- Optimized Flask API Endpoints (/api/status, /api/dashboard,
  /api/health, /api/alerts, /api/history, /api/camera, /api/heatmap)
-------------------------------------------------------
"""

import unittest
import numpy as np
from services.heatmap_service import HeatmapService
from models.state import state
from core.shared_services import container
from app import app


class TestPhase2Architecture(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_heatmap_service_generation(self):
        heatmap = HeatmapService()
        heatmap.start()

        people = [
            {"bbox": (100, 100, 180, 300)},
            {"bbox": (400, 200, 480, 400)}
        ]

        colored_frame = heatmap.update(people, frame_shape=(720, 1280, 3))
        self.assertIsNotNone(colored_frame)
        self.assertIsInstance(colored_frame, np.ndarray)
        self.assertEqual(colored_frame.shape, (720, 1280, 3))

        # Check density matrix has accumulated values
        self.assertGreater(np.max(heatmap.density_matrix), 0)

        # Check state buffer
        saved_frame = state.get_heatmap_frame()
        self.assertIsNotNone(saved_frame)
        self.assertEqual(saved_frame.shape, (720, 1280, 3))
        heatmap.stop()

    def test_api_status_endpoint(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # Check required consistent naming keys
        required_keys = [
            "people", "occupancy", "unique", "entry", "exit",
            "risk_score", "status", "trend", "piezo", "ir",
            "sw420", "fps", "health", "timestamp"
        ]
        for key in required_keys:
            self.assertIn(key, data)

    def test_api_dashboard_endpoint(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn("status", data)
        self.assertIn("health", data)
        self.assertIn("alerts", data)
        self.assertIn("timestamp", data)
        self.assertIsInstance(data["alerts"], list)

    def test_api_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        required_health_keys = [
            "cpu", "ram", "database", "camera", "esp8266",
            "ai_model", "network", "fps"
        ]
        for key in required_health_keys:
            self.assertIn(key, data)

    def test_api_alerts_and_history_endpoints(self):
        resp_alerts = self.client.get("/api/alerts")
        self.assertEqual(resp_alerts.status_code, 200)
        self.assertIsInstance(resp_alerts.get_json(), list)

        resp_history = self.client.get("/api/history")
        self.assertEqual(resp_history.status_code, 200)
        self.assertIsInstance(resp_history.get_json(), list)

    def test_api_camera_and_heatmap_stream_generators(self):
        # Verify MJPEG frame generators directly without infinite blocking
        cam_gen = container.camera.generate_frames()
        cam_chunk = next(cam_gen)
        self.assertIn(b"--frame", cam_chunk)
        self.assertIn(b"Content-Type: image/jpeg", cam_chunk)

        heat_gen = container.heatmap.generate_heatmap_frames()
        heat_chunk = next(heat_gen)
        self.assertIn(b"--frame", heat_chunk)
        self.assertIn(b"Content-Type: image/jpeg", heat_chunk)


if __name__ == "__main__":
    unittest.main()
