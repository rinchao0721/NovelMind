
完整项目结构

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
