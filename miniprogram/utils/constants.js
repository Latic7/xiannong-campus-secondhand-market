// ──────────────────────────────────────────────
//  全局常量与状态枚举映射
//  前端展示所需的中文文案、颜色等统一在此维护，
//  后端状态枚举变更时只需改这一处
// ──────────────────────────────────────────────

// ── 微信云托管环境配置 ─────────────────────────
// 在云托管控制台 → 环境概览 中查看环境ID
const CLOUD_ENV = 'xiannong-prod-d2gldqk278f8b5fee'

// ── 商品状态 ───────────────────────────────────
const PRODUCT_STATUS = {
  DRAFT: { label: '草稿', color: '#999' },
  PENDING: { label: '待审核', color: '#f0ad4e' },
  PUBLISHED: { label: '已发布', color: '#5cb85c' },
  REMOVED: { label: '已下架', color: '#999' },
  SOLD: { label: '已售出', color: '#ff3b30' },
}

// ── 订单状态 ───────────────────────────────────
const ORDER_STATUS = {
  CREATED: { label: '待确认', color: '#f0ad4e' },
  RESERVED: { label: '已预订', color: '#5bc0de' },
  CONFIRMED: { label: '已确认', color: '#5cb85c' },
  COMPLETED: { label: '已完成', color: '#337ab7' },
  CANCELLED: { label: '已取消', color: '#999' },
}

// ── 举报状态 ───────────────────────────────────
const REPORT_STATUS = {
  OPEN: { label: '处理中', color: '#f0ad4e' },
  REJECTED: { label: '已驳回', color: '#999' },
  HANDLED: { label: '已处理', color: '#5cb85c' },
}

// ── 用户状态 ───────────────────────────────────
const USER_STATUS = {
  ACTIVE: { label: '正常', color: '#5cb85c' },
  BANNED: { label: '已封禁', color: '#d9534f' },
}

function normalizeStatus(status) {
  return String(status || '').toUpperCase()
}

function getStatusMeta(map, status, fallbackLabel = '未知') {
  const key = normalizeStatus(status)
  return map[key] || { label: status || fallbackLabel, color: '#999' }
}

// ── 排序选项 ───────────────────────────────────
const SORT_OPTIONS = [
  { value: 'createdAt_desc', label: '最新发布' },
  { value: 'createdAt_asc', label: '最早发布' },
  { value: 'price_asc', label: '价格从低到高' },
  { value: 'price_desc', label: '价格从高到低' },
]

// ── 分页默认值 ────────────────────────────────
const PAGE_DEFAULT = 1
const SIZE_DEFAULT = 20

// ── 图片上传限制 ───────────────────────────────
const IMAGE_MAX_COUNT = 9
const IMAGE_MAX_SIZE = 5 * 1024 * 1024  // 5MB

// ── 存储键（供 utils/storage.js 使用）──────────
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_access_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  TOKEN_EXPIRE_AT: 'auth_expire_at',
  USER_INFO: 'auth_user_info',
}

module.exports = {
  CLOUD_ENV,
  PRODUCT_STATUS,
  ORDER_STATUS,
  REPORT_STATUS,
  USER_STATUS,
  SORT_OPTIONS,
  PAGE_DEFAULT,
  SIZE_DEFAULT,
  IMAGE_MAX_COUNT,
  IMAGE_MAX_SIZE,
  STORAGE_KEYS,
  normalizeStatus,
  getStatusMeta,
}
