# 回归测试清单 v2（第二阶段）

范围：覆盖主链路成功路径 + 关键失败路径（未登录/非管理员/资源不存在/参数越界/状态机分支）。

对照依据：
- docs/api/openapi.yaml
- docs/testing/contract-test-checklist.md

前置条件：
- 后端服务可运行，基础环境变量已配置
- 数据库已按最新 schema 初始化，并具备最小演示数据

---

## 1. Auth（登录态）

### 1.1 登录成功
- 接口：POST /api/auth/wx-login
- 期望：
  - 200 + ApiResponse 外层完整
  - data.accessToken / refreshToken / expiresIn / user 字段齐全

### 1.2 刷新成功
- 接口：POST /api/auth/refresh
- 期望：
  - 200 + ApiResponse 外层完整
  - data.accessToken / refreshToken / expiresIn / user 字段齐全

### 1.3 获取当前用户
- 接口：GET /api/auth/me
- 期望：
  - 带 Bearer：200 + UserProfile
  - 不带/非法 Bearer：401 + ApiResponse

### 1.4 注销
- 接口：POST /api/auth/logout
- 期望：
  - 200 + ApiResponse

---

## 2. Users（个人资料 + 收藏）

### 2.1 查询个人资料
- 接口：GET /api/users/me
- 期望：
  - 带 Bearer：200 + UserProfile
  - 不带 Bearer：401 + ApiResponse

### 2.2 更新个人资料
- 接口：PUT /api/users/me
- 期望：
  - 带 Bearer：200 + ApiResponse（data.updated=true，或按 OpenAPI）
  - 请求体缺必填：4xx + ApiResponse

### 2.3 收藏列表
- 接口：GET /api/users/me/favorites?page=1&size=20
- 期望：
  - 200 + ApiResponse
  - data.list / data.page 字段齐全

### 2.4 新增收藏 / 取消收藏
- 接口：
  - POST /api/users/me/favorites/{productId}
  - DELETE /api/users/me/favorites/{productId}
- 期望：
  - 200 + ApiResponse
  - favorited=true/false 与动作一致
  - 重复收藏/重复取消：行为可解释（幂等成功或 4xx + ApiResponse）

---

## 3. Products（浏览 + 发布 + 图片）

### 3.1 列表检索
- 接口：GET /api/products?page=1&size=20
- 期望：
  - 200 + ApiResponse
  - 分页参数越界：4xx + ApiResponse

### 3.2 详情查询
- 接口：GET /api/products/{productId}
- 期望：
  - 存在：200 + Product
  - 不存在：404 + ApiResponse

### 3.3 发布商品
- 接口：POST /api/products
- 期望：
  - 200 + ApiResponse，返回 Product，status 在 draft/pending/published/removed/sold 枚举内
  - 缺必填：4xx + ApiResponse

### 3.4 编辑/删除（下架）
- 接口：
  - PUT /api/products/{productId}
  - DELETE /api/products/{productId}
- 期望：
  - 仅所有者/管理员可操作（越权：403 + ApiResponse）

### 3.5 图片上传/删除
- 接口：
  - POST /api/products/{productId}/images
  - DELETE /api/products/{productId}/images/{imageId}
- 期望：
  - 200 + ApiResponse
  - 图片 URL/ID 回传字段与 OpenAPI 一致

---

## 4. Orders（下单链路 + 状态机）

### 4.1 创建订单
- 接口：POST /api/orders
- 期望：
  - 200 + ApiResponse，status=created
  - productId 不存在：404 + ApiResponse

### 4.2 订单详情
- 接口：GET /api/orders/{orderId}
- 期望：
  - 200 + Order（至少 id/productId/status）
  - 不存在：404 + ApiResponse

### 4.3 卖家确认 / 取消 / 完成
- 接口：
  - POST /api/orders/{orderId}/seller-confirm
  - POST /api/orders/{orderId}/cancel
  - POST /api/orders/{orderId}/complete
- 期望：
  - 状态机：created -> reserved -> confirmed -> completed | cancelled
  - 非法跳转/重复调用：4xx + ApiResponse（或幂等策略可解释）
  - 越权：403 + ApiResponse

### 4.4 评价
- 接口：POST /api/orders/{orderId}/reviews
- 期望：
  - 仅交易参与人可提交（越权：403 + ApiResponse）
  - 状态不允许时：4xx + ApiResponse

---

## 5. Reports / Appeals（举报链路）

### 5.1 提交举报
- 接口：POST /api/reports
- 期望：
  - 200 + ApiResponse，status=open

### 5.2 举报详情
- 接口：GET /api/reports/{reportId}
- 期望：
  - 200 + Report（字段齐全）
  - 不存在：404 + ApiResponse

### 5.3 申诉提交
- 接口：POST /api/appeals
- 期望：
  - 200 + ApiResponse，字段与 OpenAPI 一致

---

## 6. Admin（后台治理）

### 6.1 用户列表与封禁/解封
- 接口：
  - GET /api/admin/users
  - PATCH /api/admin/users/{userId}/status
- 期望：
  - 非管理员：403 + ApiResponse
  - 状态变更幂等：重复封禁/解封行为可解释

### 6.2 待审核商品与审核
- 接口：
  - GET /api/admin/products/pending
  - POST /api/admin/products/{productId}/review
- 期望：
  - 审核导致产品状态变化符合约定

### 6.3 举报队列与处理
- 接口：
  - GET /api/admin/reports
  - POST /api/admin/reports/{reportId}/handle
- 期望：
  - 举报状态：open -> handled / rejected
  - 已处理举报重复处理：4xx + ApiResponse（或幂等策略可解释）

### 6.4 统计与日志
- 接口：
  - GET /api/admin/stats/overview
  - GET /api/admin/stats/products
  - GET /api/admin/stats/trades
  - GET /api/admin/stats/users
  - GET /api/admin/logs
- 期望：
  - 200 + ApiResponse，字段类型与 OpenAPI 一致
