Page({
  data: {},

  onLoad() {
    // 管理后台页面逻辑
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
