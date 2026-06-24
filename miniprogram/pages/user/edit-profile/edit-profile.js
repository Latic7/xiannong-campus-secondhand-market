// ──────────────────────────────────────────────
//  编辑个人资料页
//  昵称、学院、手机号
// ──────────────────────────────────────────────
const { getUserInfo, setUserInfo } = require('../../../utils/storage')
const userService = require('../../../services/user')
const { validatePhone } = require('../../../utils/validator')

const NICKNAME_MAX = 20
const COLLEGE_MAX = 30
const PHONE_MAX = 11

Page({
  data: {
    nickname: '',
    college: '',
    phone: '',

    nicknameCount: 0,
    collegeCount: 0,
    phoneCount: 0,

    phoneError: '',
    saving: false,
  },

  onLoad() {
    const user = getUserInfo()
    if (user) {
      this.setData({
        nickname: user.nickname || '',
        college: user.college || '',
        phone: user.contact || '',
        nicknameCount: (user.nickname || '').length,
        collegeCount: (user.college || '').length,
        phoneCount: (user.contact || '').length,
      })
    }
  },

  // ── 输入绑定 ──────────────────────────────
  onNicknameInput(e) {
    const val = e.detail.value || ''
    this.setData({
      nickname: val.slice(0, NICKNAME_MAX),
      nicknameCount: val.length,
    })
  },

  onCollegeInput(e) {
    const val = e.detail.value || ''
    this.setData({
      college: val.slice(0, COLLEGE_MAX),
      collegeCount: val.length,
    })
  },

  onPhoneInput(e) {
    const val = e.detail.value || ''
    // 只允许输入数字
    const digits = val.replace(/\D/g, '').slice(0, PHONE_MAX)
    // 仅在用户已输入内容但格式不对时显示错误，空值不报错
    const showError = digits.length > 0 ? validatePhone(digits) : { valid: true }
    this.setData({
      phone: digits,
      phoneCount: digits.length,
      phoneError: !showError.valid ? showError.message : '',
    })
  },

  // ── 保存资料 ──────────────────────────────
  async onSave() {
    if (this.data.saving) return

    const { nickname, phone } = this.data
    if (!nickname.trim()) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' })
      return
    }

    // 手机号校验（有值时检查格式，允许为空）
    if (phone) {
      const phoneResult = validatePhone(phone)
      if (!phoneResult.valid) {
        this.setData({ phoneError: phoneResult.message })
        wx.showToast({ title: phoneResult.message, icon: 'none' })
        return
      }
    }

    this.setData({ saving: true })
    wx.showLoading({ title: '保存中...' })

    try {
      const payload = {
        nickname: nickname.trim(),
        college: this.data.college.trim() || undefined,
        contact: phone,
      }
      await userService.updateProfile(payload)

      // 更新本地缓存
      const user = getUserInfo()
      if (user) {
        setUserInfo({
          ...user,
          nickname: payload.nickname,
          college: payload.college || user.college,
          contact: payload.contact,
        })
      }

      wx.hideLoading()
      wx.showToast({ title: '保存成功', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 1200)
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: err.message || '保存失败', icon: 'none' })
    } finally {
      this.setData({ saving: false })
    }
  },
})
