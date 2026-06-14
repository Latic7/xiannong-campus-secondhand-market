import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.models.product import Product
from app.tests.backend_b_test_support import (
    TestingSessionLocal,
    auth_header,
    clear_db_override,
    install_db_override,
    reset_backend_b_db,
)


class BackendBContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        install_db_override()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        clear_db_override()

    def setUp(self) -> None:
        reset_backend_b_db()

    def assert_api_ok(self, response, status_code: int = 200):
        self.assertEqual(response.status_code, status_code, response.text)
        body = response.json()
        for key in ("code", "message", "data", "requestId", "timestamp"):
            self.assertIn(key, body)
        return body["data"]

    def test_product_order_review_flow(self) -> None:
        products = self.assert_api_ok(self.client.get("/api/products", params={"page": 1, "size": 10}))
        self.assertEqual(products["page"]["total"], 1)

        created = self.assert_api_ok(
            self.client.post(
                "/api/products",
                headers=auth_header(1),
                json={"title": "Test product", "price": 12.5, "categoryId": 9, "images": []},
            )
        )
        product_id = created["id"]
        self.assertEqual(created["ownerId"], 1)
        self.assertEqual(created["status"], "pending")

        with TestingSessionLocal() as db:
            persisted = db.get(Product, product_id)
            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.title, "Test product")

        order = self.assert_api_ok(
            self.client.post("/api/orders", headers=auth_header(2), json={"productId": 1001, "remark": "meet tonight"})
        )
        order_id = order["id"]
        self.assertEqual(order["status"], "reserved")

        confirmed = self.assert_api_ok(
            self.client.post(f"/api/orders/{order_id}/seller-confirm", headers=auth_header(1))
        )
        self.assertEqual(confirmed["status"], "confirmed")

        completed = self.assert_api_ok(
            self.client.post(f"/api/orders/{order_id}/complete", headers=auth_header(2))
        )
        self.assertEqual(completed["status"], "completed")

        review = self.assert_api_ok(
            self.client.post(
                f"/api/orders/{order_id}/reviews",
                headers=auth_header(2),
                json={"score": 5, "content": "smooth trade"},
            )
        )
        self.assertEqual(review["orderId"], order_id)

    def test_not_found_uses_unified_error_response(self) -> None:
        response = self.client.get("/api/products/999999")
        self.assertEqual(response.status_code, 404)
        body = response.json()
        self.assertEqual(body["code"], 4040)
        self.assertEqual(body["message"], "product not found")
