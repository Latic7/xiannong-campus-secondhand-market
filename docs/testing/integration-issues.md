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
| 2026-06-09 | ISSUE-006 | 全局 | 大多数接口未鉴权仍返回200 | 后端A | P0 | Open |
| 2026-06-09 | ISSUE-002 | Orders | 订单详情 data 缺 productId | 后端B | P1 | Open |
| 2026-06-09 | ISSUE-008 | Orders | 状态机/幂等约束缺失 | 后端B | P1 | Open |
| 2026-06-09 | ISSUE-003 | Reports | 举报详情 data 缺关键字段 | 后端C | P1 | Open |
| 2026-06-18 | ISSUE-009 | Admin | 非管理员访问 /api/admin/stats/overview 返回 {"detail":...}，未走 ApiResponse | 后端A | P0 | Open |
| 2026-06-18 | ISSUE-010 | Auth/Users | /api/auth/me 与 /api/users/me 返回字段为 is_admin，但 OpenAPI required 为 isAdmin | 后端A | P0 | Open |
| 2026-06-18 | ISSUE-011 | Auth/Users | UserProfile 返回含 publishedCount/soldCount，若 OpenAPI 未定义则契约不一致 | 后端A | P1 | Open |
| 2026-06-18 | ISSUE-013 | Favorites/Products | 收藏列表中的图片 URL 带反引号和空格，疑似脏数据/seed 问题 | 后端B | P1 | Open |

---

## 一、字段不一致（Field Mismatch）

### ISSUE-001（POST /api/auth/refresh：data 缺少 user）
- 类型：字段不一致
- 接口：POST /api/auth/refresh
- 优先级：P0
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) 准备一个合法 refreshToken（typ=refresh，使用同一 JWT_SECRET）
  2) 请求体：{"refreshToken":"..."}
- OpenAPI 期望：
  - 200：data 为 AuthTokens（required: accessToken/refreshToken/expiresIn/user）
- 当前实际：
  - 200：data 仅有 accessToken/refreshToken/expiresIn（缺 user）
- 影响范围：
  - 前端刷新登录态后无法更新 user，容易联调卡住
- 备注：
  - 临时绕过：refresh 后再调 GET /api/auth/me（不建议作为最终契约）

---

### ISSUE-002（GET /api/orders/{orderId}：data 不是完整 Order）
- 类型：字段不一致
- 接口：GET /api/orders/{orderId}
- 优先级：P1
- 责任人：后端B
- 状态：Open
- 复现步骤：
  1) GET /api/orders/5001
- OpenAPI 期望：
  - 200：data 为 Order（required: id, productId, status）
- 当前实际：
  - 200：data 只有 id/status（缺 productId）
- 影响范围：
  - 前端订单详情无法展示关联商品/状态信息
- 备注：
  - 需要后端补齐返回字段（至少 productId）

---

### ISSUE-003（GET /api/reports/{reportId}：data 不是完整 Report）
- 类型：字段不一致
- 接口：GET /api/reports/{reportId}
- 优先级：P1
- 责任人：后端C
- 状态：Open
- 复现步骤：
  1) GET /api/reports/7001
- OpenAPI 期望：
  - 200：data 为 Report（required: id,targetType,targetId,reason,status）
- 当前实际：
  - 200：data 只有 id/status（缺 targetType/targetId/reason）
- 影响范围：
  - 前端无法展示举报详情（目标与原因缺失）
- 备注：
  - 需要后端补齐返回字段

---

### ISSUE-010（GET /api/auth/me、GET /api/users/me：is_admin vs isAdmin 字段命名不一致）
- 类型：字段不一致
- 接口：
  - GET /api/auth/me
  - GET /api/users/me
- 优先级：P0
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) 生成仅包含 uid/sub/nickname/typ/exp 的 access token（不包含 isAdmin）
  2) 用普通用户 token（uid=1）请求 GET /api/auth/me
  3) 用管理员 token（uid=10）请求 GET /api/auth/me
  4) 同样方式请求 GET /api/users/me
- OpenAPI 期望：
  - UserProfile.required 包含 isAdmin
  - 前后端联调用字段应为 isAdmin
- 当前实际：
  - 返回字段为 is_admin
  - 普通用户返回 is_admin=false，管理员返回 is_admin=true
- 影响范围：
  - 字段命名与契约不一致，前端若按 isAdmin 取值会失败
