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

```
novelmind/
├── electron/                    # Electron 主进程
│   ├── main.ts                  # 主进程入口
│   ├── preload.ts               # 预加载脚本
│   └── ipc/                     # IPC 通信处理
│       ├── index.ts
│       ├── file-handler.ts      # 文件操作
│       └── backend-manager.ts   # 后端进程管理
├── src/                         # Vue 前端源码
│   ├── main.ts                  # 前端入口
│   ├── App.vue
│   ├── router/                  # 路由配置
│   ├── stores/                  # Pinia 状态管理
│   │   ├── novel.ts             # 小说数据状态
│   │   ├── analysis.ts          # 分析结果状态
│   │   └── settings.ts          # 设置状态
│   ├── views/                   # 页面视图
│   │   ├── HomeView.vue         # 首页/导入
│   │   ├── AnalysisView.vue     # 分析面板
│   │   ├── GraphView.vue        # 关系图谱
│   │   ├── TimelineView.vue     # 时间线
│   │   ├── CharacterView.vue    # 人物详情
│   │   └── SettingsView.vue     # 设置页面
│   ├── components/              # 可复用组件
│   │   ├── common/              # 通用组件
│   │   ├── graph/               # 图谱相关组件
│   │   ├── analysis/            # 分析相关组件
│   │   └── import/              # 导入相关组件
│   ├── composables/             # 组合式函数
│   ├── api/                     # API 调用封装
│   ├── types/                   # TypeScript 类型定义
│   └── assets/                  # 静态资源
├── backend/                     # Python 后端
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 配置管理
│   ├── api/                     # API 路由
│   │   ├── __init__.py
│   │   ├── novels.py            # 小说管理API
│   │   ├── analysis.py          # 分析API
│   │   ├── characters.py        # 人物API
│   │   └── settings.py          # 设置API
│   ├── services/                # 业务逻辑
│   │   ├── __init__.py
│   │   ├── file_parser.py       # 文件解析服务
│   │   ├── llm_service.py       # LLM 调用服务
│   │   ├── analysis_engine.py   # AI分析引擎
│   │   └── graph_builder.py     # 图谱构建服务
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── novel.py
│   │   ├── character.py
│   │   ├── relationship.py
│   │   └── chapter.py
│   ├── llm/                     # LLM 提供商
│   │   ├── __init__.py
│   │   ├── base.py              # 基类接口
│   │   ├── openai_provider.py
│   │   ├── claude_provider.py
│   │   ├── gemini_provider.py
│   │   ├── deepseek_provider.py
│   │   ├── qwen_provider.py
│   │   ├── zhipu_provider.py
│   │   └── custom_provider.py
│   ├── prompts/                 # AI 提示词模板
│   │   ├── character_extraction.py
│   │   ├── relationship_analysis.py
│   │   ├── plot_analysis.py
│   │   └── summary_generation.py
│   ├── database/                # 数据库
│   │   ├── __init__.py
│   │   ├── sqlite_db.py         # SQLite 操作
│   │   └── neo4j_db.py          # Neo4j 操作
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── text_utils.py
│       └── encoding_utils.py
├── resources/                   # 应用资源
│   └── icons/                   # 应用图标
├── scripts/                     # 构建脚本
│   ├── setup.ps1                # Windows安装脚本
│   └── build.ps1                # Windows打包脚本
├── package.json                 # 前端依赖
├── pyproject.toml               # 后端依赖
├── electron-builder.json        # 打包配置
├── vite.config.ts               # Vite 配置
├── tsconfig.json                # TS 配置
├── .env.example                 # 环境变量示例
├── PROJECT_PLAN.md              # 项目计划文档
└── README.md                    # 项目说明
```

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

**创建时间**: 2026-01-27  
**版本**: 1.0.0  
**作者**: rinchao

