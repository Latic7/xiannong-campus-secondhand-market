Component({
  properties: {
    message: {
      type: String,
      value: '加载失败，请重试'
    },
    buttonText: {
      type: String,
      value: '重新加载'
    }
  },
  methods: {
    onRetry() {
      this.triggerEvent('retry')
    }
  }
})
