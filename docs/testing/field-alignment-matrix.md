# 字段核对表

第一阶段最小范围 · 基于 openapi.yaml 与当前实现代码

---

## A. 全局统一返回结构（所有接口）

| 字段 | OpenAPI 期望 | 当前实现 | 结论 |
|------|-------------|----------|------|
| code | integer，成功为0 | 成功固定0；错误使用业务码 | 对齐 |
| message | string，默认ok | 成功"ok"；错误为具体文本 | 对齐 |
| data | object/nullable | 成功data为dict；错误可为null | 对齐 |
| requestId | string | uuid4字符串 | 对齐 |
| timestamp | date-time(UTC) | ISO8601 +00:00 | 对齐 |

> ⚠️ 注意：触发FastAPI/Pydantic默认422错误时，响应为默认结构（非ApiResponse），见问题ISSUE-002。

---

## B1. POST /api/auth/wx-login

| 字段 | 必填 | 类型 | 当前实现 | 结论 |
|------|:----:|------|----------|------|
| code | 是 | string | 读取并用于换取openid | 通过 |
| clientId | 否 | string | 允许传入 | 通过 |
| accessToken | 是 | string | 有 | 通过 |
| refreshToken | 是 | string | 有 | 通过 |
| expiresIn | 是 | int | 有 | 通过 |
| user | 是 | UserProfile | 有 | 通过 |
| user.id | 是 | int | 有 | 通过 |
| user.nickname | 是 | string | 有 | 通过 |
| user.avatar | 是 | uri | 有 | 通过 |
| user.score | 是 | int | 100 | 通过 |
| user.status | 是 | active/banned | active | 通过 |
| user.favorites | 否 | nullable | 未返回 | 可接受 |
| user.college | 否 | nullable | 未返回 | 可接受 |
| user.contact | 否 | nullable | 未返回 | 可接受 |

---

## B2. POST /api/auth/refresh

| 字段 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| refreshToken(请求体) | 必填 | 有JWT校验 | 通过 |
| accessToken(响应) | 必填 | 有 | 通过 |
| refreshToken(响应) | 必填 | 有 | 通过 |
| expiresIn | 必填 | 有 | 通过 |
| user | 必填 | 缺失 | **不通过** |

---

## B3. GET /api/auth/me

| 检查项 | OpenAPI | 当前实现 | 结论 |
|--------|---------|----------|------|
| Bearer鉴权 | 需要 | 已校验，无效返回401 | 通过 |
| id/nickname/avatar/score/status | 必填 | 有 | 通过 |
| favorites/college/contact | 可空 | 未返回 | 可接受 |

---

## B4. GET /api/users/me

| 检查项 | OpenAPI | 当前实现 | 结论 |
|--------|---------|----------|------|
| Bearer鉴权 | 需要 | 未校验，不带token也返回200 | **不通过** |
| 必填字段 | 有 | 有 | 通过 |

---

## B5. GET /api/products

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| page参数 | ≥1，默认1 | 不校验，page=0也接受 | **不通过** |
| size参数 | 1~100，默认20 | 不校验，size=999也接受 | **不通过** |
| keyword/sort/categoryId | 可选 | 回显到filters | 通过 |
| data.list | Product数组 | 返回[] | 最小可用 |
| data.page | 必填 | page/size回显，total=0 | 最小可用 |
| data.filters | 可选 | 有keyword/sort/categoryId | 通过 |

---

## B6. POST /api/products

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| Bearer鉴权 | 需要 | 未校验 | **不通过** |
| title/price/categoryId | 必填 | 有 | 通过 |
| description/images | 可选 | 有/空列表 | 通过 |
| 响应id/title/price | 必填 | 有(1001) | 通过 |
| 响应status | 枚举 | pending | 通过 |
| 其他可空字段 | 可空 | 部分有 | 可接受 |

---

## B7. GET /api/products/{productId}

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| 必填字段(id/title/price/status) | 必须有 | 有 | 通过 |
| 资源不存在返回404 | 需要 | 始终200返回"Draft Product" | **不通过** |

---

## B8. POST /api/orders

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| Bearer鉴权 | 需要 | 未校验 | **不通过** |
| productId(请求体) | 必填 | 有 | 通过 |
| 响应id/productId/status | 必填 | id=5001, status=created | 通过 |
| 重复下单/状态机限制 | 需要 | 未实现，永远成功 | **不通过** |

---

## B9. GET /api/orders/{orderId}

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| 响应data完整性 | 完整Order对象 | 只返回{id,status} | **不通过** |
| 资源不存在返回404 | 需要 | 始终200 | **不通过** |

---

## B10. POST /api/reports

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| Bearer鉴权 | 需要 | 未校验 | **不通过** |
| targetType/targetId/reason | 必填 | 有 | 通过 |
| 响应id/status | 需要 | id=7001, status=open | 通过 |
| 重复举报幂等 | 需要 | 未实现 | **不通过** |

---

## B11. GET /api/reports/{reportId}

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| 响应data完整性 | 完整Report字段 | 只返回{id,status} | **不通过** |
| 资源不存在返回404 | 需要 | 始终200 | **不通过** |

---

## B12. GET /api/admin/stats/overview

| 项目 | OpenAPI | 当前实现 | 结论 |
|------|---------|----------|------|
| users/products/orders/reports | int计数 | 全部返回0 | 通过 |
| 管理员鉴权 | 应限制 | 未实现 | 待完善 |

> 📌 鉴权说明：OpenAPI未细化管理员角色，按项目约定后续需增加权限控制，当前stub阶段未实现。

✅ 基于静态代码+OpenAPI对比生成 · 实际表现以运行时测试为准