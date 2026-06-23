// ──────────────────────────────────────────────
//  订单消息未读追踪
//  使用 localStorage 记录每个订单最后阅读的消息 ID
//  无需后端记录，前端自行判断未读
// ──────────────────────────────────────────────

const STORAGE_KEY = 'order_read_markers'

/** 获取所有订单的阅读记录 */
function getMarkers() {
  try {
    return wx.getStorageSync(STORAGE_KEY) || {}
  } catch (e) {
    return {}
  }
}

/** 保存阅读记录 */
function saveMarkers(markers) {
  try {
    wx.setStorageSync(STORAGE_KEY, markers)
  } catch (e) {
    // 存储满时静默失败
  }
}

/**
 * 标记某订单已读至指定消息
 * @param {number} orderId
 * @param {number} messageId
 */
function markAsRead(orderId, messageId) {
  if (!orderId || !messageId) return
  const markers = getMarkers()
  const prev = markers[orderId] || { lastReadId: 0 }
  if (messageId > prev.lastReadId) {
    markers[orderId] = { lastReadId: messageId, updatedAt: Date.now() }
    saveMarkers(markers)
  }
}

/**
 * 判断某订单是否有未读消息
 * @param {object} order - 订单对象（需包含 latestMessage）
 * @param {number} currentUserId - 当前登录用户 ID
 * @returns {boolean}
 */
function hasUnread(order, currentUserId) {
  if (!order || !order.latestMessage) return false
  if (order.latestMessage.senderId === currentUserId) return false
  const markers = getMarkers()
  const marker = markers[order.id]
  return !marker || order.latestMessage.id > marker.lastReadId
}

/**
 * 计算所有未读订单数
 * @param {object[]} orders
 * @param {number} currentUserId
 * @returns {number}
 */
function totalUnread(orders, currentUserId) {
  if (!orders || !orders.length) return 0
  return orders.filter(o => hasUnread(o, currentUserId)).length
}

module.exports = {
  markAsRead,
  hasUnread,
  totalUnread,
}
