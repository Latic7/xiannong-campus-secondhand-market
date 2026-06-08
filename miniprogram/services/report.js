// ──────────────────────────────────────────────
//  举报服务
//  创建举报
// ──────────────────────────────────────────────
const api = require('../utils/api')

module.exports = {

  /** 创建举报 */
  create(data) {
    // 后端期望: { targetType, targetId, reason }
    return api.post('/api/reports', {
      targetType: 'product',
      targetId: data.productId,
      reason: data.reason,
    })
  },
}
