Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },
  data: {
    computedImage: '',
    computedStatusClass: '',
    displayStatus: '',
    displayPrice: '',
    imgFilterClass: '',
  },
  observers: {
    'item': function(item) {
      if (!item) return;
      const images = item.images;
      const firstImage = images && images.length > 0 ? images[0] : '';
      const image = typeof firstImage === 'string' ? firstImage : (firstImage.url || '');
      const status = String(item.status || '').toUpperCase();

      let statusClass = 'status-default';
      let displayStatus = status;
      if (status === 'PUBLISHED') {
        statusClass = 'status-available';
        displayStatus = '在售';
      } else if (status === 'PENDING') {
        statusClass = 'status-pending';
        displayStatus = '待审核';
      } else if (status === 'REMOVED') {
        statusClass = 'status-removed';
        displayStatus = '已下架';
      } else if (status === 'REJECTED') {
        statusClass = 'status-removed';
        displayStatus = '审核未通过';
      } else if (status === 'SOLD') {
        statusClass = 'status-sold';
        displayStatus = '已售出';
      } else if (!status) {
        displayStatus = '';
      }

      const imgFilterClass = (status === 'REMOVED' || status === 'SOLD') ? 'img-grayscale' : '';

      this.setData({
        computedImage: image,
        computedStatusClass: statusClass,
        displayStatus: displayStatus,
        displayPrice: this.formatPrice(item.price),
        imgFilterClass,
      });
    }
  },
  methods: {
    formatPrice(price) {
      if (price === null || price === undefined || price === '') return '面议';
      const n = Number(price);
      if (Number.isNaN(n)) return String(price);
      return '¥' + n.toFixed(2).replace(/\.00$/, '');
    },
    onTap() {
      this.triggerEvent('tap', { productId: this.properties.item.id });
    }
  }
});
