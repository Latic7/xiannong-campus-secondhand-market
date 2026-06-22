// ──────────────────────────────────────────────
//  订单服务
//  创建订单、查看详情、卖家确认、取消、完成
// ──────────────────────────────────────────────
const api = require('../utils/api')

module.exports = {

  /** 我的订单列表 */
  list(params = {}) {
    return api.get('/api/orders', params)
  },

  /** 创建订单 */
  create(data) {
    return api.post('/api/orders', data)
  },

  /** 订单详情 */
  getDetail(orderId) {
    return api.get('/api/orders/' + orderId)
  },

  /** 卖家确认 */
  sellerConfirm(orderId) {
    return api.post('/api/orders/' + orderId + '/seller-confirm')
  },

  /** 取消订单 */
  cancel(orderId) {
    return api.post('/api/orders/' + orderId + '/cancel')
  },

  /** 完成订单 */
  complete(orderId) {
    return api.post('/api/orders/' + orderId + '/complete')
  },

  /** 获取订单消息列表 */
  getMessages(orderId, params = {}) {
    return api.get('/api/orders/' + orderId + '/messages', params)
  },

  /** 发送订单消息 */
  sendMessage(orderId, data) {
    return api.post('/api/orders/' + orderId + '/messages', data)
  },
}
