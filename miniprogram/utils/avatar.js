// ──────────────────────────────────────────────
//  头像生成工具 — GitHub 风格几何色块 Identicon
//  根据用户 ID 生成确定性的 5×5 镜像几何头像
//  纯前端实现，不依赖后端
// ──────────────────────────────────────────────

// 背景色（用作底色）
const BG_COLORS = [
  '#1abc9c', '#2ecc71', '#3498db', '#9b59b6',
  '#e67e22', '#e74c3c', '#1a8a6a', '#2980b9',
  '#8e44ad', '#d35400', '#c0392b', '#16a085',
  '#27ae60', '#2c3e50', '#f39c12', '#7f8c8d',
]

// 色块颜色（比背景稍亮/暗，形成对比）
const CELL_COLORS = [
  '#1ce0b5', '#3dfc8e', '#5dade2', '#bb8fce',
  '#f0b27a', '#f1948a', '#1dd1a1', '#85c1e9',
  '#af7ac5', '#e59866', '#e6b0aa', '#48c9b0',
  '#58d68d', '#34495e', '#f7dc6f', '#bdc3c7',
]

const GRID_SIZE = 5
const HALF = 3 // 左半部分列数（5→0,1,2 | 3,4镜像）

/**
 * FNV-1a 哈希，32位，比特分布均匀
 */
function hash32(str) {
  let h = 2166136261
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}

/**
 * 根据用户 ID 生成 GitHub 风格的 5×5 镜像几何头像
 * @param {number|string} userId
 * @returns {{ bgColor: string, cellColor: string, cells: boolean[][] }}
 */
function generateAvatar(userId) {
  const idStr = String(userId || '0')

  // 不同种子产生颜色和网格，确保分布均匀
  const hColor = hash32('c' + idStr)
  const hGrid = hash32('g' + idStr)

  const colorN = BG_COLORS.length
  const bgIndex = (hColor >>> 0) % colorN
  const cellIndex = ((hColor >>> 16) + bgIndex + 1) % colorN

  const bgColor = BG_COLORS[bgIndex]
  const cellColor = CELL_COLORS[cellIndex]

  // 生成 3×5 左半网格（15 bits，从 hGrid 逐位取）
  let bits = hGrid
  const leftHalf = []
  for (let row = 0; row < GRID_SIZE; row++) {
    const rowCells = []
    for (let col = 0; col < HALF; col++) {
      const bit = bits & 1
      rowCells.push(bit === 1)
      bits >>>= 1
    }
    leftHalf.push(rowCells)
  }

  // 镜像生成完整 5×5
  const cells = []
  for (let row = 0; row < GRID_SIZE; row++) {
    const fullRow = []
    for (let col = 0; col < GRID_SIZE; col++) {
      const srcCol = col < HALF ? col : (GRID_SIZE - 1 - col)
      fullRow.push(leftHalf[row][srcCol])
    }
    cells.push(fullRow)
  }

  return { bgColor, cellColor, cells }
}

module.exports = { generateAvatar }
