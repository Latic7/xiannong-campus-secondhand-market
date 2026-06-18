# Backend B Domain Migration Design

## 1. Goal

Migrate Backend B's product, product-image, order, and review flows from
process-local dictionaries to the existing SQLAlchemy/MySQL infrastructure.
The migration assumes the phase-one main flow is already integration-ready and
focuses on phase-two and phase-three requirements: strict state transitions,
clear conflict responses, idempotency, concurrency safety, query indexes, and
repeatable regression evidence.

## 2. Scope

### Included

- Persist products, product images, orders, and reviews with SQLAlchemy.
- Preserve the current OpenAPI paths and response field names.
- Enforce product and order state transitions.
- Reject duplicate active orders and duplicate reviews.
- Make repeat confirm, cancel, and complete operations idempotent.
- Validate uploaded image metadata and return a stable URL reference.
- Add ownership checks for product and order mutations using the authenticated
  user identity supplied by Backend A.
- Protect order creation with a database transaction and product row lock.
- Review and add indexes needed by Backend B's common queries.
- Add state-machine, conflict, persistence, permission, and concurrency tests.
- Produce Backend B state-machine, conflict-test, index-review, and demo notes.

### Excluded

- Changing authentication token formats or implementing a new login system.
- Changing report, administration, or statistics business logic.
- Implementing object-storage integration; image bytes remain outside the
  database and the API stores/returns a generated URL reference.
- Replacing Backend D's formal full-database export process.
- Adding new public endpoints not already present in the OpenAPI draft.

## 3. Architectural Approach

The existing layering remains:

`router -> service -> CRUD/repository -> SQLAlchemy session -> database`

- Routers receive a SQLAlchemy `Session` through FastAPI dependency injection
  and authenticated actor information through a shared dependency.
- Services own state-machine, ownership, idempotency, and transaction rules.
- CRUD modules perform database queries and mapping only; they do not decide
  whether a transition is allowed.
- SQLAlchemy models describe Backend B tables and indexes.
- API responses continue using the existing `api_ok` and global business-error
  mapping.

Backend B will not keep a runtime fallback to dictionary storage. Tests use an
isolated SQLite database through dependency overrides, while local integration
uses the configured MySQL database.

## 4. Authentication and Ownership

Backend B requires an authenticated actor for mutation endpoints:

- Product creation assigns `owner_id` to the current user.
- Product update, unlist, image upload, and image deletion require the current
  user to own the product.
- Order creation assigns the current user as buyer and rejects self-purchase.
- Seller confirmation requires the current user to be the seller.
- Cancellation is allowed for the related buyer or seller, subject to state.
- Completion is allowed for the buyer.
- Review creation is allowed for the buyer of a completed order.

Read-only product list/detail endpoints remain public. Order detail requires the
current user to be the order's buyer or seller.

The shared actor dependency decodes Backend A's existing access token. Tests
override the dependency directly, so they do not depend on WeChat login.

## 5. Product State Machine

Product statuses remain:

`draft`, `pending`, `published`, `removed`, `sold`

Allowed transitions:

| Current | Allowed target | Reason |
| --- | --- | --- |
| `draft` | `pending`, `removed` | Submit for review or discard |
| `pending` | `published`, `removed` | Administrator review or owner withdrawal |
| `published` | `removed`, `sold` | Owner unlists or completed trade |
| `removed` | `pending` | Owner resubmits for review |
| `sold` | none | Terminal state |

Rules:

- Product creation defaults to `pending`, preserving the phase-one API.
- Owner-facing update cannot set `published` directly. Publishing remains an
  administrative review action.
- A sold product cannot be edited or unlisted.
- Price cannot change while the product has an active `reserved` or
  `confirmed` order.
- Unlisting is rejected while an active order exists.
- Completing an order changes the related product to `sold` in the same
  transaction.

## 6. Order State Machine

Order statuses remain:

`created`, `reserved`, `confirmed`, `completed`, `cancelled`

The existing public create-order endpoint produces `reserved`, because creating
the request reserves the single second-hand product immediately.

Allowed transitions:

| Action | Current | Target | Actor |
| --- | --- | --- | --- |
| Create order | published product, no active order | `reserved` | buyer |
| Seller confirm | `reserved` | `confirmed` | seller |
| Cancel | `reserved`, `confirmed` | `cancelled` | buyer or seller |
| Complete | `confirmed` | `completed` | buyer |
| Review | `completed` | no status change | buyer |

Rules:

- Completed and cancelled orders are terminal.
- Cancelling a reserved/confirmed order makes the product available again by
  keeping its status `published`.
- Order amount is copied from the product price during creation and never
  changes afterwards.
- Only one active (`reserved` or `confirmed`) order may exist per product.

## 7. Idempotency and Conflict Semantics

Operations users may repeat due to double-clicks or retries are idempotent:

