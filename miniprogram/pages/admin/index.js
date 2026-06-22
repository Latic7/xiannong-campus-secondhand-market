const adminService = require('../../services/admin')

Page({
  data: {
    pendingReports: 0,
    pendingProducts: 0,
  },

  onLoad() {
    this.loadPendingCounts()
  },

  onShow() {
    this.loadPendingCounts()
  },

  async loadPendingCounts() {
    try {
      // 获取待处理举报数
      const reportRes = await adminService.listReports({ status: 'OPEN', size: 1 })
      this.setData({ pendingReports: reportRes?.page?.total || 0 })

      // 获取待审核商品数
      const productRes = await adminService.listPendingProducts({ size: 1 })
      this.setData({ pendingProducts: productRes?.page?.total || 0 })
    } catch (e) {
      // 静默失败
    }
  },

  // ── 跳转：商品审核 ────────────────────────
  onReviewProducts() {
    wx.navigateTo({ url: '/pages/admin-products/index' })
  },

  // ── 跳转：举报审核 ────────────────────────
  onReviewReports() {
    wx.navigateTo({ url: '/pages/admin-reports/index' })
  },
})
