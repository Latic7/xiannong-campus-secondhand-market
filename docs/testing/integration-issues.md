# 联调问题记录表（第一阶段最小范围）

只记录三类：
- 字段不一致
- 状态不一致
- 返回结构不一致（包含：鉴权语义不一致、参数校验缺失导致的“该报错却成功返回”）

对照依据：docs/api/openapi.yaml

---

## 0. 第二阶段联调期台账（按天维护 + 优先级）

优先级定义：
- P0：阻塞主链路联调/影响大面积功能
- P1：不阻塞主链路但会导致明显功能缺失/状态错误
- P2：体验/边角/低频问题

台账（每天只追加新行，不覆盖旧行）：

| 日期 | ISSUE | 接口/模块 | 现象摘要 | 责任人 | 优先级 | 状态 |
|------|-------|-----------|----------|--------|--------|------|
| 2026-06-09 | ISSUE-001 | Auth | refresh 响应 data 缺 user | 后端A | P0 | Open |
| 2026-06-09 | ISSUE-004 | 全局 | 422 不走统一 ApiResponse | 后端A | P0 | Open |
| 2026-06-09 | ISSUE-006 | 全局 | POST /api/reports、POST /api/appeals 未带 token 仍返回 200 | 后端A | P0 | Open |
| 2026-06-09 | ISSUE-002 | Orders | 订单详情已返回完整 Order 结构，productId 已补齐 | 后端B | P1 | Fixed |
| 2026-06-09 | ISSUE-008 | Orders | 订单状态机约束与幂等策略已生效 | 后端B | P1 | Fixed |
| 2026-06-09 | ISSUE-003 | Reports | 举报详情已返回完整 Report 结构，关键字段已补齐 | 后端C | P1 | Fixed |
| 2026-06-18 | ISSUE-005 | Products | /api/products 分页参数越界时返回默认 422 detail，未统一为 ApiResponse | 后端A | P1 | Open |
| 2026-06-18 | ISSUE-009 | Admin | 非管理员访问 /api/admin/stats/* 的 403 错误结构已统一为 ApiResponse | 后端A | P0 | Fixed |
| 2026-06-18 | ISSUE-010 | Auth/Users | /api/auth/me 与 /api/users/me 返回字段命名已统一为 isAdmin | 后端A | P0 | Fixed |
| 2026-06-18 | ISSUE-011 | Auth/Users | UserProfile 中 publishedCount/soldCount 已在 OpenAPI 中定义，契约已对齐 | 后端A | P1 | Fixed |
| 2026-06-18 | ISSUE-013 | Favorites/Products | images URL 反引号/空格现象经复测未在真实 payload 中复现 | 后端B | P1 | Closed |
| 2026-06-19 | ISSUE-007 | Reports | /api/reports/{reportId} 已返回 404 + ApiResponse，资源不存在语义已对齐 | 后端C | P1 | Fixed |
| 2026-06-20 | ISSUE-001 | Auth | refresh 响应 data 复测仍缺 user | 后端A | P0 | Open |
| 2026-06-20 | ISSUE-004 | 全局 | products/orders/reports/appeals 缺参复测仍返回默认 422 detail | 后端A | P0 | Open |
| 2026-06-20 | ISSUE-005 | Products | /api/products 分页参数越界复测仍返回默认 422 detail | 后端A | P1 | Open |
| 2026-06-20 | ISSUE-006 | Reports/Appeals | reports 未带 token 已返回 401；appeals 未带 token 仍返回 200 | 后端A | P0 | Open |
| 2026-06-20 | ISSUE-013 | Favorites/Products | images URL 现象经 MySQL + products/favorites 原始字节复测，确认未在真实 payload 中复现 | 后端B | P1 | Closed |
| 2026-06-20 | ISSUE-001 | Auth | refresh 响应 data 已返回 user，AuthTokens 契约已对齐 | 后端A | P0 | Fixed |
| 2026-06-20 | ISSUE-004 | 全局 | products/orders/reports/appeals 缺参已统一返回 422 + ApiResponse | 后端A | P0 | Fixed |
| 2026-06-20 | ISSUE-005 | Products | /api/products 分页参数越界已返回 422 + ApiResponse | 后端A | P1 | Fixed |
| 2026-06-20 | ISSUE-006 | Appeals | POST /api/appeals 未带 token 仍返回 200，reports 侧已修复 | 后端A | P0 | Open |

---

## 一、字段不一致（Field Mismatch）

### ISSUE-001（POST /api/auth/refresh：data 缺少 user）
- 类型：字段不一致
- 接口：POST /api/auth/refresh
- 优先级：P0
- 责任人：后端A
- 状态：Fixed
- 复现步骤：
  1) 准备一个合法 refreshToken（typ=refresh，使用同一 JWT_SECRET）
  2) 请求体：{"refreshToken":"..."}
- OpenAPI 期望：
  - 200：data 为 AuthTokens（required: accessToken/refreshToken/expiresIn/user）
- 当前实际：
  - 2026-06-19 复测仍缺 user，响应体中未返回用户资料对象
  - 2026-06-20 使用合法 refreshToken 构造合法 JSON 请求体后再次复测，返回 200 + ApiResponse
  - data 已包含 accessToken、refreshToken、expiresIn、user
- 影响范围：
  - 已修复
- 备注：
  - refresh 响应当前已与 AuthTokens 契约对齐

---

### ISSUE-002（GET /api/orders/{orderId}：data 不是完整 Order）
- 类型：字段不一致
- 接口：GET /api/orders/{orderId}
- 优先级：P1
- 责任人：后端B
- 状态：Fixed
- 复现步骤：
  1) GET /api/orders/5001
- OpenAPI 期望：
  - 200：data 为 Order（required: id, productId, status）
- 当前实际：
  - 2026-06-19 复测结果：200 + ApiResponse
  - data 已包含 id、productId、buyerId、sellerId、amount、remark、status、createdAt、expireAt
- 影响范围：
  - 已修复
- 备注：
  - 订单详情返回字段已能满足当前联调需要

---

### ISSUE-003（GET /api/reports/{reportId}：data 不是完整 Report）
- 类型：字段不一致
- 接口：GET /api/reports/{reportId}
- 优先级：P1
- 责任人：后端C
- 状态：Fixed
- 复现步骤：
  1) GET /api/reports/7001
- OpenAPI 期望：
  - 200：data 为 Report（required: id,targetType,targetId,reason,status）
- 当前实际：
  - 2026-06-19 复测结果：200 + ApiResponse
  - data 已包含 id、reporterId、targetType、targetId、reason、status、createdAt、handledAt、assigneeId、handleAction、handleReason
- 影响范围：
  - 已修复
- 备注：
  - 举报详情字段已能满足当前联调需要

---

### ISSUE-010（GET /api/auth/me、GET /api/users/me：is_admin vs isAdmin 字段命名不一致）
- 类型：字段不一致
- 接口：
  - GET /api/auth/me
  - GET /api/users/me
- 优先级：P0
- 责任人：后端A
- 状态：Fixed
- 复现步骤：
  1) 生成仅包含 uid/sub/nickname/typ/exp 的 access token（不包含 isAdmin）
  2) 用普通用户 token（uid=1）请求 GET /api/auth/me
  3) 用管理员 token（uid=10）请求 GET /api/auth/me
  4) 同样方式请求 GET /api/users/me
- OpenAPI 期望：
  - UserProfile.required 包含 isAdmin
  - 前后端联调用字段应为 isAdmin
- 当前实际：
  - 2026-06-19 复测结果：返回字段已统一为 isAdmin
  - 普通用户返回 isAdmin=false，管理员返回 isAdmin=true
- 影响范围：
  - 已修复
- 备注：
  - 当前“是否管理员”的识别逻辑本身正确，且返回层字段命名已统一为 isAdmin
  - 数据库字段仍为 is_admin，不影响接口返回契约

---

### ISSUE-011（GET /api/auth/me、GET /api/users/me：publishedCount/soldCount 是否纳入契约）
- 类型：字段不一致
- 接口：
  - GET /api/auth/me
  - GET /api/users/me
- 优先级：P1
- 责任人：后端A
- 状态：Fixed
- 复现步骤：
  1) 用合法 access token 请求 GET /api/auth/me
  2) 用合法 access token 请求 GET /api/users/me
  3) 检查 docs/api/openapi.yaml 中 UserProfile 定义
- OpenAPI 期望：
  - UserProfile 需明确列出返回字段
- 当前实际：
  - data 中返回 publishedCount / soldCount
  - 2026-06-19 复测 OpenAPI，已确认 UserProfile 中存在 publishedCount / soldCount 定义
- 影响范围：
  - 已修复
- 备注：
  - 最新 OpenAPI 已补齐 publishedCount / soldCount
  - 当前接口返回与契约一致

---

### ISSUE-013（Favorites/Products：images 图片 URL 含反引号和空格）
- 类型：字段不一致
- 接口：
  - GET /api/users/me/favorites
  - GET /api/products
  - GET /api/products/{productId}
- 优先级：P1
- 责任人：后端B
- 状态：Closed
- 复现步骤：
  1) 用普通用户 access token 请求 GET /api/users/me/favorites?page=1&size=20
  2) 请求 GET /api/products?page=1&size=20
  3) 请求 GET /api/products/1001
- OpenAPI 期望：
  - images 为标准 URL 字符串数组
- 当前实际：
  - 2026-06-19 复测数据库 `product_images.url` 的 `HEX(url)`，值均为正常 URL 字节流，不含空格或反引号字节
  - 2026-06-20 将服务切换到 MySQL 数据源后，复测 `GET /api/products/1001`，返回的 `images[0]` 原始字节仍为正常 URL
  - 2026-06-20 复测 `GET /api/users/me/favorites?page=1&size=20`，返回列表中的 `images[0]` 原始字节同样为正常 URL
  - 前期看到的反引号/空格现象未在真实 payload 中复现
- 影响范围：
  - 当前不构成后端缺陷
- 备注：
  - 判定为显示/复制过程中的视觉痕迹，本 issue 关闭
  - `products` 与 `favorites` 均为直接读取 `ProductImage.url`，未发现额外拼接空格或反引号的逻辑

---

## 二、返回结构不一致（Envelope / Validation / Auth Semantics）

### ISSUE-004（请求体缺必填字段时：返回结构未统一为 ApiResponse）
- 类型：返回结构不一致
- 接口：示例 POST /api/products（同类：POST /api/orders、POST /api/reports、POST /api/appeals 等）
- 优先级：P0
- 责任人：后端A
- 状态：Fixed
- 复现步骤：
  1) POST /api/products
  2) 请求体缺 title/price/categoryId 任意一个
- OpenAPI 期望：
  - 失败也应返回 ApiResponse 外层：code/message/data/requestId/timestamp
- 当前实际：
  - 2026-06-19 复测 POST /api/products 缺少 title 时，仍返回默认 422 detail
  - 2026-06-19 复测 POST /api/orders 缺少 productId 时，仍返回默认 422 detail
  - 2026-06-19 复测 POST /api/reports 缺少 reason 时，仍返回默认 422 detail
  - 2026-06-19 复测 POST /api/appeals 缺少 targetId 时，仍返回默认 422 detail
  - 2026-06-20 再次复测 POST /api/products、POST /api/orders、POST /api/reports、POST /api/appeals 缺参场景，均返回 422 + ApiResponse
  - 返回体已统一包含 code/message/data/requestId/timestamp，错误明细收敛到 data.errors
- 影响范围：
  - 已修复
- 备注：
  - 全局请求体验证异常已接入统一 ApiResponse

---

### ISSUE-005（GET /api/products：page/size 越界时错误结构未统一）
- 类型：返回结构不一致
- 接口：GET /api/products
- 优先级：P1
- 责任人：后端A
- 状态：Fixed
- 复现步骤：
  1) GET /api/products?page=0&size=999
- OpenAPI 期望：
  - page>=1，size<=100；越界应返回失败 ApiResponse
- 当前实际：
  - 2026-06-19 初测时，GET /api/products?page=0&size=999 返回 HTTP 422，响应体仍为默认 {"detail":[...]}
  - 2026-06-20 复测时，返回 HTTP 422 + ApiResponse
  - 响应体已包含 code/message/data/requestId/timestamp，data.errors 中能正确给出 page / size 校验失败信息
- 影响范围：
  - 已修复
- 备注：
  - 参数校验与统一错误结构现已同时生效

---

### ISSUE-006（OpenAPI 顶层 bearerAuth：appeals 鉴权仍未完全接入）
- 类型：返回结构不一致
- 接口：
  - POST /api/reports
  - POST /api/appeals
- 优先级：P0
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) 不带 Authorization 请求 POST /api/reports
  2) 不带 Authorization 请求 POST /api/appeals
- OpenAPI 期望：
  - OpenAPI 顶层声明了 bearerAuth，除显式 security: [] 的接口外，其余默认需要 Bearer
  - 未登录应返回 401 + ApiResponse
- 当前实际：
  - 2026-06-19 初测时，POST /api/reports 未带 Authorization 仍返回 200 + ApiResponse，并成功创建举报
  - 2026-06-19 初测时，POST /api/appeals 未带 Authorization 仍返回 200 + ApiResponse，并成功提交申诉
  - 2026-06-20 复测时，POST /api/reports 未带 Authorization 已返回 401 + ApiResponse，reports 侧已修复
  - 2026-06-20 复测时，POST /api/appeals 未带 Authorization 仍返回 200 + ApiResponse，并成功提交申诉
- 影响范围：
  - 当前仍存在未登录用户可直接执行申诉写操作的问题，权限边界与契约不一致
- 备注：
  - 这不是 reports/appeals 业务字段问题，而是统一鉴权依赖接入不完整
  - 当前问题范围已收敛为 appeals

---

### ISSUE-007（资源不存在语义：reports 已对齐 404 + ApiResponse）
- 类型：返回结构不一致
- 接口：
  - GET /api/products/{productId}
  - GET /api/orders/{orderId}
  - GET /api/reports/{reportId}
- 优先级：P1
- 责任人：后端C
- 状态：Fixed
- 复现步骤：
  1) 用任意不存在的 id 调用
- OpenAPI 期望：
  - 不存在应 404 + ApiResponse
- 当前实际：
  - GET /api/products/999999 已复测通过：HTTP 404 + ApiResponse
  - GET /api/orders/999999 已复测通过：HTTP 404 + ApiResponse，body 为 {"code":4040,"message":"order not found","data":{"orderId":999999},...}
  - GET /api/reports/999999 已复测通过：HTTP 404 + ApiResponse，body 为 {"code":4040,"message":"举报记录 999999 不存在","data":null,...}
- 影响范围：
  - 已修复
- 备注：
  - products、orders、reports 的详情接口均已通过 404 语义复测

---

### ISSUE-009（非管理员访问后台接口时：403 未包装为 ApiResponse）
- 类型：返回结构不一致
- 接口：GET /api/admin/stats/overview（同类：/api/admin/users、/api/admin/logs、/api/admin/stats/*）
- 优先级：P0
- 责任人：后端A
- 状态：Fixed
- 初始现象：
  - 非管理员访问后台接口时返回 {"detail":"admin permission required"}，未统一包装为 ApiResponse
- 最新复测（2026-06-19）：
  - GET /api/admin/stats/overview：403 + ApiResponse
  - GET /api/admin/users：403 + ApiResponse
  - GET /api/admin/logs：403 + ApiResponse
  - GET /api/admin/stats/products：403 + ApiResponse
  - GET /api/admin/stats/trades：403 + ApiResponse
  - GET /api/admin/stats/users：403 + ApiResponse
- 结论：
  - admin 权限错误返回结构已修复并统一

## 三、状态不一致（State Machine / Idempotency Semantics）

### ISSUE-008（订单状态机未受约束：confirm/cancel/complete 可任意重复调用）
- 类型：状态不一致
- 接口：
  - POST /api/orders/{orderId}/seller-confirm
  - POST /api/orders/{orderId}/cancel
  - POST /api/orders/{orderId}/complete
- 优先级：P1
- 责任人：后端B
- 状态：Fixed
- 复现步骤：
  1) 创建订单后依次测试 seller-confirm / complete / cancel
  2) 对同一 orderId 重复调用 confirm / complete / cancel
  3) 测试 completed 后 cancel、cancelled 后 complete
- 约定/期望（开工前约定清单）：
  - created -> reserved -> confirmed -> completed | cancelled
  - 不允许随意回退/重复完成
- 当前实际：
  - 2026-06-19 复测结果：状态机约束已生效
  - RESERVED -> CONFIRMED：成功
  - 重复 seller-confirm：200 + CONFIRMED（幂等成功）
  - CONFIRMED -> COMPLETED：成功
  - 重复 complete：200 + COMPLETED（幂等成功）
  - COMPLETED -> cancel：409 Conflict
  - RESERVED -> CANCELLED：成功
  - 重复 cancel：200 + CANCELLED（幂等成功）
  - CANCELLED -> complete：409 Conflict
- 影响范围：
  - 已修复
- 备注：
  - 当前策略为“重复同一动作幂等成功，非法跨状态流转返回 409”

---

## 四、数据库迁移脚本执行记录（第二阶段交付物）

记录原则：每次 schema.sql 或建库脚本有变化，都补一条记录，并在群里通知大家同步更新。

| 日期 | 变更摘要 | 影响表/字段 | 执行方式 | 执行人 | 结果 |
|------|----------|-------------|----------|--------|------|
| 2026-06-09 | users.id 自增主键 + openid 唯一索引；枚举小写口径统一 | users / products / orders / reports | MySQL SOURCE server/app/db/schema.sql | 后端D | OK |
| 2026-06-18 | 使用最新 schema.sql 重建 campus_market，验证 users.status 大写枚举与 is_admin 字段 | users | DROP/CREATE DATABASE + MySQL SOURCE app/db/schema.sql | 后端D | OK |

---

## 五、测试执行记录（2026-06-18 ~ 2026-06-20，后端D）

环境：
- 分支：dev（已与 origin/dev 同步）
- 服务：uvicorn app.main:app（127.0.0.1:8000）
- 数据库：MySQL campus_market，已 DROP/CREATE 后 SOURCE app/db/schema.sql 重建
- users 表关键字段确认：status=ACTIVE/BANNED；is_admin 存在；AdminDemo(id=10) is_admin=1

执行结果（包含正确与错误）：

1) GET /health
- 结果：PASS
- 实际：200 + ApiResponse（code/message/data/requestId/timestamp 完整）

2) GET /api/auth/me
- 结果：PASS（按数据库 is_admin 识别）
- 普通用户（uid=1）：200 + data.isAdmin=false
- 管理员（uid=10）：200 + data.isAdmin=true
- 不带 token：401 + ApiResponse（code=10030）

3) GET /api/admin/stats/overview
- 结果：PASS
- 普通用户访问：403 + 统一 ApiResponse（code=10060，message=admin permission required）
- 管理员访问：200 + ApiResponse，正常返回统计数据
- 说明：admin 权限拦截与统一错误结构均已生效

4) 当前阶段结论
- “是否管理员”的识别链路已验证通过：当前实现按数据库 users.is_admin 判定，不依赖 token 中额外携带 isAdmin
- auth/users/admin 这条链路当前复测结果：
  - 非管理员访问 admin 接口时，403 已统一包装为 ApiResponse
  - UserProfile 返回字段已统一为 isAdmin
  - publishedCount / soldCount 已在 OpenAPI 中定义，契约已对齐

5) GET /api/users/me
- 结果：PASS
- 普通用户：200 + ApiResponse，isAdmin=false
- 管理员：200 + ApiResponse，isAdmin=true
- 不带 token：401 + ApiResponse

6) PUT /api/users/me
- 结果：PASS
- 使用合法 JSON 请求体更新 nickname / college 后返回 updated=true
- 再次查询 GET /api/users/me，nickname 已成功更新为 DemoUser1_test

7) Favorites 链路
- 结果：PASS（主链路）
- GET /api/users/me/favorites：200 + ApiResponse
- POST /api/users/me/favorites/{productId}：200 + favorited=true
- DELETE /api/users/me/favorites/{productId}：200 + favorited=false
- 收藏列表数量增减与操作一致

8) GET /api/admin/users
- 结果：PASS
- 普通用户：403 + ApiResponse
- 管理员：200 + ApiResponse

9) GET /api/admin/logs
- 结果：PASS
- 普通用户：403 + ApiResponse
- 管理员：200 + ApiResponse
- 返回 list/page 结构正常

10) GET /api/admin/stats/products
- 结果：PASS
- 普通用户：403 + ApiResponse
- 管理员：200 + ApiResponse
- 返回 series/total/dimension/description 结构正常

11) GET /api/admin/stats/trades
- 结果：PASS
- 普通用户：403 + ApiResponse
- 管理员：200 + ApiResponse
- 返回 series/total/dimension/description 结构正常

12) GET /api/admin/stats/users
- 结果：PASS
- 普通用户：403 + ApiResponse
- 管理员：200 + ApiResponse
- 返回 series/total/dimension/description 结构正常

13) GET /api/products
- 结果：PASS（正常分页、关键词筛选、分类筛选）
- GET /api/products?page=1&size=20：200 + ApiResponse
- GET /api/products?keyword=教材：200 + ApiResponse
- GET /api/products?categoryId=2：200 + ApiResponse

14) GET /api/products?page=0&size=999
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：返回 HTTP 422，响应体为 FastAPI 默认 {"detail":[...]}
- 2026-06-20 复测：返回 HTTP 422 + ApiResponse，data.errors 中已正确给出 page / size 校验失败信息
- 说明：分页参数越界的校验与统一错误结构现已同时生效，对应 ISSUE-005 已修复

15) GET /api/products/{productId}
- 结果：PASS
- GET /api/products/1001：200 + ApiResponse，商品详情返回正常
- GET /api/products/999999：404 + ApiResponse，body 为 {"code":4040,"message":"product not found","data":{"productId":999999},...}
- 说明：products 详情接口的 404 语义已生效，products 侧不再构成 ISSUE-007

16) POST /api/products（正常创建）
- 结果：PASS
- 使用合法 JSON 请求体创建成功，返回 200 + ApiResponse
- 实际新建商品：id=1006，status=PENDING，images=[]，seller 信息完整

17) POST /api/products（缺必填字段）
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：缺少 title 时返回 HTTP 422，响应体为 FastAPI 默认 {"detail":[...]}
- 2026-06-20 复测：缺少 title/price/categoryId 时返回 HTTP 422 + ApiResponse，body 中已包含 code/message/data/requestId/timestamp
- 说明：请求体验证错误已统一包装，对应 ISSUE-004 在 products 侧已修复

18) GET /api/orders/{orderId}
- 结果：PASS
- GET /api/orders/5001：200 + ApiResponse，data 已包含 productId、buyerId、sellerId、amount、remark、status、createdAt、expireAt
- GET /api/orders/999999：404 + ApiResponse，body 为 {"code":4040,"message":"order not found","data":{"orderId":999999},...}
- 说明：orders 详情接口字段完整性与 404 语义均已通过复测，对应 ISSUE-002 已修复，ISSUE-007 的 orders 部分已排除

19) POST /api/orders（商品拥有者下单）
- 结果：PASS
- 使用 tokenUser 对 productId=1001 下单时，返回 409 + ApiResponse
- 响应为 {"code":4090,"message":"product owner cannot buy own product","data":{"productId":1001},...}
- 说明：商品拥有者不能购买自己的商品，这条业务规则生效，不能作为缺陷记录

20) POST /api/orders（缺必填字段）
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：缺少 productId 时返回 HTTP 422，响应体为 FastAPI 默认 {"detail":[...]}
- 2026-06-20 复测：缺少 productId 时返回 HTTP 422 + ApiResponse，body 中已包含 code/message/data/requestId/timestamp
- 说明：请求体验证错误已统一包装，对应 ISSUE-004 在 orders 侧已修复

21) GET /api/reports/{reportId}
- 结果：PASS
- GET /api/reports/7001：200 + ApiResponse，data 已包含 reporterId、targetType、targetId、reason、status、createdAt、handledAt、assigneeId、handleAction、handleReason
- GET /api/reports/999999：404 + ApiResponse，body 为 {"code":4040,"message":"举报记录 999999 不存在","data":null,...}
- 说明：reports 详情接口字段完整性与 404 语义均已通过复测，对应 ISSUE-003、ISSUE-007 已修复

22) POST /api/reports（未带 Authorization）
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：未带 Authorization 仍返回 200 + ApiResponse，并成功创建举报
- 2026-06-20 复测：返回 401 + ApiResponse，message=missing bearer token
- 说明：reports 写操作已接入 Bearer 校验，ISSUE-006 在 reports 侧已修复

23) POST /api/reports（缺必填字段）
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：缺少 reason 时返回 HTTP 422，响应体为 FastAPI 默认 {"detail":[...]}
- 2026-06-20 复测：缺参时返回 HTTP 422 + ApiResponse，body 中已包含 code/message/data/requestId/timestamp
- 说明：请求体验证错误已统一包装，对应 ISSUE-004 在 reports 侧已修复

24) POST /api/appeals（未带 Authorization）
- 结果：FAIL
- 2026-06-19 初测：未带 Authorization 仍返回 200 + ApiResponse，并成功提交申诉
- 实际返回 data：{"submitted":true,"targetType":"report","targetId":7001,"reason":"申诉测试"}
- 2026-06-20 复测：未带 Authorization 仍返回 200 + ApiResponse，问题仍存在
- 对应 ISSUE-006：已复测确认
- 说明：当前后端A剩余待修问题已收敛为 appeals 写操作未接入 Bearer 校验

25) POST /api/appeals（缺必填字段）
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：缺少 targetId 时返回 HTTP 422，响应体为 FastAPI 默认 {"detail":[...]}
- 2026-06-20 复测：缺参时返回 HTTP 422 + ApiResponse，body 中已包含 code/message/data/requestId/timestamp
- 说明：请求体验证错误已统一包装，对应 ISSUE-004 在 appeals 侧已修复

26) POST /api/auth/refresh
- 结果：PASS（2026-06-20 复测已修复）
- 2026-06-19 初测：使用合法 refreshToken 请求后返回 200 + ApiResponse，但 data 中仅包含 accessToken、refreshToken、expiresIn，未返回 user
- 2026-06-20 使用合法 refreshToken 构造合法 JSON 请求体再次复测：返回 200 + ApiResponse
- data 中已包含 accessToken、refreshToken、expiresIn、user
- 说明：AuthTokens 契约已对齐，对应 ISSUE-001 已修复

27) Orders 状态机 / 幂等复测
- 结果：PASS
- 订单 5003：
  - seller-confirm：200 + CONFIRMED
  - 重复 seller-confirm：200 + CONFIRMED（幂等成功）
  - complete：200 + COMPLETED
  - 重复 complete：200 + COMPLETED（幂等成功）
  - completed 后 cancel：409 + ApiResponse，message=order cannot be cancelled from current status
- 订单 5004：
  - cancel：200 + CANCELLED
  - 重复 cancel：200 + CANCELLED（幂等成功）
  - cancelled 后 complete：409 + ApiResponse，message=order cannot be completed from current status
- 说明：orders 状态机约束与幂等策略均已生效，对应 ISSUE-008 已修复

28) POST /api/products（未带 Authorization）
- 结果：PASS
- 返回 401 + ApiResponse，message=missing bearer token
- 说明：products 写操作已接入 Bearer 校验，不属于 ISSUE-006 范围

29) POST /api/orders（未带 Authorization）
- 结果：PASS
- 返回 401 + ApiResponse，message=missing bearer token
- 说明：orders 写操作已接入 Bearer 校验，不属于 ISSUE-006 范围

30) images URL 原始值复测
- 结果：PASS
- 数据库 `product_images.url` 的 `HEX(url)` 均显示为正常 URL 字节流，不含空格或反引号字节
- 前期看到的反引号/空格现象未在真实 payload 中复现
- 对应 ISSUE-013 关闭

31) 2026-06-20 定点复测 ISSUE-001 / ISSUE-004 / ISSUE-005 / ISSUE-006
- 结果：PARTIAL
- `POST /api/auth/refresh`：200 + ApiResponse，`data` 已返回 `user`
- `POST /api/products`、`POST /api/orders`、`POST /api/reports`、`POST /api/appeals` 缺参：均已返回 422 + ApiResponse
- `GET /api/products?page=0&size=999`：已返回 422 + ApiResponse
- `POST /api/reports` 未带 Authorization：已返回 401 + ApiResponse
- `POST /api/appeals` 未带 Authorization：仍返回 200 + ApiResponse
- 说明：ISSUE-001 / ISSUE-004 / ISSUE-005 已修复；ISSUE-006 已收敛为 appeals 单点问题

32) 2026-06-20 切换到 MySQL 数据源后复测 images URL
- 结果：PASS
- 直接查询 MySQL `product_images.url`，`HEX(url)` 为正常 URL 字节流
- `GET /api/products/1001` 返回 `images[0]` 后，读取原始字符串并查看 hex，结果为正常 URL 字节流
- `GET /api/users/me/favorites?page=1&size=20` 返回列表中的 `images[0]` 后，读取原始字符串并查看 hex，结果同样为正常 URL 字节流
- 说明：`Favorites/Products` 图片 URL 问题不是后端真实缺陷，ISSUE-013 保持 Closed