// ──────────────────────────────────────────────
//  个人中心页
//  用户资料、信誉分、收藏入口、发布入口
// ──────────────────────────────────────────────
const {
  isLoggedIn, getUserInfo, saveAuth, clearAuth, dumpAuth,
} = require('../../utils/storage')

Page({
  data: {
    // 用户信息
    user: null,
    isLoggedIn: false,

    // 统计数据
    stats: {
      published: 0,
      sold: 0,
      favorites: 0,
    },

    // UI 状态
    loading: true,
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
  refreshUserState() {
    const loggedIn = isLoggedIn()
    let user = null

    if (loggedIn) {
      user = getUserInfo()
      // TODO: 从服务器拉取最新信誉分和统计数据
      // await this.fetchUserProfile()
    }

    this.setData({
      isLoggedIn: loggedIn,
      user: this.formatUser(user),
      loading: false,
    })

    if (loggedIn) {
      this.loadStats()
    }
  },

  // ── Mock 格式化用户（开发期）──────────────
  formatUser(u) {
    if (!u) {
      // 未登录时展示默认占位
      return {
        nickname: '点击登录',
        avatar: '',
        reputation: 0,
        userId: '',
      }
    }
    return {
      ...u,
      avatar: u.avatar || 'https://picsum.photos/seed/default_avatar/200/200',
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

  // ── 加载统计数据 ──────────────────────────
  async loadStats() {
    try {
      // TODO: 替换为 API → user.getStats()
      this.setData({
        stats: {
          published: 5,
          sold: 3,
          favorites: 12,
        },
      })
    } catch (err) {
      // 静默失败，使用默认值
    }
  },

  // ── 登录 ──────────────────────────────────
  onLogin() {
    if (this.data.isLoggedIn) return

    wx.showLoading({ title: '登录中...' })

    // 模拟微信登录流程
    // TODO: 替换为实际登录 API → auth.login()
    setTimeout(() => {
      const mockAuthData = {
        accessToken: 'mock_token_' + Date.now(),
        refreshToken: 'mock_refresh_' + Date.now(),
        expiresIn: 7200,
        user: {
          id: 'user_001',
          nickname: '小明同学',
          avatar: 'https://picsum.photos/seed/avatar1/200/200',
          reputation: 98,
        },
      }

      saveAuth(mockAuthData)
      wx.hideLoading()
      wx.showToast({ title: '登录成功', icon: 'success' })
      this.refreshUserState()
    }, 800)
  },

  // ── 退出登录 ──────────────────────────────
  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
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
    // TODO: 跳转到我的发布列表
    wx.navigateTo({ url: '/pages/list/index?type=my_published' })
  },

  // ── 跳转：我的收藏 ────────────────────────
  onMyFavorites() {
    if (!this.checkLogin()) return
    // TODO: 跳转到我的收藏列表
    wx.navigateTo({ url: '/pages/list/index?type=my_favorites' })
  },

  // ── 跳转：我的订单 ────────────────────────
  onMyOrders() {
    if (!this.checkLogin()) return
    // TODO: 跳转到我的订单页
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
    // TODO: 跳转编辑资料页
    wx.showToast({ title: '编辑资料功能开发中', icon: 'none' })
  },
})

