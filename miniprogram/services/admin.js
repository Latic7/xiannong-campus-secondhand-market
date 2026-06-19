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

  /** 待审核商品列表 */
  listPendingProducts(params = {}) {
    return api.get('/api/admin/products/pending', params)
  },

  /** 审核商品（通过/驳回） */
  reviewProduct(productId, data) {
    return api.post('/api/admin/products/' + productId + '/review', data)
  },
}
