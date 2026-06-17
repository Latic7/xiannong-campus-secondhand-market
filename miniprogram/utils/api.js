// ──────────────────────────────────────────────
//  API 协议封装层
//  统一处理 baseURL、Token 注入、错误提示、
//  401 自动刷新、超时与重试
// ──────────────────────────────────────────────
const { getAccessToken, getRefreshToken, saveAuth, clearAuth } = require('./storage')

// ── 配置（生产环境需替换为实际域名）───────────
const BASE_URL = 'http://localhost:8000'
const TIMEOUT = 15000

// ── 请求计数器（避免并发刷新 token）───────────
let refreshing = false
let refreshQueue = []

// ── 状态回调（供页面监听登录过期）─────────────
let onAuthExpired = null

function setAuthExpiredHandler(fn) {
  onAuthExpired = fn
}

// ── 核心请求方法 ──────────────────────────────

function request(method, url, data, extraHeader = {}) {
  return new Promise((resolve, reject) => {
    const token = getAccessToken()
    const header = {
      'Content-Type': 'application/json',
      ...extraHeader,
    }
    if (token) {
      header['Authorization'] = 'Bearer ' + token
    }

    wx.request({
      url: BASE_URL + url,
      method,
      data,
      header,
      timeout: TIMEOUT,
      success(res) {
        if (res.statusCode === 200 && res.data && res.data.code === 0) {
          resolve(res.data.data)
        } else if (res.statusCode === 401 || (res.data && res.data.code >= 10030 && res.data.code <= 10032)) {
          // token 过期，尝试静默刷新
          handleTokenRefresh(method, url, data, extraHeader).then(resolve).catch((err) => {
            clearAuth()
            if (onAuthExpired) onAuthExpired()
            reject(err)
          })
        } else {
          const msg = (res.data && res.data.message) ? res.data.message : '请求失败'
          reject(new Error(msg))
        }
      },
      fail() {
        reject(new Error('网络异常，请检查网络连接'))
      },
    })
  })
}

// ── Token 刷新队列 ────────────────────────────

function handleTokenRefresh(method, url, data, extraHeader) {
  return new Promise((resolve, reject) => {
    refreshQueue.push({ method, url, data, extraHeader, resolve, reject })
    if (!refreshing) {
      refreshing = true
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        drainRefreshQueue(new Error('登录已过期，请重新登录'))
        return
      }
      wx.request({
        url: BASE_URL + '/api/auth/refresh',
        method: 'POST',
        data: { refreshToken },
        header: { 'Content-Type': 'application/json' },
        timeout: TIMEOUT,
        success(res) {
          if (res.statusCode === 200 && res.data && res.data.code === 0) {
            const d = res.data.data
            saveAuth({
              accessToken: d.accessToken,
              refreshToken: d.refreshToken,
              expiresIn: d.expiresIn,
            })
            drainRefreshQueue(null)
          } else {
            drainRefreshQueue(new Error('登录已过期，请重新登录'))
          }
        },
        fail() {
          drainRefreshQueue(new Error('网络异常'))
        },
      })
    }
  })
}

function drainRefreshQueue(err) {
  refreshing = false
  const q = refreshQueue
  refreshQueue = []
  q.forEach(({ method, url, data, extraHeader, resolve, reject }) => {
    if (err) {
      reject(err)
    } else {
      request(method, url, data, extraHeader).then(resolve).catch(reject)
    }
  })
}

// ── 上传文件 ──────────────────────────────────

function uploadFile(url, filePath, formData = {}) {
  return new Promise((resolve, reject) => {
    const token = getAccessToken()
    const header = {}
    if (token) {
      header['Authorization'] = 'Bearer ' + token
    }
    wx.uploadFile({
      url: BASE_URL + url,
      filePath,
      name: 'file',
      formData,
      header,
      timeout: 30000,
      success(res) {
        try {
          const data = JSON.parse(res.data)
          if (data && data.code === 0) {
            resolve(data.data)
          } else {
            reject(new Error((data && data.message) || '上传失败'))
          }
        } catch (e) {
          reject(new Error('服务器响应异常'))
        }
      },
      fail() {
        reject(new Error('网络异常，请检查网络连接'))
      },
    })
  })
}

// ── 便捷方法 ──────────────────────────────────

function get(url, params) {
  const query = params ? '?' + Object.keys(params)
    .filter(k => params[k] != null)
    .map(k => k + '=' + encodeURIComponent(params[k]))
    .join('&') : ''
  return request('GET', url + query)
}

function post(url, data) {
  return request('POST', url, data)
}

function put(url, data) {
  return request('PUT', url, data)
}

function del(url) {
  return request('DELETE', url)
}

module.exports = {
  BASE_URL,
  setAuthExpiredHandler,
  request,
  uploadFile,
  get,
  post,
  put,
  del,
}
