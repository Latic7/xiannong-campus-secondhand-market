const orderService = require('../../services/order')
const { ORDER_STATUS, getStatusMeta } = require('../../utils/constants')
const { getUserInfo } = require('../../utils/storage')

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
    if (!orderId) {
      this.setData({ loading: false })
      wx.showToast({ title: '订单 ID 缺失', icon: 'none' })
      return
    }
    this.loadOrder()
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
