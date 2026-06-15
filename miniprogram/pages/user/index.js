// ──────────────────────────────────────────────
//  个人中心页
//  微信登录、用户资料、信誉分、收藏入口、发布入口
// ──────────────────────────────────────────────
const {
  isLoggedIn, getUserInfo, saveAuth, clearAuth, setUserInfo,
} = require('../../utils/storage')
const authService = require('../../services/auth')
const userService = require('../../services/user')
const { setAuthExpiredHandler } = require('../../utils/api')

Page({
  data: {
    user: null,
    isLoggedIn: false,

    stats: {
      published: 0,
      sold: 0,
      favorites: 0,
    },

    loading: true,
    loginLoading: false,
  },

  onLoad() {
    // 注册全局登录过期回调
    setAuthExpiredHandler(() => {
      clearAuth()
      this.refreshUserState()
      wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
    })
  },

  onShow() {
    // 同步底部导航栏选中状态（避免 getCurrentPages 时序问题）
    const tabBar = this.getTabBar();
    if (tabBar) {
      tabBar.setData({ selected: 2 });
    }

    // 每次显示时刷新登录态和用户信息
    this.refreshUserState()
  },

  // ── 刷新用户状态 ──────────────────────────
  async refreshUserState() {
    const loggedIn = isLoggedIn()
    let user = null

    if (loggedIn) {
      // 先从本地缓存读取基本信息快速展示
      user = getUserInfo()
      this.setData({
        isLoggedIn: true,
        user: this.formatUser(user),
        loading: false,
      })
      // 异步从服务器拉取最新资料和统计
      this.fetchUserProfile()
    } else {
      this.setData({
        isLoggedIn: false,
        user: this.formatUser(null),
        loading: false,
        stats: { published: 0, sold: 0, favorites: 0 },
      })
    }
  },

  // ── 从服务器拉取最新用户资料 ──────────────
  async fetchUserProfile() {
    try {
      const profile = await userService.getProfile()
      console.log('[fetchUserProfile] raw profile:', JSON.stringify(profile))
      // 合并更新本地缓存和页面数据
      const updated = {
        id: profile.id,
        nickname: profile.nickname,
        avatar: profile.avatar,
        reputation: profile.score,
      }
      setUserInfo(updated)
      this.setData({
        user: this.formatUser(updated),
        stats: {
          published: profile.publishedCount || 0,
          sold: profile.soldCount || 0,
          favorites: profile.favorites || 0,
        },
      })
      console.log('[fetchUserProfile] stats set:', {
        published: profile.publishedCount,
        sold: profile.soldCount,
        favorites: profile.favorites,
      })
    } catch (err) {
      // 静默失败，使用本地缓存数据
      console.warn('获取用户资料失败:', err.message)
    }
  },

  // ── 格式化用户展示数据 ────────────────────
  formatUser(u) {
    if (!u) {
      return {
        nickname: '点击登录',
        avatar: '',
        reputation: 0,
        userId: '',
      }
    }
    return {
      ...u,
      avatar: u.avatar || '',
      reputation: u.reputation != null ? u.reputation : 100,
      reputationText: this.getReputationLabel(u.reputation),
      reputationColor: this.getReputationColor(u.reputation),
    }
  },

  getReputationLabel(score) {
    if (score >= 95) return '信用极好'
    if (score >= 80) return '信用良好'
    if (score >= 60) return '信用一般'
    return '信用较低'
  },

  getReputationColor(score) {
    if (score >= 95) return '#10b981'
    if (score >= 80) return '#3b82f6'
    if (score >= 60) return '#f59e0b'
    return '#ef4444'
  },

  // ── 微信登录（真实 API）───────────────────
  async onLogin() {
    if (this.data.isLoggedIn || this.data.loginLoading) return

    this.setData({ loginLoading: true })
    wx.showLoading({ title: '登录中...' })

    try {
      await authService.wxLogin()
      wx.hideLoading()
      wx.showToast({ title: '登录成功', icon: 'success' })
      this.refreshUserState()
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: err.message || '登录失败', icon: 'none' })
    } finally {
      this.setData({ loginLoading: false })
    }
  },

  // ── 退出登录 ──────────────────────────────
  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await authService.logout()
          } catch (e) {
            // 忽略后端注销错误
          }
          clearAuth()
          wx.showToast({ title: '已退出', icon: 'success' })
          this.refreshUserState()
        }
      },
    })
  },

  // ── 跳转：我的发布 ────────────────────────
  onMyPublished() {
    if (!this.checkLogin()) return
    wx.navigateTo({ url: '/pages/list/index?type=my_published' })
  },

  // ── 跳转：我的收藏 ────────────────────────
  onMyFavorites() {
    if (!this.checkLogin()) return
    wx.navigateTo({ url: '/pages/list/index?type=my_favorites' })
  },

  // ── 跳转：我的订单 ────────────────────────
  onMyOrders() {
    if (!this.checkLogin()) return
    wx.showToast({ title: '订单功能开发中', icon: 'none' })
  },

  // ── 跳转：关于我们 ────────────────────────
  onAbout() {
    wx.showModal({
      title: '校园二手交易',
      content: '版本 1.0.0\n\n专为校园师生打造的二手交易平台，安全、便捷、值得信赖。',
      showCancel: false,
    })
  },

  // ── 登录校验 ──────────────────────────────
  checkLogin() {
    if (!this.data.isLoggedIn) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return false
    }
    return true
  },

  // ── 编辑个人资料 ──────────────────────────
  onEditProfile() {
    if (!this.checkLogin()) return
    wx.showToast({ title: '编辑资料功能开发中', icon: 'none' })
  },
})

