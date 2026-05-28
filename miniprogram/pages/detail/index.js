// ──────────────────────────────────────────────
//  商品详情页
//  根据商品 ID 加载并展示商品完整信息
// ──────────────────────────────────────────────
const { isLoggedIn, getUserInfo } = require('../../utils/storage')
const { PRODUCT_STATUS } = require('../../utils/constants')
const productService = require('../../services/product')
const orderService = require('../../services/order')
const reportService = require('../../services/report')
const userService = require('../../services/user')

// ── 分类 ID → 名称映射（与后端 categoryId 对齐）──
const CATEGORY_MAP = {
  1: '数码电子', 2: '书籍教材', 3: '生活用品',
  4: '服饰鞋包', 5: '运动户外', 6: '美妆护肤',
  7: '食品饮料', 8: '其他',
}

Page({
  data: {
    product: null,
    productId: '',
    loading: true,
    errorMsg: '',
    currentImageIndex: 0,
    images: [],
    isFavorited: false,
    favoriting: false,
    isOwner: false,
    isLoggedIn: false,
  },

  onLoad(options) {
    const productId = options.id || ''
    this.setData({ productId })
    if (!productId) {
      this.setData({ loading: false, errorMsg: '商品 ID 缺失' })
      return
    }
    this.loadProduct(productId)
  },

  // ── 加载商品详情（真实 API）───────────────
  async loadProduct(productId) {
    this.setData({ loading: true, errorMsg: '' })
    try {
      const raw = await productService.getDetail(productId)
      const product = this.mapBackendProduct(raw)
      const formatted = this.formatProduct(product)
      this.setData({
        product: formatted,
        images: formatted.images || [],
        loading: false,
        isOwner: this.checkIsOwner(formatted),
        isLoggedIn: isLoggedIn(),
      })
      if (isLoggedIn()) {
        this.checkFavoriteStatus(productId)
      }
    } catch (err) {
      this.setData({ loading: false, errorMsg: err.message || '加载失败，请重试' })
    }
  },

  // ── 后端数据 → 前端展示数据映射 ───────────
  mapBackendProduct(raw) {
    return {
      id: raw.id,
      title: raw.title || '',
      description: raw.description || '',
      price: raw.price,
      originalPrice: raw.originalPrice || null,
      images: raw.images || [],
      category: CATEGORY_MAP[raw.categoryId] || '其他',
      categoryId: raw.categoryId,
      condition: raw.condition || 'used_good',
      campus: raw.campus || '',
      status: raw.status || 'published',
      viewCount: raw.viewCount || 0,
      favoriteCount: raw.favoriteCount || 0,
      seller: raw.seller || {
        id: raw.ownerId || '',
        nickname: raw.ownerNickname || '未知用户',
        avatar: raw.ownerAvatar || '',
        reputation: raw.ownerScore || 100,
        publishedCount: 0,
        soldCount: 0,
      },
      createdAt: raw.createdAt || '',
      updatedAt: raw.updatedAt || '',
    }
  },

  // ── 格式化 ────────────────────────────────
  formatProduct(product) {
    const st = PRODUCT_STATUS[product.status] || {}
    const condMap = { brand_new: '全新', used_like_new: '几乎全新', used_good: '良好', used_fair: '一般' }
    const fmtPrice = (p) => p == null ? '面议' : '¥' + Number(p).toFixed(2).replace(/\.00$/, '')
    const fmtTime = (t) => {
      if (!t) return ''
      const d = new Date(t), pad = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
    }
    return {
      ...product,
      priceText: fmtPrice(product.price),
      originalPriceText: product.originalPrice ? fmtPrice(product.originalPrice) : '',
      conditionText: condMap[product.condition] || product.condition || '未知',
      statusText: st.label || product.status,
      statusColor: st.color || '#999',
      createdAtText: fmtTime(product.createdAt),
    }
  },

  checkIsOwner(product) {
    const u = getUserInfo()
    if (!u || !product) return false
    return u.id === product.seller.id || u.id === product.id
  },

  // ── 检查收藏状态 ──────────────────────────
  async checkFavoriteStatus(productId) {
    try {
      // 通过收藏列表判断是否已收藏
      const res = await userService.getFavorites(1, 100)
      const favList = res.list || []
      this.setData({
        isFavorited: favList.some(f => f.productId === Number(productId)),
      })
    } catch (e) {
      // 静默失败
    }
  },

  // ── 图片操作 ──────────────────────────────
  onSwiperChange(e) { this.setData({ currentImageIndex: e.detail.current }) },
  onPreviewImage() {
    const { images, currentImageIndex } = this.data
    if (images.length) wx.previewImage({ urls: images, current: images[currentImageIndex] })
  },

  // ── 收藏 ──────────────────────────────────
  async onToggleFavorite() {
    if (!this.data.isLoggedIn) { wx.showToast({ title: '请先登录', icon: 'none' }); return }
    if (this.data.favoriting) return
    this.setData({ favoriting: true })
    try {
      const { productId, isFavorited } = this.data
      if (isFavorited) {
        await productService.removeFavorite(productId)
      } else {
        await productService.addFavorite(productId)
      }
      this.setData({ isFavorited: !isFavorited })
      wx.showToast({ title: isFavorited ? '已取消收藏' : '已收藏', icon: 'success' })
    } catch (e) {
      wx.showToast({ title: e.message || '操作失败', icon: 'none' })
    } finally { this.setData({ favoriting: false }) }
  },

  // ── 下单 ──────────────────────────────────
  onPlaceOrder() {
    if (!this.data.isLoggedIn) { wx.showToast({ title: '请先登录', icon: 'none' }); return }
    if (this.data.isOwner) { wx.showToast({ title: '不能购买自己的商品', icon: 'none' }); return }
    const p = this.data.product
    if (!p || p.status !== 'published') { wx.showToast({ title: '该商品暂不可购买', icon: 'none' }); return }
    wx.showModal({
      title: '确认下单',
      content: `确认购买「${p.title}」？\n价格：${p.priceText}`,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '下单中...' })
            await orderService.create({ productId: Number(this.data.productId) })
            wx.hideLoading()
            wx.showToast({ title: '下单成功', icon: 'success' })
            // 刷新详情
            this.loadProduct(this.data.productId)
          } catch (e) {
            wx.hideLoading()
            wx.showToast({ title: e.message || '下单失败', icon: 'none' })
          }
        }
      },
    })
  },

  // ── 举报 ──────────────────────────────────
  onReport() {
    if (!this.data.isLoggedIn) { wx.showToast({ title: '请先登录', icon: 'none' }); return }
    wx.showActionSheet({
      itemList: ['信息不实', '违规商品', '侵权内容', '其他原因'],
      success: async (res) => {
        const reasons = ['信息不实', '违规商品', '侵权内容', '其他原因']
        try {
          await reportService.create({
            productId: Number(this.data.productId),
            reason: reasons[res.tapIndex],
          })
          wx.showToast({ title: '举报已提交', icon: 'success' })
        } catch (e) {
          wx.showToast({ title: e.message || '举报失败', icon: 'none' })
        }
      },
    })
  },

  // ── 联系卖家 ──────────────────────────────
  onContactSeller() {
    if (this.data.isOwner) { wx.showToast({ title: '这是您自己的商品', icon: 'none' }); return }
    // TODO: 跳转聊天页
    wx.showToast({ title: '聊天功能开发中', icon: 'none' })
  },

  onShareAppMessage() {
    const { product } = this.data
    return { title: product ? product.title : '校园二手 - 商品详情', path: `/pages/detail/index?id=${this.data.productId}` }
  },

  onRetry() { if (this.data.productId) this.loadProduct(this.data.productId) },
})
