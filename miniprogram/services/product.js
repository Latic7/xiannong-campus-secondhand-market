// ──────────────────────────────────────────────
//  商品服务
//  封装所有商品相关 API 调用
// ──────────────────────────────────────────────
const api = require('../utils/api')

module.exports = {

  /** 商品列表 */
  list(params = {}) {
    return api.get('/api/products', params)
  },

  /** 商品详情 */
  getDetail(productId) {
    return api.get('/api/products/' + productId)
  },

  /** 发布商品 */
  create(data) {
    return api.post('/api/products', data)
  },

  /** 更新商品 */
  update(productId, data) {
    return api.put('/api/products/' + productId, data)
  },

  /** 上传商品图片（需先创建商品获得 productId） */
  uploadImage(productId, filePath) {
    return api.uploadFile('/api/products/' + productId + '/images', filePath)
  },

  /** 批量上传图片：依次上传，返回 URL 数组 */
  async uploadImages(productId, filePaths) {
    const results = []
    for (const fp of filePaths) {
      const res = await api.uploadFile('/api/products/' + productId + '/images', fp)
      results.push(res.url || res)
    }
    return results
  },

  /** 添加收藏 */
  addFavorite(productId) {
    return api.post('/api/users/me/favorites/' + productId)
  },

  /** 取消收藏 */
  removeFavorite(productId) {
    return api.del('/api/users/me/favorites/' + productId)
  },
}
