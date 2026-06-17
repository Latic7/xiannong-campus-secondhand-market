// ──────────────────────────────────────────────
//  分类服务
//  从后端获取分类列表，避免前端硬编码
// ──────────────────────────────────────────────
const api = require('../utils/api')

let cachedCategories = null

module.exports = {

  /** 获取分类列表（带缓存） */
  async getCategories() {
    if (cachedCategories) return cachedCategories
    const data = await api.get('/api/categories')
    cachedCategories = data || []
    return cachedCategories
  },

  /** 获取分类名称映射 { id: name } */
  async getCategoryMap() {
    const list = await this.getCategories()
    const map = {}
    list.forEach(c => { map[c.id] = c.name })
    return map
  },

  /** 清空缓存（页面间切换时） */
  clearCache() {
    cachedCategories = null
  },
}
