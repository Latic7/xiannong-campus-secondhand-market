Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },
  data: {
    defaultImage: '/assets/images/placeholder.png',
    computedImage: '',
    computedStatusClass: '',
    displayStatus: ''
  },
  observers: {
    'item': function(item) {
      if (!item) return;
      const images = item.images;
      const image = (images && images.length > 0) ? images[0] : this.data.defaultImage;
      const status = item.status;

      let statusClass = 'status-default';
      let displayStatus = status;
      if (status === 'available') {
        statusClass = 'status-published';
        displayStatus = '在售';
      } else if (status === 'reserved') {
        statusClass = 'status-reserved';
        displayStatus = '已预订';
      } else if (status === 'sold') {
        statusClass = 'status-sold';
        displayStatus = '已售出';
      }

      this.setData({
        computedImage: image,
        computedStatusClass: statusClass,
        displayStatus: displayStatus
      });
    }
  },
  methods: {
    onTap() {
      this.triggerEvent('tap', { productId: this.properties.item.id });
    }
  }
});