# NovelMind

<div align="center">

**AI 驱动的小说剧情分析与人物关系可视化工具**

[![License](https://img.shields.io/github/license/rinchao0721/NovelMind)](LICENSE)
[![Release](https://img.shields.io/github/v/release/rinchao0721/NovelMind)](https://github.com/rinchao0721/NovelMind/releases)

一款基于 Electron + Vue 3 + Python 的桌面应用，使用大语言模型自动分析小说结构、提取人物关系，并以精美图谱呈现。

[快速开始](#-快速开始) • [功能特性](#-功能特性)

</div>

---

## ✨ 功能特性

- **🤖 AI 智能提取**：自动识别小说中的角色、别名、性格特征及关键剧情点。
- **📊 交互式图谱**：使用力导向图可视化人物关系网络，支持拖拽和缩放。
- **📖 多格式支持**：支持导入 `.txt`、`.docx`、`.epub` 和 `.mobi` 格式文件。
- **🔌 多模型集成**：支持 OpenAI、Claude、Gemini、DeepSeek、阿里百炼(Qwen)、智谱 AI 和百度文心。
- **🔒 隐私优先**：数据本地存储，API 密钥加密保存，保护您的隐私。
- **📤 数据导出**：支持将分析结果导出为 JSON、Markdown 文档或高清 PNG 图片。

---

## 🚀 快速开始

### 环境要求
- **Node.js**: 18.x 或更高版本
- **Python**: 3.11 或 3.12
- **uv**: (推荐) 快速 Python 包管理器

### 安装与运行
```bash
# 1. 克隆仓库
git clone https://github.com/rinchao0721/NovelMind.git
cd NovelMind

# 2. 安装依赖 (自动安装前后端依赖)
npm run setup

# 3. 启动开发模式
npm run dev
```
*应用将自动启动，前端运行在 `http://localhost:3000`，后端运行在 `http://localhost:5001`。*

## 📦 打包

```bash
# 构建 Windows 安装包
npm run build:win

# 构建 macOS 安装包
npm run build:mac
```

- 本项目采用 **MIT** 许可证。
