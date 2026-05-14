项目框架与任务拆分（占位，供组长分配）

- **前端页面**
  - `pages/home`：首页，显示推荐/最新
  - `pages/list`：商品列表，支持筛选/分页
  - `pages/detail`：商品详情，联系/下单/收藏
  - `pages/post`：发布商品，表单与图片上传
  - `pages/user`：用户中心，登录/我的发布

- **组件**
  - `components/item-card`：商品卡片

- **工具/服务**
  - `utils/api.js`：与后端交互封装
  - `utils/storage.js`：本地存储封装

建议把每个条目拆成 1-2 天的小任务，分别分配给组员，并在 PR 合并后删除临时分支。
