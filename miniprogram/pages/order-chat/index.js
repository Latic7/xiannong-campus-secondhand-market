const orderService = require('../../services/order')
const chatSocket = require('../../services/chatSocket')
const { ORDER_STATUS, getStatusMeta } = require('../../utils/constants')
const { getUserInfo } = require('../../utils/storage')
const orderUnread = require('../../utils/orderUnread')

Page({
  data: {
    orderId: '',
    order: null,
    messages: [],
    inputValue: '',
    inputFocus: false,
    loading: true,
    sending: false,
    currentUserId: null,
    isTerminal: false,
    page: 1,
    hasMore: false,
  },

  onLoad(options) {
    const orderId = options.orderId || ''
    this.setData({ orderId })
    const user = getUserInfo()
    this.setData({ currentUserId: user ? user.id : null })
    if (!orderId) {
      this.setData({ loading: false })
      wx.showToast({ title: '订单 ID 缺失', icon: 'none' })
      return
    }
    this.loadOrder()
  },

  onUnload() {
    chatSocket.off('onMessage')
    chatSocket.close()
  },

  onShow() {
    if (this.data.orderId && !this.data.loading) {
      this.loadMessages()
    }
  },

  // ── Load order detail ──
  async loadOrder() {
    try {
      const data = await orderService.getDetail(this.data.orderId)
      const meta = getStatusMeta(ORDER_STATUS, data.status)
      const isTerminal = data.status === 'CANCELLED' || data.status === 'COMPLETED'
      this.setData({
        order: {
          ...data,
          amountText: data.amount == null ? '待确认' : '¥' + Number(data.amount).toFixed(2).replace(/\.00$/, ''),
          statusText: meta.label,
          statusColor: meta.color,
          productTitle: data.product?.title || '商品信息不可用',
          productImage: data.product?.image || '',
        },
        isTerminal,
        loading: false,
      })
      this.loadMessages()
    } catch (err) {
      this.setData({ loading: false })
      wx.showToast({ title: err.message || '加载失败', icon: 'none' })
    }
  },

  // ── Load messages via REST, then connect WebSocket for real-time updates ──
  async loadMessages() {
    try {
      const data = await orderService.getMessages(this.data.orderId, { page: 1, size: 50 })
      const list = (data.list || []).map(m => this.formatMessage(m))
      this.setData({
        messages: list,
        page: 2,
        hasMore: list.length >= 50,
      })
      // Mark as read
      if (list.length > 0) {
        const lastMsg = list[list.length - 1]
        orderUnread.markAsRead(this.data.orderId, lastMsg.id)
      }
      // Connect WebSocket for real-time updates (only for active orders)
      if (!this.data.isTerminal) {
        this._connectSocket()
      }
    } catch (err) {
      console.warn('加载消息失败:', err.message)
    }
  },

  // ── Connect WebSocket and set up handlers ──
  _connectSocket() {
    chatSocket.connect(this.data.orderId)
    chatSocket.on('onMessage', (data) => {
      if (data.type === 'new_message') {
        const msg = this.formatMessage(data.data)
        // Avoid duplicates
        const exists = this.data.messages.some(m => m.id === msg.id)
        if (!exists) {
          this.setData({
            messages: [...this.data.messages, msg],
          })
        }
        orderUnread.markAsRead(this.data.orderId, msg.id)
      }
    })
  },

  formatMessage(msg) {
    const isMine = this.data.currentUserId && msg.senderId === this.data.currentUserId
    const time = msg.createdAt ? this.fmtTime(msg.createdAt) : ''
    return {
      ...msg,
      isMine,
      time,
    }
  },

  fmtTime(t) {
    const d = new Date(t)
    const pad = (n) => String(n).padStart(2, '0')
    return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  // ── Keep input focused after send ──
  _refocusInput() {
    this.setData({ inputFocus: false })
    wx.nextTick(() => {
      this.setData({ inputFocus: true })
    })
  },

  onBlur() {
    this.setData({ inputFocus: false })
  },

  // ── Send via WebSocket (fallback to REST) ──
  async onSend() {
    const content = this.data.inputValue.trim()
    if (!content || this.data.sending || this.data.isTerminal) return

    this.setData({ sending: true })
    // Try WebSocket first
    const sent = chatSocket.send(content)
    if (sent) {
      this.setData({ inputValue: '', sending: false })
      this._refocusInput()
      return
    }
    // Fallback to REST API
    try {
      const msg = await orderService.sendMessage(this.data.orderId, { content })
      const formatted = this.formatMessage(msg)
      this.setData({
        messages: [...this.data.messages, formatted],
        inputValue: '',
        sending: false,
      })
      this._refocusInput()
      orderUnread.markAsRead(this.data.orderId, msg.id)
    } catch (err) {
      this.setData({ sending: false })
      wx.showToast({ title: err.message || '发送失败', icon: 'none' })
    }
  },

  onPullDownRefresh() {
    this.loadMessages().finally(() => wx.stopPullDownRefresh())
  },

  onRetry() {
    this.setData({ loading: true })
    this.loadOrder()
  },
})
