const { fetchProductList } = require('../../services/product.js');

Page({
  data: {
    products: [],
    page: 1,
    size: 20,
    total: 0,
    loading: false,
    hasMore: true,

    keyword: '',
    categoryId: null,
    sort: 'createdAt_desc',
    priceMin: null,
    priceMax: null,

    showFilter: false,

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
    selectedPriceIndex: 0,

    sortOptions: [
      { value: 'createdAt_desc', label: '最新发布' },
      { value: 'price_asc', label: '价格从低到高' },
      { value: 'price_desc', label: '价格从高到低' },
      { value: 'hot', label: '热门' }
    ],
    selectedSort: 'createdAt_desc',

    currentSortLabel: '排序',
    hasActiveFilter: false,
    filterSummary: ''
  },
  onLoad(options) {
    if (options.keyword) {
      this.setData({ keyword: options.keyword });
    }
    if (options.categoryId) {
      this.setData({ categoryId: parseInt(options.categoryId) });
    }
    this.loadData();
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
  updateFilterState() {
    const { sortOptions, selectedSort, keyword, categoryId, priceMin, priceMax, categories } = this.data;
    const sortLabel = sortOptions.find(s => s.value === selectedSort)?.label || '排序';
    const categoryName = categories.find(c => c.id === categoryId)?.name;
    const parts = [];
    if (keyword) parts.push('关键词:' + keyword);
    if (categoryName) parts.push('分类:' + categoryName);
    if (priceMin !== null || priceMax !== null) {
      parts.push('价格:' + (priceMin || 0) + '-' + (priceMax || '∞') + '元');
    }
    this.setData({
      currentSortLabel: sortLabel,
      hasActiveFilter: parts.length > 0,
      filterSummary: parts.join(' ')
    });
  },
  async loadData() {
    const { loading } = this.data;
    if (loading) return;

    this.setData({ loading: true });
    this.updateFilterState();
    try {
      const data = await fetchProductList(this.buildParams());
      this.setData({
        products: data.list || [],
        total: data.page?.total || 0,
        page: 2,
        hasMore: (data.list || []).length >= this.data.size,
        loading: false
      });
    } catch (err) {
      this.setData({ loading: false });
    }
  },
  onPullDownRefresh() {
    this.setData({ page: 1, products: [], hasMore: true });
    this.loadData().then(() => wx.stopPullDownRefresh());
  },
  onReachBottom() {
    const { loading, hasMore, page, size } = this.data;
    if (loading || !hasMore) return;

    this.setData({ loading: true });
    const params = this.buildParams();
    params.page = page;

    fetchProductList(params).then(data => {
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
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
  },
  onSearchConfirm(e) {
    this.setData({ keyword: e.detail.value, page: 1, products: [], hasMore: true });
    this.loadData();
  },
  onCategoryChange(e) {
    const { id } = e.currentTarget.dataset;
    this.setData({ categoryId: id, page: 1, products: [], hasMore: true });
    this.loadData();
  },
  onSortChange(e) {
    const { value } = e.currentTarget.dataset;
    this.setData({ sort: value, selectedSort: value, page: 1, products: [], hasMore: true });
    this.loadData();
  },
  onPriceRangeChange(e) {
    const { min, max, index } = e.currentTarget.dataset;
    this.setData({
      priceMin: min,
      priceMax: max,
      selectedPriceIndex: index,
      page: 1,
      products: [],
      hasMore: true
    });
    this.loadData();
  },
  onFilterToggle() {
    this.setData({ showFilter: !this.data.showFilter });
  },
  onCardTap(e) {
    const productId = e.detail?.productId || e.currentTarget.dataset?.productId;
    if (productId) {
      wx.navigateTo({ url: `/pages/detail/index?id=${productId}` });
    }
  }
});