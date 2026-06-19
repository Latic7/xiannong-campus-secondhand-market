const orderService = require('../../services/order')
const { ORDER_STATUS, getStatusMeta } = require('../../utils/constants')

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
  },

  onLoad() {
    this.loadOrders()
  },

  formatOrder(order) {
    const meta = getStatusMeta(ORDER_STATUS, order.status)
    return {
      ...order,
      amountText: order.amount == null ? '待确认' : '¥' + Number(order.amount).toFixed(2).replace(/\.00$/, ''),
      statusText: meta.label,
      statusColor: meta.color,
      productTitle: order.product?.title || '商品信息不可用',
      productImage: order.product?.image || '',
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
