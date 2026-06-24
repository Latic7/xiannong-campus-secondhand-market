const adminService = require('../../services/admin')
const { PRODUCT_STATUS, REPORT_STATUS, getStatusMeta } = require('../../utils/constants')

const REVIEW_OPTIONS = [
  { action: 'approved', label: '通过', confirm: '确认通过该商品的审核？商品将公开发布。' },
  { action: 'rejected', label: '驳回', confirm: '确认驳回该商品？商品将被下架。' },
]

const REPORT_ACTIONS = [
  { action: 'warning', label: '警告', confirm: '确认警告该用户？将扣除信誉分。' },
  { action: 'ban_user', label: '封禁', confirm: '确认封禁该用户？' },
  { action: 'unlist_product', label: '下架商品', confirm: '确认下架该商品？' },
  { action: 'reject', label: '驳回举报', confirm: '确认驳回该举报？' },
]

const TAB_OPTIONS = [
  { key: 'products', label: '商品审核' },
  { key: 'reports', label: '举报审核' },
  { key: 'stats', label: '报表' },
]

Page({
  data: {
    tabIndex: 0,
    tabs: TAB_OPTIONS,
    // 商品审核
    products: [],
    prodPage: 1,
    prodSize: 20,
    prodHasMore: true,
    prodLoading: false,
    prodError: '',
    // 举报审核
    reports: [],
    rptPage: 1,
    rptSize: 20,
    rptHasMore: true,
    rptLoading: false,
    rptError: '',
    REPORT_ACTIONS,
    // 待处理计数
    pendingReports: 0,
    pendingProducts: 0,
    // 筛选开关（pending=待处理, handled=已处理）
    prodFilter: 'pending',
    rptFilter: 'pending',
    // ── 报表 ──
    statsDateStart: '',
    statsDateEnd: '',
    overview: null,
    productStats: null,
    tradeStats: null,
    userStats: null,
    statsLoading: false,
  },

  onLoad() {
    this.loadCounts()
    this.loadTabData()
  },

  onShow() {
    this.loadCounts()
    this.loadTabData()
  },

  onTabChange(e) {
    const idx = typeof e === 'number' ? e : (e.currentTarget?.dataset?.index ?? 0)
    if (idx === this.data.tabIndex) return
    this.setData({ tabIndex: idx })
    this.loadTabData()
  },

  loadTabData() {
    const tab = TAB_OPTIONS[this.data.tabIndex]?.key
    if (tab === 'products') this.loadProducts()
    else if (tab === 'reports') this.loadReports()
    else if (tab === 'stats') this.loadStats()
  },

  async loadCounts() {
    try {
      const [reportRes, productRes] = await Promise.all([
        adminService.listReports({ status: 'OPEN', size: 1 }),
        adminService.listPendingProducts({ size: 1 }),
      ])
      this.setData({
        pendingReports: reportRes?.page?.total || 0,
        pendingProducts: productRes?.page?.total || 0,
      })
    } catch (e) { /* 静默 */ }
  },

  // ── 筛选切换 ──────────────────────────────
  onProdFilterChange(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({ prodFilter: filter, products: [], prodPage: 1, prodHasMore: true })
    this.loadProducts()
  },

  onRptFilterChange(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({ rptFilter: filter, reports: [], rptPage: 1, rptHasMore: true })
    this.loadReports()
  },

  // ── 商品审核 ──────────────────────────────
  async loadProducts({ append = false } = {}) {
    if (this.data.prodLoading) return
    this.setData({ prodLoading: true })
    try {
      const p = append ? this.data.prodPage : 1
      const params = { page: p, size: this.data.prodSize }
      if (this.data.prodFilter === 'handled') params.status = 'PUBLISHED,REMOVED'
      const data = await adminService.listPendingProducts(params)
      const list = (data.list || []).map(item => this.formatProduct(item))
      this.setData({
        products: append ? this.data.products.concat(list) : list,
        prodPage: p + 1,
        prodHasMore: list.length >= this.data.prodSize,
        prodLoading: false,
        prodError: '',
      })
    } catch (err) {
      this.setData({ prodLoading: false, prodError: err.message || '加载失败' })
    }
  },

  formatProduct(product) {
    const meta = getStatusMeta(PRODUCT_STATUS, product.status)
    return {
      ...product,
      statusText: meta.label,
      statusColor: meta.color,
      priceText: product.price != null ? '¥' + Number(product.price).toFixed(2) : '¥0.00',
      // 取第一张图片（可能是云存储 fileID）
      coverImage: (product.images && product.images.length > 0) ? product.images[0] : '',
      sellerName: product.seller?.nickname || '未知卖家',
    }
  },

  async onReviewProduct(e) {
    const productId = e.currentTarget.dataset.id
    const action = e.currentTarget.dataset.action
    const opt = REVIEW_OPTIONS.find(o => o.action === action)
    wx.showModal({
      title: '审核确认',
      content: opt.confirm,
      success: async (res) => {
        if (!res.confirm) return
        try {
          await adminService.reviewProduct(productId, { result: action })
          wx.showToast({ title: action === 'approved' ? '已通过' : '已驳回', icon: 'success' })
          this.setData({ products: [], prodPage: 1, prodHasMore: true })
          this.loadProducts()
          this.loadCounts()
        } catch (err) {
          wx.showToast({ title: err.message || '操作失败', icon: 'none' })
        }
      },
    })
  },

  onProdScrollBottom() {
    if (!this.data.prodHasMore || this.data.prodLoading) return
    this.loadProducts({ append: true })
  },

  // ── 举报审核 ──────────────────────────────
  async loadReports({ append = false } = {}) {
    if (this.data.rptLoading) return
    this.setData({ rptLoading: true })
    try {
      const p = append ? this.data.rptPage : 1
      const rptStatus = this.data.rptFilter === 'handled' ? 'HANDLED,REJECTED' : 'OPEN'
      const data = await adminService.listReports({ status: rptStatus, page: p, size: this.data.rptSize })
      const list = (data.list || []).map(item => this.formatReport(item))
      this.setData({
        reports: append ? this.data.reports.concat(list) : list,
        rptPage: p + 1,
        rptHasMore: list.length >= this.data.rptSize,
        rptLoading: false,
        rptError: '',
      })
    } catch (err) {
      this.setData({ rptLoading: false, rptError: err.message || '加载失败' })
    }
  },

  formatReport(report) {
    const meta = getStatusMeta(REPORT_STATUS, report.status)
    const targetType = String(report.targetType || '').toUpperCase()
    const target = report.target || {}
    const summary = this.formatTargetSummary(report, target)
    return {
      ...report,
      targetType,
      targetTypeText: targetType === 'PRODUCT' ? '商品' : targetType === 'USER' ? '用户' : targetType === 'ORDER' ? '订单' : '未知',
      statusText: meta.label,
      statusColor: meta.color,
      ...summary,
    }
  },

  formatTargetSummary(report, target) {
    if (report.targetType === 'PRODUCT') {
      return {
        targetTitle: target.title || '商品信息不可用',
        targetImage: target.image || '',
        targetPrice: target.price != null ? '¥' + Number(target.price).toFixed(2) : '',
        targetSeller: target.seller?.nickname || '',
        targetStatus: target.status || '',
      }
    }
    if (report.targetType === 'USER') {
      return {
        targetTitle: target.nickname || '未知用户',
        targetImage: target.avatar || '',
        targetScore: target.score != null ? '信誉: ' + target.score : '',
        targetStatus: target.status || '',
      }
    }
    if (report.targetType === 'ORDER') {
      return {
        targetTitle: target.product?.title || '订单商品不可用',
        targetImage: target.product?.image || '',
        targetPrice: target.amount != null ? '¥' + Number(target.amount).toFixed(2) : '',
        targetStatus: target.status || '',
      }
    }
    return {}
  },

  // 点击商品卡片 → 跳转商品详情
  onTapProduct(e) {
    const id = e.currentTarget.dataset.id
    if (id) wx.navigateTo({ url: '/pages/detail/index?id=' + id })
  },

  // 点击举报目标 → 跳转对应详情
  onTapReportTarget(e) {
    const { type, id } = e.currentTarget.dataset
    if (!id) return
    if (type === 'PRODUCT') {
      wx.navigateTo({ url: '/pages/detail/index?id=' + id })
    } else if (type === 'USER') {
      // 暂跳转到该用户的商品列表
      wx.navigateTo({ url: '/pages/list/index?ownerId=' + id })
    }
    // ORDER 暂不跳转
  },

  async onHandleReport(e) {
    const reportId = e.currentTarget.dataset.id
    const action = e.currentTarget.dataset.action
    const opt = REPORT_ACTIONS.find(o => o.action === action)
    wx.showModal({
      title: '处理确认',
      content: opt.confirm,
      success: async (res) => {
        if (!res.confirm) return
        try {
          await adminService.handleReport(reportId, { action })
          wx.showToast({ title: '已处理', icon: 'success' })
          this.setData({ reports: [], rptPage: 1, rptHasMore: true })
          this.loadReports()
          this.loadCounts()
        } catch (err) {
          wx.showToast({ title: err.message || '操作失败', icon: 'none' })
        }
      },
    })
  },

  onRptScrollBottom() {
    if (!this.data.rptHasMore || this.data.rptLoading) return
    this.loadReports({ append: true })
  },

  // ── 报表 ──────────────────────────────────
  onStatsDateStartInput(e) {
    this.setData({ statsDateStart: e.detail.value })
  },
  onStatsDateEndInput(e) {
    this.setData({ statsDateEnd: e.detail.value })
  },

  async loadStats() {
    this.setData({ statsLoading: true })
    try {
      const params = {}
      if (this.data.statsDateStart) params.startDate = this.data.statsDateStart
      if (this.data.statsDateEnd) params.endDate = this.data.statsDateEnd
      const [overview, productStats, tradeStats, userStats] = await Promise.all([
        adminService.statsOverview(params),
        adminService.statsProducts(params),
        adminService.statsTrades(params),
        adminService.statsUsers(params),
      ])
      this.setData({ overview, productStats, tradeStats, userStats, statsLoading: false })
    } catch (err) {
      this.setData({ statsLoading: false })
      wx.showToast({ title: err.message || '加载报表失败', icon: 'none' })
    }
  },
})
