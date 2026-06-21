const { setAuthExpiredHandler } = require('./utils/api')
const { clearAuth } = require('./utils/storage')
const { CLOUD_ENV } = require('./utils/constants')

App({
  onLaunch() {
    console.log('小程序启动了')

    // 初始化云托管 SDK（对象存储等能力需要）
    wx.cloud.init({
      env: CLOUD_ENV
    })

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
