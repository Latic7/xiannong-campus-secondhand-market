# 后端 B 索引复核记录

## 商品查询

| 索引 | 支持查询 |
| --- | --- |
| `idx_products_status_created(status, created_at)` | 按状态和发布时间浏览商品 |
| `idx_products_owner(owner_id)` | 查询某用户发布的商品 |
| `idx_products_category(category_id)` | 分类商品查询 |
| `idx_products_category_status_created(category_id, status, created_at)` | 分类、状态和时间组合筛选 |

## 订单查询

| 索引 | 支持查询 |
| --- | --- |
| `idx_orders_status_created(status, created_at)` | 状态订单分页与后台统计 |
| `idx_orders_buyer(buyer_id)` | 我的购买订单 |
| `idx_orders_seller(seller_id)` | 我的售出订单 |
| `idx_orders_product(product_id)` | 商品关联订单 |
| `idx_orders_product_status(product_id, status)` | 下单前检查商品有效订单 |

## 图片与评价约束

| 约束或索引 | 用途 |
| --- | --- |
| `uq_product_images_product_url(product_id, url)` | 防止同一商品重复保存同一图片 URL |
| `idx_product_images_product(product_id)` | 加载商品图片 |
| `uq_reviews_order_reviewer(order_id, reviewer_id)` | 防止同一用户重复评价订单 |
| `idx_reviews_order(order_id)` | 查询订单评价 |
| `idx_reviews_product(product_id)` | 查询商品评价 |

SQLAlchemy 模型和 `server/app/db/schema.sql` 已同步。正式完整建库导出脚本仍由后端 D 统一生成和发布。

已有数据库可执行增量迁移：

```text
server/app/db/migrations/20260614_backend_b_query_indexes.sql
```

该脚本只增加本次复核得到的两个组合索引，不替代后端 D 的正式全库导出。
