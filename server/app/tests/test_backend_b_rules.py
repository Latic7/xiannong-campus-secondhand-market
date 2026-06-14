import unittest

from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.main import app
from app.models.order import Order
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.review import Review
from app.tests.backend_b_test_support import (
    TestingSessionLocal,
    auth_header,
    clear_db_override,
    engine,
    install_db_override,
    reset_backend_b_db,
)


class BackendBRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        install_db_override()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        clear_db_override()

    def setUp(self) -> None:
        reset_backend_b_db()

    def assert_error(self, response, status_code: int, code: int) -> dict:
        self.assertEqual(response.status_code, status_code, response.text)
        body = response.json()
        self.assertEqual(body["code"], code)
        self.assertIn("message", body)
        return body

    def create_order(self) -> dict:
        response = self.client.post("/api/orders", headers=auth_header(2), json={"productId": 1001})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["data"]

    def confirm_order(self, order_id: int) -> dict:
        response = self.client.post(f"/api/orders/{order_id}/seller-confirm", headers=auth_header(1))
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["data"]

    def test_metadata_contains_backend_b_indexes_and_constraints(self) -> None:
        inspector = inspect(engine)
        self.assertIn("idx_products_category_status_created", {item["name"] for item in inspector.get_indexes("products")})
        self.assertIn("idx_orders_product_status", {item["name"] for item in inspector.get_indexes("orders")})
        self.assertIn(
            "uq_product_images_product_url",
            {item["name"] for item in inspector.get_unique_constraints("product_images")},
        )
        self.assertIn(
            "uq_reviews_order_reviewer",
            {item["name"] for item in inspector.get_unique_constraints("reviews")},
        )

    def test_product_mutations_require_owner_and_valid_state(self) -> None:
        missing_auth = self.client.put("/api/products/1001", json={"title": "x"})
        self.assert_error(missing_auth, 401, 4010)

        forbidden = self.client.put("/api/products/1001", headers=auth_header(2), json={"title": "x"})
        self.assert_error(forbidden, 403, 4030)

        direct_publish = self.client.put("/api/products/1001", headers=auth_header(1), json={"status": "published"})
        self.assert_error(direct_publish, 403, 4030)

        with TestingSessionLocal() as db:
            product = db.get(Product, 1001)
            product.status = "sold"
            db.commit()
        sold = self.client.put("/api/products/1001", headers=auth_header(1), json={"price": 1})
        self.assert_error(sold, 409, 4090)

    def test_admin_review_connects_pending_queue_to_product_state(self) -> None:
        created = self.client.post(
            "/api/products",
            headers=auth_header(1),
            json={"title": "Pending review", "price": 10, "categoryId": 1},
        ).json()["data"]
        pending = self.client.get("/api/admin/products/pending", headers=auth_header(10)).json()["data"]
        self.assertIn(created["id"], {item["id"] for item in pending["list"]})

        reviewed = self.client.post(
            f"/api/admin/products/{created['id']}/review",
            headers=auth_header(10),
            json={"result": "approved", "reason": "ok"},
        )
        self.assertEqual(reviewed.status_code, 200, reviewed.text)
        self.assertEqual(reviewed.json()["data"]["status"], "published")
        detail = self.client.get(f"/api/products/{created['id']}").json()["data"]
        self.assertEqual(detail["status"], "published")

    def test_active_order_locks_product_and_duplicate_order_conflicts(self) -> None:
        self.create_order()

        duplicate = self.client.post("/api/orders", headers=auth_header(3), json={"productId": 1001})
        self.assert_error(duplicate, 409, 4091)

        price = self.client.put("/api/products/1001", headers=auth_header(1), json={"price": 20})
        self.assert_error(price, 409, 4090)

        unlist = self.client.delete("/api/products/1001", headers=auth_header(1))
        self.assert_error(unlist, 409, 4090)

    def test_order_actor_rules_and_idempotency(self) -> None:
        order = self.create_order()
        order_id = order["id"]

        wrong_seller = self.client.post(f"/api/orders/{order_id}/seller-confirm", headers=auth_header(3))
        self.assert_error(wrong_seller, 403, 4030)

        self.assertEqual(self.confirm_order(order_id)["status"], "confirmed")
        self.assertEqual(self.confirm_order(order_id)["status"], "confirmed")

        wrong_buyer = self.client.post(f"/api/orders/{order_id}/complete", headers=auth_header(1))
        self.assert_error(wrong_buyer, 403, 4030)

        complete = self.client.post(f"/api/orders/{order_id}/complete", headers=auth_header(2))
        self.assertEqual(complete.json()["data"]["status"], "completed")
        complete_again = self.client.post(f"/api/orders/{order_id}/complete", headers=auth_header(2))
        self.assertEqual(complete_again.json()["data"]["status"], "completed")

        with TestingSessionLocal() as db:
            self.assertEqual(db.get(Product, 1001).status, "sold")
            self.assertEqual(db.get(Order, order_id).amount, db.get(Product, 1001).price)

    def test_cancel_is_idempotent_and_terminal(self) -> None:
        order_id = self.create_order()["id"]
        cancelled = self.client.post(f"/api/orders/{order_id}/cancel", headers=auth_header(2))
        self.assertEqual(cancelled.json()["data"]["status"], "cancelled")
        cancelled_again = self.client.post(f"/api/orders/{order_id}/cancel", headers=auth_header(1))
        self.assertEqual(cancelled_again.json()["data"]["status"], "cancelled")
        confirm = self.client.post(f"/api/orders/{order_id}/seller-confirm", headers=auth_header(1))
        self.assert_error(confirm, 409, 4090)

    def test_review_requires_completion_and_is_unique(self) -> None:
        order_id = self.create_order()["id"]
        early = self.client.post(
            f"/api/orders/{order_id}/reviews",
            headers=auth_header(2),
            json={"score": 5, "content": "too early"},
        )
        self.assert_error(early, 409, 4090)
        self.confirm_order(order_id)
        self.client.post(f"/api/orders/{order_id}/complete", headers=auth_header(2))

        first = self.client.post(
            f"/api/orders/{order_id}/reviews",
            headers=auth_header(2),
            json={"score": 5, "content": "ok"},
        )
        self.assertEqual(first.status_code, 200, first.text)
        duplicate = self.client.post(
            f"/api/orders/{order_id}/reviews",
            headers=auth_header(2),
            json={"score": 4, "content": "again"},
        )
        self.assert_error(duplicate, 409, 4091)
        with TestingSessionLocal() as db:
            self.assertEqual(db.query(Review).count(), 1)

    def test_image_validation_and_ownership(self) -> None:
        bad_type = self.client.post(
            "/api/products/1001/images",
            headers=auth_header(1),
            files={"file": ("note.txt", b"text", "text/plain")},
        )
        self.assert_error(bad_type, 400, 4000)

        empty = self.client.post(
            "/api/products/1001/images",
            headers=auth_header(1),
            files={"file": ("empty.jpg", b"", "image/jpeg")},
        )
        self.assert_error(empty, 400, 4000)

        forbidden = self.client.post(
            "/api/products/1001/images",
            headers=auth_header(2),
            files={"file": ("cover.jpg", b"image", "image/jpeg")},
        )
        self.assert_error(forbidden, 403, 4030)

        uploaded = self.client.post(
            "/api/products/1001/images",
            headers=auth_header(1),
            files={"file": ("cover.jpg", b"image", "image/jpeg")},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        image_id = uploaded.json()["data"]["imageId"]
        with TestingSessionLocal() as db:
            self.assertIsNotNone(db.get(ProductImage, image_id))

    def test_list_filter_and_sort_remain_compatible(self) -> None:
        response = self.client.get(
            "/api/products",
            params={"keyword": "高数", "categoryId": 1, "sort": "price_desc", "page": 1, "size": 10},
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()["data"]
        self.assertEqual(data["page"]["total"], 1)
        self.assertEqual(data["filters"]["categoryId"], 1)


if __name__ == "__main__":
    unittest.main()
