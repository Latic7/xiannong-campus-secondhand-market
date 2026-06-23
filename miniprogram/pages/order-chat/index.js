const orderService = require('../../services/order')
const { ORDER_STATUS, getStatusMeta } = require('../../utils/constants')
const { getUserInfo } = require('../../utils/storage')
const orderUnread = require('../../utils/orderUnread')

Page({
  data: {
    orderId: '',
    order: null,
    messages: [],
    inputValue: '',
    loading: true,
    sending: false,
    currentUserId: null,
    isTerminal: false,   // CANCELLED or COMPLETED → no more messages
    page: 1,
    hasMore: false,
  },

  onLoad(options) {
    const orderId = options.orderId || ''
    this.setData({ orderId })
    const user = getUserInfo()
    this.setData({ currentUserId: user ? user.id : null })
    this._pollTimer = null
    if (!orderId) {
      this.setData({ loading: false })
      wx.showToast({ title: '订单 ID 缺失', icon: 'none' })
      return
    }
    this.loadOrder()
  },

  onUnload() {
    // Stop polling when leaving the page
    if (this._pollTimer) {
      clearInterval(this._pollTimer)
      this._pollTimer = null
    }
  },

  onShow() {
    // Refresh messages when page becomes visible
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

  // ── Start auto-polling (every 5s for active orders) ──
  _startPolling() {
    if (this._pollTimer) return
    if (this.data.isTerminal) return
    this._pollTimer = setInterval(() => {
      this._pollNewMessages()
    }, 5000)
  },

  // ── Poll for new messages (lightweight, only fetches latest) ──
  async _pollNewMessages() {
    try {
      const data = await orderService.getMessages(this.data.orderId, { page: 1, size: 50 })
      const newList = (data.list || []).map(m => this.formatMessage(m))
      const oldIds = new Set(this.data.messages.map(m => m.id))
      // Only append messages we don't already have
      const appended = newList.filter(m => !oldIds.has(m.id))
      if (appended.length > 0) {
        this.setData({
          messages: [...this.data.messages, ...appended],
        })
        // Mark new messages as read
        const lastMsg = appended[appended.length - 1]
        orderUnread.markAsRead(this.data.orderId, lastMsg.id)
      }
    } catch (err) {
      // Silently fail on poll errors
    }
  },

  // ── Load messages ──
  async loadMessages() {
    try {
      const data = await orderService.getMessages(this.data.orderId, { page: 1, size: 50 })
      const list = (data.list || []).map(m => this.formatMessage(m))
      this.setData({
        messages: list,
        page: 2,
        hasMore: list.length >= 50,
      })
      // Mark as read: get the latest message ID
      if (list.length > 0) {
        const lastMsg = list[list.length - 1]
        orderUnread.markAsRead(this.data.orderId, lastMsg.id)
      }
      // Start polling for new messages (active orders only)
      this._startPolling()
    } catch (err) {
      // Silently fail — messages are secondary
      console.warn('加载消息失败:', err.message)
    }
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

  // ── Send message ──
  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  async onSend() {
    const content = this.data.inputValue.trim()
    if (!content || this.data.sending || this.data.isTerminal) return

    this.setData({ sending: true })
    try {
      const msg = await orderService.sendMessage(this.data.orderId, { content })
      const formatted = this.formatMessage(msg)
      this.setData({
        messages: [...this.data.messages, formatted],
        inputValue: '',
        sending: false,
      })
      // Mark own message as read
      orderUnread.markAsRead(this.data.orderId, msg.id)
    } catch (err) {
      this.setData({ sending: false })
      wx.showToast({ title: err.message || '发送失败', icon: 'none' })
    }
  },

  // ── Pull down refresh ──
  onPullDownRefresh() {
    this.loadMessages().finally(() => wx.stopPullDownRefresh())
  },

  onRetry() {
    this.setData({ loading: true })
    this.loadOrder()
  },
})
