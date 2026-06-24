// ──────────────────────────────────────────────
//  发布商品页
//  表单校验 + 图片上传 + 发布提交
// ──────────────────────────────────────────────
const { isLoggedIn } = require('../../utils/storage')
const { IMAGE_MAX_COUNT, IMAGE_MAX_SIZE } = require('../../utils/constants')
const productService = require('../../services/product')
const categoryService = require('../../services/category')

// ── 常量 ──────────────────────────────────────
const TITLE_MAX = 50
const DESC_MAX = 500

const CONDITIONS = [
  { value: 'brand_new', label: '全新未拆封' },
  { value: 'used_like_new', label: '几乎全新' },
  { value: 'used_good', label: '良好,有轻微使用痕迹' },
  { value: 'used_fair', label: '一般,有明显使用痕迹' },
]

const CAMPUSES = [
  { value: 'east', label: '东校区' },
  { value: 'west', label: '西校区' },
]

Page({
  data: {
    title: '',
    description: '',
    price: '',
    categoryIndex: -1,
    categoryText: '请选择分类',
    conditionValue: '',
    conditionText: '请选择成色',
    campusIndex: -1,
    campusText: '请选择校区',

    images: [],

    titleCount: 0,
    descCount: 0,

    submitting: false,
    categoryPickerVisible: false,
    conditionPickerVisible: false,
    campusPickerVisible: false,
    errors: {},

    categories: [],
    conditions: CONDITIONS,
    campuses: CAMPUSES,
  },

  onLoad() {
    if (!isLoggedIn()) {
      wx.showToast({ title: '请先登录后再发布', icon: 'none' })
    }

    // 动态加载分类（异步，不阻塞页面渲染）
    categoryService.clearCache()
    categoryService.getCategories().then(raw => {
      this.setData({ categories: raw })
    }).catch(() => {
      // 静默失败，分类为空将阻止提交
    })
  },

  onShow() {
    // 同步底部导航栏选中状态（避免 getCurrentPages 时序问题）
    const tabBar = this.getTabBar();
    if (tabBar) {
      tabBar.setData({ selected: 1 });
      tabBar.refreshBadge();
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

  // ── 分类选择 ──────────────────────────────
  onCategoryTap() {
    this.setData({ categoryPickerVisible: true })
  },
  onCategoryChange(e) {
    const idx = Number(e.detail.value)
    const cat = this.data.categories[idx]
    if (!cat) return
    this.setData({
      categoryIndex: idx,
      categoryText: cat.name,
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

  // ── 校区选择 ──────────────────────────────
  onCampusTap() {
    this.setData({ campusPickerVisible: true })
  },
  onCampusChange(e) {
    const idx = Number(e.detail.value)
    this.setData({
      campusIndex: idx,
      campusText: CAMPUSES[idx].label,
      campusPickerVisible: false,
    })
    this.clearError('campus')
  },
  onCampusCancel() {
    this.setData({ campusPickerVisible: false })
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
    const { title, price, categoryIndex, conditionValue, campusIndex } = this.data

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
    if (priceNum > 99999999.99) {
      this.setError('price', '价格超出上限（最高 99999999.99 元）')
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

    if (campusIndex < 0) {
      this.setError('campus', '请选择所在校区')
      return false
    }

    if (this.data.images.length === 0) {
      wx.showToast({ title: '请至少上传一张图片', icon: 'none' })
      return false
    }

    return true
  },

  // ── 发布提交（真实 API）───────────────────
  async onSubmit() {
    if (this.data.submitting) return
    if (!this.validate()) return

    this.setData({ submitting: true })
    wx.showLoading({ title: '发布中...', mask: true })

    try {
      const { title, description, price, categoryIndex, campusIndex, categories } = this.data
      const categoryId = categories[categoryIndex]?.id
      const campus = CAMPUSES[campusIndex].label

      // 1. 先创建商品（不含图片）
      const created = await productService.create({
        title: title.trim(),
        price: parseFloat(price),
        categoryId,
        description: description.trim() + (campus ? '\n\n所在校区：' + campus : ''),
      })

      const productId = created.id
      if (!productId) throw new Error('创建商品失败')

      // 2. 上传图片
      const filePaths = this.data.images.map(img => img.tempPath || img.path)
      if (filePaths.length > 0) {
        await productService.uploadImages(productId, filePaths)
      }

      // 3. 清空表单，防止重复提交
      this.resetForm()

      wx.hideLoading()
      wx.showToast({ title: '发布成功', icon: 'success', duration: 2000 })
      setTimeout(() => {
        wx.switchTab({ url: '/pages/home/index' })
      }, 2000)
    } catch (err) {
      wx.hideLoading()
      const msg = err.message || ''
      // 根据后端返回的错误信息给出直观提示
      if (msg.includes('price') && msg.includes('le')) {
        wx.showToast({ title: '价格超出上限（最高 99999999.99 元）', icon: 'none' })
      } else if (msg.includes('title') && (msg.includes('min_length') || msg.includes('max_length'))) {
        wx.showToast({ title: '标题长度不符合要求（1-128字）', icon: 'none' })
      } else if (msg.includes('category') || msg.includes('categoryId')) {
        wx.showToast({ title: '请选择有效的商品分类', icon: 'none' })
      } else if (msg.includes('validation error') || msg.includes('10001')) {
        wx.showToast({ title: '表单数据有误，请检查输入内容', icon: 'none' })
      } else if (msg.includes('internal server error')) {
        wx.showToast({ title: '服务器开小差了，请稍后重试', icon: 'none' })
      } else {
        wx.showToast({ title: msg || '发布失败', icon: 'none' })
      }
    } finally {
      this.setData({ submitting: false })
    }
  },

  // ── 重置表单到初始状态 ────────────────────
  resetForm() {
    this.setData({
      title: '',
      description: '',
      price: '',
      categoryIndex: -1,
      categoryText: '请选择分类',
      conditionValue: '',
      conditionText: '请选择成色',
      campusIndex: -1,
      campusText: '请选择校区',
      images: [],
      titleCount: 0,
      descCount: 0,
      errors: {},
    })
  },
})

