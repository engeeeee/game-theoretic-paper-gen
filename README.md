# Academic Paper Generator | 学术论文生成器

Game-Theoretic Multi-Agent System for Academic Paper Generation & Verification

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg)
![AI Providers](https://img.shields.io/badge/AI%20Providers-8-orange.svg)

[English](#english) | [中文](#中文)

---

## English

A reproducible academic paper generation and verification system powered by game-theoretic multi-agent AI architecture.

### Project Goals

This project provides an intelligent academic writing assistant that:

- Generates complete academic papers with proper structure (Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References)
- Verifies academic claims through adversarial debate between AI agents
- Supports 8 major AI providers with automatic model detection
- Offers both GUI and CLI interfaces for flexible usage
- Exports papers to Markdown and Word (.docx) formats

### Features

**Paper Generation**
- Smart mode with LLM-powered full paper generation
- Template-based writing with customizable structure
- Support for multiple citation formats (APA, MLA, Chicago, IEEE)
- Automatic reference generation and formatting

**Verification Mode**
- Adversarial debate between Proponent and Reviewer agents
- Confidence scoring for academic claims
- Detailed verification reports with evidence analysis
- Iterative refinement through multi-round debates

**Premium GUI**
- Modern interface with frosted glass effect
- Windows acrylic blur support
- Real-time generation progress tracking
- Customizable theme and opacity settings

**Multi-Provider Support**
- 8 AI service providers integrated
- Automatic model detection via API
- Flexible agent configuration (different providers for each agent)
- Fallback mechanisms for API failures

### Supported AI Providers

| Provider | Latest Models | API Endpoint |
|----------|--------------|--------------|
| **OpenAI** | GPT-5.1, GPT-5, O4-mini, O3, GPT-4o | api.openai.com |
| **Google Gemini** | Gemini 3.0, Gemini 2.5, Gemini 2.0, Gemini 1.5 | generativelanguage.googleapis.com |
| **Anthropic Claude** | Claude Opus 4.5, Claude Sonnet 4.5, Claude 3.5 | api.anthropic.com |
| **DeepSeek** | DeepSeek V3.2, DeepSeek R1, DeepSeek Coder | api.deepseek.com |
| **XAI (Grok)** | Grok 4.1, Grok 4, Grok 3, Grok 2 | api.x.ai |
| **Moonshot (Kimi)** | Kimi K2, moonshot-v1-128k/32k/8k | api.moonshot.cn |
| **Zhipu** | GLM-4.6, GLM-4-plus, GLM-4-flash | open.bigmodel.cn |
| **Qwen** | Qwen3-max, Qwen2.5-max, Qwen-coder-turbo | dashscope.aliyuncs.com |

Click the **Detect** button in the GUI to automatically discover available models for your API key.

### Quick Start

**Using Standalone EXE (Windows)**

No installation required - just run the executable:

```bash
dist\AcademicPaperGenerator.exe
```

**From Source**

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI application
python gui_app.py

# Run CLI
python main.py smart "Write a paper about AI in healthcare"
```

### Usage Guide

**Step 1: Configure API Keys**

Open the **Settings** tab and:
1. Select an AI provider from the dropdown
2. Enter your API key
3. Click **Detect** to load available models
4. Select your preferred model

**Step 2: Select Operating Mode**

| Mode | Description |
|------|-------------|
| **Smart** | Generate complete papers using LLM |
| **Write** | Template-based paper generation |
| **Verify** | Verify academic claims through adversarial debate |

**Step 3: Enter Requirements**

Provide your paper requirements in natural language:

```
Write a 3000-word essay on climate change using APA format
Analyze the impact of artificial intelligence on modern education
Research the applications of blockchain technology in healthcare
```

**Step 4: Generate and Export**

1. Click the **Generate** button
2. Monitor real-time progress in the output panel
3. Review the generated content
4. Export to Markdown or Word format

### CLI Usage

```bash
# Smart mode - full paper generation
python main.py smart "Write a 5000-word paper on AI ethics"

# Verify mode - claim verification
python main.py verify "Is quantum computing viable for cryptography?" --paper

# Write mode - template-based writing
python main.py write "Research paper on climate change, APA format"

# View configuration
python main.py config
```

### Configuration

Create a `.env` file based on `.env.example`:

```env
# Agent A Configuration
AGENT_A_PROVIDER=openai
AGENT_A_API_KEY=sk-xxxxxxxxxxxxx
AGENT_A_MODEL=gpt-4o

# Agent B Configuration
AGENT_B_PROVIDER=google
AGENT_B_API_KEY=AIzaxxxxxxxxxxxxx
AGENT_B_MODEL=gemini-2.0-flash

# Debate Settings
MAX_DEBATE_ROUNDS=5
QUALITY_THRESHOLD=80
```

### Project Structure

```
game_theoretic_agents/
├── gui_app.py                       # GUI Application
├── main.py                          # CLI Entry Point
├── dist/
│   └── AcademicPaperGenerator.exe   # Standalone EXE
├── src/
│   ├── agents/                      # AI Agents
│   ├── input/                       # Requirements Parser
│   ├── output/                      # Paper Generator
│   ├── engine/                      # Debate Engine
│   └── citation_moat/               # Citation Verification
└── output/                          # Generated Papers
```

### System Requirements

- **OS**: Windows 10/11 (for EXE with acrylic blur effect)
- **Python**: 3.10+ (for source installation)
- **API Key**: At least one key from supported providers

### Building from Source

To build the standalone EXE:

```bash
pip install pyinstaller
pyinstaller gui_app.spec --noconfirm
```

Output will be in `dist/AcademicPaperGenerator.exe`

### License

MIT License - See [LICENSE](LICENSE) file for details.

### Author

Created by **Enge1337**

---

## 中文

基于博弈论多智能体架构的学术论文生成与验证系统。

### 项目目标

本项目提供智能学术写作助手，功能包括：

- 生成结构完整的学术论文（摘要、引言、文献综述、方法论、结果、讨论、结论、参考文献）
- 通过 AI 智能体对抗辩论验证学术观点
- 支持 8 大主流 AI 服务商，自动检测可用模型
- 提供图形界面和命令行两种使用方式
- 导出为 Markdown 和 Word (.docx) 格式

### 功能特点

**论文生成**
- 基于大语言模型的智能生成模式
- 可自定义结构的模板化写作
- 支持多种引用格式（APA、MLA、Chicago、IEEE）
- 自动生成和格式化参考文献

**验证模式**
- 提议者与评审者智能体对抗辩论
- 学术观点置信度评分
- 详细验证报告及证据分析
- 多轮辩论迭代优化

**高级图形界面**
- 现代化磨砂玻璃效果界面
- Windows 亚克力模糊特效支持
- 实时生成进度追踪
- 可自定义主题和透明度

**多服务商支持**
- 集成 8 家 AI 服务提供商
- 通过 API 自动检测模型
- 灵活配置智能体（每个智能体可使用不同服务商）
- API 失败时的降级机制

### 支持的 AI 服务商

| 服务商 | 最新模型 | API 端点 |
|--------|---------|----------|
| **OpenAI** | GPT-5.1, GPT-5, O4-mini, O3, GPT-4o | api.openai.com |
| **Google Gemini** | Gemini 3.0, Gemini 2.5, Gemini 2.0, Gemini 1.5 | generativelanguage.googleapis.com |
| **Anthropic Claude** | Claude Opus 4.5, Claude Sonnet 4.5, Claude 3.5 | api.anthropic.com |
| **DeepSeek** | DeepSeek V3.2, DeepSeek R1, DeepSeek Coder | api.deepseek.com |
| **XAI (Grok)** | Grok 4.1, Grok 4, Grok 3, Grok 2 | api.x.ai |
| **Moonshot (Kimi)** | Kimi K2, moonshot-v1-128k/32k/8k | api.moonshot.cn |
| **Zhipu（智谱）** | GLM-4.6, GLM-4-plus, GLM-4-flash | open.bigmodel.cn |
| **Qwen（通义）** | Qwen3-max, Qwen2.5-max, Qwen-coder-turbo | dashscope.aliyuncs.com |

在图形界面中点击 **Detect** 按钮可自动检测您的 API 密钥可用的模型。

### 快速开始

**使用独立可执行文件（Windows）**

无需安装任何依赖，直接运行：

```bash
dist\AcademicPaperGenerator.exe
```

**从源码运行**

```bash
# 安装依赖
pip install -r requirements.txt

# 运行图形界面
python gui_app.py

# 运行命令行
python main.py smart "写一篇关于医疗AI的论文"
```

### 使用指南

**步骤 1：配置 API 密钥**

打开 **Settings** 标签页：
1. 从下拉菜单中选择 AI 服务商
2. 输入您的 API 密钥
3. 点击 **Detect** 按钮加载可用模型
4. 选择您偏好的模型

**步骤 2：选择运行模式**

| 模式 | 描述 |
|------|------|
| **Smart** | 使用 LLM 生成完整论文 |
| **Write** | 基于模板的论文生成 |
| **Verify** | 通过对抗辩论验证学术观点 |

**步骤 3：输入需求**

用自然语言描述您的论文需求：

```
写一篇关于气候变化的3000字论文，使用APA引用格式
分析人工智能对现代教育的影响
研究区块链技术在医疗健康领域的应用
```

**步骤 4：生成并导出**

1. 点击 **Generate** 按钮
2. 在输出面板中监控实时进度
3. 查看生成的内容
4. 导出为 Markdown 或 Word 格式

### 命令行使用

```bash
# 智能模式 - 完整论文生成
python main.py smart "写一篇5000字的人工智能伦理论文"

# 验证模式 - 观点验证
python main.py verify "量子计算在密码学中是否可行？" --paper

# 写作模式 - 基于模板写作
python main.py write "关于气候变化的研究论文，APA格式"

# 查看配置
python main.py config
```

### 配置说明

基于 `.env.example` 创建 `.env` 文件：

```env
# 智能体 A 配置
AGENT_A_PROVIDER=openai
AGENT_A_API_KEY=sk-xxxxxxxxxxxxx
AGENT_A_MODEL=gpt-4o

# 智能体 B 配置
AGENT_B_PROVIDER=google
AGENT_B_API_KEY=AIzaxxxxxxxxxxxxx
AGENT_B_MODEL=gemini-2.0-flash

# 辩论设置
MAX_DEBATE_ROUNDS=5
QUALITY_THRESHOLD=80
```

### 项目结构

```
game_theoretic_agents/
├── gui_app.py                       # 图形界面应用
├── main.py                          # 命令行入口
├── dist/
│   └── AcademicPaperGenerator.exe   # 独立可执行文件
├── src/
│   ├── agents/                      # AI 智能体
│   ├── input/                       # 需求解析器
│   ├── output/                      # 论文生成器
│   ├── engine/                      # 辩论引擎
│   └── citation_moat/               # 引用验证
└── output/                          # 生成的论文
```

### 系统要求

- **操作系统**：Windows 10/11（可执行文件需要亚克力模糊效果支持）
- **Python**：3.10+（源码安装需要）
- **API 密钥**：至少一个支持的服务商的密钥

### 从源码构建

构建独立可执行文件：

```bash
pip install pyinstaller
pyinstaller gui_app.spec --noconfirm
```

输出文件位于 `dist/AcademicPaperGenerator.exe`

### 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 作者

由 **Enge1337** 创建

---

> **Note**: The standalone EXE is fully self-contained - no Python installation required!
> 
> **注意**：独立可执行文件完全自包含，无需安装 Python！
