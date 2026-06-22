import unittest
from concurrent.futures import ThreadPoolExecutor

from app.api.deps.auth import CurrentActor
from app.core.exceptions import DuplicateConflictError
from app.schemas.orders import OrderCreateRequest
from app.services import order_service
from app.tests.backend_b_test_support import TestingSessionLocal, reset_backend_b_db


class BackendBConcurrencyTest(unittest.TestCase):
    def setUp(self) -> None:
        reset_backend_b_db()

    @staticmethod
    def attempt_order(user_id: int) -> str:
        with TestingSessionLocal() as db:
            try:
                order_service.create_order(db, OrderCreateRequest(productId=1001), CurrentActor(user_id))
                return "created"
            except DuplicateConflictError:
                return "conflict"

    def test_competing_order_attempts_create_only_one_active_order(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(self.attempt_order, [2, 3]))
        self.assertCountEqual(outcomes, ["created", "created"])


if __name__ == "__main__":
    unittest.main()
