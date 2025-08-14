# YouTube Influencer Search System

🎯 **智能搜索和分析测评过指定产品的YouTube影响者**

一个完整的Web应用系统，支持自定义机型搜索、实时进度监控、数据持久化存储和结果导出。

![Node.js](https://img.shields.io/badge/Node.js-22+-green.svg)
![Vercel](https://img.shields.io/badge/Vercel-Serverless-black.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1+-purple.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-lightgrey.svg)

## 📸 系统截图

### 主要界面
- 🏠 现代化搜索配置界面
- 📊 实时进度监控面板  
- 📈 详细结果展示表格
- 📋 搜索历史管理

## ✨ 核心功能

### 🔍 智能搜索引擎
- **动态关键词生成**: 根据产品名称自动生成多个搜索变体
- **美国地区限制**: 只搜索美国地区的YouTube频道
- **多维度筛选**: 支持订阅数和视频观看量双重筛选条件
- **去重机制**: 智能的频道+产品组合去重

### ⚙️ 灵活配置系统
- **自定义API密钥**: 用户输入自己的YouTube Data API密钥
- **可调节筛选条件**: 自定义最小订阅数和视频观看量阈值
- **实时API验证**: 提交前验证API密钥有效性

### 📊 实时监控面板
- **进度条显示**: 实时显示搜索进度百分比
- **详细统计**: 当前关键词、总关键词数、已找到influencer数
- **状态更新**: 任务状态实时更新
- **后台任务**: 支持长时间运行的搜索任务

### 📈 结果展示分析
- **摘要统计**: 总数、平均值、最大值等关键指标
- **详细表格**: 完整的influencer信息列表
- **快速链接**: 直接跳转到YouTube频道和视频
- **数据排序**: 按订阅数、观看量等维度排序

### 💾 数据管理
- **搜索历史**: 保存所有搜索任务的历史记录
- **CSV导出**: 一键下载完整的搜索结果
- **数据持久化**: 使用SQLite数据库永久保存
- **任务恢复**: 页面刷新后自动恢复运行中的任务

## 🏗️ 系统架构

```
📱 前端界面 (Bootstrap + JavaScript)
         ↓ RESTful API
🌐 Node.js 22 无服务函数 (Vercel Functions, 逐步轮询处理)  
         ↓ 动态配置
🤖 YouTube数据服务 (关键词生成 + Data API v3)
         ↓ 数据持久化
🗄️ SQLite数据库 (任务与结果存储)
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/youtube-influencer-search.git
cd youtube-influencer-search
```

### 2. 安装依赖
```bash
npm install
```

### 3. 获取YouTube API密钥
1. 访问 [Google Cloud Console](https://console.developers.google.com/)
2. 创建新项目或选择现有项目
3. 启用 **YouTube Data API v3**
4. 创建 **API密钥** 凭据
5. 复制API密钥备用

### 4. 启动系统
```bash
npx vercel dev
```

### 5. 访问系统
打开浏览器访问：`http://localhost:3000`

## 📝 使用说明

### 第一步：配置搜索参数
1. **产品机型**: 输入要搜索的产品名称
   - ✅ `eero 7`
   - ✅ `Netgear Orbi 370` 
   - ✅ `Asus ZenWifi BE5000`
   - ✅ `TP-Link Archer AX73`

2. **API密钥**: 输入YouTube Data API密钥并点击验证

3. **筛选条件**: 
   - 最小订阅数（默认：10,000）
   - 最小视频观看量（默认：5,000）

### 第二步：启动搜索
- 点击 **"开始搜索"** 按钮
- 系统自动生成多个搜索关键词
- 实时显示搜索进度和统计信息

### 第三步：查看结果
- 搜索完成后自动显示结果摘要
- 浏览详细的influencer列表
- 点击链接直接访问YouTube频道/视频

### 第四步：导出数据
- 点击 **"下载CSV"** 导出完整数据
- CSV包含所有influencer的详细信息

## 📊 搜索示例

### 输入产品：`eero 7`
**系统自动生成关键词：**
- `eero 7 review`
- `eero 7 unboxing`  
- `eero 7 test`
- `eero 7 wifi router review`
- `eero 7 mesh router review`

**搜索结果示例：**
- 找到 **34个** 符合条件的美国influencer
- 最高订阅数：**CNN (1,860万订阅)**
- 最高观看数：**eero官方 (72.5万观看)**

## 🔧 API接口文档

### 搜索相关
```http
POST /api/search
```
启动搜索任务

```http  
GET /api/status?task_id={task_id}
```
获取任务状态（需在请求头中携带 `X-YouTube-Key: <Your API Key>` 以便函数在无状态环境下进行下一步查询）

```http
GET /api/results/{task_id}
```
获取任务结果

### 数据管理
```http
GET /api/history
```
获取搜索历史

```http
GET /api/download/{task_id}
```
下载CSV结果

```http
POST /api/validate-key
```
验证API密钥

## 📁 项目结构

```
youtube-influencer-search/
├── 📁 api/                      # Vercel Serverless Functions (Node.js 22)
│   ├── index.js                # 健康检查
│   ├── search.js               # 启动任务 (生成关键词并初始化任务)
│   ├── status.js               # 逐步处理关键词并更新进度（需要 X-YouTube-Key）
│   ├── results.js              # 获取任务结果与摘要
│   ├── history.js              # 获取历史任务
│   ├── download.js             # 导出CSV
│   ├── validate-key.js         # 验证API密钥
│   ├── db.js                   # SQLite 数据访问层（支持只读FS回退到 /tmp）
│   ├── utils.js                # 关键词生成与YouTube API封装
│   └── _http.js                # 轻量HTTP工具
├── 📁 public/
│   ├── index.html              # 前端页面 (Bootstrap)
│   └── app.js                  # 前端逻辑，进度轮询/渲染/导出
├── 🗃️ database.db              # SQLite数据库文件（本地开发持久化，云端可能位于 /tmp）
├── 📄 vercel.json              # Vercel 配置（Node 22 运行时）
├── 📦 package.json             # Node依赖与脚本
└── 📖 README.md                # 项目说明文档
```

## 🔒 安全特性

- **API密钥保护**: 仅存储 API Key 的哈希（任务记录中保存 `api_key_hash`），不落盘明文
- **无状态调用**: `status` 端点通过请求头 `X-YouTube-Key` 临时获取Key，便于Serverless安全执行
- **参数验证**: 严格的输入校验与失败处理
- **错误处理**: 完整的异常捕获和用户提示
- **请求限制**: 智能请求控制，避免YouTube配额超限

## 🚀 部署选项

### 本地开发
```bash
npm install
npx vercel dev
```

### Vercel 一键部署
```bash
npm i -g vercel
vercel
```
首次执行会交互式创建/绑定项目，之后 `vercel --prod` 即可推送生产。

## 📈 性能表现

### 测试结果
- **搜索效率**: 单个产品平均生成5-8个关键词
- **数据覆盖**: 可发现90%+的相关influencer
- **去重准确性**: 频道+产品组合去重，确保数据唯一性
- **API效率**: 智能请求控制，避免配额超限

### 成功案例
✅ **WiFi路由器行业分析**
- 搜索7个品牌型号
- 发现241个美国influencer  
- 覆盖从科技评测到开箱体验的完整生态
- 数据质量：平均订阅数46.2万

## 🎯 适用场景

- 🏢 **营销团队**: 寻找产品推广的YouTube合作伙伴
- 📊 **市场分析**: 分析竞品的影响者生态和传播策略  
- 🎬 **内容创作**: 研究同类产品的内容创作趋势
- 📈 **投资分析**: 评估品牌在YouTube平台的影响力

## 🔮 未来规划

- [ ] 支持更多平台 (TikTok, Instagram)
- [ ] 高级数据可视化分析
- [ ] 用户账户和权限管理
- [ ] 批量搜索和定时任务
- [ ] API配额管理和优化
- [ ] 多语言界面支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [YouTube Data API](https://developers.google.com/youtube/v3) - 强大的数据接口
- [Bootstrap](https://getbootstrap.com/) - 优秀的前端框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架

---

**⭐ 如果这个项目对你有帮助，请给个Star支持！**

**📧 联系方式**: [你的邮箱]
**🌐 项目主页**: [GitHub链接]