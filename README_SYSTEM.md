# YouTube Influencer 搜索系统

## 🎯 系统概述

这是一个完整的Web应用系统，用于搜索和分析测评过指定产品的YouTube influencer。系统提供了用户友好的Web界面，支持自定义搜索条件和实时进度监控。

## ✨ 核心功能

### 🔍 智能搜索
- **动态关键词生成**：根据产品名称自动生成多个搜索变体
- **美国地区限制**：只搜索美国地区的YouTube频道
- **多维度筛选**：支持订阅数和视频观看量双重筛选条件

### ⚙️ 灵活配置
- **自定义API密钥**：用户输入自己的YouTube Data API密钥
- **可调节筛选条件**：自定义最小订阅数和视频观看量阈值
- **实时API验证**：提交前验证API密钥有效性

### 📊 实时监控
- **进度条显示**：实时显示搜索进度百分比
- **详细统计**：当前关键词、总关键词数、已找到influencer数
- **状态更新**：任务状态实时更新

### 📈 结果展示
- **摘要统计**：总数、平均值、最大值等关键指标
- **详细表格**：完整的influencer信息列表
- **快速链接**：直接跳转到YouTube频道和视频

### 💾 数据管理
- **搜索历史**：保存所有搜索任务的历史记录
- **CSV导出**：一键下载完整的搜索结果
- **数据持久化**：使用SQLite数据库永久保存

## 🏗️ 系统架构

```
前端界面 (Bootstrap + JavaScript)
         ↓
Flask API 服务 (RESTful接口)
         ↓
YouTube爬虫服务 (动态配置)
         ↓
SQLite数据库 (数据持久化)
```

## 📁 文件结构

```
youtube_influencer_system/
├── app.py                    # Flask主应用
├── scraper_service.py        # 重构的爬虫服务类
├── models.py                # SQLite数据库模型
├── templates/
│   └── index.html           # 前端HTML模板
├── static/
│   └── js/
│       └── app.js           # 前端JavaScript逻辑
├── temp/                    # 临时文件目录
├── database.db              # SQLite数据库文件
├── requirements.txt         # Python依赖包
└── README_SYSTEM.md         # 系统说明文档
```

## 🚀 启动系统

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动Web服务
```bash
python app.py
```

### 3. 访问系统
打开浏览器访问：`http://localhost:8080`

## 📝 使用说明

### 1. 配置搜索参数
- **产品机型**：输入要搜索的产品名称（如"eero 7", "Netgear Orbi 370"）
- **API密钥**：输入YouTube Data API密钥并验证
- **筛选条件**：设置最小订阅数和视频观看量

### 2. 启动搜索
- 点击"开始搜索"按钮
- 系统自动生成多个搜索关键词
- 实时显示搜索进度和统计信息

### 3. 查看结果
- 搜索完成后自动显示结果
- 查看摘要统计和详细表格
- 点击链接直接访问YouTube频道/视频

### 4. 导出数据
- 点击"下载CSV"按钮导出完整数据
- CSV文件包含所有找到的influencer信息

### 5. 历史记录
- 点击"搜索历史"查看过往搜索
- 重新查看已完成任务的结果

## 🔧 API接口

### 搜索相关
- `POST /api/search` - 启动搜索任务
- `GET /api/status/<task_id>` - 获取任务状态
- `GET /api/results/<task_id>` - 获取任务结果

### 数据管理
- `GET /api/history` - 获取搜索历史
- `GET /api/download/<task_id>` - 下载CSV结果
- `POST /api/validate-key` - 验证API密钥

### 任务监控
- `GET /api/running-tasks` - 获取运行中的任务

## 🎨 界面特性

- **响应式设计**：支持PC和移动端
- **Bootstrap样式**：现代化美观界面
- **实时更新**：无需刷新页面的动态更新
- **友好提示**：操作反馈和错误提示
- **进度可视化**：直观的进度条和统计图表

## 🔒 安全特性

- **API密钥哈希**：数据库中存储密钥哈希而非明文
- **参数验证**：所有输入参数的严格验证
- **错误处理**：完善的异常捕获和错误提示
- **请求限制**：自动控制API请求频率

## 🚀 部署选项

### 本地开发
```bash
python app.py  # 开发模式，端口8080
```

### 生产部署
推荐使用Gunicorn等WSGI服务器：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Docker部署
系统支持Docker容器化部署（需要创建Dockerfile）

## 📊 系统优势

1. **智能关键词生成** - 自动生成多种搜索变体，提高覆盖率
2. **实时进度监控** - 长时间任务的透明化进度显示
3. **数据持久化** - 搜索历史和结果永久保存
4. **用户友好界面** - 现代化Web界面，操作简单直观
5. **灵活配置** - 支持自定义API密钥和筛选条件
6. **高效去重** - 智能的频道+产品组合去重机制

## 🔧 扩展功能

系统架构支持以下扩展：
- 多语言支持
- 更多平台集成（TikTok、Instagram等）
- 高级数据分析和可视化
- 用户账户系统
- 批量搜索功能
- API配额管理

---

**开发完成时间**: 2025年8月
**技术栈**: Python Flask + SQLite + Bootstrap + JavaScript
**目标用户**: 营销人员、产品经理、市场分析师