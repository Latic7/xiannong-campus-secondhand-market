const adminService = require('../../services/admin')
const {
  REPORT_STATUS,
  PRODUCT_STATUS,
  ORDER_STATUS,
  USER_STATUS,
  getStatusMeta,
} = require('../../utils/constants')

const TARGET_TYPE_MAP = {
  PRODUCT: '商品',
  ORDER: '订单',
  USER: '用户',
}

const ACTION_OPTIONS = [
  { action: 'reject', label: '驳回', desc: '驳回该举报，不予处理', confirm: '确认驳回该举报？' },
  { action: 'warning', label: '警告', desc: '对被举报对象发送警告', confirm: '确认发送警告？' },
  { action: 'unlist_product', label: '下架商品', desc: '下架被举报的商品', confirm: '确认下架该商品？' },
  { action: 'ban_user', label: '封禁用户', desc: '封禁被举报的用户', confirm: '确认封禁该用户？此操作不可撤销。' },
]

function formatPrice(value) {
  if (value == null) return '待确认'
  return '¥' + Number(value).toFixed(2).replace(/\.00$/, '')
}

function formatTarget(report) {
  const target = report.target
  if (!target) return null

  if (report.targetType === 'PRODUCT') {
    return {
      id: target.id,
      title: target.title || '商品信息不可用',
      price: target.price,
      priceText: formatPrice(target.price),
      image: target.image || '',
      status: target.status,
      statusText: getStatusMeta(PRODUCT_STATUS, target.status).label,
    }
  }

  if (report.targetType === 'USER') {
    return {
      id: target.id,
      nickname: target.nickname || '未知用户',
      avatar: target.avatar || '',
      status: target.status,
      statusText: getStatusMeta(USER_STATUS, target.status).label,
      score: target.score == null ? '—' : target.score,
    }
  }

  if (report.targetType === 'ORDER') {
    const product = target.product || {}
    return {
      id: target.id,
      amount: target.amount,
      amountText: formatPrice(target.amount),
      status: target.status,
      statusText: getStatusMeta(ORDER_STATUS, target.status).label,
      product: {
        title: product.title || '订单商品不可用',
        image: product.image || '',
      },
    }
  }

  return null
}

Page({
  data: {
    reports: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,
    errorMsg: '',
    statusFilter: '',
    statusOptions: [
      { label: '全部', value: '' },
      { label: '处理中', value: 'OPEN' },
      { label: '已处理', value: 'HANDLED' },
      { label: '已驳回', value: 'REJECTED' },
    ],
  },

  onLoad() {
    this.loadReports()
  },

  formatReport(report) {
    const meta = getStatusMeta(REPORT_STATUS, report.status)
    // targetType 统一为大写，供 wxml 条件判断使用
    const targetType = String(report.targetType || '').toUpperCase()
    return {
      ...report,
      targetType,
      targetTypeText: TARGET_TYPE_MAP[targetType] || report.targetType || '未知',
      target: formatTarget({ ...report, targetType }),
      statusText: meta.label,
      statusColor: meta.color,
      isOpen: String(report.status || '').toUpperCase() === 'OPEN',
    }
  },

  async loadReports({ append = false } = {}) {
    if (this.data.loading) return
    this.setData({ loading: true, errorMsg: append ? this.data.errorMsg : '' })
    try {
      const targetPage = append ? this.data.page : 1
      const params = { page: targetPage, size: this.data.size }
      if (this.data.statusFilter) params.status = this.data.statusFilter
      const data = await adminService.listReports(params)
      const list = (data.list || []).map(item => this.formatReport(item))
      this.setData({
        reports: append ? this.data.reports.concat(list) : list,
        page: targetPage + 1,
        hasMore: list.length >= this.data.size,
        loading: false,
        errorMsg: '',
      })
    } catch (err) {
      this.setData({
        loading: false,
        errorMsg: err.message || '举报列表加载失败，请重试',
      })
    }
  },

  onPullDownRefresh() {
    this.setData({ page: 1, reports: [], hasMore: true })
    this.loadReports().finally(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (!this.data.hasMore || this.data.loading) return
    this.loadReports({ append: true })
  },

  onRetry() {
    this.setData({ page: 1, reports: [], hasMore: true })
    this.loadReports()
  },

  onStatusFilter(e) {
    const status = e.currentTarget.dataset.status
    if (status === this.data.statusFilter) return
    this.setData({ statusFilter: status, page: 1, reports: [], hasMore: true })
    this.loadReports()
  },

  onHandleReport(e) {
    const { action } = e.currentTarget.dataset
    const reportId = e.currentTarget.dataset.reportId
    const option = ACTION_OPTIONS.find(o => o.action === action)
    if (!option) return

    wx.showModal({
      title: option.label,
      content: option.confirm,
      success: async (res) => {
        if (!res.confirm) return
        try {
          await adminService.handleReport(reportId, { action, reason: option.label })
          wx.showToast({ title: '处理成功', icon: 'success' })
          // 刷新当前列表
          this.setData({ page: 1, reports: [], hasMore: true })
          this.loadReports()
        } catch (err) {
          wx.showToast({ title: err.message || '处理失败', icon: 'none' })
        }
      },
    })
  },
})
