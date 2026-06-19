Page({
  data: {},

  onLoad() {
    // 管理后台页面逻辑
  },

  // ── 跳转：举报审核 ────────────────────────
  onReviewReports() {
    wx.navigateTo({ url: '/pages/admin-reports/index' })
  },
})
