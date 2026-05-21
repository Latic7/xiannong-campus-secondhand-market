from __future__ import annotations

import unittest


if __name__ == "__main__":
    from app.tests.test_backend_c import BackendCIntegrationTest

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BackendCIntegrationTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)