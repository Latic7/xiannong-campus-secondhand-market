// ──────────────────────────────────────────────
//  举报服务
//  创建举报
// ──────────────────────────────────────────────
const api = require('../utils/api')

module.exports = {

  /** 我的举报列表 */
  listMine(params = {}) {
    return api.get('/api/reports', params)
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