- 备注：
  - 当前“是否管理员”的识别逻辑本身是正确的，问题在返回字段命名
  - 建议保持数据库字段 is_admin 不变，返回层统一映射为 isAdmin

---

### ISSUE-011（GET /api/auth/me、GET /api/users/me：publishedCount/soldCount 是否纳入契约）
- 类型：字段不一致
- 接口：
  - GET /api/auth/me
  - GET /api/users/me
- 优先级：P1
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) 用合法 access token 请求 GET /api/auth/me
  2) 用合法 access token 请求 GET /api/users/me
- OpenAPI 期望：
  - UserProfile 需明确列出返回字段
- 当前实际：
  - data 中返回 publishedCount / soldCount
  - 若 OpenAPI 当前未定义这两个字段，则属于契约不一致
- 影响范围：
  - 前端/测试无法确认这两个字段是否为稳定契约
- 备注：
  - 二选一：
    - 若要保留：在 OpenAPI UserProfile 中补充定义
    - 若不需要：后端移除返回字段，保持契约最小化

---

### ISSUE-013（GET /api/users/me/favorites：图片 URL 含反引号和空格）
- 类型：字段不一致
- 接口：GET /api/users/me/favorites
- 优先级：P1
- 责任人：后端B
- 状态：Open
- 复现步骤：
  1) 用普通用户 access token 请求 GET /api/users/me/favorites?page=1&size=20
- OpenAPI 期望：
  - images 为标准 URL 字符串数组
- 当前实际：
  - images 元素类似 " `https://cdn.example.com/p/demo-1004-1.jpg` "
  - URL 前后存在空格及反引号，不像正常 URI
- 影响范围：
  - 前端图片加载可能失败
  - 契约测试中的 URI 格式校验会失败
- 备注：
  - 更像 seed 数据或图片 URL 组装逻辑问题

---

## 二、返回结构不一致（Envelope / Validation / Auth Semantics）

### ISSUE-004（请求体缺必填字段时：返回 FastAPI 默认 422，不是 ApiResponse 外层）
- 类型：返回结构不一致
- 接口：示例 POST /api/products（同类：POST /api/orders、POST /api/reports 等）
- 优先级：P0
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) POST /api/products
  2) 请求体缺 title/price/categoryId 任意一个
- OpenAPI 期望：
  - 失败也应返回 ApiResponse 外层：code/message/data/requestId/timestamp
- 当前实际：
  - 多数情况下返回 {"detail":[...]}（没有 code/requestId/timestamp）
- 影响范围：
  - 前端统一错误处理无法按 code/message 解析
- 备注：
  - 需要全局异常处理把 422 转成 ApiResponse（后端基础设施）

---

### ISSUE-005（GET /api/products：page/size 越界不报错）
- 类型：返回结构不一致
- 接口：GET /api/products
- 优先级：P1
- 责任人：后端B
- 状态：Open
- 复现步骤：
  1) GET /api/products?page=0&size=999
- OpenAPI 期望：
  - page>=1，size<=100；越界应返回失败 ApiResponse
- 当前实际：
  - 仍返回 200 + ApiResponse，且 page/size 原样回显
- 影响范围：
  - 前端分页逻辑可能异常（page=0）
- 备注：
  - 需要参数校验（依赖注入或 pydantic 校验）

---

### ISSUE-006（OpenAPI 顶层 bearerAuth：多数接口未带 token 仍返回 200）
- 类型：返回结构不一致
- 接口：示例 GET /api/users/me、POST /api/products、POST /api/orders、POST /api/reports 等
- 优先级：P0
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) 不带 Authorization 调用上述接口
- OpenAPI 期望：
  - 除 /api/auth/wx-login 显式 security: [] 外，其余默认需要 Bearer；未登录应 401 + ApiResponse
- 当前实际：
  - 多数接口仍返回 200（仅 /api/auth/me 做了 Bearer 校验）
- 影响范围：
  - 无法验证“已登录/未登录”行为差异；权限边界联调卡住
- 备注：
  - 需要统一鉴权依赖（后端实现工作；你这里只记录）

---

### ISSUE-007（资源不存在语义缺失：GET /api/products/{id}、GET /api/orders/{id}、GET /api/reports/{id} 均未实现 404）
- 类型：返回结构不一致
- 接口：
  - GET /api/products/{productId}
  - GET /api/orders/{orderId}
  - GET /api/reports/{reportId}
