const reportService = require('../../services/report')
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

// 管理员处理动作 → 中文文案，用于展示「处理结果」
const ACTION_LABEL = {
  reject: '驳回',
  warning: '警告',
  unlist_product: '下架商品',
  ban_user: '封禁用户',
}

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

const TAB_OPTIONS = [
  { key: 'mine', label: '我举报的' },
  { key: 'against', label: '我被举报的' },
]

Page({
  data: {
    tabIndex: 0,
    tabs: TAB_OPTIONS,
    reports: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,
    errorMsg: '',
    againstBadge: 0,
  },

  onLoad() {
    this.loadReports()
    this.loadAgainstBadge()
  },

  async loadAgainstBadge() {
    try {
      const data = await reportService.listAgainstMe({ size: 1 })
      this.setData({ againstBadge: data?.page?.total || 0 })
    } catch (e) {
      // 静默
    }
  },

  onTabChange(e) {
    const idx = typeof e === 'number' ? e : (e.currentTarget?.dataset?.index ?? 0)
    if (idx === this.data.tabIndex) return
    this.setData({ tabIndex: idx, page: 1, reports: [], hasMore: true })
    this.loadReports()
  },

  formatReport(report) {
    const meta = getStatusMeta(REPORT_STATUS, report.status)
    // targetType 统一为大写，供 wxml 条件判断使用
    const targetType = String(report.targetType || '').toUpperCase()
    const action = report.handleAction
    return {
      ...report,
      targetType,
      targetTypeText: TARGET_TYPE_MAP[targetType] || report.targetType || '未知',
      target: formatTarget({ ...report, targetType }),
      statusText: meta.label,
      statusColor: meta.color,
      isOpen: String(report.status || '').toUpperCase() === 'OPEN',
      handleAction: action ? (ACTION_LABEL[action] || action) : '',
    }
  },

  async loadReports({ append = false } = {}) {
    if (this.data.loading) return
    this.setData({ loading: true, errorMsg: append ? this.data.errorMsg : '' })
    try {
      const targetPage = append ? this.data.page : 1
      const isAgainst = this.data.tabIndex === 1
      const fetcher = isAgainst ? reportService.listAgainstMe : reportService.listMine
      const data = await fetcher({ page: targetPage, size: this.data.size })
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
})
