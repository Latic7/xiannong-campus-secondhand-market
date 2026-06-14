# Backend B Domain Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Backend B's in-memory/hard-coded product and order flows with persistent SQLAlchemy implementations that enforce ownership, state transitions, idempotency, image validation, and transaction-safe order creation.

**Architecture:** Preserve the existing router-service-CRUD layering. FastAPI routers inject a database session and authenticated actor; services own business rules and transaction boundaries; CRUD modules perform SQLAlchemy queries and serialize database entities into the existing OpenAPI camelCase response shape.

**Tech Stack:** Python 3.12, FastAPI 0.116.1, Pydantic 2.11.7, SQLAlchemy 2.0.36, PyMySQL 1.1.1, unittest, SQLite test database, MySQL 8.0 integration database.

---

## Baseline

- Branch: `feature/backend-b-followup-migration`, based on `origin/dev` commit `67d6f7e`.
- Existing full test run: 3 Backend C tests pass; 2 Backend B tests fail because the latest `dev` routes contain hard-coded responses and undefined service references.
- Preserve all unrelated untracked user files.

## File Structure

- Create `server/app/api/deps/auth.py`: shared current-actor dependency using Backend A's JWT contract.
- Create `server/app/models/product_image.py`: persisted image URL entity.
- Create `server/app/models/review.py`: persisted order review entity.
- Modify `server/app/models/product.py`: product query indexes.
- Modify `server/app/models/order.py`: active-order query index.
- Modify `server/app/models/__init__.py`: register new models.
- Replace `server/app/crud/product.py`: SQLAlchemy product/image repository and serializers.
- Replace `server/app/crud/order.py`: SQLAlchemy order/review repository and serializers.
- Replace `server/app/services/product_service.py`: ownership, state, active-order, and image rules.
- Replace `server/app/services/order_service.py`: order transaction, state machine, actor checks, and idempotency.
- Replace `server/app/api/routers/products.py`: database/actor injection and file-content validation handoff.
- Replace `server/app/api/routers/orders.py`: database/actor injection.
- Modify `server/app/core/exceptions.py`: forbidden, validation, and duplicate conflict business errors.
- Modify `server/app/db/schema.sql`: Backend B indexes and unique constraints.
- Modify `server/app/tests/test_backend_b_contract.py`: persistent authenticated phase-one regression.
- Create `server/app/tests/test_backend_b_rules.py`: phase-two state, permission, idempotency, image, and persistence tests.
- Create `server/app/tests/test_backend_b_concurrency.py`: transaction/concurrency behavior tests.
- Create `docs/qa/backend-b-state-machine.md`.
- Create `docs/qa/backend-b-idempotency-conflict-tests.md`.
- Create `docs/qa/backend-b-index-review.md`.
- Create `docs/qa/backend-b-demo-notes.md`.

### Task 1: Build Isolated Backend B Test Harness and Actor Dependency

**Files:**
- Create: `server/app/api/deps/auth.py`
- Modify: `server/app/api/deps/__init__.py`
- Modify: `server/app/core/exceptions.py`
- Modify: `server/app/tests/test_backend_b_contract.py`
- Create: `server/app/tests/backend_b_test_support.py`

- [ ] **Step 1: Write failing authenticated persistence test**

Add a test support module that creates a temporary SQLite engine, overrides
`get_db`, overrides `get_current_actor`, resets metadata, and seeds users 1, 2,
and 10. Update the contract test so mutation requests run as actor 1 or 2 and
assert a created product can be read through a new session.

- [ ] **Step 2: Run test and verify RED**

Run:

```powershell
conda run -n xiannong python -m unittest app.tests.test_backend_b_contract -v
```

Expected: FAIL because `get_current_actor` does not exist and Backend B routes
do not use database sessions.

- [ ] **Step 3: Implement shared actor dependency and error types**

Implement:

```python
@dataclass(frozen=True)
class CurrentActor:
    user_id: int
    nickname: str = ""

def get_current_actor(authorization: str | None = Header(default=None)) -> CurrentActor:
    # Decode Backend A's HS256 access token and require typ == "access".
```

Add `ForbiddenError` (`403`) and `InvalidRequestError` (`400`) under the
existing `BusinessError` hierarchy.

- [ ] **Step 4: Run focused tests**

Expected: actor dependency tests pass; persistence test still fails because CRUD
is not migrated.

- [ ] **Step 5: Commit**

```powershell
git add server/app/api/deps server/app/core/exceptions.py server/app/tests
git commit -m "test: add backend B database and actor harness"
```

