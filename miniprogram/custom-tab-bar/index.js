Component({
  data: {
    selected: 0,
    list: [
      {
        "pagePath": "/pages/home/index",
        "iconPath": "/assets/icons/home-gray.svg",
        "iconPathActive": "/assets/icons/home-active.svg",
        "text": "首页"
      },
      {
        "pagePath": "/pages/post/index",
        "iconPath": "",
        "iconPathActive": "",
        "text": "发布"
      },
      {
        "pagePath": "/pages/user/index",
        "iconPath": "/assets/icons/user-gray.svg",
        "iconPathActive": "/assets/icons/user-active.svg",
        "text": "我的"
      }
    ]
  },
  attached() {
    // 首次加载兜底；后续选中状态由各页面 onShow 主动调用 getTabBar().setData() 同步
    this.updateSelectedIndex();
  },
  methods: {
    switchTab(e) {
      const index = e.currentTarget.dataset.index;
      const url = this.data.list[index].pagePath;
      // 先更新状态，切换页面后show会再次更新
      this.setData({ selected: index });
      wx.switchTab({ url });
    },
    updateSelectedIndex() {
      try {
        const pages = getCurrentPages();
        if (!pages || pages.length === 0) return;
        const currentPage = pages[pages.length - 1];
        if (!currentPage || !currentPage.route) return;
        const route = '/' + currentPage.route;
        const index = this.data.list.findIndex(item => item.pagePath === route);
        if (index > -1 && this.data.selected !== index) {
          this.setData({ selected: index });
        }
      } catch (err) {
        console.log('tabBar updateSelectedIndex error:', err);
      }
    }
  }
})
