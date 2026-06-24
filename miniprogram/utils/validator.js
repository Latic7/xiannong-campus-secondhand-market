// ──────────────────────────────────────────────
//  表单校验工具集
//  提供通用校验函数，供 post 页及其他表单复用
// ──────────────────────────────────────────────

function validateTitle(value) {
  if (!value || !value.trim()) return { valid: false, message: '请输入商品标题' }
  if (value.trim().length < 2) return { valid: false, message: '标题至少2个字' }
  if (value.length > 50) return { valid: false, message: '标题最多50个字' }
  return { valid: true }
}

function validatePrice(value) {
  if (value == null || String(value).trim() === '') return { valid: false, message: '请输入价格' }
  const num = parseFloat(value)
  if (isNaN(num) || num < 0) return { valid: false, message: '请输入有效的价格' }
  if (num > 9999999) return { valid: false, message: '价格超出上限' }
  if (!/^\d+(\.\d{1,2})?$/.test(String(value).trim())) return { valid: false, message: '价格最多两位小数' }
  return { valid: true }
}

function validateDescription(value) {
  if (!value || !value.trim()) return { valid: false, message: '请输入商品描述' }
  if (value.trim().length < 10) return { valid: false, message: '描述至少10个字' }
  if (value.length > 500) return { valid: false, message: '描述最多500字' }
  return { valid: true }
}

function validateImages(images) {
  if (!images || images.length === 0) return { valid: false, message: '请至少上传一张图片' }
  if (images.length > 9) return { valid: false, message: '最多上传9张图片' }
  return { valid: true }
}

function validatePhone(value) {
  if (!value) return { valid: true } // 允许为空
  if (!/^1[3-9]\d{9}$/.test(value)) return { valid: false, message: '请输入正确的手机号' }
  return { valid: true }
}

module.exports = {
  validateTitle,
  validatePrice,
  validateDescription,
  validateImages,
  validatePhone,
}