### Task 2: Add Product Image and Review Models and Backend B Indexes

**Files:**
- Create: `server/app/models/product_image.py`
- Create: `server/app/models/review.py`
- Modify: `server/app/models/product.py`
- Modify: `server/app/models/order.py`
- Modify: `server/app/models/__init__.py`
- Modify: `server/app/db/schema.sql`
- Test: `server/app/tests/test_backend_b_rules.py`

- [ ] **Step 1: Write failing model/index tests**

Assert metadata contains `product_images`, `reviews`,
`idx_products_category_status_created`, `idx_orders_product_status`,
`uq_product_images_product_url`, and `uq_reviews_order_reviewer`.

- [ ] **Step 2: Run test and verify RED**

Expected: FAIL because new models and composite indexes are absent.

- [ ] **Step 3: Implement models and indexes**

Define `ProductImage(id, product_id, url, created_at)` and
`Review(id, order_id, product_id, reviewer_id, reviewee_id, score, content,
created_at)`. Add matching SQLAlchemy indexes/unique constraints and align
`schema.sql`.

- [ ] **Step 4: Run focused tests and verify GREEN**

- [ ] **Step 5: Commit**

```powershell
git add server/app/models server/app/db/schema.sql server/app/tests/test_backend_b_rules.py
git commit -m "feat: add backend B persistence models and indexes"
```

### Task 3: Migrate Product and Image CRUD to SQLAlchemy

**Files:**
- Replace: `server/app/crud/product.py`
- Test: `server/app/tests/test_backend_b_rules.py`

- [ ] **Step 1: Write failing product repository tests**

Cover:

- persisted product create/read/list across sessions;
- paging, keyword, category, and price sorting;
- view-count increment;
- image create/list/delete;
- duplicate image URL integrity conflict.

- [ ] **Step 2: Run test and verify RED**

Expected: FAIL because CRUD still uses module-level dictionaries.

- [ ] **Step 3: Implement SQLAlchemy product repository**

Repository functions accept `Session` explicitly and return OpenAPI-compatible
dicts. Use `select`, `func.count`, `offset`, `limit`, and `order_by`. Serialize
`Decimal` to float and timestamps to ISO strings.

- [ ] **Step 4: Run focused tests and verify GREEN**

- [ ] **Step 5: Commit**

```powershell
git add server/app/crud/product.py server/app/tests/test_backend_b_rules.py
git commit -m "feat: persist products and images with SQLAlchemy"
```

### Task 4: Migrate Product Service and Routes with State and Ownership Rules

**Files:**
- Replace: `server/app/services/product_service.py`
- Replace: `server/app/api/routers/products.py`
- Modify: `server/app/schemas/products.py`
- Test: `server/app/tests/test_backend_b_rules.py`

- [ ] **Step 1: Write failing product API rule tests**

Cover:

- create assigns current actor as owner and defaults to pending;
- non-owner update/unlist/image mutation returns `403`;
- sold product mutation returns `409`;
- owner cannot directly publish through product update;
- active order blocks price change and unlisting;
- repeated unlist is idempotent;
- public list/detail still work;
- image extension, MIME, empty file, and 5 MiB limit validation.

- [ ] **Step 2: Run test and verify RED**

- [ ] **Step 3: Implement product service and routes**

Inject `Session` and `CurrentActor` into mutation routes. Keep read routes public.
Read upload bytes once, validate metadata/content, generate a collision-resistant
filename, store a stable URL, and return the existing response shape.

- [ ] **Step 4: Run focused and contract tests**

- [ ] **Step 5: Commit**

```powershell
git add server/app/services/product_service.py server/app/api/routers/products.py server/app/schemas/products.py server/app/tests
git commit -m "feat: enforce persistent product lifecycle rules"
```

### Task 5: Migrate Order and Review CRUD to SQLAlchemy

**Files:**
- Replace: `server/app/crud/order.py`
- Test: `server/app/tests/test_backend_b_rules.py`

- [ ] **Step 1: Write failing order repository tests**

Cover persisted order create/read, active-order query, order row lock query,
status update, review create/read, and duplicate review conflict.

- [ ] **Step 2: Run test and verify RED**

- [ ] **Step 3: Implement SQLAlchemy order repository**

All functions accept `Session`. Provide lock-aware `get_order(..., for_update)`
and active-order queries. Do not commit inside CRUD; services own commits.

- [ ] **Step 4: Run focused tests and verify GREEN**

