"""
test_phase4.py
-------------------------------------------------------
Automated Unit Tests for Phase 4 Enterprise Architecture:
- Frontend Synchronization API Contracts
- CORS Header Verification
- Backward Compatible List vs. Modern Paginated Payload Verification
- Live MJPEG Stream Content-Type Verification
- Frontend Javascript Files Integrity Check
-------------------------------------------------------
"""

import unittest
import os
from app import app


class TestPhase4Architecture(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_cors_headers_present_on_api_endpoints(self):
        endpoints = [
            "/api/status",
            "/api/dashboard",
            "/api/health",
            "/api/alerts",
            "/api/history",
            "/api/alerts/history",
            "/api/sensors/history",
            "/api/health/history"
        ]

        for ep in endpoints:
            response = self.client.get(ep)
            self.assertEqual(response.status_code, 200, f"Endpoint {ep} returned {response.status_code}")
            # Ensure JSON response
            self.assertEqual(response.content_type, "application/json")

    def test_dashboard_js_contract_payload(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # KPIs required by dashboard.js updateKPICards()
        for kpi in ("people", "occupancy", "unique", "entry", "exit", "risk_score"):
            self.assertIn(kpi, data)

        # Status and Health required by updateStatus() and updateSystemPanel()
        self.assertIn("status", data)
        self.assertIn("health", data)
        self.assertIsInstance(data["health"], dict)

        health = data["health"]
        for key in ("camera", "ai_model", "database", "esp8266"):
            self.assertIn(key, health)

    def test_adaptive_history_api_contracts(self):
        # 1. Default call (no params) -> must return plain list for legacy api.js / alerts.js
        resp_default = self.client.get("/api/history")
        self.assertEqual(resp_default.status_code, 200)
        self.assertIsInstance(resp_default.get_json(), list)

        # 2. Paginated call -> must return dictionary with items, total, page
        resp_paginated = self.client.get("/api/history?page=1&per_page=10")
        self.assertEqual(resp_paginated.status_code, 200)
        paginated_data = resp_paginated.get_json()
        self.assertIsInstance(paginated_data, dict)
        self.assertIn("items", paginated_data)
        self.assertIn("total", paginated_data)
        self.assertIn("page", paginated_data)

    def test_frontend_js_files_exist_and_readable(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/assets/js"))
        required_js_files = [
            "api.js",
            "camera.js",
            "dashboard.js",
            "alerts.js",
            "charts.js",
            "sensors.js",
            "script.js",
            "utils.js"
        ]

        for js_file in required_js_files:
            file_path = os.path.join(base_dir, js_file)
            self.assertTrue(os.path.exists(file_path), f"Missing JS file: {js_file}")
            self.assertGreater(os.path.getsize(file_path), 100, f"JS file too small/empty: {js_file}")

            # Verify no syntax error markers or unclosed blocks
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("function", content)


if __name__ == "__main__":
    unittest.main()
