const { setAuthExpiredHandler } = require('./utils/api')
const { clearAuth } = require('./utils/storage')

App({
  onLaunch() {
    console.log('小程序启动了')
    setAuthExpiredHandler(() => {
      clearAuth()
      wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
      setTimeout(() => {
        wx.switchTab({ url: '/pages/user/index' })
      }, 800)
    })
  },
  globalData: {
    userInfo: null
  }
})
