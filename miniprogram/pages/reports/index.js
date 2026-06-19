const reportService = require('../../services/report')
const { REPORT_STATUS, getStatusMeta } = require('../../utils/constants')

Page({
  data: {
    reports: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,
    errorMsg: '',
  },

  onLoad() {
    this.loadReports()
  },

  formatReport(report) {
    const meta = getStatusMeta(REPORT_STATUS, report.status)
    return {
      ...report,
      targetTypeText: report.targetType === 'PRODUCT' ? '商品' : report.targetType === 'ORDER' ? '订单' : '用户',
      statusText: meta.label,
      statusColor: meta.color,
    }
  },

  async loadReports({ append = false } = {}) {
    if (this.data.loading) return
    this.setData({ loading: true, errorMsg: append ? this.data.errorMsg : '' })
    try {
      const targetPage = append ? this.data.page : 1
      const data = await reportService.listMine({ page: targetPage, size: this.data.size })
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
