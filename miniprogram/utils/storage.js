// ──────────────────────────────────────────────
//  登录态与本地存储统一管理
//  所有页面 / services 都只通过本模块读写登录态，
//  不直接调用 wx.setStorageSync / wx.getStorageSync
// ──────────────────────────────────────────────

// ── 存储键常量（仅供本模块内部使用）──────────
const KEY = {
  ACCESS_TOKEN: 'auth_access_token',
  REFRESH_TOKEN: 'auth_refresh_token',
  TOKEN_EXPIRE_AT: 'auth_expire_at',
  USER_INFO: 'auth_user_info',
}

// ── 底层原子读写（与微信原生 API 之间加一层 try-catch）──

export function setItem(key, value) {
  try { wx.setStorageSync(key, value); return true; } catch (e) { return false; }
}
export function getItem(key) {
  try { return wx.getStorageSync(key); } catch (e) { return null; }
}
export function removeItem(key) {
  try { wx.removeStorageSync(key); return true; } catch (e) { return false; }
}

// ── Token 读写 ────────────────────────────────

/** 获取当前 accessToken，不存在或已过期返回 null */
export function getAccessToken() {
  if (isTokenExpired()) return null
  return getItem(KEY.ACCESS_TOKEN)
}

export function setAccessToken(token) {
  return setItem(KEY.ACCESS_TOKEN, token)
}

export function getRefreshToken() {
  return getItem(KEY.REFRESH_TOKEN)
}

export function setRefreshToken(token) {
  return setItem(KEY.REFRESH_TOKEN, token)
}

// ── Token 过期时间管理 ─────────────────────────

/**
 * 获取 token 过期时刻的毫秒时间戳（Date.now() 基准）
 * 未存储时返回 0
 */
export function getTokenExpireAt() {
  const v = getItem(KEY.TOKEN_EXPIRE_AT)
  return v ? Number(v) : 0
}

export function setTokenExpireAt(expireAt) {
  return setItem(KEY.TOKEN_EXPIRE_AT, expireAt)
}

// ── 用户信息缓存 ──────────────────────────────

export function getUserInfo() {
  return getItem(KEY.USER_INFO)
}

export function setUserInfo(user) {
  return setItem(KEY.USER_INFO, user)
}

// ── 登录态判定 ────────────────────────────────

/** token 存在且未过期 */
export function isLoggedIn() {
  const token = getItem(KEY.ACCESS_TOKEN)
  if (!token) return false
  return !isTokenExpired()
}

/** 当前 token 是否已过期（提前 60 秒视为过期，避免边界问题） */
export function isTokenExpired() {
  const expireAt = getTokenExpireAt()
  if (!expireAt) return true
  return Date.now() > expireAt - 60000
}

// ── 一次写入 / 一次清除 ───────────────────────

/**
 * 登录成功后调用：一次写入 token + 用户信息。
 * @param {Object} authData  对应 OpenAPI AuthTokens 结构
 * @param {string} authData.accessToken
 * @param {string} authData.refreshToken
 * @param {number} authData.expiresIn  秒数
 * @param {Object} authData.user       UserProfile
 */
export function saveAuth(authData) {
  const { accessToken, refreshToken, expiresIn, user } = authData
  setAccessToken(accessToken)
  setRefreshToken(refreshToken || '')
  setTokenExpireAt(Date.now() + (expiresIn || 3600) * 1000)
  setUserInfo(user || null)
}

/** 退出登录 / 登录过期时调用：清空全部认证数据 */
export function clearAuth() {
  removeItem(KEY.ACCESS_TOKEN)
  removeItem(KEY.REFRESH_TOKEN)
  removeItem(KEY.TOKEN_EXPIRE_AT)
  removeItem(KEY.USER_INFO)
}

// ── 调试工具（仅开发期使用）────────────────────
export function dumpAuth() {
  return {
    accessToken: getItem(KEY.ACCESS_TOKEN),
    refreshToken: getItem(KEY.REFRESH_TOKEN),
    expireAt: getTokenExpireAt(),
    isLoggedIn: isLoggedIn(),
    user: getUserInfo(),
  }
}
