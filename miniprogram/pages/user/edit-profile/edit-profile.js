// ──────────────────────────────────────────────
//  编辑个人资料页
//  昵称、学院、联系方式（头像上传待后端确定方案后补充）
// ──────────────────────────────────────────────
const { getUserInfo, setUserInfo } = require('../../../utils/storage')
const userService = require('../../../services/user')

const NICKNAME_MAX = 20
const COLLEGE_MAX = 30
const CONTACT_MAX = 30

Page({
  data: {
    nickname: '',
    college: '',
    contact: '',

    nicknameCount: 0,
    collegeCount: 0,
    contactCount: 0,

    saving: false,
  },

  onLoad() {
    const user = getUserInfo()
    if (user) {
      this.setData({
        nickname: user.nickname || '',
        college: user.college || '',
        contact: user.contact || '',
        nicknameCount: (user.nickname || '').length,
        collegeCount: (user.college || '').length,
        contactCount: (user.contact || '').length,
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

  onContactInput(e) {
    const val = e.detail.value || ''
    this.setData({
      contact: val.slice(0, CONTACT_MAX),
      contactCount: val.length,
    })
  },

  // ── 保存资料 ──────────────────────────────
  async onSave() {
    if (this.data.saving) return

    const { nickname } = this.data
    if (!nickname.trim()) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' })
      return
    }

    this.setData({ saving: true })
    wx.showLoading({ title: '保存中...' })

    try {
      const payload = {
        nickname: nickname.trim(),
        college: this.data.college.trim() || undefined,
        contact: this.data.contact.trim() || undefined,
      }
      await userService.updateProfile(payload)

      // 更新本地缓存
      const user = getUserInfo()
      if (user) {
        setUserInfo({
          ...user,
          nickname: payload.nickname,
          college: payload.college || user.college,
          contact: payload.contact || user.contact,
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
