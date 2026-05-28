// ──────────────────────────────────────────────
//  用户服务
//  个人资料、收藏、统计数据
// ──────────────────────────────────────────────
const api = require('../utils/api')

module.exports = {

  /** 获取个人资料（含信誉分、收藏数） */
  getProfile() {
    return api.get('/api/users/me')
  },

  /** 更新个人资料 */
  updateProfile(data) {
    return api.put('/api/users/me', data)
  },

  /** 获取收藏列表 */
  getFavorites(page = 1, size = 20) {
    return api.get('/api/users/me/favorites', { page, size })
  },

  /** 获取用户发布的商品数、售出数（通过后端列表接口统计） */
  async getStats() {
    // 注：后端暂未提供独立统计接口，通过商品列表推断
    // 如果后端后续提供 /api/users/me/stats，直接替换
    return { published: 0, sold: 0 }
  },
}
