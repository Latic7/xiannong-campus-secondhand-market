// ──────────────────────────────────────────────
//  举报服务
//  创建举报
// ──────────────────────────────────────────────
const api = require('../utils/api')

module.exports = {

  /** 我的举报列表（我发起的） */
  listMine(params = {}) {
    return api.get('/api/reports', params)
  },

  /** 我被举报的列表（针对我的） */
  listAgainstMe(params = {}) {
    return api.get('/api/reports/against-me', params)
  },

  /** 标记所有针对我的举报为已读 */
  markAgainstMeSeen() {
    return api.post('/api/reports/against-me/mark-seen')
  },

  /** 创建举报 */
  create(data) {
    // 后端期望: { targetType, targetId, reason }
    return api.post('/api/reports', {
      targetType: data.targetType || 'PRODUCT',
      targetId: data.productId,
      reason: data.reason,
    })
  },
}
