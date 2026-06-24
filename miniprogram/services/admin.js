const api = require('../utils/api')

module.exports = {
  /** 举报队列 */
  listReports(params = {}) {
    return api.get('/api/admin/reports', params)
  },

  /** 处理举报 */
  handleReport(reportId, data) {
    return api.post('/api/admin/reports/' + reportId + '/handle', data)
  },

  /** 待审核商品列表（支持 status 参数筛选状态） */
  listPendingProducts(params = {}) {
    return api.get('/api/admin/products/pending', params)
  },

  /** 审核商品（通过/驳回） */
  reviewProduct(productId, data) {
    return api.post('/api/admin/products/' + productId + '/review', data)
  },

  // ── 报表统计 ──────────────────────────────

  /** 平台运营总览（用户/商品/订单/举报数） */
  statsOverview(params = {}) {
    return api.get('/api/admin/stats/overview', params)
  },

  /** 商品维度统计（按状态分布） */
  statsProducts(params = {}) {
    return api.get('/api/admin/stats/products', params)
  },

  /** 交易维度统计（按订单状态分布） */
  statsTrades(params = {}) {
    return api.get('/api/admin/stats/trades', params)
  },

  /** 用户维度统计（按用户状态分布） */
  statsUsers(params = {}) {
    return api.get('/api/admin/stats/users', params)
  },

  /** 管理员操作日志 */
  listAdminLogs(params = {}) {
    return api.get('/api/admin/logs', params)
  },

  /** 每日趋势（商品发布/成交/注册） */
  statsTrends(params = {}) {
    return api.get('/api/admin/stats/trends', params)
  },

  /** 热门商品类别 */
  statsCategories(params = {}) {
    return api.get('/api/admin/stats/categories', params)
  },
}
