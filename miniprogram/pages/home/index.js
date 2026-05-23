const { fetchProductList } = require('../../services/product.js');

Page({
  data: {
    statusBarHeight: 44,
    categories: [
      { id: 1, name: '书籍', icon: '📚', bgColor: '#EEF2FF' },
      { id: 2, name: '数码', icon: '📱', bgColor: '#FEF3C7' },
      { id: 3, name: '生活', icon: '🛋️', bgColor: '#D1FAE5' },
      { id: 4, name: '服饰', icon: '👕', bgColor: '#FCE7F3' },
      { id: 5, name: '其他', icon: '📦', bgColor: '#E5E7EB' }
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

  onShow() {
    // 同步底部导航栏选中状态（避免 getCurrentPages 时序问题）
    const tabBar = this.getTabBar();
    if (tabBar) {
      tabBar.setData({ selected: 0 });
    }
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
    // 兼容 item-card 组件的 detail 和推荐卡片的 dataset
    const productId = e.detail?.productId || e.currentTarget?.dataset?.productId;
    if (productId) {
      wx.navigateTo({ url: `/pages/detail/index?id=${productId}` });
    }
  }
});