# 🎓 Academic Paper Generator | 学术论文生成器

**Game-Theoretic Multi-Agent System for Academic Paper Generation & Verification**

**基于博弈论多智能体系统的学术论文生成与验证工具**

---

## ✨ Features | 功能特点

### 📝 Paper Generation | 论文生成
- **Smart Mode**: LLM-powered full paper generation with proper structure (Title, Abstract, Introduction, Body, Conclusion, References)
- **智能模式**：基于大语言模型生成完整论文（标题、摘要、引言、正文、结论、参考文献）

### 🔍 Verification Mode | 验证模式
- Adversarial debate between two AI agents (Proponent vs Reviewer)
- 双智能体对抗辩论验证学术观点（提议者 vs 评审者）

### 🌫️ Premium GUI | 高级图形界面
- Gray frosted glass effect with Windows acrylic blur
- 灰色磨砂玻璃效果，Windows 亚克力模糊特效

### 📄 Export | 导出功能
- Export papers to Markdown and Word (.docx)
- 支持导出为 Markdown 和 Word 文档

---

## 🚀 Quick Start | 快速开始

### Standalone EXE | 独立可执行文件

**Just run the exe - no installation required!**

**直接运行 exe 文件，无需安装任何依赖！**

```
dist\AcademicPaperGenerator.exe
```

### From Source | 从源码运行

```bash
# Install dependencies | 安装依赖
pip install -r requirements.txt

# Run GUI | 运行图形界面
python gui_app.py
```

---

## 🤖 Supported AI Providers (8 Providers) | 支持的 AI 服务商（8家）

| Provider | Models | API Endpoint |
|----------|--------|--------------|
| **OpenAI** | GPT-5.1, GPT-5, O4-mini, O3, GPT-4o, GPT-4-turbo | api.openai.com |
| **Google Gemini** | Gemini 3.0, Gemini 2.5, Gemini 2.0, Gemini 1.5 | generativelanguage.googleapis.com |
| **Anthropic Claude** | Claude Opus 4.5, Claude Sonnet 4.5, Claude 3.5 | api.anthropic.com |
| **DeepSeek** | DeepSeek V3.2, DeepSeek R1, DeepSeek Coder | api.deepseek.com |
| **XAI (Grok)** | Grok 4.1, Grok 4, Grok 3, Grok 2 | api.x.ai |
| **Moonshot (Kimi)** | Kimi K2, moonshot-v1-128k/32k/8k | api.moonshot.cn |
| **Zhipu (智谱)** | GLM-4.6, GLM-4-plus, GLM-4-flash, GLM-4-vision | open.bigmodel.cn |
| **Qwen (通义)** | Qwen3-max, Qwen2.5-max, Qwen-coder-turbo | dashscope.aliyuncs.com |

> 💡 Click **Detect** button to auto-discover available models for your API key.
> 
> 💡 点击 **Detect** 按钮自动检测可用模型。

---

## 📖 Usage Guide | 使用指南

### Step 1: Configure API Keys | 配置 API 密钥

Open **Settings** tab and select a provider, then enter your API key.

打开 **Settings** 标签页，选择服务商并输入 API 密钥。

### Step 2: Select Mode | 选择模式

| Mode | Description (EN) | 描述 (中文) |
|------|------------------|-------------|
| **🧠 Smart** | Generate complete papers using LLM | 使用 LLM 生成完整论文 |
| **📝 Write** | Same as Smart - full paper generation | 同 Smart 模式，生成完整论文 |
| **🔍 Verify** | Verify claims through adversarial debate | 通过对抗辩论验证学术观点 |

### Step 3: Enter Requirements | 输入需求

**English Examples:**
```
Write a 3000-word essay on climate change using APA format
Analyze the impact of AI on modern education
```

**中文示例：**
```
写一篇关于人工智能对教育影响的论文，约2000字，使用APA引用格式
我需要一篇关于区块链技术的研究论文，大概5000字
```

### Step 4: Generate & Export | 生成并导出

1. Click **Generate** button | 点击 **Generate** 按钮
2. Wait for LLM to generate content | 等待 LLM 生成内容
3. Click **Export MD** or **Export Word** | 点击导出按钮

---

## 📋 Model List by Provider | 各服务商模型列表

### OpenAI
| Series | Models |
|--------|--------|
| **GPT-5.1** | gpt-5.1, gpt-5.1-thinking, gpt-5.1-pro, gpt-5.1-codex-max |
| **GPT-5** | gpt-5, gpt-5-chat, gpt-5-mini |
| **O-Series** | o4-mini, o3, o3-mini, o3-pro, o1, o1-mini |
| **GPT-4.x** | gpt-4.1, gpt-4.5, gpt-4o, gpt-4-turbo |

### Google Gemini
| Series | Models |
|--------|--------|
| **Gemini 3.0** | gemini-3.0-pro, gemini-3.0-pro-deep-think |
| **Gemini 2.5** | gemini-2.5-pro, gemini-2.5-flash |
| **Gemini 2.0** | gemini-2.0-flash, gemini-2.0-pro-exp |
| **Gemini 1.5** | gemini-1.5-pro, gemini-1.5-flash |

