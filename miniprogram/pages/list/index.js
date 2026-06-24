const { list: fetchProductList } = require('../../services/product.js');
const userService = require('../../services/user.js');
const categoryService = require('../../services/category.js');
const orderService = require('../../services/order.js');
const { getUserInfo } = require('../../utils/storage.js');

const PAGE_TITLES = {
  my_published: '我的发布',
  my_favorites: '我的收藏',
  my_sold: '我的售出',
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
    errorMsg: '',

    listType: '',        // '' | 'my_published' | 'my_favorites'
    pageTitle: '全部商品',

    keyword: '',
    categoryId: null,        // 单分类（首页分类入口传入，兼容用）
    selectedCategoryIds: [], // 多分类选中
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
    selectedCategorySet: {},

    categories: [],

    sortOptions: [
      { value: 'createdAt_desc', label: '默认排序' },
      { value: 'price_desc', label: '价格从高到低' },
      { value: 'price_asc', label: '价格从低到高' },
      { value: 'hot', label: '热门推荐' }
    ],
    statusFilter: [],          // 商品状态筛选，如 ['PUBLISHED', 'SOLD']
    statusActiveSet: {},
    statusOptions: [
      { value: 'PUBLISHED', label: '在售' },
      { value: 'SOLD', label: '已售出' },
      { value: 'REMOVED', label: '已下架' },
    ],
  },

  onLoad(options) {
    const listType = options.type || '';

    // 根据入口设置页面标题
    const pageTitle = PAGE_TITLES[listType] || PAGE_TITLES.default;
    wx.setNavigationBarTitle({ title: pageTitle });

    this.setData({ listType, pageTitle });

    // 从后端动态加载分类（异步，不阻塞页面渲染）
    this.loadCategories();

    // 分类页入口
    if (options.keyword) {
      this.setData({ keyword: options.keyword });
    }
    if (options.categoryId) {
      const catId = parseInt(options.categoryId);
      this.setData({
        categoryId: catId,
        selectedCategoryIds: [catId],
        selectedCategorySet: this.computeCategoryActiveSet([catId])
      });
    }

    this.loadData();
  },

  // ── 异步加载分类（从后端）───────────────
  loadCategories() {
    categoryService.getCategories().then(raw => {
      const categories = [{ id: null, name: '全部' }, ...raw.map(c => ({ id: c.id, name: c.name }))];
      this.setData({ categories });
    }).catch(() => {
      // 静默失败
    });
  },

  // ---- 筛选状态管理 ----

  // 根据 selectedCategoryIds 生成选中集合，供 WXML 高效判断
  computeCategoryActiveSet(selectedCategoryIds) {
    const set = {};
    selectedCategoryIds.forEach(id => { set[id] = true; });
    return set;
  },

  // 根据 statusFilter 生成选中集合，供 WXML 高效判断
  computeStatusActiveSet(statusFilter) {
    const set = {};
    statusFilter.forEach(s => { set[s] = true; });
    return set;
  },

  computeActiveTags() {
    const { keyword, selectedCategoryIds, categories, priceMin, priceMax, statusFilter, statusOptions } = this.data;
    const tags = [];
    if (keyword) {
      tags.push({ key: 'keyword', label: keyword, prefix: '搜索' });
    }
    if (selectedCategoryIds.length > 0) {
      selectedCategoryIds.forEach(catId => {
        const cat = categories.find(c => c.id === catId);
        if (cat) {
          tags.push({ key: 'category-' + catId, categoryId: catId, label: cat.name, prefix: '分类' });
        }
      });
    }
    if (priceMin !== null || priceMax !== null) {
      const low = priceMin !== null ? priceMin : '0';
      const high = priceMax !== null ? priceMax : '∞';
      tags.push({ key: 'price', label: '¥' + low + ' - ¥' + high, prefix: '价格' });
    }
    if (statusFilter.length > 0) {
      statusFilter.forEach(st => {
        const opt = statusOptions.find(o => o.value === st);
        if (opt) {
          tags.push({ key: 'status-' + st, statusValue: st, label: opt.label, prefix: '状态' });
        }
      });
    }
    this.setData({
      activeTags: tags,
      hasFilters: tags.length > 0,
      selectedCategorySet: this.computeCategoryActiveSet(selectedCategoryIds),
      statusActiveSet: this.computeStatusActiveSet(statusFilter)
    });
  },

  hasActiveFilters() {
    const { keyword, selectedCategoryIds, priceMin, priceMax, statusFilter } = this.data;
    return !!(keyword || selectedCategoryIds.length > 0 || priceMin !== null || priceMax !== null || statusFilter.length > 0);
  },

  buildParams() {
    const { page, size, keyword, selectedCategoryIds, sort, priceMin, priceMax, statusFilter } = this.data;
    const params = { page, size, sort };
    if (keyword) params.keyword = keyword;
    if (selectedCategoryIds.length > 0) {
      params.categoryIds = selectedCategoryIds.join(',');
    }
    if (priceMin !== null) params.priceMin = priceMin;
    if (priceMax !== null) params.priceMax = priceMax;
    if (statusFilter.length > 0) {
      params.status = statusFilter.join(',');
    }
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

    this.setData({ loading: true, errorMsg: '' });
    try {
      let data;

      if (listType === 'my_favorites') {
        data = await userService.getFavorites(this.data.page, this.data.size, this.buildParams());
      } else if (listType === 'my_sold') {
        data = await orderService.list({ role: 'seller', status: 'COMPLETED', page: this.data.page, size: this.data.size });
        // 将订单数据映射为商品卡片可用的格式
        if (data.list) {
          data.list = data.list.map(order => ({
            id: order.productId,
            orderId: order.id,
            title: order.product?.title || '商品信息不可用',
            price: order.product?.price || 0,
            images: order.product?.image ? [order.product.image] : [],
            status: order.product?.status || 'SOLD',
            description: '',
          }))
        }
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
        loading: false,
        errorMsg: ''
      });
    } catch (err) {
      const elapsed = Date.now() - startTime;
      if (elapsed < MIN_LOADING_TIME) {
        await new Promise(resolve => setTimeout(resolve, MIN_LOADING_TIME - elapsed));
      }
      this.setData({ loading: false, errorMsg: err.message || '列表加载失败，请重试' });
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
      : listType === 'my_sold'
        ? orderService.list({ role: 'seller', status: 'COMPLETED', page, size }).then(data => {
            if (data.list) {
              data.list = data.list.map(order => ({
                id: order.productId,
                orderId: order.id,
                title: order.product?.title || '商品信息不可用',
                price: order.product?.price || 0,
                images: order.product?.image ? [order.product.image] : [],
                status: order.product?.status || 'SOLD',
                description: '',
              }))
            }
            return data
          })
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

  // ---- 分类（多选）----

  onCategoryChange(e) {
    const { id } = e.currentTarget.dataset;
    let { selectedCategoryIds } = this.data;
    if (id === null || id === undefined) {
      // 点击"全部"时清除所有分类
      selectedCategoryIds = [];
    } else {
      const idx = selectedCategoryIds.indexOf(id);
      if (idx !== -1) {
        // 已选中则取消
        selectedCategoryIds = selectedCategoryIds.filter(cid => cid !== id);
      } else {
        // 未选中则添加
        selectedCategoryIds = [...selectedCategoryIds, id];
      }
    }
    this.setData({
      selectedCategoryIds,
      selectedCategorySet: this.computeCategoryActiveSet(selectedCategoryIds)
    });
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

  // ---- 商品状态筛选（多选）----

  onStatusToggle(e) {
    const { value } = e.currentTarget.dataset;
    let { statusFilter } = this.data;
    const idx = statusFilter.indexOf(value);
    if (idx !== -1) {
      statusFilter = statusFilter.filter(s => s !== value);
    } else {
      statusFilter = [...statusFilter, value];
    }
    // 不关闭面板，让用户能看见选中/取消的高亮反馈
    this.setData({ statusFilter, statusActiveSet: this.computeStatusActiveSet(statusFilter) });
  },

  // ---- 价格筛选 ----

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
    const wasOpen = this.data.showFilter;
    this.setData({
      showFilter: !wasOpen,
      showSortPanel: false
    });
    // 关闭筛选面板时触发刷新
    if (wasOpen) this.reload();
  },

  onCloseFloatingPanels() {
    const hadFilter = this.data.showFilter;
    this.setData({
      showSortPanel: false,
      showFilter: false
    });
    // 关闭筛选面板时触发刷新
    if (hadFilter) this.reload();
  },

  noop() {},

  // ---- 已选标签操作 ----

  onRemoveTag(e) {
    const { key, categoryid, statusvalue } = e.currentTarget.dataset;
    if (key === 'keyword') {
      this.setData({ keyword: '' });
    } else if (key && key.startsWith('category-')) {
      const { selectedCategoryIds } = this.data;
      const newIds = selectedCategoryIds.filter(cid => cid !== categoryid);
      this.setData({
        selectedCategoryIds: newIds,
        selectedCategorySet: this.computeCategoryActiveSet(newIds)
      });
    } else if (key === 'price') {
      this.setData({
        priceMin: null,
        priceMax: null,
        customPriceMin: '',
        customPriceMax: ''
      });
    } else if (key && key.startsWith('status-')) {
      const { statusFilter } = this.data;
      const newFilter = statusFilter.filter(s => s !== statusvalue);
      this.setData({
        statusFilter: newFilter,
        statusActiveSet: this.computeStatusActiveSet(newFilter)
      });
    }
    this.reload();
  },

  onClearAllFilters() {
    this.setData({
      keyword: '',
      categoryId: null,
      selectedCategoryIds: [],
      selectedCategorySet: {},
      priceMin: null,
      priceMax: null,
      customPriceMin: '',
      customPriceMax: '',
      statusFilter: [],
      statusActiveSet: {},
      showFilter: false,
      showSortPanel: false
    });
    this.reload();
  },

  // ---- 商品卡片 ----

  onCardTap(e) {
    const productId = e.detail?.productId || e.currentTarget.dataset?.productId;
    if (!productId) return
    // 我的售出：跳转到订单详情
    if (this.data.listType === 'my_sold') {
      // 从 products 中查找对应的 orderId
      const item = this.data.products.find(p => p.id === productId)
      if (item && item.orderId) {
        wx.navigateTo({ url: `/pages/orders/detail?orderId=${item.orderId}` })
        return
      }
    }
    wx.navigateTo({ url: `/pages/detail/index?id=${productId}` });
  },

  onRetry() {
    this.reload()
  }
});
