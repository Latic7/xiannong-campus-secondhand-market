// ──────────────────────────────────────────────
//  商品详情页
//  根据商品 ID 加载并展示商品完整信息
// ──────────────────────────────────────────────
const { isLoggedIn, getUserInfo } = require('../../utils/storage')
const { PRODUCT_STATUS, getStatusMeta, normalizeStatus } = require('../../utils/constants')
const productService = require('../../services/product')
const orderService = require('../../services/order')
const reportService = require('../../services/report')
const userService = require('../../services/user')

const categoryService = require('../../services/category')

// ── 分类 ID → 名称映射（启动时从后端加载，见 onLoad）──
let CATEGORY_MAP = {}

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
    activeOrderId: null,
    canUnlist: false,               // 是否可下架（true=显示红色可点击按钮）
    unlistBlockedReason: '',        // 不可下架的原因提示文案
    // ── 下单状态 ──
    orderBtnText: '立即购买',       // 按钮文案：立即购买 / 已预约 / 交易进行中 / 已售出
    orderBtnDisabled: false,        // 按钮是否禁用
  },

  onLoad(options) {
    const productId = options.id || ''
    this.setData({ productId })

    // 加载分类映射（异步，不阻塞页面渲染）
    categoryService.getCategoryMap().then(map => {
      CATEGORY_MAP = map
    }).catch(() => {
      // 静默失败，mapBackendProduct 会用 '其他' 兜底
    })

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
      const isOwner = this.checkIsOwner(formatted)
      const st = normalizeStatus(formatted.status)
      let canUnlist = false
      let unlistBlockedReason = ''
      if (isOwner) {
        if (st === 'SOLD') {
          unlistBlockedReason = '商品已售出，不可下架'
        } else if (['PUBLISHED', 'PENDING', 'DRAFT'].includes(st)) {
          canUnlist = true
        }
      }
      this.setData({
        product: formatted,
        images: formatted.images || [],
        loading: false,
        isOwner,
        canUnlist,
        unlistBlockedReason,
        isLoggedIn: isLoggedIn(),
      })
      // 重置按钮状态
      this.updateOrderBtnState(formatted)
      if (isLoggedIn()) {
        this.checkFavoriteStatus(productId)
        // 异步检测当前用户对该商品是否有活跃订单
        this.checkActiveOrder(productId)
      } else {
        this.setData({ activeOrderId: null })
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
      status: normalizeStatus(raw.status || 'PENDING'),
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
    const st = getStatusMeta(PRODUCT_STATUS, product.status)
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
        isFavorited: favList.some(f => Number(f.productId || f.id) === Number(productId)),
      })
    } catch (e) {
      // 静默失败
    }
  },

  // ── 检查当前用户对该商品是否有活跃订单 ──
  async checkActiveOrder(productId) {
    try {
      const res = await orderService.list({ page: 1, size: 100 })
      const orders = res.list || []
      const activeOrder = orders.find(
        o => Number(o.productId) === Number(productId) && ['RESERVED', 'CONFIRMED'].includes(o.status)
      )
      if (activeOrder) {
        const isConfirmed = activeOrder.status === 'CONFIRMED'
        this.setData({
          orderBtnText: isConfirmed ? '交易进行中' : '已预约',
          orderBtnDisabled: true,
          activeOrderId: activeOrder.id,
        })
        // 有已确认订单时，更新下架按钮状态
        if (isConfirmed) {
          this.setData({
            canUnlist: false,
            unlistBlockedReason: '商品已进入交易确认阶段，不可下架',
          })
        }
      }
    } catch (e) {
      // 静默失败，不影响页面正常使用
    }
  },

  // ── 根据商品状态更新按钮文案 ────────────────
  updateOrderBtnState(product) {
    const status = normalizeStatus(product.status)
    if (status === 'SOLD') {
      this.setData({ orderBtnText: '已售出', orderBtnDisabled: true })
    } else if (this.checkIsOwner(product)) {
      this.setData({ orderBtnText: '我的商品', orderBtnDisabled: true })
    } else if (status !== 'PUBLISHED') {
      this.setData({ orderBtnText: '暂不可购买', orderBtnDisabled: true })
    } else {
      this.setData({ orderBtnText: '立即购买', orderBtnDisabled: false })
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
    if (this.data.orderBtnDisabled) { return }
    const p = this.data.product
    if (!p || normalizeStatus(p.status) !== 'PUBLISHED') { wx.showToast({ title: '该商品暂不可购买', icon: 'none' }); return }
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
            // 立即切换按钮为「已预约」
            this.setData({ orderBtnText: '已预约', orderBtnDisabled: true })
          } catch (e) {
            wx.hideLoading()
            if (e.message && e.message.includes('you already have an active order')) {
              wx.showToast({ title: '您已预约过该商品', icon: 'none' })
              this.setData({ orderBtnText: '已预约', orderBtnDisabled: true })
            } else {
              wx.showToast({ title: e.message || '下单失败', icon: 'none' })
            }
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
            targetType: 'PRODUCT',
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

  // ── 下架商品 ──────────────────────────────
  onUnlistProduct() {
    const { unlistBlockedReason } = this.data
    // 如果不可下架（已售出/已确认），直接提示原因
    if (unlistBlockedReason) {
      wx.showToast({ title: unlistBlockedReason, icon: 'none' })
      return
    }
    wx.showModal({
      title: '确认下架',
      content: '下架后商品将显示为"已下架"，其他用户将无法购买。确定要下架吗？',
      success: async (res) => {
        if (!res.confirm) return
        try {
          wx.showLoading({ title: '下架中...' })
          await productService.remove(this.data.productId)
          wx.hideLoading()
          wx.showToast({ title: '已下架', icon: 'success' })
          this.loadProduct(this.data.productId)
        } catch (e) {
          wx.hideLoading()
          wx.showToast({ title: '下架失败，请稍后重试', icon: 'none' })
        }
      },
    })
  },

  // ── 联系卖家 ──────────────────────────────
  onContactSeller() {
    if (this.data.isOwner) { wx.showToast({ title: '这是您自己的商品', icon: 'none' }); return }
    const seller = this.data.product?.seller
    const contact = seller?.contact
    if (contact) {
      wx.showModal({
        title: '卖家联系方式',
        content: `手机号：${contact}\n\n您可复制该号码到微信或电话联系卖家`,
        confirmText: '复制号码',
        success(res) {
          if (res.confirm) {
            wx.setClipboardData({ data: contact })
          }
        }
      })
    } else {
      wx.showToast({ title: '卖家暂未填写联系方式', icon: 'none' })
    }
  },

  // ── 通过聊天联系卖家（跳转到订单聊天页）──
  onContactSellerChat() {
    const orderId = this.data.activeOrderId
    if (!orderId) {
      wx.showToast({ title: '请先下单后再使用聊天功能', icon: 'none' })
      return
    }
    // 商品已下架时阻止进入聊天
    const st = this.data.product?.status || ''
    if (st === 'REMOVED') {
      wx.showToast({ title: '商品已下架，无法继续沟通', icon: 'none' })
      return
    }
    wx.navigateTo({ url: `/pages/order-chat/index?orderId=${orderId}` })
  },

  onShareAppMessage() {
    const { product } = this.data
    return { title: product ? product.title : '校园二手 - 商品详情', path: `/pages/detail/index?id=${this.data.productId}` }
  },

  onRetry() { if (this.data.productId) this.loadProduct(this.data.productId) },
})
