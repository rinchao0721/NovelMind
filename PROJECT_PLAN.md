# NovelMind - 小说剧情拆解与人物关系分析系统

## 一、项目概述

**NovelMind** 是一款基于 AI 技术的小说剧情拆解与人物关系分析桌面应用。专注于：

- **剧情结构分析**：自动识别章节、情节线索、伏笔与悬念
- **人物关系图谱**：构建可交互的角色关系网络
- **多维度可视化**：时间线、统计图表、关系演变

## 二、技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     NovelMind 架构图                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Electron 主进程                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │ │
│  │  │  窗口管理    │  │  IPC通信    │  │  Python后端进程管理  │ │ │
│  │  └─────────────┘  └─────────────┘  └──────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌───────────────────────────┼─────────────────────────────────┐ │
│  │          Vue 3 + TypeScript 前端渲染进程                     │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │ │
│  │  │ 文件导入  │  │ 分析面板  │  │ 关系图谱  │  │  设置/API配置│ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────────┐│ │
│  │  │           ECharts + D3.js 可视化层                        ││ │
│  │  └──────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │ HTTP/IPC                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Python FastAPI 后端                          │ │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────────────┐│ │
│  │  │ 文件解析器  │  │  AI分析引擎 │  │  图谱构建器            ││ │
│  │  └────────────┘  └────────────┘  └─────────────────────────┘│ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │              LLM 统一接口层 (多API支持)                  │ │ │
│  │  │  OpenAI│Claude│Gemini│DeepSeek│Qwen│ZhipuAI│Baidu...  │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                      数据存储层                              │ │
│  │  ┌──────────────────────┐  ┌──────────────────────────────┐ │ │
│  │  │   SQLite (元数据)     │  │   Neo4j (人物关系图谱)       │ │ │
│  │  └──────────────────────┘  └──────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 三、技术栈详情

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **桌面框架** | Electron | 28+ | 跨平台桌面应用框架 |
| **前端框架** | Vue 3 + TypeScript | 3.4+ | 响应式UI框架 |
| **UI组件** | Element Plus | 2.5+ | Vue 3 组件库 |
| **可视化** | ECharts + D3.js | 5.5+ / 7+ | 图表与关系图 |
| **后端框架** | FastAPI | 0.109+ | 高性能异步Python框架 |
| **数据库** | SQLite | 3.40+ | 轻量级关系数据库 |
| **图数据库** | Neo4j | 5.x | 人物关系存储与查询 |
| **LLM SDK** | LiteLLM | 1.30+ | 统一LLM调用接口 |
| **Python** | Python | 3.11-3.12 | 后端运行时 |
| **包管理** | pnpm + uv | 最新 | 前后端包管理器 |

## 四、核心功能模块

### 1. 文件处理模块
- TXT 纯文本解析
- DOCX Word文档解析 (python-docx)
- EPUB 电子书解析 (ebooklib)
- MOBI 电子书解析 (mobi)
- 自动章节识别与分割
- 编码自动检测 (chardet)

### 2. AI分析引擎
- 人物识别与提取
- 人物属性分析 (性格、外貌、背景)
- 关系类型识别 (亲属、朋友、敌对、暧昧等)
- 情节线索追踪
- 伏笔与悬念检测
- 章节摘要生成
- 情感走向分析

### 3. 图谱构建与可视化
- Neo4j 图数据存储
- 力导向关系图 (ECharts)
- 关系热力图
- 时间线展示
- 人物出场频率统计
- 关系强度分析
- 交互式缩放、过滤、搜索

### 4. LLM API 管理
- OpenAI 官方API
- Anthropic Claude API
- Google Gemini API
- DeepSeek API
- 阿里百炼 (Qwen)
- 智谱AI (GLM)
- 百度文心
- OpenRouter 聚合API
- 自定义 OpenAI 兼容端点

## 五、目录结构

### 完整项目结构（基于实际代码库）