### Anthropic Claude
| Series | Models |
|--------|--------|
| **Claude 4.5** | claude-opus-4.5, claude-sonnet-4.5, claude-haiku-4.5 |
| **Claude 4** | claude-opus-4, claude-sonnet-4 |
| **Claude 3.5** | claude-3-5-sonnet-latest, claude-3-5-haiku-latest |

### DeepSeek
| Type | Models |
|------|--------|
| **V3.2** | deepseek-chat, deepseek-reasoner, deepseek-v3.2-speciale |
| **R1** | deepseek-r1, deepseek-r1-distill |
| **Coder** | deepseek-coder, deepseek-coder-v2 |

### XAI Grok
| Series | Models |
|--------|--------|
| **Grok 4.x** | grok-4.1, grok-4, grok-4-heavy, grok-4-code |
| **Grok 3** | grok-3, grok-3-mini, grok-3-fast |
| **Grok 2** | grok-2, grok-2-latest, grok-beta |

### Moonshot (Kimi)
| Series | Models |
|--------|--------|
| **Kimi K2** | kimi-k2-thinking, kimi-k2-instruct |
| **Moonshot V1** | moonshot-v1-128k, moonshot-v1-32k, moonshot-v1-8k |

### Zhipu (智谱)
| Series | Models |
|--------|--------|
| **GLM-4** | glm-4.6, glm-4-plus, glm-4, glm-4-flash |
| **Multimodal** | glm-4-vision, glm-4-voice |

### Qwen (通义)
| Series | Models |
|--------|--------|
| **Qwen3** | qwen3-max, qwen3-max-thinking, qwen3-plus, qwen3-turbo |
| **Qwen2.5** | qwen2.5-max, qwen-plus, qwen-turbo, qwen2.5-1m |
| **Specialized** | qwen-coder-turbo, qwen-math-turbo, qwen2.5-vl |

---

## 🏗️ Three Operating Modes | 三种运行模式

### 1. Smart / Write Mode | 智能/写作模式
```
Input: "Write a paper about AI in healthcare"
       "写一篇关于医疗AI的论文"

Output: Complete paper with:
        - Title | 标题
        - Abstract | 摘要  
        - Introduction | 引言
        - Literature Review | 文献综述
        - Main Body | 正文
        - Discussion | 讨论
        - Conclusion | 结论
        - References | 参考文献
```

### 2. Verify Mode | 验证模式
```
Input: "Is the methodology in recent AI papers reliable?"
       "最近的AI论文方法论是否可靠？"

Output: Verification Report with:
        - Confidence Score | 置信度分数
        - Verified Claims | 已验证声明
        - Rejected Claims | 被拒绝声明
        - Debate Summary | 辩论摘要
```

---

## 📁 Project Structure | 项目结构

```
game_theoretic_agents/
├── gui_app.py                       # GUI Application | 图形界面
├── main.py                          # CLI Entry Point | 命令行入口
├── dist/
│   └── AcademicPaperGenerator.exe   # Standalone EXE | 独立可执行文件
├── src/
│   ├── agents/                      # AI Agents | AI 智能体
│   ├── input/                       # Requirements Parser | 需求解析
│   ├── output/                      # Paper Generator | 论文生成
│   ├── engine/                      # Debate Engine | 辩论引擎
│   └── citation_moat/               # Citation Verification | 引用验证
└── output/                          # Generated Papers | 生成的论文
```

---

## 💻 CLI Usage | 命令行使用

```bash
# Smart paper generation | 智能论文生成
python main.py smart "Write a 5000-word paper on AI ethics"

# Verification with report | 验证并生成报告
python main.py verify "Is quantum computing viable?" --paper

# Template-based writing | 基于模板写作
python main.py write "Research paper on climate change, APA format"

# View config | 查看配置
python main.py config
```

---

## ⚙️ Configuration | 配置

### Environment Variables | 环境变量 (`.env.example`)

```env
# Agent A Configuration | 智能体 A 配置
AGENT_A_PROVIDER=openai          # openai/google/anthropic/deepseek/xai/moonshot/zhipu/qwen
AGENT_A_API_KEY=sk-xxxxxxxxxxxxx
AGENT_A_MODEL=gpt-4o

# Agent B Configuration | 智能体 B 配置  
AGENT_B_PROVIDER=google
AGENT_B_API_KEY=AIzaxxxxxxxxxxxxx
AGENT_B_MODEL=gemini-2.0-flash

# Debate Settings | 辩论设置
MAX_DEBATE_ROUNDS=5
QUALITY_THRESHOLD=80
```

---

## 📋 System Requirements | 系统要求

- **OS**: Windows 10/11 (for EXE with blur effect)
- **Python**: 3.10+ (for source)
- **API Key**: Any of the 8 supported providers

---

## 🔧 Build EXE | 构建可执行文件

```bash
pip install pyinstaller
pyinstaller gui_app.spec --noconfirm
```

Output: `dist/AcademicPaperGenerator.exe`

---

## 📄 License | 许可证

MIT License - See [LICENSE](LICENSE) file.

---

## 👨‍💻 Author | 作者

Created by **Enge1337**

---

> 🎯 **Note**: The EXE is fully standalone - no Python installation required!
> 
> 🎯 **注意**：EXE 文件完全独立，无需安装 Python！
