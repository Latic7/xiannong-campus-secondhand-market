-- Backend B incremental query-index migration.
-- Apply once to an existing campus_market-compatible database.

ALTER TABLE products
  ADD INDEX idx_products_category_status_created (category_id, status, created_at);

ALTER TABLE orders
  ADD INDEX idx_orders_product_status (product_id, status);