- Confirming an already confirmed order returns confirmed success.
- Cancelling an already cancelled order returns cancelled success.
- Completing an already completed order returns completed success.
- Deleting an already removed product returns removed success.

Operations that would create duplicate business records return a clear conflict:

- A second active order for the same product returns HTTP `409`.
- A second review by the same buyer for the same order returns HTTP `409`.
- Uploading the same image URL for the same product returns HTTP `409`.

Illegal state transitions and ownership violations use the existing unified
error envelope. State and duplicate conflicts use `409`; forbidden ownership
uses `403`; missing resources use `404`; invalid image input uses `400`.

## 8. Concurrency and Transaction Boundaries

Order creation is the critical concurrency path:

1. Begin one database transaction.
2. Select the product with `SELECT ... FOR UPDATE`.
3. Verify the product is `published`.
4. Verify the buyer is not the owner.
5. Query for an active order for the product.
6. Insert the reserved order with the current product price.
7. Commit once.

This serializes competing order requests for the same product on MySQL. The
service also maps database integrity conflicts to the same HTTP `409` response.

Confirm, cancel, complete, and review operations update/query the relevant order
inside one transaction. Completion locks both order and product before changing
the order to `completed` and product to `sold`.

## 9. Image Upload Minimum Capability

The endpoint continues accepting one multipart `file`.

Validation:

- Filename is required.
- Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.webp`.
- Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`.
- Empty files are rejected.
- Maximum size is 5 MiB.

The implementation does not introduce object storage. It generates a stable
URL reference under `/static/products/{product_id}/{generated_name}`, stores
that URL in `product_images`, and returns `productId`, `filename`, `imageId`,
and `url`.

## 10. Database Models and Indexes

Backend B uses these existing tables:

- `products`
- `product_images`
- `orders`
- `reviews`

Existing indexes retained:

- `idx_products_status_created`
- `idx_products_owner`
- `idx_products_category`
- `idx_orders_status_created`
- `idx_orders_buyer`
- `idx_orders_seller`
- `idx_orders_product`
- product-image and review lookup indexes

Indexes/constraints added or confirmed:

- `idx_products_category_status_created(category_id, status, created_at)` for
  filtered product lists.
- `idx_orders_product_status(product_id, status)` for active-order checks.
- `uq_product_images_product_url(product_id, url)` for image idempotency.
- `uq_reviews_order_reviewer(order_id, reviewer_id)` for review idempotency.

The SQLAlchemy models and `server/app/db/schema.sql` must remain aligned. Formal
full-database export remains Backend D's responsibility.

## 11. API Compatibility

Public paths remain unchanged:

- `GET/POST /api/products`
- `GET/PUT/DELETE /api/products/{productId}`
- `POST /api/products/{productId}/images`
- `DELETE /api/products/{productId}/images/{imageId}`
- `POST /api/orders`
- `GET /api/orders/{orderId}`
- `POST /api/orders/{orderId}/seller-confirm`
- `POST /api/orders/{orderId}/cancel`
- `POST /api/orders/{orderId}/complete`
- `POST /api/orders/{orderId}/reviews`

Responses continue using camelCase fields defined by the OpenAPI draft. The
router layer keeps response shapes stable while services return persisted data.

## 12. Testing Strategy

Tests follow TDD and use a fresh isolated database per test class.

Required coverage:

- Product persistence survives a new session.
- Product ownership blocks unauthorized update/unlist/image mutation.
- Product state-machine allowed and forbidden transitions.
- Price update and unlist blocked by active order.
- Order amount remains locked after product changes.
- Duplicate active order returns `409`.
- Competing order attempts yield one success and one conflict.
- Confirm, cancel, and complete idempotency.
- Illegal order transitions return `409`.
- Completion marks the product sold atomically.
- Duplicate review returns `409`.
- Review before completion returns `409`.
- Image extension, MIME, empty content, and size validation.
- Product list paging/filter/sort fields remain OpenAPI-compatible.

The existing phase-one contract flow remains as a regression test, updated only
to authenticate mutation calls and use persisted records.

## 13. Deliverables

- Backend B SQLAlchemy models, CRUD, services, dependencies, and routes.
- Updated schema indexes/constraints.
- Automated Backend B persistence/state/idempotency/concurrency tests.
- `docs/qa/backend-b-state-machine.md`
- `docs/qa/backend-b-idempotency-conflict-tests.md`
- `docs/qa/backend-b-index-review.md`
- `docs/qa/backend-b-demo-notes.md`

## 14. Acceptance Criteria

- No Backend B production path reads or writes process-local dictionaries.
- Product/order/image/review data persists through SQLAlchemy sessions.
- All documented legal state transitions succeed.
- All documented illegal transitions return a unified, explainable error.
- Duplicate and concurrent active-order attempts create at most one order.
- Backend B tests and existing project tests pass.
- OpenAPI paths and response field names remain compatible.
- Documentation provides evidence for second-stage, third-stage, and final
  presentation deliverables.
