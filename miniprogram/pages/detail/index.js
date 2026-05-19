// ──────────────────────────────────────────────
//  商品详情页
//  根据商品 ID 加载并展示商品完整信息
// ──────────────────────────────────────────────
const { isLoggedIn, getUserInfo } = require('../../utils/storage')
const { PRODUCT_STATUS } = require('../../utils/constants')

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

  // ── 加载商品详情 ──────────────────────────
  async loadProduct(productId) {
    this.setData({ loading: true, errorMsg: '' })
    try {
      // TODO: 替换为实际 API → services/product.getDetail(productId)
      const product = this.mockLoadProduct(productId)
      const formatted = this.formatProduct(product)
      this.setData({
        product: formatted,
        images: formatted.images || [],
        loading: false,
        isOwner: this.checkIsOwner(formatted),
        isLoggedIn: isLoggedIn(),
      })
      if (isLoggedIn()) this.checkFavoriteStatus(productId)
    } catch (err) {
      this.setData({ loading: false, errorMsg: err.message || '加载失败，请重试' })
    }
  },

  // ── Mock（开发期临时）──────────────────────
  mockLoadProduct(productId) {
    return {
      id: productId,
      title: '九成新 iPad Pro 2024 M4 11英寸',
      description: '去年11月购入，使用不到半年，无磕碰无划痕，屏幕贴膜，电池健康98%。附赠原装充电器和包装盒。\n\n因换新款 MacBook 故出，限校内面交。',
      price: 5200,
      originalPrice: 6999,
      images: [
        'https://picsum.photos/seed/ipad1/750/750',
        'https://picsum.photos/seed/ipad2/750/750',
        'https://picsum.photos/seed/ipad3/750/750',
        'https://picsum.photos/seed/ipad4/750/750',
      ],
      category: '数码电子',
      condition: 'used_like_new',
      campus: '北校区',
      status: 'published',
      viewCount: 328,
      favoriteCount: 15,
      seller: {
        id: 'user_001', nickname: '小明同学',
        avatar: 'https://picsum.photos/seed/avatar1/200/200',
        reputation: 98, publishedCount: 12, soldCount: 8,
      },
      createdAt: '2026-05-15T10:30:00Z',
      updatedAt: '2026-05-18T14:20:00Z',
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
    return u && product.seller ? u.id === product.seller.id : false
  },

  async checkFavoriteStatus(productId) {
    // TODO: 替换为 API → product.isFavorited(productId)
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
      // TODO: API → product.toggleFavorite(productId, isFavorited ? 'remove' : 'add')
      const n = !this.data.isFavorited
      this.setData({ isFavorited: n })
      wx.showToast({ title: n ? '已收藏' : '已取消收藏', icon: 'success' })
    } catch (e) {
      wx.showToast({ title: '操作失败', icon: 'none' })
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
      success: (res) => {
        if (res.confirm) {
          // TODO: API → order.create(productId)
          wx.showToast({ title: '下单成功', icon: 'success' })
        }
      },
    })
  },

  // ── 举报 ──────────────────────────────────
  onReport() {
    if (!this.data.isLoggedIn) { wx.showToast({ title: '请先登录', icon: 'none' }); return }
    wx.showActionSheet({
      itemList: ['信息不实', '违规商品', '侵权内容', '其他原因'],
      success: (res) => {
        const reasons = ['信息不实', '违规商品', '侵权内容', '其他原因']
        // TODO: API → report.create({ productId, reason: reasons[res.tapIndex] })
        wx.showToast({ title: '举报已提交', icon: 'success' })
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
