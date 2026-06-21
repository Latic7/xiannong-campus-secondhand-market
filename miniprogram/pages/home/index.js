const { list: fetchProductList } = require('../../services/product.js');
const categoryService = require('../../services/category.js');

// 分类前端展示图标（不存数据库，按分类 ID 映射）
const CATEGORY_ICONS = {
  1: { iconPath: '/assets/icons/book-white.svg', bgColor: '#0B6B43' },
  2: { iconPath: '/assets/icons/phone-white.svg', bgColor: '#C8A24A' },
  3: { iconPath: '/assets/icons/lamp-white.svg', bgColor: '#34A853' },
  4: { iconPath: '/assets/icons/shirt-white.svg', bgColor: '#FF2D55' },
  5: { iconPath: '/assets/icons/phone-white.svg', bgColor: '#5856D6' },
  6: { iconPath: '/assets/icons/lamp-white.svg', bgColor: '#FF6482' },
  7: { iconPath: '/assets/icons/book-white.svg', bgColor: '#FF9500' },
  8: { iconPath: '/assets/icons/dots-white.svg', bgColor: '#8E8E93' },
}

Page({
  data: {
    statusBarHeight: 44,
    categories: [],
    recommends: [],
    latestProducts: [],
    loading: true,
    errorMsg: ''
  },
  onLoad() {
    const systemInfo = wx.getSystemInfoSync();
    this.setData({ statusBarHeight: systemInfo.statusBarHeight });

    // 从后端动态加载分类（异步，不阻塞页面渲染）
    this.loadCategories();

    this.loadData();
  },

  loadCategories() {
    categoryService.getCategories().then(raw => {
      const categories = raw.map(c => ({
        id: c.id,
        name: c.name,
        ...(CATEGORY_ICONS[c.id] || { iconPath: '/assets/icons/dots-white.svg', bgColor: '#8E8E93' }),
      }))
      this.setData({ categories })
    }).catch(() => {
      // 静默失败，分类为空不影响首页加载
    })
  },

  onShow() {
    // 同步底部导航栏选中状态（避免 getCurrentPages 时序问题）
    const tabBar = this.getTabBar();
    if (tabBar) {
      tabBar.setData({ selected: 0 });
    }
    // 每次回到首页自动刷新商品列表，按时间倒序
    this.loadData();
  },
  async loadData() {
    const MIN_LOADING_TIME = 800; // 骨架屏最小可见时长（ms）
    const startTime = Date.now();
    try {
      this.setData({ loading: true, errorMsg: '' });
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

      this.setData({ recommends, latestProducts, loading: false, errorMsg: '' });
    } catch (err) {
      // 兜底：即使出错也保证骨架屏可见
      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_LOADING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_LOADING_TIME - elapsed));
      }
      this.setData({ loading: false, errorMsg: err.message || '首页加载失败，请重试' });
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
  },
  onRetry() {
    this.loadData()
  }
});
