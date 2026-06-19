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
}
