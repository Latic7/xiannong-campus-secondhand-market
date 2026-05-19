// ──────────────────────────────────────────────
//  发布商品页
//  表单校验 + 图片上传 + 发布提交
// ──────────────────────────────────────────────
const { isLoggedIn } = require('../../utils/storage')
const { IMAGE_MAX_COUNT, IMAGE_MAX_SIZE } = require('../../utils/constants')

// ── 常量 ──────────────────────────────────────
const TITLE_MAX = 50
const DESC_MAX = 500

const CATEGORIES = [
  '数码电子', '书籍教材', '生活用品', '服饰鞋包',
  '运动户外', '美妆护肤', '食品饮料', '其他',
]

const CONDITIONS = [
  { value: 'brand_new', label: '全新未拆封' },
  { value: 'used_like_new', label: '几乎全新' },
  { value: 'used_good', label: '良好,有轻微使用痕迹' },
  { value: 'used_fair', label: '一般,有明显使用痕迹' },
]

Page({
  data: {
    // 表单字段
    title: '',
    description: '',
    price: '',
    categoryIndex: -1,
    categoryText: '请选择分类',
    conditionValue: '',
    conditionText: '请选择成色',
    campus: '',

    // 图片列表 [{path, tempPath}]
    images: [],

    // 输入计数
    titleCount: 0,
    descCount: 0,

    // UI 状态
    submitting: false,
    categoryPickerVisible: false,
    conditionPickerVisible: false,
    errors: {},

    // 选择器数据
    categories: CATEGORIES,
    conditions: CONDITIONS,
  },

  onLoad() {
    if (!isLoggedIn()) {
      wx.showToast({ title: '请先登录后再发布', icon: 'none' })
    }
  },

  // ── 输入绑定 ──────────────────────────────
  onTitleInput(e) {
    const val = e.detail.value || ''
    this.setData({
      title: val.slice(0, TITLE_MAX),
      titleCount: val.length,
    })
    this.clearError('title')
  },

  onDescInput(e) {
    const val = e.detail.value || ''
    this.setData({
      description: val.slice(0, DESC_MAX),
      descCount: val.length,
    })
    this.clearError('description')
  },

  onPriceInput(e) {
    const val = e.detail.value || ''
    this.setData({ price: val })
    this.clearError('price')
  },

  onCampusInput(e) {
    this.setData({ campus: e.detail.value || '' })
    this.clearError('campus')
  },

  // ── 分类选择 ──────────────────────────────
  onCategoryTap() {
    this.setData({ categoryPickerVisible: true })
  },
  onCategoryChange(e) {
    const idx = Number(e.detail.value)
    this.setData({
      categoryIndex: idx,
      categoryText: CATEGORIES[idx],
      categoryPickerVisible: false,
    })
    this.clearError('category')
  },
  onCategoryCancel() {
    this.setData({ categoryPickerVisible: false })
  },

  // ── 成色选择 ──────────────────────────────
  onConditionTap() {
    this.setData({ conditionPickerVisible: true })
  },
  onConditionChange(e) {
    const idx = Number(e.detail.value)
    const item = CONDITIONS[idx]
    this.setData({
      conditionValue: item.value,
      conditionText: item.label,
      conditionPickerVisible: false,
    })
    this.clearError('condition')
  },
  onConditionCancel() {
    this.setData({ conditionPickerVisible: false })
  },

  // ── 图片操作 ──────────────────────────────
  onAddImage() {
    const remaining = IMAGE_MAX_COUNT - this.data.images.length
    if (remaining <= 0) {
      wx.showToast({ title: `最多上传${IMAGE_MAX_COUNT}张图片`, icon: 'none' })
      return
    }

    wx.chooseMedia({
      count: remaining,
      mediaType: ['image'],
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const newImages = res.tempFiles
          .filter((f) => {
            if (f.size > IMAGE_MAX_SIZE) {
              wx.showToast({ title: '单张图片不能超过5MB', icon: 'none' })
              return false
            }
            return true
          })
          .map((f) => ({ path: f.tempFilePath, tempPath: f.tempFilePath }))

        this.setData({
          images: [...this.data.images, ...newImages].slice(0, IMAGE_MAX_COUNT),
        })
      },
    })
  },

  onPreviewImage(e) {
    const idx = e.currentTarget.dataset.index
    const urls = this.data.images.map((i) => i.path)
    wx.previewImage({ urls, current: urls[idx] })
  },

  onRemoveImage(e) {
    const idx = e.currentTarget.dataset.index
    const images = this.data.images.filter((_, i) => i !== idx)
    this.setData({ images })
  },

  // ── 表单校验 ──────────────────────────────
  clearError(field) {
    if (this.data.errors[field]) {
      const errors = { ...this.data.errors }
      delete errors[field]
      this.setData({ errors })
    }
  },

  setError(field, msg) {
    const errors = { ...this.data.errors, [field]: msg }
    this.setData({ errors })
  },

  validate() {
    const { title, price, categoryIndex, conditionValue, campus } = this.data

    if (!title || !title.trim()) {
      this.setError('title', '请输入商品标题')
      return false
    }
    if (title.trim().length < 2) {
      this.setError('title', '标题至少2个字')
      return false
    }

    if (!price || price.trim() === '') {
      this.setError('price', '请输入价格')
      return false
    }
    const priceNum = parseFloat(price)
    if (isNaN(priceNum) || priceNum < 0) {
      this.setError('price', '请输入有效的价格')
      return false
    }
    if (!/^\d+(\.\d{1,2})?$/.test(price.trim())) {
      this.setError('price', '价格最多两位小数')
      return false
    }

    if (categoryIndex < 0) {
      this.setError('category', '请选择商品分类')
      return false
    }

    if (!conditionValue) {
      this.setError('condition', '请选择商品成色')
      return false
    }

    if (!campus || !campus.trim()) {
      this.setError('campus', '请输入所在校区')
      return false
    }

    if (this.data.images.length === 0) {
      wx.showToast({ title: '请至少上传一张图片', icon: 'none' })
      return false
    }

    return true
  },

  // ── 发布提交 ──────────────────────────────
  async onSubmit() {
    if (this.data.submitting) return
    if (!this.validate()) return

    this.setData({ submitting: true })

    try {
      // TODO: 先上传图片获取 URL，再提交表单
      // const imageUrls = await this.uploadImages()
      // await require('../../services/product').create({ ...formData, images: imageUrls })

      wx.showToast({ title: '发布成功', icon: 'success', duration: 2000 })
      setTimeout(() => {
        wx.navigateBack()
      }, 2000)
    } catch (err) {
      wx.showToast({ title: err.message || '发布失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  // TODO: 图片上传逻辑（后续接入）
  async uploadImages() {
    const uploads = this.data.images.map((img) => {
      return new Promise((resolve, reject) => {
        // TODO: 调用上传 API
        // wx.uploadFile({ filePath: img.path, ... })
        resolve(img.path)
      })
    })
    return Promise.all(uploads)
  },
})

