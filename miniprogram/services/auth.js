// ──────────────────────────────────────────────
//  认证服务
//  微信登录、Token 刷新、注销、获取当前用户
// ──────────────────────────────────────────────
const api = require('../utils/api')
const { saveAuth, setUserInfo } = require('../utils/storage')

module.exports = {

  /**
   * 微信登录
   * 调用 wx.login 获取 code，然后换取后端 token
   */
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success(res) {
          if (!res.code) {
            reject(new Error('获取微信登录凭证失败'))
            return
          }
          api.post('/api/auth/wx-login', { code: res.code })
            .then((data) => {
              // 持久化登录态
              saveAuth({
                accessToken: data.accessToken,
                refreshToken: data.refreshToken,
                expiresIn: data.expiresIn,
                user: data.user,
              })
              resolve(data.user)
            })
            .catch(reject)
        },
        fail() {
          reject(new Error('微信登录失败'))
        },
      })
    })
  },

  /** 刷新 token */
  refreshToken(refreshToken) {
    return api.post('/api/auth/refresh', { refreshToken }).then((data) => {
      saveAuth({
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
        expiresIn: data.expiresIn,
      })
      return data
    })
  },

  /** 获取当前登录用户信息（通过 token） */
  getMe() {
    return api.get('/api/auth/me')
  },

  /** 注销 */
  logout() {
    return api.post('/api/auth/logout').catch(() => {
      // 即使后端注销失败也清除本地状态
    })
  },
}
