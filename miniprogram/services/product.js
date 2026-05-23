const { getProducts } = require('../utils/api.js');

/**
 * 获取商品列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
function fetchProductList(params = {}) {
  return getProducts(params);
}

/**
 * 获取商品详情
 * @param {number} id - 商品ID
 * @returns {Promise}
 */
function fetchProductDetail(id) {
  const { getProduct } = require('../utils/api.js');
  return getProduct(id);
}

module.exports = {
  fetchProductList,
  fetchProductDetail
};
