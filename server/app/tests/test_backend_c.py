from __future__ import annotations

import sys
from pathlib import Path
import unittest

from fastapi.testclient import TestClient


SERVER_ROOT = Path(__file__).resolve().parents[2]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app.main import app  # noqa: E402


class BackendCIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_report_flow(self) -> None:
        response = self.client.post(
            "/api/reports",
            json={"targetType": "product", "targetId": 1001, "reason": "测试举报"},
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["code"], 0)
        self.assertEqual(payload["data"]["status"], "open")
        self.assertEqual(payload["data"]["targetType"], "product")

        report_id = payload["data"]["id"]
        response = self.client.get(f"/api/reports/{report_id}")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["id"], report_id)
        self.assertEqual(payload["data"]["reason"], "测试举报")

        response = self.client.post(
            "/api/appeals",
            json={"targetType": "report", "targetId": report_id, "reason": "申诉测试"},
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["data"]["submitted"])

    def test_admin_report_queue_and_handle(self) -> None:
        response = self.client.get("/api/admin/reports")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("list", payload["data"])
        self.assertIn("page", payload["data"])

        response = self.client.post(
            "/api/admin/reports/7001/handle",
            json={"action": "warning", "reason": "处理备注"},
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["reportId"], 7001)
        self.assertEqual(payload["data"]["action"], "warning")

    def test_statistics_and_logs(self) -> None:
        response = self.client.get("/api/admin/stats/overview")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["reports"], 3)

        response = self.client.get("/api/admin/stats/products")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("series", payload["data"])
        self.assertIn("total", payload["data"])

        response = self.client.get("/api/admin/stats/trades")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("series", payload["data"])

        response = self.client.get("/api/admin/stats/users")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("series", payload["data"])

        response = self.client.get("/api/admin/logs")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(payload["data"]["page"]["total"], 0)
        self.assertGreaterEqual(len(payload["data"]["list"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)