- 优先级：P1
- 责任人：后端B（products/orders）、后端C（reports）
- 状态：Open
- 复现步骤：
  1) 用任意不存在的 id 调用
- OpenAPI 期望：
  - 不存在应 404 + ApiResponse
- 当前实际：
  - 始终 200（返回占位数据）
- 影响范围：
  - 前端无法区分“真实不存在”和“占位成功”
- 备注：
  - 后续落库时必须补齐 404 语义

---

### ISSUE-009（非管理员访问后台接口时：403 未包装为 ApiResponse）
- 类型：返回结构不一致
- 接口：GET /api/admin/stats/overview
- 优先级：P0
- 责任人：后端A
- 状态：Open
- 复现步骤：
  1) 生成仅包含 uid/sub/nickname/typ/exp 的普通用户 access token（uid=1，不包含 isAdmin）
  2) 请求 GET /api/admin/stats/overview
- OpenAPI / 统一返回期望：
  - 403 + ApiResponse（code/message/data/requestId/timestamp）
- 当前实际：
  - 返回 {"detail":"admin permission required"}
- 影响范围：
  - 前端无法统一按 code/message 处理权限错误
  - 契约测试无法通过
- 备注：
  - 当前管理员识别逻辑本身是正确的（普通用户确实被拦截）
  - 问题在于 admin 依赖抛的是 HTTPException，未被全局转换成 ApiResponse
  - 建议：
    - 要么全局处理 HTTPException
    - 要么改为抛 BusinessError / 统一 api_error

---

## 三、状态不一致（State Machine / Idempotency Semantics）

### ISSUE-008（订单状态机未受约束：confirm/cancel/complete 可任意重复调用）
- 类型：状态不一致
- 接口：
  - POST /api/orders/{orderId}/seller-confirm
  - POST /api/orders/{orderId}/cancel
  - POST /api/orders/{orderId}/complete
- 优先级：P1
- 责任人：后端B
- 状态：Open
- 复现步骤：
  1) 对同一 orderId 重复调用 complete/cancel/confirm 任意组合
- 约定/期望（开工前约定清单）：
  - created -> reserved -> confirmed -> completed | cancelled
  - 不允许随意回退/重复完成
- 当前实际：
  - 直接返回目标状态，不检查前置状态
- 影响范围：
  - 联调无法验证状态机；后续落库易产生脏状态
- 备注：
  - 需要状态机与幂等策略（后端实现工作；你这里只记录）

---

## 四、数据库迁移脚本执行记录（第二阶段交付物）

记录原则：每次 schema.sql 或建库脚本有变化，都补一条记录，并在群里通知大家同步更新。

| 日期 | 变更摘要 | 影响表/字段 | 执行方式 | 执行人 | 结果 |
|------|----------|-------------|----------|--------|------|
| 2026-06-09 | users.id 自增主键 + openid 唯一索引；枚举小写口径统一 | users / products / orders / reports | MySQL SOURCE server/app/db/schema.sql | 后端D | OK |
| 2026-06-18 | 使用最新 schema.sql 重建 campus_market，验证 users.status 大写枚举与 is_admin 字段 | users | DROP/CREATE DATABASE + MySQL SOURCE app/db/schema.sql | 后端D | OK |

---

## 五、测试执行记录（2026-06-18，后端D）

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
- 普通用户（uid=1）：200 + data.is_admin=false
- 管理员（uid=10）：200 + data.is_admin=true
- 不带 token：401 + ApiResponse（code=10030）

3) GET /api/admin/stats/overview
- 结果：PARTIAL PASS
- 普通用户访问：已正确拦截，但返回 {"detail":"admin permission required"}，未走 ApiResponse
- 管理员访问：200 + ApiResponse 正常返回统计数据

4) 当前阶段结论
- “是否管理员”的识别链路已验证通过：当前实现按数据库 users.is_admin 判定，不依赖 token 中额外携带 isAdmin
- 仍需修复的契约问题：
  - 非管理员 403 未统一包装为 ApiResponse
  - UserProfile 返回字段 is_admin 与 OpenAPI 的 isAdmin 不一致
  - publishedCount / soldCount 是否纳入契约需统一决定

5) GET /api/users/me
- 结果：PASS
- 普通用户：200 + ApiResponse，is_admin=false
- 管理员：200 + ApiResponse，is_admin=true
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
- 备注：images URL 存在格式异常，已单独记录 ISSUE-013