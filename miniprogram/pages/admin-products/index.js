const adminService = require('../../services/admin')
const { PRODUCT_STATUS, getStatusMeta } = require('../../utils/constants')

const REVIEW_OPTIONS = [
  { action: 'approved', label: '通过', confirm: '确认通过该商品的审核？商品将公开发布。' },
  { action: 'rejected', label: '驳回', confirm: '确认驳回该商品？商品将被下架。' },
]

Page({
  data: {
    products: [],
    page: 1,
    size: 20,
    hasMore: true,
    loading: false,
    errorMsg: '',
  },

  onLoad() {
    this.loadProducts()
  },

  // ── 格式化商品展示数据 ────────────────────
  formatProduct(product) {
    const meta = getStatusMeta(PRODUCT_STATUS, product.status)
    return {
      ...product,
      statusText: meta.label,
      statusColor: meta.color,
      priceText: product.price != null ? Number(product.price).toFixed(2) : '0.00',
      firstImage: (product.images && product.images.length > 0)
        ? product.images[0]
        : (product.imageUrls && product.imageUrls.length > 0)
          ? product.imageUrls[0]
          : '',
      createdAtText: product.createdAt
        ? product.createdAt.replace('T', ' ').substring(0, 16)
        : '',
      description: product.description || '',
      categoryName: product.categoryName || product.category || '',
      ownerName: product.ownerName || product.ownerNickname || '',
    }
  },

  // ── 加载待审核商品 ────────────────────────
  async loadProducts({ append = false } = {}) {
    if (this.data.loading) return
    this.setData({ loading: true, errorMsg: append ? this.data.errorMsg : '' })
    try {
      const targetPage = append ? this.data.page : 1
      const params = { page: targetPage, size: this.data.size }
      const data = await adminService.listPendingProducts(params)
      const list = (data.list || []).map(item => this.formatProduct(item))
      this.setData({
        products: append ? this.data.products.concat(list) : list,
        page: targetPage + 1,
        hasMore: list.length >= this.data.size,
        loading: false,
        errorMsg: '',
      })
    } catch (err) {
      this.setData({
        loading: false,
        errorMsg: err.message || '商品列表加载失败，请重试',
      })
    }
  },

  // ── 下拉刷新 ──────────────────────────────
  onPullDownRefresh() {
    this.setData({ page: 1, products: [], hasMore: true })
    this.loadProducts().finally(() => wx.stopPullDownRefresh())
  },

  // ── 触底加载更多 ──────────────────────────
  onReachBottom() {
    if (!this.data.hasMore || this.data.loading) return
    this.loadProducts({ append: true })
  },

  // ── 重试 ──────────────────────────────────
  onRetry() {
    this.setData({ page: 1, products: [], hasMore: true })
    this.loadProducts()
  },

  // ── 审核商品（通过/驳回）──────────────────
  onReviewProduct(e) {
    const { action } = e.currentTarget.dataset
    const productId = e.currentTarget.dataset.productId
    const option = REVIEW_OPTIONS.find(o => o.action === action)
    if (!option) return

    wx.showModal({
      title: option.label + '审核',
      content: option.confirm,
      success: async (res) => {
        if (!res.confirm) return

        try {
          wx.showLoading({ title: '处理中...' })
          await adminService.reviewProduct(productId, {
            result: action,
            reason: '',
          })
          wx.hideLoading()
          wx.showToast({ title: '操作成功', icon: 'success' })

          // 从列表中移除已处理的商品
          const products = this.data.products.filter(p => p.id !== productId)
          this.setData({ products })
        } catch (err) {
          wx.hideLoading()
          wx.showToast({ title: err.message || '操作失败', icon: 'none' })
        }
      },
    })
  },
})
