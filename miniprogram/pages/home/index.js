const { fetchProductList } = require('../../services/product.js');

Page({
  data: {
    statusBarHeight: 44,
    categories: [
      { id: 1, name: '书籍', icon: '📚' },
      { id: 2, name: '数码', icon: '📱' },
      { id: 3, name: '生活', icon: '🛋️' },
      { id: 4, name: '服饰', icon: '👕' },
      { id: 5, name: '其他', icon: '📦' }
    ],
    recommends: [],
    latestProducts: [],
    loading: true
  },
  onLoad() {
    const systemInfo = wx.getSystemInfoSync();
    this.setData({ statusBarHeight: systemInfo.statusBarHeight });
    this.loadData();
  },
  async loadData() {
    try {
      this.setData({ loading: true });
      const [recommendData, latestData] = await Promise.all([
        fetchProductList({ page: 1, size: 6, sort: 'createdAt_desc' }),
        fetchProductList({ page: 1, size: 10, sort: 'createdAt_desc' })
      ]);
      this.setData({
        recommends: recommendData.list || [],
        latestProducts: latestData.list || [],
        loading: false
      });
    } catch (err) {
      this.setData({ loading: false });
    }
  },
  onPullDownRefresh() {
    this.loadData().then(() => wx.stopPullDownRefresh());
  },
  onSearchTap() {
    wx.navigateTo({ url: '/pages/list/index' });
  },
  onCategoryTap(e) {
    const { id, name } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/list/index?categoryId=${id}&categoryName=${name}` });
  },
  onProductTap(e) {
    const { productId } = e.detail;
    wx.navigateTo({ url: `/pages/detail/index?id=${productId}` });
  }
});