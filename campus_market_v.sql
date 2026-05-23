/*
 Navicat Premium Dump SQL

 Source Server         : 软件工程
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42)
 Source Host           : localhost:3306
 Source Schema         : campus_market

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42)
 File Encoding         : 65001

 Date: 21/05/2026 17:35:36
*/

-- ----------------------------
-- Create database if not exists
-- ----------------------------
CREATE DATABASE IF NOT EXISTS `campus_market`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE `campus_market`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin_logs
-- ----------------------------
DROP TABLE IF EXISTS `admin_logs`;
CREATE TABLE `admin_logs`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `actor_id` bigint NOT NULL,
  `action` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `target_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `target_id` bigint NOT NULL,
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_admin_logs_actor`(`actor_id` ASC) USING BTREE,
  INDEX `idx_admin_logs_created`(`created_at` ASC) USING BTREE,
  INDEX `idx_admin_logs_target`(`target_type` ASC, `target_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9104 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of admin_logs
-- ----------------------------
INSERT INTO `admin_logs` VALUES (9101, 10, 'warning', 'user', 2, '测试：管理员警告用户', '2026-05-21 17:25:53');
INSERT INTO `admin_logs` VALUES (9102, 10, 'unlist_product', 'product', 1003, '测试：下架商品', '2026-05-21 17:30:13');
INSERT INTO `admin_logs` VALUES (9103, 10, 'handle_report', 'report', 7002, '测试：处理举报', '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for categories
-- ----------------------------
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parent_id` bigint NULL DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_categories_parent_name`(`parent_id` ASC, `name` ASC) USING BTREE,
  INDEX `idx_categories_parent`(`parent_id` ASC) USING BTREE,
  INDEX `idx_categories_sort`(`sort_order` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of categories
-- ----------------------------
INSERT INTO `categories` VALUES (1, '教材', NULL, 10, '2026-05-21 17:23:21', '2026-05-21 17:25:53');
INSERT INTO `categories` VALUES (2, '电子产品', NULL, 20, '2026-05-21 17:23:21', '2026-05-21 17:25:53');
INSERT INTO `categories` VALUES (3, '生活用品', NULL, 30, '2026-05-21 17:23:21', '2026-05-21 17:25:53');
INSERT INTO `categories` VALUES (4, '其他', NULL, 99, '2026-05-21 17:30:13', '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for favorites
-- ----------------------------
DROP TABLE IF EXISTS `favorites`;
CREATE TABLE `favorites`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_favorites_user_product`(`user_id` ASC, `product_id` ASC) USING BTREE,
  INDEX `idx_favorites_user`(`user_id` ASC) USING BTREE,
  INDEX `idx_favorites_product`(`product_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of favorites
-- ----------------------------
INSERT INTO `favorites` VALUES (1, 2, 1001, '2026-05-21 17:25:53');
INSERT INTO `favorites` VALUES (2, 2, 1002, '2026-05-21 17:30:13');
INSERT INTO `favorites` VALUES (3, 1, 1004, '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for orders
-- ----------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `buyer_id` bigint NULL DEFAULT NULL,
  `seller_id` bigint NULL DEFAULT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL,
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` enum('created','reserved','confirmed','completed','cancelled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'created',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expire_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_orders_status_created`(`status` ASC, `created_at` ASC) USING BTREE,
  INDEX `idx_orders_buyer`(`buyer_id` ASC) USING BTREE,
  INDEX `idx_orders_seller`(`seller_id` ASC) USING BTREE,
  INDEX `idx_orders_product`(`product_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5003 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of orders
-- ----------------------------
INSERT INTO `orders` VALUES (5001, 1001, 2, 1, 35.00, '想今晚当面交付', 'created', '2026-05-21 17:25:53', NULL);
INSERT INTO `orders` VALUES (5002, 1002, 2, 1, 28.00, '明天中午可以吗', 'confirmed', '2026-05-21 17:30:13', NULL);

-- ----------------------------
-- Table structure for product_images
-- ----------------------------
DROP TABLE IF EXISTS `product_images`;
CREATE TABLE `product_images`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_product_images_product_url`(`product_id` ASC, `url` ASC) USING BTREE,
  INDEX `idx_product_images_product`(`product_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6005 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of product_images
-- ----------------------------
INSERT INTO `product_images` VALUES (6001, 1001, 'https://cdn.example.com/p/demo-1001-1.jpg', '2026-05-21 17:25:53');
INSERT INTO `product_images` VALUES (6002, 1002, 'https://cdn.example.com/p/demo-1002-1.jpg', '2026-05-21 17:25:53');
INSERT INTO `product_images` VALUES (6003, 1003, 'https://cdn.example.com/p/demo-1003-1.jpg', '2026-05-21 17:30:13');
INSERT INTO `product_images` VALUES (6004, 1004, 'https://cdn.example.com/p/demo-1004-1.jpg', '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for products
-- ----------------------------
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `owner_id` bigint NULL DEFAULT NULL,
  `title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `price` decimal(10, 2) NOT NULL,
  `category_id` bigint NULL DEFAULT NULL,
  `status` enum('draft','pending','published','removed','sold') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'pending',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `favorite_count` int NULL DEFAULT 0,
  `view_count` int NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_products_status_created`(`status` ASC, `created_at` ASC) USING BTREE,
  INDEX `idx_products_owner`(`owner_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1005 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of products
-- ----------------------------
INSERT INTO `products` VALUES (1001, 1, '二手高数教材', '九成新，可小刀', 35.00, 1, 'published', '2026-05-21 17:25:53', '2026-05-21 17:30:13', 2, 12);
INSERT INTO `products` VALUES (1002, 1, '二手计算机网络教材', '有少量笔记', 28.00, 1, 'published', '2026-05-21 17:25:53', '2026-05-21 17:30:13', 1, 5);
INSERT INTO `products` VALUES (1003, 1, '二手充电宝', '容量20000mAh', 45.00, 2, 'published', '2026-05-21 17:30:13', '2026-05-21 17:30:13', 0, 3);
INSERT INTO `products` VALUES (1004, 2, '小台灯', '宿舍用，正常亮', 12.00, 3, 'published', '2026-05-21 17:30:13', '2026-05-21 17:30:13', 0, 1);

-- ----------------------------
-- Table structure for refresh_tokens
-- ----------------------------
DROP TABLE IF EXISTS `refresh_tokens`;
CREATE TABLE `refresh_tokens`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_refresh_tokens_token`(`token` ASC) USING BTREE,
  INDEX `idx_refresh_tokens_user`(`user_id` ASC) USING BTREE,
  INDEX `idx_refresh_tokens_expires`(`expires_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8003 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of refresh_tokens
-- ----------------------------
INSERT INTO `refresh_tokens` VALUES (8001, 1, 'demo-refresh-token-1', '2026-05-28 17:34:46', 0, '2026-05-21 17:25:53');
INSERT INTO `refresh_tokens` VALUES (8002, 2, 'demo-refresh-token-2', '2026-05-28 17:34:46', 0, '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for reports
-- ----------------------------
DROP TABLE IF EXISTS `reports`;
CREATE TABLE `reports`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reporter_id` bigint NULL DEFAULT NULL,
  `target_type` enum('product','user','order') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `target_id` bigint NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` enum('open','rejected','handled') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'open',
  `assignee_id` bigint NULL DEFAULT NULL,
  `handle_action` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `handle_reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `handled_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_reports_status_created`(`status` ASC, `created_at` ASC) USING BTREE,
  INDEX `idx_reports_target`(`target_type` ASC, `target_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7003 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of reports
-- ----------------------------
INSERT INTO `reports` VALUES (7001, 2, 'product', 1001, '疑似虚假信息', 'open', NULL, NULL, NULL, '2026-05-21 17:25:53', NULL);
INSERT INTO `reports` VALUES (7002, 1, 'user', 2, '疑似骚扰', 'handled', NULL, NULL, NULL, '2026-05-21 17:30:13', NULL);

-- ----------------------------
-- Table structure for reviews
-- ----------------------------
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `reviewer_id` bigint NOT NULL,
  `reviewee_id` bigint NULL DEFAULT NULL,
  `score` int NOT NULL,
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_reviews_order_reviewer`(`order_id` ASC, `reviewer_id` ASC) USING BTREE,
  INDEX `idx_reviews_order`(`order_id` ASC) USING BTREE,
  INDEX `idx_reviews_product`(`product_id` ASC) USING BTREE,
  INDEX `idx_reviews_reviewer`(`reviewer_id` ASC) USING BTREE,
  INDEX `idx_reviews_reviewee`(`reviewee_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9003 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of reviews
-- ----------------------------
INSERT INTO `reviews` VALUES (9001, 5001, 1001, 2, 1, 5, '卖家回复很快，交易顺利。', '2026-05-21 17:25:53');
INSERT INTO `reviews` VALUES (9002, 5002, 1002, 2, 1, 4, '总体不错，书页有一点点折痕。', '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for stats_daily
-- ----------------------------
DROP TABLE IF EXISTS `stats_daily`;
CREATE TABLE `stats_daily`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `stat_date` date NOT NULL,
  `users` int NOT NULL DEFAULT 0,
  `products` int NOT NULL DEFAULT 0,
  `orders` int NOT NULL DEFAULT 0,
  `reports` int NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_stats_daily_date`(`stat_date` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of stats_daily
-- ----------------------------
INSERT INTO `stats_daily` VALUES (1, '2026-05-21', 3, 4, 2, 2, '2026-05-21 17:25:53');
INSERT INTO `stats_daily` VALUES (2, '2026-05-20', 2, 4, 2, 1, '2026-05-21 17:30:13');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint NOT NULL,
  `openid` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `nickname` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `score` int NOT NULL DEFAULT 100,
  `status` enum('active','banned') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'active',
  `college` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `contact` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ux_users_openid`(`openid` ASC) USING BTREE,
  INDEX `idx_users_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'wx_openid_demo_1', 'DemoUser1', '', 100, 'active', '中国农业大学', '13800000001', '2026-05-21 17:23:21', '2026-05-21 17:25:53');
INSERT INTO `users` VALUES (2, 'wx_openid_demo_2', 'DemoUser2', '', 95, 'active', '中国农业大学', '13800000002', '2026-05-21 17:23:21', '2026-05-21 17:25:53');
INSERT INTO `users` VALUES (10, 'wx_openid_admin_10', 'AdminDemo', '', 100, 'active', '中国农业大学', '13800000010', '2026-05-21 17:30:13', '2026-05-21 17:30:13');

SET FOREIGN_KEY_CHECKS = 1;
