const { list: fetchProductList } = require('../../services/product.js');

Page({
  data: {
    statusBarHeight: 44,
    categories: [
      { id: 1, name: '书籍', iconPath: '/assets/icons/book-white.svg', bgColor: '#0B6B43' },
      { id: 2, name: '数码', iconPath: '/assets/icons/phone-white.svg', bgColor: '#C8A24A' },
      { id: 3, name: '生活', iconPath: '/assets/icons/lamp-white.svg', bgColor: '#34A853' },
      { id: 4, name: '服饰', iconPath: '/assets/icons/shirt-white.svg', bgColor: '#FF2D55' },
      { id: 5, name: '其他', iconPath: '/assets/icons/dots-white.svg', bgColor: '#8E8E93' }
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
    const MIN_LOADING_TIME = 800; // 骨架屏最小可见时长（ms）
    const startTime = Date.now();
    try {
      this.setData({ loading: true });
      const [recommendData, latestData] = await Promise.allSettled([
        fetchProductList({ page: 1, size: 6, sort: 'createdAt_desc' }),
        fetchProductList({ page: 1, size: 10, sort: 'createdAt_desc' })
      ]);

      const recommends = recommendData.status === 'fulfilled' ? (recommendData.value.list || []) : [];
      const latestProducts = latestData.status === 'fulfilled' ? (latestData.value.list || []) : [];

      // 保证骨架屏至少可见 MIN_LOADING_TIME，避免请求太快导致一闪而过
      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_LOADING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_LOADING_TIME - elapsed));
      }

      this.setData({ recommends, latestProducts, loading: false });
    } catch (err) {
      // 兜底：即使出错也保证骨架屏可见
      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_LOADING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_LOADING_TIME - elapsed));
      }
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