- [ ] **Step 5: Commit**

```powershell
git add server/app/crud/order.py server/app/tests/test_backend_b_rules.py
git commit -m "feat: persist orders and reviews with SQLAlchemy"
```

### Task 6: Implement Transactional Order State Machine and Idempotency

**Files:**
- Replace: `server/app/services/order_service.py`
- Replace: `server/app/api/routers/orders.py`
- Modify: `server/app/schemas/orders.py`
- Test: `server/app/tests/test_backend_b_rules.py`
- Create: `server/app/tests/test_backend_b_concurrency.py`

- [ ] **Step 1: Write failing order API and concurrency tests**

Cover:

- buyer cannot buy own product;
- competing/duplicate order requests create at most one active order;
- amount remains locked;
- only seller confirms;
- buyer or seller cancels;
- only buyer completes;
- confirm/cancel/complete retries are idempotent;
- illegal terminal-state transitions return `409`;
- completion marks product sold in the same transaction;
- only completed order can be reviewed;
- only buyer reviews;
- duplicate review returns `409`;
- unrelated user cannot read order detail.

- [ ] **Step 2: Run tests and verify RED**

- [ ] **Step 3: Implement transactional services/routes**

Use `with db.begin()` or explicit commit/rollback around each mutation. Lock the
product during order creation and lock order/product during completion. Map
`IntegrityError` to duplicate conflicts without leaking database errors.

- [ ] **Step 4: Run focused tests and verify GREEN**

- [ ] **Step 5: Commit**

```powershell
git add server/app/services/order_service.py server/app/api/routers/orders.py server/app/schemas/orders.py server/app/tests
git commit -m "feat: enforce transactional order state machine"
```

### Task 7: Preserve Cross-Module Regression and MySQL Compatibility

**Files:**
- Modify as needed: `server/app/db/seed.py`
- Modify as needed: `server/app/db/init_db.py`
- Modify as needed: Backend B files from previous tasks
- Test: all `server/app/tests`

- [ ] **Step 1: Run full test suite**

```powershell
conda run -n xiannong python -m unittest discover -s app/tests -v
```

Expected: all Backend B and Backend C tests pass.

- [ ] **Step 2: Run MySQL schema/data smoke test**

Import/use the configured MySQL test database, then exercise product creation,
order creation, confirmation, completion, and review through the API or service
layer.

- [ ] **Step 3: Fix only migration-related regressions**

Do not refactor Backend A/C beyond compatibility fixes required by registered
models, seed data, or shared database setup.

- [ ] **Step 4: Re-run full suite and MySQL smoke**

- [ ] **Step 5: Commit**

```powershell
git add server/app
git commit -m "fix: preserve backend integration after domain migration"
```

### Task 8: Produce Backend B Follow-up Deliverables

**Files:**
- Create: `docs/qa/backend-b-state-machine.md`
- Create: `docs/qa/backend-b-idempotency-conflict-tests.md`
- Create: `docs/qa/backend-b-index-review.md`
- Create: `docs/qa/backend-b-demo-notes.md`

- [ ] **Step 1: Document state and actor rules**

Include product/order transition tables, terminal states, actor permissions, and
HTTP error semantics.

- [ ] **Step 2: Document conflict/concurrency evidence**

Record exact test names and observed outcomes for duplicate order, duplicate
review, repeat state actions, and competing order attempts.

- [ ] **Step 3: Document index review**

Map every retained/added index to its query and note that Backend D owns the
formal full export.

- [ ] **Step 4: Document demo flow**

Provide one main flow and at least two explainable failure flows suitable for
the final presentation.

- [ ] **Step 5: Commit**

```powershell
git add docs/qa
git commit -m "docs: add backend B follow-up evidence"
```

### Task 9: Final Verification and Branch Readiness

**Files:**
- Verify all changed files

- [ ] **Step 1: Run complete automated verification**

```powershell
conda run -n xiannong python -m unittest discover -s app/tests -v
git diff --check origin/dev...HEAD
git status --short --branch
```

- [ ] **Step 2: Verify OpenAPI path compatibility**

Generate `app.openapi()` and assert every Backend B path remains present.

- [ ] **Step 3: Review diff scope**

Confirm no unrelated user files are staged or committed and no Backend A/C
behavior changed beyond necessary compatibility.

- [ ] **Step 4: Prepare merge summary**

Summarize state rules, persistence, test evidence, MySQL evidence, residual
risks, and any Backend D schema-export follow-up.
