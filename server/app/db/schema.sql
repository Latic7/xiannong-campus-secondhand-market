-- schema.sql (MySQL 8.0)
-- 数据库：campus_market
-- 字符集：utf8mb4

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY,
  nickname VARCHAR(64) NOT NULL,
  avatar VARCHAR(255) NOT NULL DEFAULT '',
  score INT NOT NULL DEFAULT 100,
  status ENUM('active','banned') NOT NULL DEFAULT 'active',
  college VARCHAR(128) NULL,
  contact VARCHAR(64) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_id BIGINT NULL,
  title VARCHAR(128) NOT NULL,
  description TEXT NULL,
  price DECIMAL(10,2) NOT NULL,
  category_id BIGINT NULL,
  status ENUM('draft','pending','published','removed','sold') NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  favorite_count INT NULL DEFAULT 0,
  view_count INT NULL DEFAULT 0,
  INDEX idx_products_status_created (status, created_at),
  INDEX idx_products_owner (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_images (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  url VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_product_images_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  buyer_id BIGINT NULL,
  seller_id BIGINT NULL,
  amount DECIMAL(10,2) NULL,
  remark VARCHAR(255) NULL,
  status ENUM('created','reserved','confirmed','completed','cancelled') NOT NULL DEFAULT 'created',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expire_at DATETIME NULL,
  INDEX idx_orders_status_created (status, created_at),
  INDEX idx_orders_buyer (buyer_id),
  INDEX idx_orders_seller (seller_id),
  INDEX idx_orders_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS reports (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  reporter_id BIGINT NULL,
  target_type ENUM('product','user','order') NOT NULL,
  target_id BIGINT NOT NULL,
  reason VARCHAR(255) NOT NULL,
  status ENUM('open','rejected','handled') NOT NULL DEFAULT 'open',
  assignee_id BIGINT NULL,
  handle_action VARCHAR(32) NULL,
  handle_reason VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  handled_at DATETIME NULL,
  INDEX idx_reports_status_created (status, created_at),
  INDEX idx_reports_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;