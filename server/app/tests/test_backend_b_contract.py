import unittest

from fastapi.testclient import TestClient

from app.main import app


class BackendBContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def assert_api_ok(self, response, status_code: int = 200):
        self.assertEqual(response.status_code, status_code, response.text)
        body = response.json()
        for key in ("code", "message", "data", "requestId", "timestamp"):
            self.assertIn(key, body)
        return body["data"]

    def test_product_order_review_flow(self) -> None:
        products = self.assert_api_ok(self.client.get("/api/products", params={"page": 1, "size": 10}))
        self.assertGreaterEqual(products["page"]["total"], 2)
        self.assertIn("list", products)

        created_product = self.assert_api_ok(
            self.client.post(
                "/api/products",
                json={
                    "title": "Test product",
                    "description": "Created by backend B contract test",
                    "price": 12.5,
                    "categoryId": 9,
                    "images": [],
                },
            )
        )
        self.assertEqual(created_product["status"], "pending")
        product_id = created_product["id"]

        updated = self.assert_api_ok(self.client.put(f"/api/products/{product_id}", json={"status": "published"}))
        self.assertTrue(updated["updated"])

        detail = self.assert_api_ok(self.client.get(f"/api/products/{product_id}"))
        self.assertEqual(detail["id"], product_id)
        self.assertEqual(detail["viewCount"], 1)

        upload = self.assert_api_ok(
            self.client.post(
                f"/api/products/{product_id}/images",
                files={"file": ("cover.jpg", b"demo", "image/jpeg")},
            )
        )
        self.assertEqual(upload["productId"], product_id)
        self.assertIn("imageId", upload)

        deleted_image = self.assert_api_ok(
            self.client.delete(f"/api/products/{product_id}/images/{upload['imageId']}")
        )
        self.assertTrue(deleted_image["deleted"])

        order = self.assert_api_ok(self.client.post("/api/orders", json={"productId": 1001, "remark": "meet tonight"}))
        self.assertEqual(order["status"], "reserved")
        order_id = order["id"]

        order_detail = self.assert_api_ok(self.client.get(f"/api/orders/{order_id}"))
        self.assertEqual(order_detail["id"], order_id)

        confirmed = self.assert_api_ok(self.client.post(f"/api/orders/{order_id}/seller-confirm"))
        self.assertEqual(confirmed["status"], "confirmed")

        completed = self.assert_api_ok(self.client.post(f"/api/orders/{order_id}/complete"))
        self.assertEqual(completed["status"], "completed")

        review = self.assert_api_ok(
            self.client.post(f"/api/orders/{order_id}/reviews", json={"score": 5, "content": "smooth trade"})
        )
        self.assertEqual(review["orderId"], order_id)

    def test_not_found_uses_unified_error_response(self) -> None:
        response = self.client.get("/api/products/999999")
        self.assertEqual(response.status_code, 404)
        body = response.json()
        self.assertEqual(body["code"], 4040)
        self.assertEqual(body["message"], "product not found")
        self.assertEqual(body["data"]["productId"], 999999)


if __name__ == "__main__":
    unittest.main()
