-- schema.sql (MySQL 8.0)
-- 数据库：campus_market
-- 字符集：utf8mb4

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY,
  openid VARCHAR(64) NULL,
  nickname VARCHAR(64) NOT NULL,
  avatar VARCHAR(255) NOT NULL DEFAULT '',
  score INT NOT NULL DEFAULT 100,
  status ENUM('active','banned') NOT NULL DEFAULT 'active',
  college VARCHAR(128) NULL,
  contact VARCHAR(64) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY ux_users_openid (openid),
  INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS categories (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  parent_id BIGINT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_categories_parent_name (parent_id, name),
  INDEX idx_categories_parent (parent_id),
  INDEX idx_categories_sort (sort_order)
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
  INDEX idx_products_owner (owner_id),
  INDEX idx_products_category (category_id)
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

CREATE TABLE IF NOT EXISTS favorites (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_favorites_user_product (user_id, product_id),
  INDEX idx_favorites_user (user_id),
  INDEX idx_favorites_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  token VARCHAR(255) NOT NULL,
  expires_at DATETIME NOT NULL,
  revoked TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_refresh_tokens_token (token),
  INDEX idx_refresh_tokens_user (user_id),
  INDEX idx_refresh_tokens_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS reviews (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  reviewer_id BIGINT NOT NULL,
  reviewee_id BIGINT NULL,
  score INT NOT NULL,
  content VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_reviews_order_reviewer (order_id, reviewer_id),
  INDEX idx_reviews_order (order_id),
  INDEX idx_reviews_product (product_id),
  INDEX idx_reviews_reviewer (reviewer_id),
  INDEX idx_reviews_reviewee (reviewee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS admin_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  actor_id BIGINT NOT NULL,
  action VARCHAR(32) NOT NULL,
  target_type VARCHAR(32) NOT NULL,
  target_id BIGINT NOT NULL,
  remark VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_admin_logs_actor (actor_id),
  INDEX idx_admin_logs_created (created_at),
  INDEX idx_admin_logs_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stats_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stat_date DATE NOT NULL,
  users INT NOT NULL DEFAULT 0,
  products INT NOT NULL DEFAULT 0,
  orders INT NOT NULL DEFAULT 0,
  reports INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_stats_daily_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (id, openid, nickname, avatar, score, status, college, contact)
VALUES
  (1, 'wx_openid_demo_1', 'DemoUser1', '', 100, 'active', '中国农业大学', '13800000001'),
  (2, 'wx_openid_demo_2', 'DemoUser2', '', 95, 'active', '中国农业大学', '13800000002'),
  (10, 'wx_openid_admin_10', 'AdminDemo', '', 100, 'active', '中国农业大学', '13800000010')
AS src
ON DUPLICATE KEY UPDATE
  openid = src.openid,
  nickname = src.nickname,
  avatar = src.avatar,
  score = src.score,
  status = src.status,
  college = src.college,
  contact = src.contact;

INSERT INTO categories (id, name, parent_id, sort_order)
VALUES
  (1, '教材', NULL, 10),
  (2, '电子产品', NULL, 20),
  (3, '生活用品', NULL, 30),
  (4, '其他', NULL, 99)
AS src
ON DUPLICATE KEY UPDATE
  name = src.name,
  parent_id = src.parent_id,
  sort_order = src.sort_order;

INSERT INTO products (id, owner_id, title, description, price, category_id, status, favorite_count, view_count)
VALUES
  (1001, 1, '二手高数教材', '九成新，可小刀', 35.00, 1, 'published', 2, 12),
  (1002, 1, '二手计算机网络教材', '有少量笔记', 28.00, 1, 'published', 1, 5),
  (1003, 1, '二手充电宝', '容量20000mAh', 45.00, 2, 'published', 0, 3),
  (1004, 2, '小台灯', '宿舍用，正常亮', 12.00, 3, 'published', 0, 1)
AS src
ON DUPLICATE KEY UPDATE
  owner_id = src.owner_id,
  title = src.title,
  description = src.description,
  price = src.price,
  category_id = src.category_id,
  status = src.status,
  favorite_count = src.favorite_count,
  view_count = src.view_count;

INSERT INTO product_images (id, product_id, url)
VALUES
  (6001, 1001, 'https://cdn.example.com/p/demo-1001-1.jpg'),
  (6002, 1002, 'https://cdn.example.com/p/demo-1002-1.jpg'),
  (6003, 1003, 'https://cdn.example.com/p/demo-1003-1.jpg'),
  (6004, 1004, 'https://cdn.example.com/p/demo-1004-1.jpg')
AS src
ON DUPLICATE KEY UPDATE
  product_id = src.product_id,
  url = src.url;

INSERT INTO favorites (user_id, product_id)
VALUES
  (2, 1001),
  (2, 1002),
  (1, 1004)
ON DUPLICATE KEY UPDATE
  created_at = created_at;

INSERT INTO orders (id, product_id, buyer_id, seller_id, amount, remark, status)
VALUES
  (5001, 1001, 2, 1, 35.00, '想今晚当面交付', 'created'),
  (5002, 1002, 2, 1, 28.00, '明天中午可以吗', 'confirmed')
AS src
ON DUPLICATE KEY UPDATE
  product_id = src.product_id,
  buyer_id = src.buyer_id,
  seller_id = src.seller_id,
  amount = src.amount,
  remark = src.remark,
  status = src.status;

INSERT INTO reports (id, reporter_id, target_type, target_id, reason, status)
VALUES
  (7001, 2, 'product', 1001, '疑似虚假信息', 'open'),
  (7002, 1, 'user', 2, '疑似骚扰', 'handled')
AS src
ON DUPLICATE KEY UPDATE
  reporter_id = src.reporter_id,
  target_type = src.target_type,
  target_id = src.target_id,
  reason = src.reason,
  status = src.status;

INSERT INTO refresh_tokens (id, user_id, token, expires_at, revoked)
VALUES
  (8001, 1, 'demo-refresh-token-1', DATE_ADD(NOW(), INTERVAL 7 DAY), 0),
  (8002, 2, 'demo-refresh-token-2', DATE_ADD(NOW(), INTERVAL 7 DAY), 0)
AS src
ON DUPLICATE KEY UPDATE
  user_id = src.user_id,
  expires_at = src.expires_at,
  revoked = src.revoked;

INSERT INTO reviews (id, order_id, product_id, reviewer_id, reviewee_id, score, content)
VALUES
  (9001, 5001, 1001, 2, 1, 5, '卖家回复很快，交易顺利。'),
  (9002, 5002, 1002, 2, 1, 4, '总体不错，书页有一点点折痕。')
AS src
ON DUPLICATE KEY UPDATE
  order_id = src.order_id,
  product_id = src.product_id,
  reviewer_id = src.reviewer_id,
  reviewee_id = src.reviewee_id,
  score = src.score,
  content = src.content;

INSERT INTO admin_logs (id, actor_id, action, target_type, target_id, remark)
VALUES
  (9101, 10, 'warning', 'user', 2, '测试：管理员警告用户'),
  (9102, 10, 'unlist_product', 'product', 1003, '测试：下架商品'),
  (9103, 10, 'handle_report', 'report', 7002, '测试：处理举报')
AS src
ON DUPLICATE KEY UPDATE
  actor_id = src.actor_id,
  action = src.action,
  target_type = src.target_type,
  target_id = src.target_id,
  remark = src.remark;

INSERT INTO stats_daily (stat_date, users, products, orders, reports)
VALUES
  (DATE_SUB(CURDATE(), INTERVAL 1 DAY), 2, 4, 2, 1),
  (CURDATE(), 3, 4, 2, 2)
AS src
ON DUPLICATE KEY UPDATE
  users = src.users,
  products = src.products,
  orders = src.orders,
  reports = src.reports;