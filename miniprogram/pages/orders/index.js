const orderService = require('../../services/order')
const { ORDER_STATUS, getStatusMeta } = require('../../utils/constants')
const { getUserInfo } = require('../../utils/storage')
const orderUnread = require('../../utils/orderUnread')

Page({
  data: {
    orders: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,
    errorMsg: '',
    role: 'all',
    roleOptions: [
      { label: '全部', value: 'all' },
      { label: '我买的', value: 'buyer' },
      { label: '我卖的', value: 'seller' },
    ],
    currentUserId: null,
  },

  onLoad() {
    const user = getUserInfo()
    this.setData({ currentUserId: user ? user.id : null })
    this.loadOrders()
  },

  onShow() {
    // Refresh user info (may have changed)
    const user = getUserInfo()
    const newUserId = user ? user.id : null
    if (newUserId !== this.data.currentUserId) {
      this.setData({ currentUserId: newUserId })
    }
    // Always refresh orders when page shows
    this.setData({ page: 1, orders: [], hasMore: true })
    this.loadOrders()
  },

  formatOrder(order) {
    const meta = getStatusMeta(ORDER_STATUS, order.status)
    const userId = this.data.currentUserId
    const isSeller = userId && order.sellerId === userId
    const isBuyer = userId && order.buyerId === userId

    // Determine which actions are available
    const canConfirm = isSeller && order.status === 'RESERVED'
    const canCancel = (isBuyer || isSeller) && (order.status === 'RESERVED' || order.status === 'CONFIRMED')
    const canComplete = isBuyer && order.status === 'CONFIRMED'

    // Check unread status
    const unread = orderUnread.hasUnread(order, userId)

    const otherPartyName = isSeller
      ? (order.buyer?.nickname || '买家')
      : (order.seller?.nickname || '卖家')

    return {
      ...order,
      amountText: order.amount == null ? '待确认' : '¥' + Number(order.amount).toFixed(2).replace(/\.00$/, ''),
      statusText: meta.label,
      statusColor: meta.color,
      productTitle: order.product?.title || '商品信息不可用',
      productImage: order.product?.image || '',
      otherPartyName,
      isSeller,
      isBuyer,
      canConfirm,
      canCancel,
      canComplete,
      hasUnread: unread,
    }
  },

  async loadOrders({ append = false } = {}) {
    if (this.data.loading) return
    this.setData({ loading: true, errorMsg: append ? this.data.errorMsg : '' })
    try {
      const targetPage = append ? this.data.page : 1
      const params = { page: targetPage, size: this.data.size }
      if (this.data.role !== 'all') params.role = this.data.role
      const data = await orderService.list(params)
      const list = (data.list || []).map(item => this.formatOrder(item))
      this.setData({
        orders: append ? this.data.orders.concat(list) : list,
        page: targetPage + 1,
        hasMore: list.length >= this.data.size,
        loading: false,
        errorMsg: '',
      })
    } catch (err) {
      this.setData({
        loading: false,
        errorMsg: err.message || '订单加载失败，请重试',
      })
    }
  },

  onRoleChange(e) {
    const { role } = e.currentTarget.dataset
    if (!role || role === this.data.role) return
    this.setData({ role, page: 1, orders: [], hasMore: true })
    this.loadOrders()
  },

  // ── Tap order card → navigate to chat page ──
  onOrderTap(e) {
    const orderId = e.currentTarget.dataset.id
    if (!orderId) return
    wx.navigateTo({ url: `/pages/order-chat/index?orderId=${orderId}` })
  },

  // ── Tap message button → navigate to chat (mark as read) ──
  onMessageTap(e) {
    const orderId = e.currentTarget.dataset.id
    if (!orderId) return
    wx.navigateTo({ url: `/pages/order-chat/index?orderId=${orderId}` })
  },

  // ── Seller confirms a buyer ──
  async onSellerConfirm(e) {
    const orderId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认交易',
      content: '确认将该商品售予当前买家？\n\n点击确认后，其他买家的预约将被自动取消，商品也将不再能被下架。请确认您已与买家沟通无误。',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '处理中...' })
            const data = await orderService.sellerConfirm(orderId)
            wx.hideLoading()
            wx.showToast({ title: '已确认交易', icon: 'success' })
            this.refreshOrders()
          } catch (err) {
            wx.hideLoading()
            wx.showToast({ title: err.message || '操作失败', icon: 'none' })
          }
        }
      },
    })
  },

  // ── Cancel order ──
  async onCancelOrder(e) {
    const orderId = e.currentTarget.dataset.id
    wx.showModal({
      title: '取消订单',
      content: '确定取消此订单？\n\n该操作不可逆，取消后无法恢复。',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '处理中...' })
            await orderService.cancel(orderId)
            wx.hideLoading()
            wx.showToast({ title: '已取消', icon: 'success' })
            this.refreshOrders()
          } catch (err) {
            wx.hideLoading()
            wx.showToast({ title: err.message || '操作失败', icon: 'none' })
          }
        }
      },
    })
  },

  // ── Buyer completes order ──
  async onCompleteOrder(e) {
    const orderId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认完成',
      content: '请确认您已收到商品且无问题后再点击确认。\n\n点击后交易将被标记为已完成，卖家将获得信誉分奖励。此后将无法撤销此操作。',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '处理中...' })
            await orderService.complete(orderId)
            wx.hideLoading()
            wx.showToast({ title: '交易完成', icon: 'success' })
            this.refreshOrders()
          } catch (err) {
            wx.hideLoading()
            wx.showToast({ title: err.message || '操作失败', icon: 'none' })
          }
        }
      },
    })
  },

  // ── Refresh list ──
  refreshOrders() {
    this.setData({ page: 1, orders: [], hasMore: true })
    this.loadOrders()
  },

  onPullDownRefresh() {
    this.setData({ page: 1, orders: [], hasMore: true })
    this.loadOrders().finally(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (!this.data.hasMore || this.data.loading) return
    this.loadOrders({ append: true })
  },

  onRetry() {
    this.setData({ page: 1, orders: [], hasMore: true })
    this.loadOrders()
  },
})
