# 故障树智能生成系统 - 前端

## 技术栈
- Vue 3：渐进式JavaScript框架
- Vite：快速构建工具
- Element Plus：UI组件库
- mxGraph：图形编辑器
- ECharts：数据可视化

## 快速启动

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本
```bash
npm run build
```

## 项目结构
```
frontend/
├── src/
│   ├── api/           # API请求封装
│   ├── components/    # 通用组件
│   ├── pages/         # 页面组件
│   ├── router/        # 路由配置
│   ├── store/         # 状态管理
│   └── utils/         # 工具函数
├── index.html         # HTML入口
└── vite.config.js     # Vite配置
```

## 功能模块
- 文件上传：支持DOCX/Excel/CSV/TXT上传
- 知识提取：展示提取的故障事件和逻辑门
- 故障树生成：图形化编辑故障树
- 结果导出：支持多种格式导出
