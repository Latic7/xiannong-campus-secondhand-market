# 契约测试清单（第二阶段增量覆盖，按 OpenAPI 字段逐项对齐）

对照依据：
- docs/api/openapi.yaml（字段、必填、枚举、参数范围）
- 统一返回结构：code/message/data/requestId/timestamp（ApiResponse）

通用检查（每个接口都要看一眼）：
- 响应外层必须包含：code（int）、message（string）、data（object/nullable）、requestId（string）、timestamp（date-time）
- 成功时 code=0，message=ok（OpenAPI 示例）
- 列表接口分页参数：page>=1（默认 1），size 1~100（默认 20）

第二阶段增量目标（只定义“应测点”，可在联调时逐项勾掉）：
- 覆盖第二阶段新增接口：admin/users、admin/products/pending、admin/products/{id}/review、admin/reports、admin/reports/{id}/handle、admin/stats/*、admin/logs、appeals
- 覆盖状态分支：Product.status / Order.status / Report.status / User.status（枚举值与大小写完全一致）
- 覆盖权限分支：未登录(401)、非管理员(403)、资源不存在(404)、参数越界(4xx)

---

## 1. Auth

### 1.1 POST /api/auth/wx-login（成功路径）
- 安全：OpenAPI 写明 security: []（不需要 Bearer）
- 请求头：
  - Content-Type: application/json
- 请求体（WxLoginRequest）：
  - code（必填，string）
  - clientId（可选，string）
- 期望响应（200）：
  - 外层：ApiResponse（code/message/data/requestId/timestamp）
  - data（AuthTokens）必含：
    - accessToken（string）
    - refreshToken（string）
    - expiresIn（integer）
    - user（UserProfile 对象）
  - data.user（UserProfile）必含：
    - id（integer）
    - nickname（string）
    - avatar（string, uri）
    - score（integer）
    - status（string，enum：active | banned）
  - data.user 可选：
    - favorites（integer，可空）
    - college（string，可空）
    - contact（string，可空）

### 1.2 POST /api/auth/wx-login（失败路径，至少记录到问题表）
- 缺少 code / code 为空：OpenAPI 没写错误码细节，但应返回统一错误结构（ApiResponse）
- 微信服务不可用/返回 errcode：应返回统一错误结构（ApiResponse）
- 记录点：实际返回是否仍满足 code/message/requestId/timestamp；HTTP 状态码是否合理（401/502/500 等）

---

### 1.3 POST /api/auth/refresh（成功路径）
- 请求头：
  - Content-Type: application/json
- 请求体（TokenRefreshRequest）：
  - refreshToken（必填，string）
- 期望响应（200）：
  - 外层：ApiResponse
  - data（AuthTokens）：
    - accessToken（string）
    - refreshToken（string）
    - expiresIn（integer）
    - user（UserProfile）
  - 注意：OpenAPI 的 TokenResponse 示例里包含 user；如果实际实现缺少 user，需要记录“字段不一致”。

### 1.4 POST /api/auth/refresh（失败路径）
- refreshToken 缺失：应返回错误结构（ApiResponse）
- refreshToken 非法/过期：应返回错误结构（ApiResponse），通常 401

---

### 1.5 GET /api/auth/me（成功路径）
- 请求头：
  - Authorization: Bearer <accessToken>
- 期望响应（200）：
  - 外层：ApiResponse
  - data（UserProfile）字段同 1.1 的 user

### 1.6 GET /api/auth/me（失败路径）
- 不带 Authorization：应返回错误结构（ApiResponse），通常 401
- Authorization 不以 "Bearer " 开头：应返回错误结构（ApiResponse），通常 401
- token 非法：应返回错误结构（ApiResponse），通常 401

---

## 2. Users

### 2.1 GET /api/users/me（成功路径）
- 请求头：
  - Authorization: Bearer <accessToken>（OpenAPI 全局 security: bearerAuth）
- 期望响应（200）：
  - 外层：ApiResponse
  - data（UserProfile）字段同上

### 2.2 GET /api/users/me（失败路径）
- 未登录/缺 token：应返回错误结构（ApiResponse），通常 401
- 记录点：如果当前 stub 没做鉴权导致仍返回 200，这是“返回结构没问题但权限逻辑缺失”，记录到问题表（类型可写“返回语义不一致/权限缺失”）。

---

## 3. Products

### 3.1 GET /api/products（成功路径）
- Query 参数（OpenAPI components.parameters）：
  - page（int，>=1，默认 1）
  - size（int，1~100，默认 20）
  - keyword（string，可选）
  - sort（string，可选，例：createdAt_desc）
  - categoryId（int，可选）
- 期望响应（200）：
  - 外层：ApiResponse
  - data（ProductListPayload）必含：
    - list（Product 数组）
    - page（PageMeta：page/size/total）
  - data.filters（可选对象，OpenAPI 定义用于回显过滤条件）：
    - keyword（string，可空）
    - sort（string，可空）
    - categoryId（int，可空）
- Product（必含字段）：
  - id（integer）
  - title（string）
  - price（number/float）
  - status（string，enum：draft | pending | published | removed | sold）
- Product（常见可空字段，OpenAPI 标为 nullable）：
  - ownerId、description、categoryId、createdAt、updatedAt、favoriteCount、viewCount
  - images（array of uri string）

### 3.2 GET /api/products（失败路径）
- page=0（不满足 minimum=1）：应返回错误结构（ApiResponse）
- size=101（超过 maximum=100）：应返回错误结构（ApiResponse）
- 记录点：如果后端仍返回 200，需要记录“参数校验缺失”。

---

### 3.3 POST /api/products（成功路径）
- 请求头：
  - Content-Type: application/json
- 请求体（ProductCreateRequest）必填：
  - title（string）
  - price（number/float）
  - categoryId（integer）
- 请求体可选：
  - description（string，可空）
  - images（array<string uri>，默认 []）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：Product（至少含 id/title/price/status）
  - status 的枚举必须是：draft/pending/published/removed/sold（注意对齐）
- 记录点：如果返回 status 不在 enum 内，属于“状态不一致”。

### 3.4 POST /api/products（失败路径）
- 缺 title/price/categoryId：应返回错误结构（ApiResponse）（常见 422 或 400）
- 记录点：Pydantic 校验失败时，响应是否仍是统一 ApiResponse（很多框架默认不是，需要记录问题）。

---

### 3.5 GET /api/products/{productId}（成功路径）
- Path 参数：
  - productId（integer）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：Product（字段同 3.1）

### 3.6 GET /api/products/{productId}（失败路径）
- productId 不存在：应返回错误结构（ApiResponse），通常 404

---

## 4. Orders

### 4.1 POST /api/orders（成功路径）
- 请求头：
  - Content-Type: application/json
- 请求体（OrderCreateRequest）必填：
  - productId（integer）
- 请求体可选：
  - remark（string，可空）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：Order（必含字段）：
    - id（integer）
    - productId（integer）
    - status（string，enum：created | reserved | confirmed | completed | cancelled）
  - Order 可空字段（OpenAPI nullable）：
    - buyerId、sellerId、amount、remark、createdAt、expireAt

### 4.2 POST /api/orders（失败路径）
- 未登录：应返回错误结构（ApiResponse），通常 401
- productId 不存在：应返回错误结构（ApiResponse），通常 404
- 重复下单/状态不允许：按“开工前约定清单”的幂等要求，应该：
  - 要么幂等返回成功（不产生脏数据）
  - 要么明确返回错误结构（ApiResponse）并说明重复/状态不允许
- 记录点：目前 stub 可能没实现这些约束，全部记到问题表。

---

### 4.3 GET /api/orders/{orderId}（成功路径）
- Path 参数：
  - orderId（integer）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：Order（字段同 4.1）

### 4.4 GET /api/orders/{orderId}（失败路径）
- orderId 不存在：应返回错误结构（ApiResponse），通常 404

---

## 5. Reports & Admin（第一阶段如果包含）

### 5.1 POST /api/reports（成功路径）
- 请求头：
  - Content-Type: application/json
- 请求体（ReportCreateRequest）必填：
  - targetType（string，enum：product | user | order）
  - targetId（integer）
  - reason（string）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：Report（必含字段）：
    - id（integer）
    - targetType（enum：product | user | order）
    - targetId（integer）
    - reason（string）
    - status（enum：open | rejected | handled）
  - Report 可空字段（OpenAPI nullable）：
    - reporterId、createdAt、handledAt、assigneeId、handleAction、handleReason

### 5.2 POST /api/reports（失败路径）
- 未登录：应返回错误结构（ApiResponse），通常 401
- 重复举报（同一目标重复提交）：按幂等要求，要么幂等成功，要么错误结构明确提示

---

### 5.3 GET /api/reports/{reportId}（成功路径）
- Path 参数：
  - reportId（integer）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：Report（字段同 5.1）

### 5.4 GET /api/reports/{reportId}（失败路径）
- reportId 不存在：应返回错误结构（ApiResponse），通常 404

---

### 5.5 GET /api/admin/stats/overview（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data（StatsOverviewPayload）字段：
    - users（integer）
    - products（integer）
    - orders（integer）
    - reports（integer）

### 5.6 GET /api/admin/stats/overview（失败路径）
- 非管理员访问：应返回错误结构（ApiResponse），通常 403（若未实现则记录问题）

---

## 6. 第二阶段新增接口覆盖（Appeals / Admin）

### 6.1 POST /api/appeals（成功路径）
- 请求头：
  - Content-Type: application/json
- 请求体（AppealCreateRequest）：
  - 对照 OpenAPI：字段/必填/枚举
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI 定义（字段与类型一致）

### 6.2 POST /api/appeals（失败路径）
- 未登录：应返回错误结构（ApiResponse），通常 401
- 必填字段缺失：应返回错误结构（ApiResponse）；若返回默认 422，需要记录“返回结构不一致”

---

### 6.3 GET /api/admin/users（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（分页结构、列表元素字段完整性）
- 重点检查：
  - User.status 枚举：active | banned

### 6.4 GET /api/admin/users（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse

---

### 6.5 PATCH /api/admin/users/{userId}/status（成功路径）
- Path 参数：
  - userId（integer）
- 请求体：
  - 对照 OpenAPI：status/原因字段（如有）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（是否回传 updated/user 等）
- 重点检查：
  - 用户状态从 active <-> banned 的幂等与可回滚（重复封禁/重复解封）

### 6.6 PATCH /api/admin/users/{userId}/status（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse
- userId 不存在：404 + ApiResponse

---

### 6.7 GET /api/admin/products/pending（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（列表/分页/字段完整性）
- 重点检查：
  - 返回的 Product.status 是否均为 pending（或至少不包含不应出现的状态）

### 6.8 GET /api/admin/products/pending（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse

---

### 6.9 POST /api/admin/products/{productId}/review（成功路径）
- 请求体：
  - result（通过/驳回等枚举，按 OpenAPI）
  - reason（可选/必填按 OpenAPI）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（被审核商品的最新状态/审核信息）
- 重点检查（状态分支）：
  - pending -> published（通过）
  - pending -> removed（驳回/下架，按约定）

### 6.10 POST /api/admin/products/{productId}/review（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse
- productId 不存在：404 + ApiResponse
- 非 pending 状态审核：应返回 4xx + ApiResponse（记录实际语义）

---

### 6.11 GET /api/admin/reports（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（分页/筛选字段、列表元素字段完整性）
- 重点检查：
  - Report.status 枚举：open | rejected | handled
  - 可筛选/过滤字段（若 OpenAPI 定义）

### 6.12 GET /api/admin/reports（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse

---

### 6.13 POST /api/admin/reports/{reportId}/handle（成功路径）
- 请求体：
  - handleAction（枚举，按 OpenAPI）
  - handleReason（可选/必填按 OpenAPI）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（举报最新状态、处理人、处理时间、动作/原因）
- 重点检查（状态分支）：
  - open -> handled
  - open -> rejected

### 6.14 POST /api/admin/reports/{reportId}/handle（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse
- reportId 不存在：404 + ApiResponse
- 非 open 状态重复处理：应返回 4xx + ApiResponse（记录幂等策略）

---

### 6.15 GET /api/admin/stats/products（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（字段齐全，类型正确）

### 6.16 GET /api/admin/stats/trades（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（字段齐全，类型正确）

### 6.17 GET /api/admin/stats/users（成功路径）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（字段齐全，类型正确）

### 6.18 GET /api/admin/stats/*（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse

---

### 6.19 GET /api/admin/logs（成功路径）
- Query 参数：
  - page/size（同通用分页约束）
  - 过滤字段（若 OpenAPI 定义）
- 期望响应（200）：
  - 外层：ApiResponse
  - data：对照 OpenAPI（分页结构、日志字段完整性）

### 6.20 GET /api/admin/logs（失败路径）
- 未登录：401 + ApiResponse
- 非管理员：403 + ApiResponse
