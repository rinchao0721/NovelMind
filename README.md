# NovelMind

<div align="center">

**AI-powered novel analysis and character relationship visualization tool**
**AI 驱动的小说剧情分析与人物关系可视化工具**

[![License](https://img.shields.io/github/license/rinchao0721/NovelMind)](LICENSE)
[![Release](https://img.shields.io/github/v/release/rinchao0721/NovelMind)](https://github.com/rinchao0721/NovelMind/releases)

一款基于 Electron + Vue 3 + Python 的桌面应用，使用大语言模型自动分析小说结构、提取人物关系，并以精美图谱呈现。

[Quick Start](#🚀-quick-start) • [Features](#✨-features) • [Tech Stack](#🛠️-tech-stack)

</div>

---

## ✨ Features

- **🤖 AI Extraction**: Automatically identify characters, aliases, personalities, and plot points.
- **📊 Interactive Graph**: Visualize relationship networks with force-directed graphs.
- **📖 Multi-Format**: Support for `.txt`, `.docx`, `.epub`, and `.mobi`.
- **🔌 Multi-LLM**: Integration with OpenAI, Claude, Gemini, DeepSeek, Qwen, Zhipu, and Baidu.
- **🔒 Privacy First**: Local storage with encrypted API key management.
- **📤 Export**: Export results to JSON, Markdown, or high-res PNG.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js**: 18.x or higher
- **Python**: 3.11 or 3.12
- **uv**: (Recommended) Fast Python package manager

### Installation & Run
```bash
# 1. Clone the repository
git clone https://github.com/rinchao0721/NovelMind.git
cd NovelMind

# 2. Install dependencies (Automated)
npm run setup

# 3. Start development mode
npm run dev
```
*App will launch at `http://localhost:3000` (Frontend) and `http://localhost:5001` (Backend).*

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Desktop** | Electron 28 |
| **Frontend**| Vue 3, TypeScript, Vite, Element Plus, Pinia |
| **Data Viz**| ECharts 5.5 |
| **Backend** | FastAPI, SQLite, Neo4j (Optional) |
| **Security**| AES-256 Encryption |

---

## 📦 Build & Release

```bash
# Build for Windows
npm run build:win

# Build for macOS
npm run build:mac
```

---

## 📄 License & Credits

- Licensed under **MIT**.
- Inspired by [MiroFish](https://github.com/666ghj/MiroFish).

---
