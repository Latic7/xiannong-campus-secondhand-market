-- --------------------------------------------------------
-- 主机:                           127.0.0.1
-- 服务器版本:                        8.0.46 - MySQL Community Server - GPL
-- 服务器操作系统:                      Win64
-- HeidiSQL 版本:                  12.18.0.7304
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 导出 campus_market 的数据库结构
DROP DATABASE IF EXISTS `campus_market`;
CREATE DATABASE IF NOT EXISTS `campus_market` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `campus_market`;

-- 导出  表 campus_market.admin_logs 结构
DROP TABLE IF EXISTS `admin_logs`;
CREATE TABLE IF NOT EXISTS `admin_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `actor_id` bigint NOT NULL,
  `action` varchar(32) NOT NULL,
  `target_type` varchar(32) NOT NULL,
  `target_id` bigint NOT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_admin_logs_actor` (`actor_id`),
  KEY `idx_admin_logs_created` (`created_at`),
  KEY `idx_admin_logs_target` (`target_type`,`target_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.admin_logs 的数据：~3 rows (大约)
DELETE FROM `admin_logs`;
INSERT INTO `admin_logs` (`id`, `actor_id`, `action`, `target_type`, `target_id`, `remark`, `created_at`) VALUES
	(9101, 10, 'warning', 'user', 2, '测试：管理员警告用户', '2026-06-12 11:30:55'),
	(9102, 10, 'unlist_product', 'product', 1003, '测试：下架商品', '2026-06-12 11:30:55'),
	(9103, 10, 'handle_report', 'report', 7002, '测试：处理举报', '2026-06-12 11:30:55');

-- 导出  表 campus_market.categories 结构
DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `parent_id` bigint DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_categories_parent_name` (`parent_id`,`name`),
  KEY `idx_categories_parent` (`parent_id`),
  KEY `idx_categories_sort` (`sort_order`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.categories 的数据：~4 rows (大约)
DELETE FROM `categories`;
INSERT INTO `categories` (`id`, `name`, `parent_id`, `sort_order`, `created_at`, `updated_at`) VALUES
	(1, '教材', NULL, 10, '2026-06-12 11:30:55', '2026-06-12 11:30:55'),
	(2, '电子产品', NULL, 20, '2026-06-12 11:30:55', '2026-06-12 11:30:55'),
	(3, '生活用品', NULL, 30, '2026-06-12 11:30:55', '2026-06-12 11:30:55'),
	(4, '其他', NULL, 99, '2026-06-12 11:30:55', '2026-06-12 11:30:55');

-- 导出  表 campus_market.favorites 结构
DROP TABLE IF EXISTS `favorites`;
CREATE TABLE IF NOT EXISTS `favorites` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_favorites_user_product` (`user_id`,`product_id`),
  KEY `idx_favorites_user` (`user_id`),
  KEY `idx_favorites_product` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.favorites 的数据：~3 rows (大约)
DELETE FROM `favorites`;
INSERT INTO `favorites` (`id`, `user_id`, `product_id`, `created_at`) VALUES
	(1, 2, 1001, '2026-06-12 11:30:55'),
	(2, 2, 1002, '2026-06-12 11:30:55'),
	(3, 1, 1004, '2026-06-12 11:30:55');

-- 导出  表 campus_market.orders 结构
DROP TABLE IF EXISTS `orders`;
CREATE TABLE IF NOT EXISTS `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `buyer_id` bigint DEFAULT NULL,
  `seller_id` bigint DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `status` enum('CREATED','RESERVED','CONFIRMED','COMPLETED','CANCELLED') NOT NULL DEFAULT 'CREATED',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expire_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_orders_status_created` (`status`,`created_at`),
  KEY `idx_orders_buyer` (`buyer_id`),
  KEY `idx_orders_seller` (`seller_id`),
  KEY `idx_orders_product` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5003 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.orders 的数据：~2 rows (大约)
DELETE FROM `orders`;
INSERT INTO `orders` (`id`, `product_id`, `buyer_id`, `seller_id`, `amount`, `remark`, `status`, `created_at`, `expire_at`) VALUES
	(5001, 1001, 2, 1, 35.00, '想今晚当面交付', 'CREATED', '2026-06-12 11:30:55', NULL),
	(5002, 1002, 2, 1, 28.00, '明天中午可以吗', 'CONFIRMED', '2026-06-12 11:30:55', NULL);

-- 导出  表 campus_market.product_images 结构
DROP TABLE IF EXISTS `product_images`;
CREATE TABLE IF NOT EXISTS `product_images` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `url` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_product_images_product` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.product_images 的数据：~5 rows (大约)
DELETE FROM `product_images`;
INSERT INTO `product_images` (`id`, `product_id`, `url`, `created_at`) VALUES
	(6001, 1001, 'https://cdn.example.com/p/demo-1001-1.jpg', '2026-06-12 11:30:55'),
	(6002, 1002, 'https://cdn.example.com/p/demo-1002-1.jpg', '2026-06-12 11:30:55'),
	(6003, 1003, 'https://cdn.example.com/p/demo-1003-1.jpg', '2026-06-12 11:30:55'),
	(6004, 1004, 'https://cdn.example.com/p/demo-1004-1.jpg', '2026-06-12 11:30:55'),
	(6005, 1005, 'http://localhost:8000/static/products/1005/f3c614e5070c460e804a6270a29d5544.jpg', '2026-06-15 02:00:13');

-- 导出  表 campus_market.products 结构
DROP TABLE IF EXISTS `products`;
CREATE TABLE IF NOT EXISTS `products` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `owner_id` bigint DEFAULT NULL,
  `title` varchar(128) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `category_id` bigint DEFAULT NULL,
  `status` enum('DRAFT','PENDING','PUBLISHED','REMOVED','SOLD') NOT NULL DEFAULT 'PENDING',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `favorite_count` int DEFAULT '0',
  `view_count` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_products_status_created` (`status`,`created_at`),
  KEY `idx_products_owner` (`owner_id`),
  KEY `idx_products_category` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.products 的数据：~5 rows (大约)
DELETE FROM `products`;
INSERT INTO `products` (`id`, `owner_id`, `title`, `description`, `price`, `category_id`, `status`, `created_at`, `updated_at`, `favorite_count`, `view_count`) VALUES
	(1001, 1, '二手高数教材', '九成新，可小刀', 35.00, 1, 'PUBLISHED', '2026-06-12 11:30:55', '2026-06-12 11:30:55', 2, 12),
	(1002, 1, '二手计算机网络教材', '有少量笔记', 28.00, 1, 'PUBLISHED', '2026-06-12 11:30:55', '2026-06-12 11:30:55', 1, 5),
	(1003, 1, '二手充电宝', '容量20000mAh', 45.00, 2, 'PUBLISHED', '2026-06-12 11:30:55', '2026-06-12 11:30:55', 0, 3),
	(1004, 2, '小台灯', '宿舍用，正常亮', 12.00, 3, 'PUBLISHED', '2026-06-12 11:30:55', '2026-06-12 11:30:55', 0, 1),
	(1005, 12, '【4K】Minecraft壁纸', '4K Minecraft壁纸，3D渲染，正版发售，未经原作者同意请勿转载！\n\n所在校区：东校区', 10.00, 1, 'PENDING', '2026-06-15 02:00:13', '2026-06-14 18:00:23', 0, 1);

-- 导出  表 campus_market.refresh_tokens 结构
DROP TABLE IF EXISTS `refresh_tokens`;
CREATE TABLE IF NOT EXISTS `refresh_tokens` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_refresh_tokens_token` (`token`),
  KEY `idx_refresh_tokens_user` (`user_id`),
  KEY `idx_refresh_tokens_expires` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=8003 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.refresh_tokens 的数据：~2 rows (大约)
DELETE FROM `refresh_tokens`;
INSERT INTO `refresh_tokens` (`id`, `user_id`, `token`, `expires_at`, `revoked`, `created_at`) VALUES
	(8001, 1, 'demo-refresh-token-1', '2026-06-19 11:30:55', 0, '2026-06-12 11:30:55'),
	(8002, 2, 'demo-refresh-token-2', '2026-06-19 11:30:55', 0, '2026-06-12 11:30:55');

-- 导出  表 campus_market.reports 结构
DROP TABLE IF EXISTS `reports`;
CREATE TABLE IF NOT EXISTS `reports` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reporter_id` bigint DEFAULT NULL,
  `target_type` enum('PRODUCT','USER','ORDER') NOT NULL,
  `target_id` bigint NOT NULL,
  `reason` varchar(255) NOT NULL,
  `status` enum('OPEN','REJECTED','HANDLED') NOT NULL DEFAULT 'OPEN',
  `assignee_id` bigint DEFAULT NULL,
  `handle_action` varchar(32) DEFAULT NULL,
  `handle_reason` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `handled_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_reports_status_created` (`status`,`created_at`),
  KEY `idx_reports_target` (`target_type`,`target_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7003 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.reports 的数据：~2 rows (大约)
DELETE FROM `reports`;
INSERT INTO `reports` (`id`, `reporter_id`, `target_type`, `target_id`, `reason`, `status`, `assignee_id`, `handle_action`, `handle_reason`, `created_at`, `handled_at`) VALUES
	(7001, 2, 'PRODUCT', 1001, '疑似虚假信息', 'OPEN', NULL, NULL, NULL, '2026-06-12 11:30:55', NULL),
	(7002, 1, 'USER', 2, '疑似骚扰', 'HANDLED', NULL, NULL, NULL, '2026-06-12 11:30:55', NULL);

-- 导出  表 campus_market.reviews 结构
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE IF NOT EXISTS `reviews` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `reviewer_id` bigint NOT NULL,
  `reviewee_id` bigint DEFAULT NULL,
  `score` int NOT NULL,
  `content` varchar(500) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_reviews_order_reviewer` (`order_id`,`reviewer_id`),
  KEY `idx_reviews_order` (`order_id`),
  KEY `idx_reviews_product` (`product_id`),
  KEY `idx_reviews_reviewer` (`reviewer_id`),
  KEY `idx_reviews_reviewee` (`reviewee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9003 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.reviews 的数据：~2 rows (大约)
DELETE FROM `reviews`;
INSERT INTO `reviews` (`id`, `order_id`, `product_id`, `reviewer_id`, `reviewee_id`, `score`, `content`, `created_at`) VALUES
	(9001, 5001, 1001, 2, 1, 5, '卖家回复很快，交易顺利。', '2026-06-12 11:30:55'),
	(9002, 5002, 1002, 2, 1, 4, '总体不错，书页有一点点折痕。', '2026-06-12 11:30:55');

-- 导出  表 campus_market.stats_daily 结构
DROP TABLE IF EXISTS `stats_daily`;
CREATE TABLE IF NOT EXISTS `stats_daily` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `stat_date` date NOT NULL,
  `users` int NOT NULL DEFAULT '0',
  `products` int NOT NULL DEFAULT '0',
  `orders` int NOT NULL DEFAULT '0',
  `reports` int NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_stats_daily_date` (`stat_date`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.stats_daily 的数据：~2 rows (大约)
DELETE FROM `stats_daily`;
INSERT INTO `stats_daily` (`id`, `stat_date`, `users`, `products`, `orders`, `reports`, `created_at`) VALUES
	(1, '2026-06-11', 2, 4, 2, 1, '2026-06-12 11:30:55'),
	(2, '2026-06-12', 3, 4, 2, 2, '2026-06-12 11:30:55');

-- 导出  表 campus_market.users 结构
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `openid` varchar(64) DEFAULT NULL,
  `nickname` varchar(64) NOT NULL,
  `avatar` varchar(255) NOT NULL DEFAULT '',
  `score` int NOT NULL DEFAULT '100',
  `status` enum('ACTIVE','BANNED') NOT NULL DEFAULT 'ACTIVE',
  `is_admin` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否为管理员: 0-否, 1-是',
  `college` varchar(128) DEFAULT NULL,
  `contact` varchar(64) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_users_openid` (`openid`),
  KEY `idx_users_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  campus_market.users 的数据：~5 rows (大约)
DELETE FROM `users`;
INSERT INTO `users` (`id`, `openid`, `nickname`, `avatar`, `score`, `status`, `is_admin`, `college`, `contact`, `created_at`, `updated_at`) VALUES
	(1, 'wx_openid_demo_1', 'DemoUser1', '', 100, 'ACTIVE', 0, '中国农业大学', '13800000001', '2026-06-12 11:30:55', '2026-06-12 11:30:55'),
	(2, 'wx_openid_demo_2', 'DemoUser2', '', 95, 'ACTIVE', 0, '中国农业大学', '13800000002', '2026-06-12 11:30:55', '2026-06-12 11:30:55'),
	(10, 'wx_openid_admin_10', 'AdminDemo', '', 100, 'ACTIVE', 1, '中国农业大学', '13800000010', '2026-06-12 11:30:55', '2026-06-12 11:30:55'),
	(11, 'orK423WwnIFshGd54OkS-nY5-gNM', 'WX_Y5-gNM', '', 100, 'ACTIVE', 0, NULL, NULL, '2026-06-12 11:31:42', '2026-06-12 11:31:42');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
