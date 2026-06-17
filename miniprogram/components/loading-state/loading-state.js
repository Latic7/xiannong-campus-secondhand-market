Component({
  properties: {
    count: {
      type: Number,
      value: 3
    },
    message: {
      type: String,
      value: ''
    }
  },
  data: {
    skeletons: []
  },
  lifetimes: {
    attached() {
      const skeletons = Array.from({ length: this.data.count }, (_, i) => i);
      this.setData({ skeletons });
    }
  }
})