```
xiaoshuotuilijiexi/              # 项目根目录
├── .github/                     # GitHub 配置
│   └── workflows/               # CI/CD 工作流
│       └── release.yml          # 自动发布流程
│
├── electron/                    # Electron 主进程
│   ├── main.ts                  # 主进程入口，窗口管理，Python后端进程管理
│   └── preload.ts               # 预加载脚本，IPC通信桥接
│
├── src/                         # Vue 3 + TypeScript 前端源码
│   ├── main.ts                  # 前端应用入口
│   ├── App.vue                  # 根组件
│   ├── vite-env.d.ts            # Vite 环境类型定义
│   ├── auto-imports.d.ts        # 自动导入类型声明
│   ├── components.d.ts          # 组件类型声明
│   │
│   ├── router/                  # Vue Router 路由配置
│   │   └── index.ts             # 路由定义与导航守卫
│   │
│   ├── stores/                  # Pinia 状态管理
│   │   ├── novel.ts             # 小说数据状态（列表、当前选中等）
│   │   ├── analysis.ts          # 分析任务状态（进度、结果）
│   │   └── settings.ts          # 应用设置状态（API配置、主题等）
│   │
│   ├── views/                   # 页面视图组件
│   │   ├── HomeView.vue         # 首页（小说导入入口）
│   │   ├── AnalysisView.vue     # 分析面板（配置与执行分析）
│   │   ├── GraphView.vue        # 关系图谱可视化页面
│   │   ├── CharacterView.vue    # 人物详情页面
│   │   └── SettingsView.vue     # 设置页面（LLM API配置）
│   │
│   ├── components/              # 可复用组件
│   │   ├── ProviderAvatar.vue   # LLM 提供商头像组件
│   │   ├── common/              # 通用基础组件
│   │   │   ├── BaseCard.vue     # 基础卡片组件
│   │   │   ├── EmptyState.vue   # 空状态占位组件
│   │   │   ├── LoadingOverlay.vue # 加载遮罩组件
│   │   │   ├── PageHeader.vue   # 页面头部组件
│   │   │   └── StatusTag.vue    # 状态标签组件
│   │   ├── import/              # 导入相关组件
│   │   │   └── FileImport.vue   # 文件拖拽上传组件
│   │   ├── analysis/            # 分析相关组件
│   │   │   ├── AnalysisConfigForm.vue   # 分析配置表单
│   │   │   ├── AnalysisProgress.vue     # 分析进度显示
│   │   │   ├── AnalysisResultCard.vue   # 分析结果卡片
│   │   │   ├── NovelSelector.vue        # 小说选择器
│   │   │   └── ExportDialog.vue         # 导出对话框
│   │   ├── character/           # 人物相关组件
│   │   │   └── CharacterCard.vue        # 人物信息卡片
│   │   └── graph/               # 图谱相关组件
│   │       ├── RelationGraph.vue        # ECharts关系图组件
│   │       ├── GraphFilter.vue          # 图谱过滤器
│   │       └── CharacterDrawer.vue      # 人物详情抽屉
│   │
│   ├── composables/             # Vue 组合式函数（可复用逻辑）
│   │   ├── useAnalysisTask.ts   # 分析任务管理逻辑
│   │   ├── useECharts.ts        # ECharts 图表封装
│   │   ├── useExport.ts         # 数据导出逻辑
│   │   └── useNovelSelection.ts # 小说选择逻辑
│   │
│   ├── api/                     # 后端API调用封装
│   │   └── index.ts             # Axios 实例配置与API方法
│   │
│   ├── types/                   # TypeScript 类型定义
│   │   └── index.ts             # 全局类型接口（Novel、Character、Relationship等）
│   │
│   ├── config/                  # 前端配置
│   │   └── providers.ts         # LLM 提供商配置（图标、名称等）
│   │
│   ├── utils/                   # 工具函数
│   │   ├── format.ts            # 格式化工具（日期、数字等）
│   │   └── relations.ts         # 关系类型处理工具
│   │
│   └── assets/                  # 静态资源
│       ├── styles/              # 样式文件
│       │   └── main.scss        # 全局样式
│       └── images/              # 图片资源
│           └── providers/       # LLM 提供商图标
│               ├── openai.png
│               ├── anthropic.png
│               ├── gemini.png
│               ├── deepseek.png
│               ├── dashscope.png
│               ├── zhipu.png
│               ├── baidu-cloud.svg
│               ├── silicon.png
│               ├── ollama.png
│               ├── openrouter.png
│               ├── aihubmix.png
│               └── custom.svg
│
├── backend/                     # Python FastAPI 后端
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置管理（环境变量、数据库路径）
│   ├── constants.py             # 常量定义
│   ├── README.md                # 后端说明文档
│   ├── pyproject.toml           # uv 依赖管理配置
│   ├── requirements.txt         # pip 依赖列表
│   ├── uv.lock                  # uv 锁文件
│   ├── novelmind.spec           # PyInstaller 打包配置
│   │
│   ├── api/                     # API 路由层
│   │   ├── __init__.py
│   │   ├── novels.py            # 小说管理API（导入、列表、删除）
│   │   ├── analysis.py          # 分析API（启动、状态、取消）
│   │   ├── characters.py        # 人物API（列表、详情）
│   │   ├── relationships.py     # 关系API（图谱数据）
│   │   ├── export.py            # 导出API（JSON、CSV、Markdown）
│   │   └── settings.py          # 设置API（获取、更新、测试连接）
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── file_parser.py       # 文件解析服务（TXT、DOCX、EPUB、MOBI）
│   │   ├── llm_service.py       # LLM 调用服务（统一接口）
│   │   ├── analysis_engine.py   # AI分析引擎（人物提取、关系分析）
│   │   └── graph_builder.py     # 图谱构建服务（Neo4j集成）
│   │
│   ├── models/                  # 数据模型层（Pydantic模型）
│   │   ├── __init__.py
│   │   ├── novel.py             # 小说模型
│   │   ├── character.py         # 人物模型
│   │   ├── relationship.py      # 关系模型
│   │   └── chapter.py           # 章节模型
│   │
│   ├── llm/                     # LLM 提供商适配器
│   │   ├── __init__.py
│   │   ├── base.py              # 基类接口定义
│   │   ├── openai_provider.py   # OpenAI API适配
│   │   ├── claude_provider.py   # Anthropic Claude适配
│   │   ├── gemini_provider.py   # Google Gemini适配
│   │   ├── deepseek_provider.py # DeepSeek适配
│   │   ├── qwen_provider.py     # 阿里百炼（Qwen）适配
│   │   ├── zhipu_provider.py    # 智谱AI适配
│   │   └── custom_provider.py   # 自定义端点适配
│   │
│   ├── prompts/                 # AI 提示词模板
│   │   ├── __init__.py
│   │   ├── character_extraction.py    # 人物提取提示词
│   │   ├── relationship_analysis.py   # 关系分析提示词
│   │   ├── plot_analysis.py           # 情节分析提示词
│   │   └── summary_generation.py      # 摘要生成提示词
│   │
│   ├── database/                # 数据库操作层
│   │   ├── __init__.py
│   │   ├── sqlite_db.py         # SQLite 数据库操作
│   │   └── neo4j_db.py          # Neo4j 图数据库操作（可选）
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── text_utils.py        # 文本处理工具
│   │   └── encoding_utils.py    # 编码检测工具
│   │
│   ├── data/                    # 运行时数据目录
│   │   ├── app.log              # 应用日志
│   │   └── novels.db            # SQLite 数据库文件（运行时生成）
│   │
│   ├── build/                   # PyInstaller 构建临时目录
│   └── dist/                    # PyInstaller 打包输出目录
│       └── novelmind/           # 后端可执行文件
│           ├── novelmind.exe    # Windows 可执行文件
│           └── _internal/       # 依赖库
│
├── public/                      # 公共静态资源（直接复制到dist）
│   └── icons/                   # 应用图标（多尺寸）
│
├── resources/                   # 应用资源（打包时使用）
│   └── icons/                   # 应用图标源文件
│
├── scripts/                     # 构建与部署脚本
│   ├── setup.ps1                # Windows 环境安装脚本
│   └── build.ps1                # Windows 打包脚本
│
├── dist/                        # 前端构建输出目录
├── dist-electron/               # Electron 构建输出
├── node_modules/                # Node.js 依赖
│
├── package.json                 # Node.js 项目配置与依赖
├── package-lock.json            # npm 依赖锁文件
├── vite.config.ts               # Vite 构建配置
├── tsconfig.json                # TypeScript 编译配置
├── tsconfig.node.json           # Node.js 环境 TS 配置
├── installer.iss                # Inno Setup 安装程序配置
│
├── .env.example                 # 环境变量示例文件
├── .gitignore                   # Git 忽略规则
├── LICENSE                      # 开源许可证
├── README.md                    # 项目说明文档
├── PROJECT_PLAN.md              # 项目计划与架构文档（本文件）
└── list_novels.py               # 小说列表工具脚本
```

