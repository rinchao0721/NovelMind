# NovelMind

<div align="center">

![NovelMind Logo](resources/icons/icon.svg)

**AI 驱动的小说剧情分析与人物关系可视化工具**

一款基于 Electron + Vue 3 + Python 的桌面应用，使用大语言模型自动分析小说结构、提取人物关系，并以精美图谱呈现。

[功能特性](#功能特性) •
[快速开始](#快速开始) •
[使用指南](#使用指南) •
[技术栈](#技术栈) •
[开发指南](#开发指南)

</div>

---

## ✨ 功能特性

### 🤖 智能分析
- **AI 人物提取** - 自动识别小说中的所有角色，包括别名、性格、描述
- **关系分析** - 分析人物之间的关系类型（亲属、朋友、敌对、恋人等）
- **情节追踪** - 提取关键剧情事件、转折点、伏笔
- **章节摘要** - 自动生成每章内容摘要

### 📊 可视化展示
- **关系图谱** - 交互式力导向图展示人物关系网络
- **重要性评分** - 根据出场频率和剧情影响计算人物重要性
- **关系筛选** - 按关系类型、重要性过滤显示
- **图谱导出** - 支持导出为高清 PNG 图片

### 🎯 多平台支持
- **文件格式** - TXT、DOCX、EPUB、MOBI
- **LLM 提供商** - OpenAI、Claude、Gemini、DeepSeek、Qwen、智谱、百度文心、自定义 API
- **操作系统** - Windows、macOS、Linux

### 🔒 数据安全
- **本地存储** - 所有数据存储在本地，不上传云端
- **加密保护** - API 密钥使用 AES 加密存储
- **隐私优先** - 仅在分析时调用 LLM API

### 📤 导出功能
- **JSON 格式** - 包含完整数据结构，便于二次开发
- **Markdown 格式** - 人类可读的文档，便于分享
- **图片导出** - 高清关系图谱 PNG

---

## 🚀 快速开始

### 环境要求

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| **Node.js** | 18.x 或更高 | 前端运行环境 |
| **Python** | 3.11 或 3.12 | 后端运行环境 |
| **uv** | 最新版 | Python 包管理器（推荐）|
| **Neo4j** | 5.x | 可选，用于图数据库存储 |

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/novelmind.git
cd novelmind
```

#### 2. 安装依赖

```bash
# 一键安装前后端所有依赖
npm run setup
```

或手动分别安装：

```bash
# 前端依赖
npm install

# 后端依赖
cd backend
uv sync
```

#### 3. 配置 API 密钥

首次运行时，在应用设置页面配置您的 LLM API 密钥。至少需要配置一个提供商：

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic Claude**: https://console.anthropic.com/
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **DeepSeek**: https://platform.deepseek.com/
- **阿里百炼**: https://dashscope.aliyun.com/
- **智谱 AI**: https://open.bigmodel.cn/
- **百度文心**: https://console.bce.baidu.com/qianfan/

#### 4. 启动应用

```bash
# 开发模式（推荐）
npm run dev

# 或分别启动前后端
npm run dev:backend    # 终端 1: 启动后端服务
npm run dev:electron   # 终端 2: 启动前端应用
```

应用将自动打开，后端服务运行在 `http://localhost:5001`

---

## 📖 使用指南

### 第一步：导入小说

1. 点击首页"**导入小说**"按钮
2. 选择小说文件（支持 TXT、DOCX、EPUB、MOBI）
3. 等待文件解析完成

### 第二步：开始分析

1. 进入"**剧情分析**"页面
2. 选择要分析的小说
3. 配置分析选项：
   - **分析范围**：全书或部分章节
   - **分析深度**：快速/标准/深度
   - **分析项目**：人物、关系、情节、摘要
4. 点击"**开始分析**"按钮
5. 等待 AI 分析完成（根据小说长度，可能需要几分钟）

### 第三步：查看结果

#### 关系图谱
- 进入"**人物关系图谱**"页面
- 使用鼠标拖拽、缩放查看图谱
- 点击节点查看人物详情
- 使用右侧筛选面板过滤关系类型

#### 人物列表
- 进入"**人物列表**"页面
- 查看所有角色的详细信息
- 按重要性、首次出场排序

#### 时间线
- 进入"**时间线**"页面
- 查看剧情发展的时间顺序

### 第四步：导出数据

1. 在分析结果页面点击"**导出结果**"
2. 选择导出格式（JSON 或 Markdown）
3. 保存文件到本地

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Electron** | 28+ | 跨平台桌面应用框架 |
| **Vue 3** | 3.4+ | 渐进式前端框架 |
| **TypeScript** | 5.3+ | 类型安全 |
| **Element Plus** | 2.5+ | UI 组件库 |
| **ECharts** | 5.5+ | 数据可视化 |
| **Pinia** | 2.1+ | 状态管理 |
| **Vue Router** | 4.3+ | 路由管理 |
| **Axios** | 1.6+ | HTTP 客户端 |
| **Vite** | 5.1+ | 构建工具 |

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11-3.12 | 后端语言 |
| **FastAPI** | 0.109+ | Web 框架 |
| **Uvicorn** | 0.27+ | ASGI 服务器 |
| **SQLite** | - | 元数据存储 |
| **Neo4j** | 5.x (可选) | 图数据库 |
| **cryptography** | 46+ | 加密存储 |
| **httpx** | 0.26+ | 异步 HTTP 客户端 |
| **python-docx** | 1.1+ | DOCX 解析 |
| **ebooklib** | 0.18+ | EPUB 解析 |

### AI 集成

- **OpenAI GPT** - GPT-4o, GPT-4 Turbo, GPT-3.5
- **Anthropic Claude** - Claude 3.5 Sonnet, Claude 3 Opus
- **Google Gemini** - Gemini 1.5 Pro, Gemini 1.5 Flash
- **DeepSeek** - DeepSeek Chat, DeepSeek Reasoner
- **阿里百炼** - Qwen-Max, Qwen-Plus, Qwen-Turbo
- **智谱 AI** - GLM-4, GLM-4-Flash
- **百度文心** - ERNIE 4.0, ERNIE 3.5

---

## 🔧 开发指南

### 项目结构

```
novelmind/
├── electron/                 # Electron 主进程
│   ├── main.ts              # 主进程入口
│   └── preload.ts           # 预加载脚本
├── src/                     # Vue 前端源码
│   ├── views/               # 页面组件
│   ├── components/          # 可复用组件
│   ├── stores/              # Pinia 状态管理
│   ├── api/                 # API 接口
│   ├── types/               # TypeScript 类型
│   └── router/              # 路由配置
├── backend/                 # Python 后端
│   ├── main.py             # FastAPI 入口
│   ├── config.py           # 配置管理
│   ├── api/                # API 路由
│   │   ├── novels.py       # 小说管理
│   │   ├── analysis.py     # 分析任务
│   │   ├── characters.py   # 人物查询
│   │   ├── settings.py     # 设置管理
│   │   └── export.py       # 数据导出
│   ├── services/           # 业务逻辑
│   │   ├── file_parser.py  # 文件解析
│   │   ├── llm_service.py  # LLM 统一接口
│   │   ├── analysis_engine.py  # 分析引擎
│   │   ├── settings_service.py # 设置服务
│   │   └── export_service.py   # 导出服务
│   ├── llm/                # LLM 提供商
│   │   └── providers.py    # 7个提供商实现
│   ├── database/           # 数据库操作
│   │   ├── sqlite_db.py    # SQLite
│   │   └── neo4j_db.py     # Neo4j
│   ├── models/             # 数据模型
│   └── prompts/            # AI 提示词模板
├── resources/              # 应用资源
│   └── icons/              # 应用图标
├── scripts/                # 构建脚本
│   └── afterPack.js        # 打包后处理
├── package.json            # npm 配置
├── vite.config.ts          # Vite 配置
├── tsconfig.json           # TypeScript 配置
└── pyproject.toml          # Python 项目配置
```

### 开发命令

```bash
# 开发模式
npm run dev              # 同时启动前后端
npm run dev:electron     # 仅启动前端
npm run dev:backend      # 仅启动后端

# 构建
npm run build            # 构建 Vue + Electron
npm run build:vue        # 仅构建 Vue
npm run build:electron   # 仅构建 Electron

# 打包发布
npm run build:win        # Windows 安装包
npm run build:mac        # macOS DMG
npm run build:linux      # Linux AppImage/DEB

# 代码质量
npm run lint             # ESLint 检查
npm run typecheck        # TypeScript 类型检查
```

### 调试技巧

#### 前端调试
- 开发模式下自动打开 DevTools
- 使用 Vue DevTools 浏览器插件
- 查看 Console 和 Network 面板

#### 后端调试
- 查看后端日志输出
- 访问 `http://localhost:5001/docs` 查看 API 文档
- 使用 `uv run python -m pdb backend/main.py` 调试

#### 数据库查看
```bash
# SQLite
sqlite3 backend/data/novelmind.db

# Neo4j
http://localhost:7474
```

### 添加新的 LLM 提供商

1. 在 `backend/llm/providers.py` 添加新的提供商类
2. 继承 `BaseLLMProvider` 实现 `chat()` 方法
3. 在 `create_provider()` 工厂函数中注册
4. 更新前端 `SettingsView.vue` 添加配置表单

示例：
```python
class CustomProvider(BaseLLMProvider):
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # 实现您的 API 调用逻辑
        pass
```

---

## 📦 打包发布

### Windows

```bash
npm run build:win
```

生成文件在 `release/` 目录：
- `NovelMind-1.0.0-win-x64.exe` - NSIS 安装程序
- `NovelMind-1.0.0-win-x64-portable.exe` - 便携版

### macOS

```bash
npm run build:mac
```

生成文件：
- `NovelMind-1.0.0-mac-x64.dmg` - Intel 芯片
- `NovelMind-1.0.0-mac-arm64.dmg` - Apple Silicon

### Linux

```bash
npm run build:linux
```

生成文件：
- `NovelMind-1.0.0-x86_64.AppImage` - 通用格式
- `novelmind_1.0.0_amd64.deb` - Debian/Ubuntu

---

## ⚙️ 配置说明

### 环境变量（可选）

如需在命令行设置环境变量，可创建 `.env` 文件：

```env
# 应用配置
APP_PORT=5001
APP_DEBUG=false
APP_SECRET_KEY=your-secret-key-here

# 数据库
DATABASE_PATH=./data/novelmind.db

# Neo4j（可选）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM API 密钥（也可在应用内配置）
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

**注意**：建议在应用内的设置页面配置 API 密钥，这样会被加密存储。

### 数据存储位置

- **Windows**: `%APPDATA%\NovelMind\`
- **macOS**: `~/Library/Application Support/NovelMind/`
- **Linux**: `~/.config/NovelMind/`

包含：
- `novelmind.db` - SQLite 数据库
- `settings.json` - 应用设置
- `secure.enc` - 加密的 API 密钥

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交 Issue

遇到 Bug 或有新功能建议？请[提交 Issue](https://github.com/your-username/novelmind/issues)

### 提交 Pull Request

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循 ESLint 和 Prettier 配置
- 使用 TypeScript 类型注解
- 编写清晰的提交信息
- 更新相关文档

---

## 🙏 致谢

本项目受 [MiroFish](https://github.com/666ghj/MiroFish) 启发，感谢原作者的创意。

技术栈致谢：
- Electron、Vue.js、FastAPI 等开源项目
- OpenAI、Anthropic、Google 等 AI 提供商

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 📮 联系方式

- **Issue**: [GitHub Issues](https://github.com/your-username/novelmind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/novelmind/discussions)

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️ Star！**

Made with ❤️ by NovelMind Team

</div>
