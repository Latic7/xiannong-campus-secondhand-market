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

  /** 下架/删除商品 */
  remove(productId) {
    return api.del('/api/products/' + productId)
  },

  /**
   * 上传商品图片（微信云托管对象存储方式）
   * 1. 用 wx.cloud.uploadFile 上传到云存储
   * 2. 将返回的 cloud:// fileId 发给后端保存
   */
  async uploadImage(productId, filePath) {
    // 上传到微信云托管对象存储
    const cloudRes = await wx.cloud.uploadFile({
      cloudPath: `products/${productId}/${Date.now()}.jpg`,
      filePath,
    })
    // cloudRes.fileID 形如 cloud://env-id/products/xxx.jpg
    // 将 fileID 发送给后端保存
    const res = await api.post('/api/products/' + productId + '/cloud-images', {
      fileId: cloudRes.fileID,
    })
    return res
  },

  /** 批量上传图片：依次上传，返回 URL/cloudID 数组 */
  async uploadImages(productId, filePaths) {
    const results = []
    for (const fp of filePaths) {
      const res = await this.uploadImage(productId, fp)
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