### 关键目录说明

#### 前端部分 (src/)
- **views/**: 页面级组件，对应路由
- **components/**: 按功能模块组织的可复用组件
- **composables/**: 组合式API，封装可复用的业务逻辑
- **stores/**: Pinia状态管理，集中管理应用状态
- **api/**: 封装所有后端API调用
- **types/**: TypeScript类型定义，确保类型安全

#### 后端部分 (backend/)
- **api/**: 路由层，定义RESTful API端点
- **services/**: 业务逻辑层，核心功能实现
- **models/**: 数据模型，使用Pydantic进行验证
- **llm/**: LLM提供商适配器，支持多种AI API
- **database/**: 数据持久化层
- **prompts/**: AI提示词管理，便于调优

#### 配置文件
- **vite.config.ts**: Vite构建配置，Electron插件设置
- **installer.iss**: Inno Setup配置，生成Windows安装程序
- **novelmind.spec**: PyInstaller配置，打包Python后端
- **pyproject.toml**: Python项目配置，使用uv管理依赖

## 六、开发阶段规划

### Phase 1: 基础框架 (P0)
- [x] 1.1 项目初始化 (Electron + Vue + FastAPI)
- [ ] 1.2 基础UI框架搭建
- [ ] 1.3 Electron与后端通信机制
- [ ] 1.4 SQLite数据库初始化
- [ ] 1.5 Neo4j连接配置

### Phase 2: 文件处理 (P0-P1)
- [ ] 2.1 TXT文件解析器
- [ ] 2.2 DOCX文件解析器
- [ ] 2.3 EPUB/MOBI解析器
- [ ] 2.4 自动章节识别
- [ ] 2.5 编码自动检测

### Phase 3: LLM集成 (P0-P1)
- [ ] 3.1 LLM统一接口设计
- [ ] 3.2 OpenAI兼容API实现
- [ ] 3.3 各官方API适配器
- [ ] 3.4 API密钥管理与存储
- [ ] 3.5 调用限流与重试机制

### Phase 4: AI分析引擎 (P0-P2)
- [ ] 4.1 人物识别与提取
- [ ] 4.2 关系类型分析
- [ ] 4.3 情节线索追踪
- [ ] 4.4 章节摘要生成
- [ ] 4.5 增量分析支持

### Phase 5: 图谱可视化 (P0-P1)
- [ ] 5.1 Neo4j图谱存储
- [ ] 5.2 ECharts关系图组件
- [ ] 5.3 交互式缩放/过滤
- [ ] 5.4 时间线可视化
- [ ] 5.5 统计图表面板

### Phase 6: 完善与优化 (P0-P2)
- [ ] 6.1 设置界面完善
- [ ] 6.2 数据导出功能
- [ ] 6.3 错误处理与日志
- [ ] 6.4 性能优化
- [ ] 6.5 打包与分发

## 七、API 设计

### 小说管理
```
POST   /api/novels/import           # 导入小说
GET    /api/novels                   # 获取小说列表
GET    /api/novels/{id}              # 获取小说详情
DELETE /api/novels/{id}              # 删除小说
GET    /api/novels/{id}/chapters     # 获取章节列表
```

### 分析相关
```
POST   /api/analysis/start           # 开始分析
GET    /api/analysis/{id}/status     # 获取分析状态
GET    /api/analysis/{id}/result     # 获取分析结果
POST   /api/analysis/{id}/cancel     # 取消分析
```

### 人物与关系
```
GET    /api/characters               # 获取所有人物
GET    /api/characters/{id}          # 人物详情
GET    /api/relationships            # 获取所有关系
GET    /api/graph/{novel_id}         # 获取关系图数据
```

### 设置
```
GET    /api/settings                 # 获取设置
PUT    /api/settings                 # 更新设置
POST   /api/settings/llm/test        # 测试LLM连接
```

## 八、数据模型

### SQLite 表结构

```sql
-- 小说表
CREATE TABLE novels (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_status TEXT DEFAULT 'pending',
    total_chapters INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0
);

-- 章节表
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    chapter_num INTEGER NOT NULL,
    title TEXT,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    summary TEXT,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

-- 人物表
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    name TEXT NOT NULL,
    aliases TEXT,           -- JSON数组
    description TEXT,
    personality TEXT,
    first_appearance INTEGER,
    importance_score REAL DEFAULT 0.5,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

-- 设置表
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分析任务表
CREATE TABLE analysis_tasks (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress REAL DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);
```

### Neo4j 图模型

```cypher
// 人物节点
(:Character {
    id: string,
    name: string,
    novel_id: string,
    importance: float,
    description: string
})

// 关系边
(:Character)-[:RELATIONSHIP {
    type: string,        // family/friend/enemy/lover/colleague/other
    subtype: string,     // 具体关系类型
    strength: float,     // 关系强度 0-1
    first_chapter: int,  // 首次互动章节
    description: string,
    events: list         // 相关事件
}]->(:Character)

// 事件节点
(:Event {
    id: string,
    novel_id: string,
    chapter: int,
    description: string,
    importance: float
})

// 人物参与事件
(:Character)-[:PARTICIPATES_IN {
    role: string         // 主角/配角/旁观者
}]->(:Event)
```

## 九、环境变量配置

```env
# LLM API 配置
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google Gemini
GOOGLE_API_KEY=your_google_api_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 阿里百炼 (Qwen)
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 智谱AI
ZHIPU_API_KEY=your_zhipu_api_key

# 百度文心
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key

# 自定义 OpenAI 兼容端点
CUSTOM_API_KEY=your_custom_api_key
CUSTOM_BASE_URL=your_custom_base_url
CUSTOM_MODEL_NAME=your_model_name

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# 应用配置
APP_PORT=5001
APP_DEBUG=false
```

## 十、开发命令

```bash
# 安装依赖
npm run setup:all          # 一键安装所有依赖

# 开发模式
npm run dev                # 同时启动前后端
npm run dev:electron       # 仅启动Electron+前端
npm run dev:backend        # 仅启动后端

# 构建打包
npm run build              # 构建前端
npm run build:electron     # 打包Electron应用

# 后端单独操作
cd backend
uv run python main.py      # 运行后端
uv run pytest              # 运行测试
```

---

## 十一、开发实施情况

### 已实现功能模块

#### ✅ 基础架构
- [x] Electron + Vue 3 + TypeScript 项目框架
- [x] FastAPI 后端服务
- [x] IPC 通信机制（Electron主进程 ↔ 渲染进程 ↔ Python后端）
- [x] 自动启动/管理Python后端进程
- [x] SQLite 数据库集成

#### ✅ 前端功能
- [x] Vue Router 路由系统
- [x] Pinia 状态管理（novel、analysis、settings stores）
- [x] Element Plus UI 组件库集成
- [x] 自动导入（unplugin-auto-import + unplugin-vue-components）
- [x] 响应式布局与主题
- [x] 文件拖拽上传组件
- [x] ECharts 关系图可视化
- [x] 人物详情抽屉
- [x] 分析进度实时显示
- [x] 导出功能（JSON、CSV、Markdown）

#### ✅ 后端功能
- [x] 小说导入 API（支持 TXT、DOCX、EPUB、MOBI）
- [x] 自动章节识别与分割
- [x] 编码自动检测（chardet）
- [x] 多种 LLM 提供商集成：
  - OpenAI
  - Anthropic Claude
  - Google Gemini
  - DeepSeek
  - 阿里百炼（Qwen/DashScope）
  - 智谱 AI（GLM）
  - 百度云（文心）
  - 硅基流动（SiliconCloud）
  - Ollama（本地模型）
  - OpenRouter
  - AiHubMix
  - 自定义 OpenAI 兼容端点
- [x] 人物提取与属性分析
- [x] 人物关系分析
- [x] 关系图谱数据构建
- [x] 分析任务管理（启动、暂停、取消、进度查询）
- [x] 数据导出服务
- [x] 日志系统

#### ✅ 打包与分发
- [x] Vite 构建配置
- [x] Electron Builder 打包配置
- [x] PyInstaller 后端打包（novelmind.exe）
- [x] Inno Setup 安装程序配置
- [x] GitHub Actions 自动发布流程
- [x] 版本管理与标签同步

### 当前版本信息
- **应用版本**: v0.1.0
- **Electron**: 28+
- **Vue**: 3.4+
- **FastAPI**: 0.109+
- **Python**: 3.12+

### 技术亮点

1. **统一的 LLM 接口层**
   - 支持 12+ 种 LLM 提供商
   - 自动重试与错误处理
   - 流式响应支持
   - API 密钥安全存储

2. **高性能文件解析**
   - 多格式支持（TXT、DOCX、EPUB、MOBI）
   - 智能章节识别
   - 编码自动检测
   - 大文件分块处理

3. **实时分析进度**
   - WebSocket 实时通信
   - 任务队列管理
   - 可暂停/取消的分析流程

4. **灵活的可视化**
   - ECharts 力导向关系图
   - 交互式过滤与搜索
   - 人物重要度可视化
   - 关系强度热力图

5. **完整的打包方案**
   - 单文件后端可执行程序
   - 一键安装的 Windows 安装程序
   - 自动化 GitHub Release 发布

### 待优化项

- [ ] Neo4j 集成（当前使用 SQLite 存储关系数据）
- [ ] 时间线视图（设计已规划，未实现）
- [ ] 增量分析（当前为全量分析）
- [ ] 多语言支持（当前仅中文）
- [ ] 性能优化（大规模小说处理）
- [ ] 单元测试覆盖

### 项目规范

#### 代码规范
- **前端**: TypeScript + ESLint + Prettier
- **后端**: Python 3.12+ + Type Hints
- **提交信息**: Conventional Commits 规范

#### 分支管理
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `fix/*`: 修复分支

#### 发布流程
1. 更新 `package.json` 版本号
2. 提交代码并创建 Git 标签（如 `v0.1.0`）
3. 推送标签触发 GitHub Actions
4. 自动构建并发布到 GitHub Releases

---

**创建时间**: 2026-01-27  
**最后更新**: 2026-01-30  
**版本**: 1.2.0  
**作者**: rinchao  
**维护者**: AI 辅助维护

