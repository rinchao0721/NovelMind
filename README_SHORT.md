# NovelMind

<div align="center">

**AI-Powered Novel Plot Analysis and Character Relationship Visualization**

A desktop application built with Electron + Vue 3 + Python that uses Large Language Models to automatically analyze novel structures, extract character relationships, and present them in beautiful visualizations.

[English](#english) | [中文](#中文)

</div>

---

## English

### ✨ Features

- **AI Character Extraction** - Automatically identify all characters including aliases, personalities, and descriptions
- **Relationship Analysis** - Analyze relationships between characters (family, friends, enemies, lovers, etc.)
- **Plot Tracking** - Extract key plot events, turning points, and foreshadowing
- **Interactive Graph** - Force-directed relationship network visualization
- **Multi-Format Support** - TXT, DOCX, EPUB, MOBI
- **Multiple LLM Providers** - OpenAI, Claude, Gemini, DeepSeek, Qwen, Zhipu, Baidu, Custom APIs
- **Data Export** - JSON and Markdown formats
- **Cross-Platform** - Windows, macOS, Linux

### 🚀 Quick Start

#### Requirements

- Node.js 18+
- Python 3.11 or 3.12
- uv (Python package manager)

#### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/novelmind.git
cd novelmind

# Install all dependencies
npm run setup

# Start the application
npm run dev
```

#### Configure API Keys

Open the application and go to Settings to configure your LLM API keys. At least one provider must be configured.

### 📖 Usage

1. **Import Novel** - Click "Import Novel" and select a file (TXT/DOCX/EPUB/MOBI)
2. **Start Analysis** - Go to "Plot Analysis", select novel, configure options, and click "Start Analysis"
3. **View Results** - Explore relationship graphs, character lists, and timeline
4. **Export Data** - Export results as JSON or Markdown

### 🛠️ Tech Stack

**Frontend**: Electron 28, Vue 3, TypeScript, Element Plus, ECharts, Pinia

**Backend**: Python 3.11-3.12, FastAPI, SQLite, Neo4j (optional)

**AI**: OpenAI, Claude, Gemini, DeepSeek, Qwen, Zhipu, Baidu

### 📦 Build

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

### 📄 License

MIT License

---

## 中文

### ✨ 功能特性

- **AI 人物提取** - 自动识别小说中的所有角色，包括别名、性格、描述
- **关系分析** - 分析人物之间的关系类型（亲属、朋友、敌对、恋人等）
- **情节追踪** - 提取关键剧情事件、转折点、伏笔
- **交互图谱** - 力导向关系网络可视化
- **多格式支持** - TXT、DOCX、EPUB、MOBI
- **多 LLM 提供商** - OpenAI、Claude、Gemini、DeepSeek、Qwen、智谱、百度、自定义 API
- **数据导出** - JSON 和 Markdown 格式
- **跨平台** - Windows、macOS、Linux

### 🚀 快速开始

#### 环境要求

- Node.js 18+
- Python 3.11 或 3.12
- uv（Python 包管理器）

#### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/your-username/novelmind.git
cd novelmind

# 安装所有依赖
npm run setup

# 启动应用
npm run dev
```

#### 配置 API 密钥

打开应用，进入设置页面配置您的 LLM API 密钥。至少需要配置一个提供商。

### 📖 使用指南

1. **导入小说** - 点击"导入小说"并选择文件（TXT/DOCX/EPUB/MOBI）
2. **开始分析** - 进入"剧情分析"，选择小说，配置选项，点击"开始分析"
3. **查看结果** - 浏览关系图谱、人物列表、时间线
4. **导出数据** - 将结果导出为 JSON 或 Markdown

### 🛠️ 技术栈

**前端**: Electron 28、Vue 3、TypeScript、Element Plus、ECharts、Pinia

**后端**: Python 3.11-3.12、FastAPI、SQLite、Neo4j（可选）

**AI**: OpenAI、Claude、Gemini、DeepSeek、Qwen、智谱、百度

### 📦 构建

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

### 📄 开源协议

MIT License

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️ Star！**

**If this project helps you, please give us a ⭐️ Star!**

Made with ❤️ by NovelMind Team

</div>
