// ──────────────────────────────────────────────
//  头像生成工具
//  根据用户 ID 生成确定性的随机头像（类似 GitHub identicon）
//  纯前端实现，不依赖后端
// ──────────────────────────────────────────────

// 精选的 18 种暖色/柔和背景色（避开太刺眼的颜色）
const COLORS = [
  '#E17076', '#F39C6D', '#EAA144', '#F5D76E',
  '#7BC8A4', '#5DADE2', '#7E8C8D', '#A89BB8',
  '#F1948A', '#AED6F1', '#A3E4D7', '#FAD7A0',
  '#D7BDE2', '#85C1E9', '#82E0AA', '#F8C471',
  '#D2B4DE', '#A9CCE3',
]

/**
 * 简单字符串哈希 → 0 ~ N-1 的索引
 */
function hashIndex(str, N) {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0
  }
  return Math.abs(h) % N
}

/**
 * 根据用户信息生成头像数据
 * @param {number|string} userId - 用户 ID
 * @param {string} nickname - 用户昵称
 * @returns {{ color: string, letter: string }}
 */
function generateAvatar(userId, nickname) {
  const idStr = String(userId || '0')
  const colorIndex = hashIndex(idStr, COLORS.length)
  const color = COLORS[colorIndex]

  // 取昵称首字符（中文直接取，英文取大写首字母）
  const name = (nickname || '?').trim()
  let letter = '?'
  if (name.length > 0) {
    letter = name.charAt(0).toUpperCase()
  }

  return { color, letter }
}

module.exports = { generateAvatar, COLORS }
