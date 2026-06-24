const { getUserInfo } = require('../utils/storage')
const orderService = require('../services/order')
const orderUnread = require('../utils/orderUnread')
const adminService = require('../services/admin')
const reportService = require('../services/report')

Component({
  data: {
    selected: 0,
    badgeCount: 0,
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
    this.refreshBadge();
  },
  methods: {
    switchTab(e) {
      const index = e.currentTarget.dataset.index;
      const url = this.data.list[index].pagePath;
      // 发布页需要登录才能进入
      if (index === 1) {
        const user = getUserInfo()
        if (!user || !user.id) {
          wx.showToast({ title: '请先登录后再发布', icon: 'none' })
          return
        }
      }
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
    },

    // ── 刷新底部 TabBar 角标 ─────────────────
    async refreshBadge() {
      const user = getUserInfo()
      if (!user || !user.id) {
        this.setData({ badgeCount: 0 })
        return
      }

      try {
        // 并行拉取三类计数
        const [orderData, reportData, adminData] = await Promise.allSettled([
          orderService.list({ page: 1, size: 100 }),
          reportService.listAgainstMe({ size: 1, seenByTarget: 'NOT_SEEN' }),
          (user.isAdmin || user.is_admin)
            ? Promise.all([
                adminService.listReports({ status: 'OPEN', size: 1 }),
                adminService.listPendingProducts({ size: 1 }),
              ])
            : Promise.resolve([null, null]),
        ])

        let unreadOrders = 0
        if (orderData.status === 'fulfilled') {
          const orders = orderData.value.list || []
          unreadOrders = orderUnread.totalUnread(orders, user.id)
        }

        let reportsAgainstMe = 0
        if (reportData.status === 'fulfilled') {
          reportsAgainstMe = reportData.value?.page?.total || 0
        }

        let adminPendingTotal = 0
        if (adminData.status === 'fulfilled' && adminData.value) {
          const [reportRes, productRes] = adminData.value
          const reports = reportRes?.page?.total || 0
          const products = productRes?.page?.total || 0
          adminPendingTotal = reports + products
        }

        this.setData({ badgeCount: unreadOrders + reportsAgainstMe + adminPendingTotal })
      } catch (e) {
        // 静默失败，保持之前的值
      }
    },
  }
})
