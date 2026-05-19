import { isLoggedIn, getUserInfo, clearAuth } from './utils/storage'

App({
  globalData: {
    userInfo: null,
    isLoggedIn: false,
  },

  onLaunch() {
    // 启动时恢复登录态
    const loggedIn = isLoggedIn()
    this.globalData.isLoggedIn = loggedIn
    if (loggedIn) {
      this.globalData.userInfo = getUserInfo()
    } else {
      clearAuth()
    }
  },

  /** 登录成功后由登录页调用，同步全局状态 */
  setLogin(authData) {
    const { saveAuth } = require('./utils/storage')
    saveAuth(authData)
    this.globalData.isLoggedIn = true
    this.globalData.userInfo = authData.user || null
  },

  /** 退出登录 */
  setLogout() {
    clearAuth()
    this.globalData.isLoggedIn = false
    this.globalData.userInfo = null
  },
})
