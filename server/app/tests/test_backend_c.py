from __future__ import annotations

import sys
from pathlib import Path
import unittest

from fastapi.testclient import TestClient


SERVER_ROOT = Path(__file__).resolve().parents[2]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app.db.init_db import reset_db  # noqa: E402
from app.main import app  # noqa: E402
from app.tests.backend_b_test_support import auth_header  # noqa: E402


class BackendCIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def setUp(self) -> None:
        reset_db()
        self.admin_headers = auth_header(10)

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

        # 验证新增字段（createdAt、handleAction 等 OpenAPI 对齐字段）
        self.assertIn("createdAt", payload["data"])
        self.assertIn("handleAction", payload["data"])
        self.assertIn("handleReason", payload["data"])
        self.assertIn("assigneeId", payload["data"])
        self.assertIsNone(payload["data"]["handleAction"])  # 刚创建，尚无处理动作
        self.assertIsNone(payload["data"]["handledAt"])

        response = self.client.post(
            "/api/appeals",
            json={"targetType": "report", "targetId": report_id, "reason": "申诉测试"},
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["data"]["submitted"])

    def test_admin_report_queue_and_handle(self) -> None:
        response = self.client.get("/api/admin/reports", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("list", payload["data"])
        self.assertIn("page", payload["data"])
        # 验证返回字段完整（包含新增的处理动作字段）
        if payload["data"]["list"]:
            item = payload["data"]["list"][0]
            self.assertIn("createdAt", item)
            self.assertIn("handleAction", item)
            self.assertIn("handleReason", item)

        # 处理举报
        response = self.client.post(
            "/api/admin/reports/7001/handle",
            headers=self.admin_headers,
            json={"action": "warning", "reason": "处理备注"},
        )
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["reportId"], 7001)
        self.assertEqual(payload["data"]["action"], "warning")

        # 验证处理后的举报记录包含处理动作字段
        response = self.client.get("/api/reports/7001")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["handleAction"], "warning")
        self.assertEqual(payload["data"]["handleReason"], "处理备注")
        self.assertIsNotNone(payload["data"]["handledAt"])
        self.assertIsNotNone(payload["data"]["assigneeId"])

    def test_admin_reports_filter(self) -> None:
        """测试后台举报队列按 status / target_type 筛选。"""
        # 筛选 status=open
        response = self.client.get("/api/admin/reports?status=open", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        for item in payload["data"]["list"]:
            self.assertEqual(item["status"], "open")

        # 筛选 target_type=user
        response = self.client.get("/api/admin/reports?target_type=user", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        for item in payload["data"]["list"]:
            self.assertEqual(item["targetType"], "user")

    def test_report_not_found(self) -> None:
        """查询不存在的举报应返回 404。"""
        response = self.client.get("/api/reports/99999")
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertIn("code", payload)

    def test_statistics_and_logs(self) -> None:
        response = self.client.get("/api/admin/stats/overview", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["reports"], 2)

        response = self.client.get("/api/admin/stats/products", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("series", payload["data"])
        self.assertIn("total", payload["data"])

        response = self.client.get("/api/admin/stats/trades", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("series", payload["data"])

        response = self.client.get("/api/admin/stats/users", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("series", payload["data"])

        response = self.client.get("/api/admin/logs", headers=self.admin_headers)
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["data"]["page"]["total"], 3)
        self.assertEqual(len(payload["data"]["list"]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
