export function setItem(key, value) {
  try { wx.setStorageSync(key, value); } catch (e) {}
}
export function getItem(key) {
  try { return wx.getStorageSync(key); } catch (e) { return null; }
}
