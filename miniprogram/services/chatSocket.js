// ──────────────────────────────────────────────
//  WebSocket 聊天客户端
//  通过 WebSocket 实现订单内实时消息通信
//  自动处理连接、心跳、断线重连
// ──────────────────────────────────────────────
const { getAccessToken } = require('../utils/storage')

// 从 api.js 的 BASE_URL 推导 WebSocket 地址
const { BASE_URL } = require('../utils/api')
const WS_BASE = BASE_URL.replace(/^http/, 'ws')

let _orderId = null
let _handlers = {}
let _reconnectTimer = null
let _heartbeatTimer = null
let _connected = false

// ── 内部回调绑定（WeChat WebSocket 是全局单例）──
function _bindCallbacks() {
  wx.onSocketOpen(() => {
    console.log('[ChatSocket] 已连接')
    _connected = true
    _startHeartbeat()
    if (_handlers.onOpen) _handlers.onOpen()
  })

  wx.onSocketMessage((res) => {
    try {
      const data = JSON.parse(res.data)
      if (data.type === 'pong') return
      if (_handlers.onMessage) _handlers.onMessage(data)
    } catch (e) {
      console.warn('[ChatSocket] 消息解析失败:', e.message)
    }
  })

  wx.onSocketClose(() => {
    console.log('[ChatSocket] 已断开')
    _connected = false
    _stopHeartbeat()
    if (_handlers.onClose) _handlers.onClose()
    _scheduleReconnect()
  })

  wx.onSocketError(() => {
    console.warn('[ChatSocket] 连接错误')
    _connected = false
    _stopHeartbeat()
    _scheduleReconnect()
  })
}

// ── 心跳（每 30 秒，防止云托管超时断开）──
function _startHeartbeat() {
  _stopHeartbeat()
  _heartbeatTimer = setInterval(() => {
    try {
      wx.sendSocketMessage({ data: JSON.stringify({ type: 'ping' }) })
    } catch (e) {
      // ignore
    }
  }, 30000)
}

function _stopHeartbeat() {
  if (_heartbeatTimer) {
    clearInterval(_heartbeatTimer)
    _heartbeatTimer = null
  }
}

function _scheduleReconnect() {
  if (_reconnectTimer) return
  if (!_orderId) return
  _reconnectTimer = setTimeout(() => {
    _reconnectTimer = null
    if (_orderId) connect(_orderId)
  }, 3000)
}

// ── 公开 API ────────────────────────────────

/**
 * 连接到订单聊天 WebSocket
 * @param {number} orderId
 */
function connect(orderId) {
  if (!orderId) return

  // 如果已连接到同一订单，不重复连接
  if (_connected && _orderId === orderId) return

  // 断开旧连接
  if (_connected) {
    close()
  }

  _orderId = orderId

  const token = getAccessToken()
  if (!token) {
    console.warn('[ChatSocket] 未登录，无法连接')
    return
  }

  const url = `${WS_BASE}/api/ws/orders/${orderId}/chat?token=${token}`
  _bindCallbacks()
  wx.connectSocket({ url })
}

/**
 * 发送聊天消息
 * @param {string} content
 */
function send(content) {
  if (!_connected || !_orderId) {
    console.warn('[ChatSocket] 未连接，无法发送')
    return false
  }
  try {
    wx.sendSocketMessage({
      data: JSON.stringify({ type: 'message', content }),
    })
    return true
  } catch (e) {
    console.warn('[ChatSocket] 发送失败:', e.message)
    return false
  }
}

/**
 * 断开连接
 */
function close() {
  _orderId = null
  _connected = false
  _stopHeartbeat()
  clearTimeout(_reconnectTimer)
  _reconnectTimer = null
  try {
    wx.closeSocket()
  } catch (e) {
    // ignore
  }
}

/**
 * 注册事件回调
 * @param {'onOpen'|'onMessage'|'onClose'} event
 * @param {function} handler
 */
function on(event, handler) {
  _handlers[event] = handler
}

/**
 * 注销事件回调
 * @param {'onOpen'|'onMessage'|'onClose'} event
 */
function off(event) {
  delete _handlers[event]
}

module.exports = {
  connect,
  send,
  close,
  on,
  off,
}
