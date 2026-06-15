const { list: fetchProductList } = require('../../services/product.js');
const userService = require('../../services/user.js');
const { getUserInfo } = require('../../utils/storage.js');

const PAGE_TITLES = {
  my_published: '我的发布',
  my_favorites: '我的收藏',
  default: '全部商品',
};

Page({
  data: {
    products: [],
    page: 1,
    size: 20,
    total: 0,
    loading: false,
    hasMore: true,

    listType: '',        // '' | 'my_published' | 'my_favorites'
    pageTitle: '全部商品',

    keyword: '',
    categoryId: null,
    sort: 'createdAt_desc',
    priceMin: null,
    priceMax: null,

    showFilter: false,
    showSortPanel: false,
    hasFilters: false,
    hasSortSelection: false,
    currentSortLabel: '排序',
    customPriceMin: '',
    customPriceMax: '',
    activeTags: [],

    categories: [
      { id: null, name: '全部' },
      { id: 1, name: '书籍' },
      { id: 2, name: '数码' },
      { id: 3, name: '生活' },
      { id: 4, name: '服饰' },
      { id: 5, name: '其他' }
    ],

    priceRanges: [
      { label: '全部', min: null, max: null },
      { label: '0-10元', min: 0, max: 10 },
      { label: '10-30元', min: 10, max: 30 },
      { label: '30-50元', min: 30, max: 50 },
      { label: '50-100元', min: 50, max: 100 },
      { label: '100元+', min: 100, max: null }
    ],

    sortOptions: [
      { value: 'createdAt_desc', label: '默认排序' },
      { value: 'price_desc', label: '价格从高到低' },
      { value: 'price_asc', label: '价格从低到高' },
      { value: 'hot', label: '热门推荐' }
    ],
    selectedPriceIndex: 0,
  },

  onLoad(options) {
    const listType = options.type || '';

    // 根据入口设置页面标题
    const pageTitle = PAGE_TITLES[listType] || PAGE_TITLES.default;
    wx.setNavigationBarTitle({ title: pageTitle });

    this.setData({ listType, pageTitle });

    // 分类页入口
    if (options.keyword) {
      this.setData({ keyword: options.keyword });
    }
    if (options.categoryId) {
      this.setData({ categoryId: parseInt(options.categoryId) });
    }

    this.loadData();
  },

  // ---- 筛选状态管理 ----

  computeActiveTags() {
    const { keyword, categoryId, categories, priceMin, priceMax } = this.data;
    const tags = [];
    if (keyword) {
      tags.push({ key: 'keyword', label: keyword, prefix: '搜索' });
    }
    if (categoryId !== null) {
      const cat = categories.find(c => c.id === categoryId);
      if (cat) tags.push({ key: 'category', label: cat.name, prefix: '分类' });
    }
    if (priceMin !== null || priceMax !== null) {
      const low = priceMin !== null ? priceMin : '0';
      const high = priceMax !== null ? priceMax : '∞';
      tags.push({ key: 'price', label: '¥' + low + ' - ¥' + high, prefix: '价格' });
    }
    this.setData({
      activeTags: tags,
      hasFilters: tags.length > 0
    });
  },

  hasActiveFilters() {
    const { keyword, categoryId, priceMin, priceMax } = this.data;
    return !!(keyword || categoryId !== null || priceMin !== null || priceMax !== null);
  },

  buildParams() {
    const { page, size, keyword, categoryId, sort, priceMin, priceMax } = this.data;
    const params = { page, size, sort };
    if (keyword) params.keyword = keyword;
    if (categoryId !== null) params.categoryId = categoryId;
    if (priceMin !== null) params.priceMin = priceMin;
    if (priceMax !== null) params.priceMax = priceMax;
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '') delete params[key];
    });
    return params;
  },

  // ---- 数据加载 ----

  async loadData() {
    const { loading, listType } = this.data;
    if (loading) return;

    const MIN_LOADING_TIME = 600;
    const startTime = Date.now();

    this.setData({ loading: true });
    try {
      let data;

      if (listType === 'my_favorites') {
        data = await userService.getFavorites(this.data.page, this.data.size, this.buildParams());
      } else {
        const params = this.buildParams();
        if (listType === 'my_published') {
          const user = getUserInfo();
          if (user && user.id) params.ownerId = user.id;
        }
        data = await fetchProductList(params);
      }

      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_LOADING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_LOADING_TIME - elapsed));
      }

      this.setData({
        products: data.list || [],
        total: data.page?.total || 0,
        page: 2,
        hasMore: (data.list || []).length >= this.data.size,
        loading: false
      });
    } catch (err) {
      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_LOADING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_LOADING_TIME - elapsed));
      }
      this.setData({ loading: false });
    }
  },

  reload() {
    this.setData({ page: 1, products: [], hasMore: true });
    this.computeActiveTags();
    this.loadData();
  },

  onPullDownRefresh() {
    this.reload();
    wx.stopPullDownRefresh();
  },

  onReachBottom() {
    const { loading, hasMore, page, size, listType } = this.data;
    if (loading || !hasMore) return;

    this.setData({ loading: true });

    const doLoad = listType === 'my_favorites'
      ? userService.getFavorites(page, size, this.buildParams())
      : (() => {
          const params = this.buildParams();
          params.page = page;
          if (listType === 'my_published') {
            const user = getUserInfo();
            if (user && user.id) params.ownerId = user.id;
          }
          return fetchProductList(params);
        })();

    doLoad.then(data => {
      const list = data.list || [];
      this.setData({
        products: this.data.products.concat(list),
        page: page + 1,
        hasMore: list.length >= size,
        loading: false
      });
    }).catch(() => {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败，请重试', icon: 'none' });
    });
  },

  // ---- 搜索 ----

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearchConfirm(e) {
    const kw = e.detail.value || '';
    this.setData({ keyword: kw });
    this.reload();
  },

  // ---- 分类 ----

  onCategoryChange(e) {
    const { id } = e.currentTarget.dataset;
    this.setData({ categoryId: id });
    this.reload();
  },

  // ---- 排序 ----

  onSortTap(e) {
    const { sort, label } = e.currentTarget.dataset;
    this.setData({
      sort,
      currentSortLabel: label || '默认排序',
      hasSortSelection: true,
      showSortPanel: false
    });
    this.reload();
  },

  // ---- 价格筛选 ----

  onPriceRangeChange(e) {
    const { min, max, index } = e.currentTarget.dataset;
    this.setData({
      priceMin: min !== undefined ? min : null,
      priceMax: max !== undefined ? max : null,
      selectedPriceIndex: index,
      customPriceMin: '',
      customPriceMax: '',
      showFilter: false,
      showSortPanel: false
    });
    this.reload();
  },

  onCustomPriceMinInput(e) {
    this.setData({ customPriceMin: e.detail.value });
  },

  onCustomPriceMaxInput(e) {
    this.setData({ customPriceMax: e.detail.value });
  },

  onCustomPriceConfirm() {
    const { customPriceMin, customPriceMax } = this.data;
    const min = customPriceMin !== '' ? Number(customPriceMin) : null;
    const max = customPriceMax !== '' ? Number(customPriceMax) : null;
    this.setData({
      priceMin: min,
      priceMax: max,
      selectedPriceIndex: -1,
      showFilter: false,
      showSortPanel: false
    });
    this.reload();
  },

  // ---- 悬浮面板 ----

  onSortToggle() {
    this.setData({
      showSortPanel: !this.data.showSortPanel,
      showFilter: false
    });
  },

  onFilterToggle() {
    this.setData({
      showFilter: !this.data.showFilter,
      showSortPanel: false
    });
  },

  onCloseFloatingPanels() {
    this.setData({
      showSortPanel: false,
      showFilter: false
    });
  },

  noop() {},

  // ---- 已选标签操作 ----

  onRemoveTag(e) {
    const { key } = e.currentTarget.dataset;
    if (key === 'keyword') {
      this.setData({ keyword: '' });
    } else if (key === 'category') {
      this.setData({ categoryId: null });
    } else if (key === 'price') {
      this.setData({
        priceMin: null,
        priceMax: null,
        selectedPriceIndex: 0,
        customPriceMin: '',
        customPriceMax: ''
      });
    }
    this.reload();
  },

  onClearAllFilters() {
    this.setData({
      keyword: '',
      categoryId: null,
      priceMin: null,
      priceMax: null,
      selectedPriceIndex: 0,
      customPriceMin: '',
      customPriceMax: '',
      showFilter: false,
      showSortPanel: false
    });
    this.reload();
  },

  // ---- 商品卡片 ----

  onCardTap(e) {
    const productId = e.detail?.productId || e.currentTarget.dataset?.productId;
    if (productId) {
      wx.navigateTo({ url: `/pages/detail/index?id=${productId}` });
    }
  }
});
