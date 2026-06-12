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
