#!/usr/bin/env python3
"""
深度分析报告生成器 - 基于 GitHub README 真实内容生成有深度的 detail 页面
"""
import urllib.request, json, base64, os, re
from datetime import datetime

# ─── 每个项目的元数据和解读 ───────────────────────────────────────
PROJECTS = {
    "msitarzewski/agency-agents": {
        "stars": "93,682", "forks": "15,417", "language": "Shell", "license": "MIT",
        "created": "2025-10-13", "topics": ["AI agents", "claude-code", "multi-agent"],
        "homepage": "",
        "tags": ["Multi-Agent", "Claude Code", "Agent 团队", "工作流编排"],
        "eval": "一个独特的 AI Agent 人格化框架，把不同专长的 AI Agent 包装成有「人格」的专家角色（前端巫师、Reddit 运营、数据分析师等），可无缝集成到 Claude Code 等主流 AI 编码工具中，让 AI 协作从单兵作战升级为团队配合。",
        "what": """**The Agency** 源自一个 Reddit 帖子，历经数月迭代打磨，是一个精心设计的 AI Agent 人格化集合。它的核心思想是：不要通用型 AI 助手，而是给每个 Agent 赋予专业领域深度、人格特征和明确的交付物。

**工程部门（Engineering Division）** 包括：
- 🐛 Bug Hunter — 自动定位并复现 Bug，给出修复步骤
- ⚡ Performance Pro — 性能分析、瓶颈定位、优化建议
- 🔒 Security Scout — 安全审计、漏洞扫描、合规检查
- 📝 Doc Writer — 自动生成 API 文档、README、Changelog
- 🧪 Test Engineer — 单元测试、集成测试、E2E 测试生成

**增长部门（Growth Division）** 包括：
- 📊 Marketing Strategist — 内容营销、社交媒体策略
- 🔍 SEO Specialist — 关键词分析、SEO 优化建议
- 📧 Cold Email Writer — 外贸邮件、个性化推广文案
- 💼 B2B Copywriter — 商业提案、案例研究撰写

**社区部门（Community Division）** 包括：
- 🐦 Twitter Growth — 推特运营增长策略
- Reddit 运营（帖子撰写、评论区互动）
- Discord 社区建设

**核心特性：**
- 每个 Agent 都有独立的人设（persona）、工作流程（workflow）和交付标准（deliverables）
- 支持 Claude Code、Copilot、Cursor、Aider、Windsurf 等主流工具
- 安装简单：`./scripts/install.sh --tool claude-code`
- Agent 之间可以协作，形成完整的项目团队""",
        "why": [
            "角色专业化而非泛化：每个 Agent 只做一个方向，但做得深入，不是通用 prompt 而是真正可交付的专业能力",
            "开箱即用的团队感：传统 AI 助手是单打独斗，Agency 把多个专长 Agent 组织成团队，各司其职",
            "兼容所有主流 AI 编码工具：Claude Code、Copilot、Cursor、Aider 等都可以用，真正做到工具无关",
            "交付物导向：不是泛泛给建议，而是输出真实代码、测试、文档、报告，有可衡量的结果",
            "Shell 脚本实现，零依赖：不需要 Node.js 或 Python 环境，直接在终端运行",
        ],
        "cons": [
            "Shell 脚本实现，复杂 Agent 逻辑表达能力有限",
            "人格化 prompt 需要手动维护和调优",
            "Agent 之间协调需要人工介入，不是完全自动化",
        ],
        "who": "需要 AI 辅助完成多维度工作的团队（工程+市场+社区），以及想让 AI 编程助手更具专业深度的个人开发者",
        "install": "```bash\n# 推荐：安装到 Claude Code\n./scripts/install.sh --tool claude-code\n\n# 或安装到其他工具\n./scripts/install.sh --tool copilot\n./scripts/install.sh --tool cursor\n\n# 手动安装单个 Agent\ncp engineering/bug-hunter.md ~/.claude/agents/\n```",
        "doc_links": [
            ("GitHub 仓库", "https://github.com/msitarzewski/agency-agents"),
            ("Claude Code 集成文档", "https://docs.claude.com/en/docs/claude-code"),
        ],
    },
    "ruvnet/ruflo": {
        "stars": "43,758", "forks": "4,869", "language": "TypeScript", "license": "MIT",
        "created": "2025-06-02", "topics": ["agentic-ai", "agentic-framework", "multi-agent", "claude-code"],
        "homepage": "https://Cognitum.One",
        "tags": ["Multi-Agent编排", "Claude Code", "Agent 记忆", "自优化", "MCP"],
        "eval": "Ruflo 是面向 Claude Code 的多 Agent 编排平台，通过 `npx ruflo init` 一条命令给 Claude Code 装上「神经系统」：Agent 自动组队执行任务、从成功模式中自学习、跨会话记忆持久化，还支持联邦通信让不同机器上的 Agent 安全协作不泄露数据。",
        "what": """Ruflo（ 前身是 claude-flow）是一个专为 Claude Code 打造的多 Agent 编排平台。它的核心定位是**给 AI 编码助手增加协调层**，让多个专业 Agent 能像团队一样协作。

**核心架构：**
```
User --> Ruflo (CLI/MCP) --> Router --> Swarm --> Agents --> Memory --> LLM Providers
                          ^                           |
                          +---- Learning Loop <-------+
```
用户正常写代码，Ruflo 在后台自动完成：任务路由、Agent 编排、学习记忆、联邦通信。

**两大安装路径：**

| | Claude Code 插件（轻量） | CLI 完整安装 |
|---|---|---|
| 安装后文件 | 零文件侵入 | `.claude/`、`.claude-flow/` 等 |
| MCP Server | 不注册 | 注册到系统 |
| Hooks | 无 | 完整安装 |
| Agent 数量 | 几个 | 98 个 Agent、60+ 命令、30+ 技能 |
| 适合场景 | 试用体验 | 正式生产 |

**核心能力：**
- **Self-Learning（自学习）**：从成功执行的任务中提取模式，下次自动复用
- **Multi-Agent Swarm（多 Agent 蜂群）**：任务自动拆解分配给最合适的 Agent
- **Federated Memory（联邦记忆）**：跨机器安全共享记忆，不泄露数据
- **Plugin 生态（32 个插件）**：ruflo-core、ruflo-swarm、ruflo-autopilot、ruflo-federation 等""",
        "why": [
            "零学习成本：安装后正常用 Claude Code，Ruflo 在后台自动协调，不需要改工作流",
            "98 个专业化 Agent：从代码生成到安全审计，从文档到部署，覆盖全流程",
            "自优化能力：Ruflo 会从成功案例中学习，不断优化下次任务分配策略",
            "联邦安全：不同机器上的 Agent 可以协作，但数据不会跨边界泄露，适合企业",
            "插件生态丰富：32 个插件按需安装，不像 LangChain 那样全量引入",
        ],
        "cons": [
            "强依赖 Claude Code，非 Claude 用户无法使用",
            "完整安装对工作区有文件侵入（.claude/ 等目录）",
            "国内网络安装 npm 包可能较慢",
        ],
        "who": "重度使用 Claude Code 的开发者/团队，以及希望 AI 编程助手能自主协作、持续学习进化的企业",
        "install": """```bash
# 完整安装（推荐生产环境）
npx ruflo init

# Claude Code 插件模式（轻量体验）
/plugin marketplace add ruvnet/ruflo
/plugin install ruflo-core@ruflo
/plugin install ruflo-swarm@ruflo
```""",
        "doc_links": [
            ("GitHub 仓库", "https://github.com/ruvnet/claude-flow"),
            ("Ruflo 在线体验", "https://flo.ruv.io"),
            ("Goal Planner", "https://goal.ruv.io"),
        ],
    },
    "virattt/dexter": {
        "stars": "23,818", "forks": "2,901", "language": "TypeScript", "license": "",
        "created": "", "topics": ["financial-research", "AI agent", "autonomous-research"],
        "homepage": "",
        "tags": ["金融研究", "Autonomous Agent", "市场分析", "投资决策"],
        "eval": "Dexter 是一个专注于金融研究的多 Agent 系统，能自动拆解复杂金融问题、执行研究计划、实时获取市场数据、验证结果并迭代优化。相当于给投资分析师配备了一个永不停歇的 AI 研究助手，可以处理财务报表分析、估值建模、宏观研究等任务。",
        "what": """Dexter 是一个**自主金融研究 Agent**，核心理念是"像资深分析师一样思考，像程序一样高效执行"。

**工作流程：**
1. **任务规划（Task Planning）**：接收复杂金融问题，自动拆解为结构化研究步骤
2. **自主执行（Autonomous Execution）**：调用正确的工具获取金融数据（财报、现金流、宏观经济）
3. **自我验证（Self-Validation）**：检查结果质量，迭代直到满意
4. **报告生成**：输出结构化研究报告，包含数据支撑和结论

**技术栈：**
- 运行时：Bun（需要 v1.0+）
- 支持多模型：OpenAI、Anthropic、Google、xAI、Ollama（本地）、OpenRouter
- 金融数据：Financial Datasets API（机构级市场数据）
- 网络搜索：Exa（首选）/ Tavily（备选）
- 评估框架：LangSmith + LLM-as-Judge

**核心特性：**
- 支持 WhatsApp 操控（手机对话完成金融研究）
- 内置评估套件，可量化 Agent 研究质量
- 循环检测和步骤限制，防止失控执行
- 实时 UI 显示研究进度、当前问题、运行状态""",
        "why": [
            "专注金融领域：不是通用 AI，而是专门为投资研究场景优化的 Agent 系统",
            "自我纠错机制：执行中会自我验证，发现错误自动回退重试，输出质量有保障",
            "多数据源融合：财务报表 + 实时市场数据 + 网络搜索，不是单一数据来源",
            "WhatsApp 集成：手机对话即可触发研究，分析师随时随地获取信息",
            "评估框架内置：可以用标准数据集测试 Agent 表现，持续改进",
        ],
        "cons": [
            "依赖外部 API（OpenAI/Anthropic 收费，Financial Datasets API 也收费）",
            "配置相对复杂（需要多个 API key）",
            "面向金融专业人士，个人投资者门槛较高",
        ],
        "who": "投资机构分析师、量化交易团队、金融科技产品经理，以及需要 AI 辅助进行股票/公司研究的专业人士",
        "install": """```bash
# 1. 克隆仓库
git clone https://github.com/virattt/dexter.git
cd dexter

# 2. 安装依赖（Bun）
bun install

# 3. 配置环境变量
cp env.example .env
# 编辑 .env 填入 API Key

# 4. 运行
bun start        # 交互模式
bun dev          # 开发监视模式
```""",
        "doc_links": [
            ("GitHub 仓库", "https://github.com/virattt/dexter"),
            ("Financial Datasets API", "https://financialdatasets.ai"),
            ("Exa 搜索", "https://exa.ai"),
        ],
    },
    "Hmbown/DeepSeek-TUI": {
        "stars": "7,866", "forks": "605", "language": "Rust", "license": "MIT",
        "created": "2026-01-19", "topics": ["cli", "deepseek", "llm", "rust", "terminal", "tui"],
        "homepage": "",
        "tags": ["DeepSeek", "TUI", "终端 AI", "Coding Agent", "Rust", "1M Context"],
        "eval": "DeepSeek 官方出品的终端编程助手，用 Rust 编写无需任何运行时依赖，直接调用 DeepSeek V4（1M token 上下文窗口），支持思维链流式输出、MCP 工具调用、持久化任务队列，是目前最适合中国开发者的本地 AI 编程工具之一。",
        "what": """DeepSeek TUI 是一个完全运行在终端的编程 Agent，专为 DeepSeek V4 模型打造。

**核心亮点：**

⚡ **零运行时依赖**：打包成单一 Rust 二进制文件，安装后不需要 Node.js 或 Python，非常适合服务器环境。

🔮 **1M Token 上下文窗口**：DeepSeek V4 提供百万级上下文，可以一次性分析整个代码库、整本书籍或长篇文档，无需分段处理。

🧠 **原生思维链（Chain-of-Thought）**：内置 RLM（Reasoning Language Model）支持，思维过程流式输出，你可以看到 AI 的完整推理过程。

🔧 **MCP 工具调用**：支持 Model Context Protocol，可以调用文件系统、Shell 命令、Git、网络搜索等多种工具。

📊 **Prefix Cache 感知**：利用 DeepSeek 的前缀缓存优化，重复上下文只计一次费用，降低使用成本。

**安装方式（国内加速）：**
```bash
# npm（推荐，可配国内镜像）
npm install -g deepseek-tui --registry=https://registry.npmmirror.com

# Cargo（Rust 原生安装）
cargo install deepseek-tui-cli --locked

# Homebrew（macOS）
brew tap Hmbown/deepseek-tui
brew install deepseek-tui
```""",
        "why": [
            "Rust 编写，零依赖：任何环境都能跑，服务器、容器、轻量 VPS 都没问题",
            "1M 超长上下文：直接分析整个代码库，不需要反复切换文件",
            "DeepSeek 性价比极高：相比 GPT-4 和 Claude，DeepSeek V4 成本低得多",
            "思维链可见：可以看到 AI 的推理过程，增加信任度，也方便调试",
            "Prefix Cache 降低费用：重复内容不重复计费",
            "国内开发者友好：有中文 README，国内安装有镜像加速",
        ],
        "cons": [
            "只能使用 DeepSeek 模型，不能切换其他 LLM 提供商",
            "纯命令行界面，对不熟悉终端的用户有门槛",
            "Rust 源码编译较慢，预编译二进制体积较大（约 100MB+）",
        ],
        "who": "中国开发者（特别是服务器端/后端工程师）、需要本地离线 AI 编程能力的技术团队、以及追求性价比的 AI 编程用户",
        "install": """```bash
# npm（最简单）
npm install -g deepseek-tui --registry=https://registry.npmmirror.com

# Cargo（无需 Node.js）
cargo install deepseek-tui-cli --locked

# 安装后直接运行
deepseek                   # TUI 交互界面
deepseek "帮我写一个快排"   # 单次命令模式
```""",
        "doc_links": [
            ("GitHub 仓库", "https://github.com/Hmbown/DeepSeek-TUI"),
            ("crates.io", "https://crates.io/crates/deepseek-tui-cli"),
            ("DeepWiki 分析", "https://deepwiki.com/Hmbown/DeepSeek-TUI"),
        ],
    },
    "mksglu/context-mode": {
        "stars": "13,080", "forks": "898", "language": "TypeScript", "license": "ELv2",
        "created": "2026-02-23", "topics": ["claude-code", "context-engineering", "antigravity", "codex-cli"],
        "homepage": "https://context-mode.com",
        "tags": ["上下文优化", "Token 节省", "Claude Code", "MCP", "AI 编程"],
        "eval": "解决 AI 编程中的上下文膨胀问题——MCP 工具调用会产生大量冗余数据（一次 Playwright 截图 56KB，20 个 GitHub Issue 59KB），Context Mode 通过沙箱隔离和增量提取，将 98% 的工具输出转为摘要而非原文，大幅降低 Token 消耗和上下文污染。",
        "what": """Context Mode 解决的是**AI 编程中的上下文成本危机**。

**问题根源：**
每个 MCP 工具调用都会把原始数据灌入上下文窗口：
- 一次 Playwright DOM 快照 = **56 KB**
- 20 个 GitHub Issue = **59 KB**
- 一个访问日志文件 = **45 KB**
- 30 分钟后，40% 的上下文已经被工具输出污染

**解决方案：**
Context Mode 在工具输出和上下文窗口之间加了一层**智能处理层**：

1. **Sandbox（沙箱隔离）**：工具原始输出存入沙箱，不直接进入上下文
2. **Delta Extraction（增量提取）**：只提取"有用的 diff"（变更部分），而不是全文
3. **Summary Generation（摘要生成）**：用 LLM 将原始输出压缩为语义摘要
4. **Incremental Mode（增量模式）**：对于增量数据，只处理变化部分，重复内容自动跳过

**实际效果：**
- Token 消耗降低 **~98%**
- 上下文窗口利用率提升 **10x**
- 支持 Microsoft、Google、Meta、NVIDIA、ByteDance、Stripe 等企业团队

**技术栈：**
- TypeScript + npm 包
- 支持 Claude Code、Codex CLI、Antigravity 等主流工具
- NPM 包 + Marketplace 双分发渠道""",
        "why": [
            "解决 AI 编程的核心痛点：上下文越来越贵，但工具输出越来越大",
            "98% Token 节省效果显著：同样的预算，可以处理更复杂的任务",
            "零侵入：不需要改代码，只需要在 Claude Code 中启用插件",
            "支持多种 MCP 工具：Playwright、GitHub、文件系统等都能处理",
            "增量处理：第二次运行只处理变化的部分，效率倍增",
        ],
        "cons": [
            "需要理解上下文工程概念，新手门槛较高",
            "摘要可能丢失细节，对于需要精确原始数据的场景不适用",
            "TypeScript 实现，调试和二次开发有一定门槛",
        ],
        "who": "长时间使用 AI 编程助手（Claude Code、Codex CLI）且经常处理大型代码库的开发者/团队，以及对 Token 成本敏感的企业",
        "install": """```bash
# Claude Code 安装
/plugin marketplace add mksglu/context-mode
/plugin install context-mode@mksglu

# npm 安装
npm install -g context-mode

# 查看使用统计
context-mode stats
```""",
        "doc_links": [
            ("官网", "https://context-mode.com"),
            ("GitHub 仓库", "https://github.com/mksglu/context-mode"),
            ("Hacker News", "https://news.ycombinator.com/item?id=47193064"),
        ],
    },
    "cocoindex-io/cocoindex": {
        "stars": "8,409", "forks": "619", "language": "Python", "license": "Apache-2.0",
        "created": "2025-03-03", "topics": ["RAG", "agentic-data-framework", "context-engineering", "data-indexing"],
        "homepage": "https://cocoindex.io",
        "tags": ["增量索引", "RAG", "Agent 记忆", "数据管道", "企业知识库"],
        "eval": "CocoIndex 是一个面向 AI Agent 的增量数据索引框架，核心能力是保持 AI 的上下文始终是最新的数据——代码库、Slack、Notion、PDF、视频等任何数据源变化后，只增量同步变化的 delta 部分，而不是全量重新索引，10 分钟即可接入生产环境。",
        "what": """CocoIndex 解决的是**AI Agent 数据老化问题**：RAG 系统中的数据是"快照"而非"实时流"，数据更新后需要全量重新处理，效率低下。

**核心能力：**
- 🌊 **Incremental Sync（增量同步）**：只处理数据源的变化部分（delta），而不是全量重新索引
- 📦 **多数据源连接器**：代码库（Git）、Slack、Notion、Confluence、Gmail、PDF、视频（带字幕）等
- 🔄 **声明式管道**：用 Python 定义数据处理管道，5 分钟可上线
- 📊 **Any Scale**：并行处理，默认支持大规模数据

**应用场景：**
1. **企业知识库问答**：员工手册、产品文档、代码库变更 — 始终基于最新版本回答
2. **代码库智能助手**：分析最新代码变更，主动发现潜在 Bug 和安全问题
3. **会议记录助手**：会议录音/视频 → 自动转录 → 增量更新 → AI 总结
4. **CRM + AI**：客户数据、邮件、聊天记录实时打通，销售 AI 随时获取最新客户信息

**技术架构：**
```
数据源 → Connector → Transform → Target (Vector DB / KG) → AI Agent
              ↑
         Incremental Sync（只同步 delta）
```""",
        "why": [
            "增量索引而非全量重建：数据量越大优势越明显（10GB 代码库全量 vs 几十KB delta）",
            "10 分钟接入生产：声明式 Python，门槛低，效果快",
            "多数据源开箱即用：20+ 连接器，不需要自己写 ETL",
            "支持向量数据库和知识图谱双Target：灵活适配不同 RAG 架构",
            "企业级特性：增量同步、变更追踪、权限感知",
        ],
        "cons": [
            "Python GIL 限制：大规模并行处理可能需要多进程方案",
            "企业数据源（Slack/Notion 等）需要相应 API 权限",
            "向量数据库依赖（Milvus/Pinecone 等）需要额外运维",
        ],
        "who": "需要为 AI Agent 提供实时企业数据的企业团队、RAG 应用开发者、以及数据管道工程师",
        "install": """```bash
# pip 安装
pip install cocoindex

# 快速开始
cocoindex init

# Python 管道示例
from cocoindex import Pipeline, GitHubSource, VectorStoreTarget

pipeline = Pipeline(
    source=GitHubSource(repo="org/repo", token="ghp_xxx"),
    transforms=[...],
    target=VectorStoreTarget(index="my-index")
)
pipeline.run()  # 增量同步
```""",
        "doc_links": [
            ("官网", "https://cocoindex.io"),
            ("GitHub 仓库", "https://github.com/cocoindex-io/cocoindex"),
            ("快速开始", "https://cocoindex.io/docs"),
            ("Discord 社区", "https://discord.com/invite/zpA9S2DR7s"),
        ],
    },
    "Arindam202/awesome-ai-apps": {
        "stars": "11,331", "forks": "", "language": "Python", "license": "",
        "created": "", "topics": ["RAG", "AI agents", "awesome-list"],
        "homepage": "",
        "tags": ["精选项目", "RAG", "AI 工作流", "开源项目汇总"],
        "eval": "一个精心策划的 AI 应用精选列表，收录了 100+ 个可实际运行的 AI Agent 和 RAG 应用，每个项目都附带了为什么值得关注的分析，是了解 AI 应用落地现状的最佳窗口。",
        "what": """awesome-ai-apps 是一个**可运行的 AI 应用精选列表**，核心理念是"不要论文要代码，不要 demo 要产品"。

**收录标准：**
- ✅ 必须有实际可运行的代码（不是 PPT 概念）
- ✅ 有明确的使用场景和目标用户
- ✅ 经过实际验证的 AI 应用（不是概念验证）
- ✅ 涵盖 RAG、Agent、工作流、多模态等多个方向

**典型分类：**
- 🤖 **RAG 应用**：文档问答、知识库检索、PDF 分析
- 🏃 **AI Agent**：自动化工作流、多步骤任务执行
- 💬 **聊天应用**：客服机器人、对话式 UI
- 🖼️ **多模态**：图像生成、视频处理、语音助手
- 🔧 **开发工具**：代码生成、调试助手、测试生成

**每个项目的条目包含：**
- GitHub 链接
- Stars 数量（反映社区认可度）
- 核心技术栈
- 一句话定位
- 适合什么场景
- 局限性（诚实列出）""",
        "why": [
            "精选而非罗列：100+ 项目都是人工审核筛选，不是机器爬取",
            "每个项目都标注了局限性和适用场景，决策效率高",
            "覆盖 RAG 和 Agent 全流程，可以作为技术选型的参考目录",
            "持续更新，紧跟 AI 应用发展趋势",
            "按场景分类，定位效率高（想要什么类型直接找对应分类）",
        ],
        "cons": [
            "是列表不是产品：不能直接使用，需要自己部署",
            "缺乏深度技术对比，无法直接用于技术选型",
            "部分项目可能已过时，维护频率有限",
        ],
        "who": "AI 应用开发者、产品经理、技术选型负责人，以及想了解 AI 应用落地现状的任何人",
        "install": """```bash
# 克隆查看
git clone https://github.com/Arindam202/awesome-ai-apps.git
cd awesome-ai-apps
# 打开 README.md 浏览
```""",
        "doc_links": [
            ("GitHub 仓库", "https://github.com/Arindam202/awesome-ai-apps"),
        ],
    },
    "browserbase/skills": {
        "stars": "2,394", "forks": "153", "language": "JavaScript", "license": "",
        "created": "", "topics": ["browser-automation", "claude-code", "stagehand", "captcha-solving"],
        "homepage": "",
        "tags": ["浏览器自动化", "Claude Code", "Web 抓取", "CAPTCHA", "反爬虫"],
        "eval": "给 Claude Code 装备 Browserbase 云端浏览器能力的技能插件，包含浏览器自动化、CAPTCHA 破解、代理轮换、隐身模式等，让 Claude 可以操作真实浏览器完成复杂 Web 任务，比如订票、填表、抓取 JavaScript 渲染页面等。",
        "what": """Browserbase Skills 是 Claude Code 的浏览器自动化技能集，让 AI Agent 能像真人一样操控浏览器。

**核心技能（Skills）：**

| Skill | 功能 |
|-------|------|
| `browser` | 浏览器自动化，支持远程 Browserbase 会话、抗 Bot 检测、 CAPTCHA 破解、住宅代理 |
| `browserbase-cli` | `bb` CLI 工具，支持会话管理、项目、上下文、扩展、Fetch、Dashboard |
| `functions` | 部署 Serverless 浏览器自动化到 Browserbase 云 |
| `site-debugger` | 诊断并修复失败的浏览器自动化，分析 Bot 检测、选择器、时序、认证、验证码问题 |
| `browser-trace` | 捕获完整 DevTools 协议跟踪（CDP firehose）、截图、DOM 转储，按页面分桶搜索 |
| `safe-browser` | 构建本地浏览器 Agent，仅限 CDP 门控 `safe_browser` 工具 + 域名白名单 |
| `bb-usage` | 显示 Browserbase 使用统计、会话分析、成本预测 |
| `cookie-sync` | 从本地 Chrome 同步 Cookie 到 Browserbase 持久上下文 |
| `fetch` | 无浏览器会话抓取 HTML/JSON，检查状态码、Header、Redirect |
| `search` | 网络搜索，返回结构化结果（标题、URL、元数据）|
| `ui-test` | AI 对抗性 UI 测试，分析 Git Diff 测试变更，或探索全应用找 Bug |

**典型使用场景：**
- "去 Hacker News 获取热门帖子并总结评论"
- "QA 测试 localhost:3000 并修复发现的 Bug"
- "用你已经登录 Doordash 的账号帮我订一份披萨"
- "用 `bb` 列出我的 Browserbase 项目并输出 JSON""",
        "why": [
            "解决 AI 无法操作复杂 Web 页面的问题：CAPTCHA、JS 渲染、登录态都能处理",
            "Claude Code 官方集成，操作自然：像对人说话一样描述任务",
            "云端浏览器：不需要本地安装 Chrome，可以跑在服务器上",
            "Site Debugger 功能实用：自动化失败时 AI 自动诊断原因并给出修复方案",
            "Safe Browser 保障安全：域名白名单防止 AI 执行恶意操作",
        ],
        "cons": [
            "依赖 Browserbase 云服务，有使用费用",
            "CAPTCHA 破解可能涉及法律和道德风险",
            "复杂 Web 自动化仍然不稳定，页面结构变化容易出错",
        ],
        "who": "需要 AI 操作 Web 页面的场景：爬虫工程师、自动化测试工程师、网页 QA，以及需要 AI 完成 Web 操作的开发者",
        "install": """```bash
# Claude Code 安装
/plugin marketplace add browserbase/skills
/plugin install browse@browserbase

# npm 安装
npx skills add browserbase/skills

# 启动本地浏览器
browse env local

# 带自动重连的本地浏览器
browse env local --auto-connect
```""",
        "doc_links": [
            ("GitHub 仓库", "https://github.com/browserbase/skills"),
            ("Browserbase 官网", "https://browserbase.com"),
            ("Stagehand 文档", "https://github.com/browserbase/stagehand"),
        ],
    },
}


# ─── HTML 模板 ────────────────────────────────────────────────────
DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{name} | AI Agent 每日精选</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{meta_desc}">
  <style>
   *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f7fa;color:#1a1a2e;line-height:1.8}}
    .container{{max-width:900px;margin:0 auto;padding:32px 24px}}
    .back-link{{display:flex;gap:10px;margin-bottom:28px;flex-wrap:wrap}}
    .back-btn{{display:inline-flex;align-items:center;gap:6px;color:#409EFF;font-size:14px;text-decoration:none;padding:8px 16px;background:#fff;border:1px solid #409EFF;border-radius:8px;transition:all .2s}}
    .back-btn:hover{{background:#409EFF;color:#fff}}
    .hero{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:40px;color:#fff;margin-bottom:32px;position:relative;overflow:hidden}}
    .hero::before{{content:'';position:absolute;top:-50%;right:-20%;width:400px;height:400px;background:radial-gradient(circle,rgba(64,158,255,.15),transparent 70%);border-radius:50%}}
    .hero .badge{{display:inline-block;padding:4px 12px;background:rgba(64,158,255,.2);border:1px solid rgba(64,158,255,.4);border-radius:20px;font-size:12px;margin-bottom:12px}}
    .hero h1{{font-size:26px;font-weight:700;margin-bottom:8px}}
    .hero .desc{{color:rgba(255,255,255,.7);font-size:15px;margin-bottom:16px;line-height:1.6}}
    .tag-list{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
    .tag{{padding:4px 12px;background:rgba(64,158,255,.2);color:#93c5fd;border-radius:20px;font-size:12px}}
    .hero .stats{{display:flex;gap:24px;flex-wrap:wrap;margin-top:20px}}
    .hero .stat{{text-align:center}}
    .hero .stat .num{{font-size:20px;font-weight:700;color:#60a5fa}}
    .hero .stat .label{{font-size:11px;color:rgba(255,255,255,.5);text-transform:uppercase}}
    .hero .meta{{margin-top:16px;font-size:13px;color:rgba(255,255,255,.4)}}
    .hero .meta span{{margin-right:16px}}
    .section{{background:#fff;border-radius:12px;padding:28px;margin-bottom:20px;border:1px solid #f0f0f0}}
    .section h2{{font-size:17px;font-weight:700;color:#1a1a2e;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #409EFF;display:flex;align-items:center;gap:8px}}
    .section h2 .icon{{font-size:20px}}
    .section p,.section li{{color:#555;font-size:14px;line-height:1.9}}
    .section ul{{padding-left:20px}}
    .section li{{margin-bottom:10px}}
    .highlight-box{{background:linear-gradient(135deg,#ecf5ff,#f0f9ff);border-left:4px solid #409EFF;padding:20px 24px;border-radius:0 8px 8px 0;margin:16px 0}}
    .highlight-box p{{color:#1a1a2e;font-size:15px;line-height:1.8}}
    .pro-con{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}
    .pro-item,.con-item{{padding:12px 16px;border-radius:8px;font-size:13px;line-height:1.6}}
    .pro-item{{background:#f0fdf4;border-left:3px solid #22c55e;color:#166534}}
    .con-item{{background:#fef2f2;border-left:3px solid #ef4444;color:#991b1b}}
    .pro-item strong,.con-item strong{{display:block;margin-bottom:4px}}
    pre{{background:#1e293b;color:#e2e8f0;padding:20px;border-radius:10px;overflow-x:auto;font-size:13px;line-height:1.7;margin:16px 0}}
    code{{font-family:'Fira Code','Cascadia Code',monospace}}
    .doc-links{{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}}
    .doc-link{{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;background:#ecf5ff;color:#409EFF;border-radius:8px;text-decoration:none;font-size:13px;transition:all .2s}}
    .doc-link:hover{{background:#409EFF;color:#fff}}
    .cta-box{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;padding:28px;text-align:center;margin-top:24px}}
    .cta-box a{{display:inline-block;padding:12px 32px;background:#409EFF;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;transition:transform .2s}}
    .cta-box a:hover{{transform:scale(1.05)}}
    .footer{{text-align:center;padding:24px;color:#b0c4de;font-size:13px;margin-top:32px}}
    .footer a{{color:#409EFF}}
    @media(max-width:640px){{
      .pro-con{{grid-template-columns:1fr}}
      .hero{{padding:24px}}
      .hero h1{{font-size:20px}}
    }}
  </style>
</head>
<body>
<div class="container">
  <div class="back-link">
    <a class="back-btn" href="/agent/index.html">← Dashboard</a>
    <a class="back-btn" href="/agent/curated.html">← 每日精选</a>
  </div>

  <div class="hero">
    <div class="badge">⭐ AI Agent 精选</div>
    <h1>{name}</h1>
    <p class="desc">{eval_text}</p>
    <div class="tag-list">{tags_html}</div>
    <div class="stats">
      <div class="stat"><div class="num">⭐ {stars}</div><div class="label">Stars</div></div>
      <div class="stat"><div class="num">{forks}</div><div class="label">Forks</div></div>
      <div class="stat"><div class="num">{language}</div><div class="label">语言</div></div>
      <div class="stat"><div class="num">{license}</div><div class="label">协议</div></div>
    </div>
    <div class="meta">
      {meta_html}
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">🔍</span> 项目详解</h2>
    <div class="highlight-box">
      <p>{what_text}</p>
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">📈</span> 为什么值得关注</h2>
    <ul>{why_list}</ul>
  </div>

  <div class="section">
    <h2><span class="icon">⚡</span> 优缺点分析</h2>
    <div class="pro-con">
      <div>
        <div class="pro-item" v-for="p in pros" :key="p">
          <strong>✅ 优势</strong>{pro_item}
        </div>
      </div>
      <div>
        <div class="con-item">
          <strong>⚠️ 局限</strong>{con_text}
        </div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">👥</span> 适合谁用</h2>
    <p>{who_text}</p>
  </div>

  <div class="section">
    <h2><span class="icon">🚀</span> 快速上手</h2>
    <pre>{install_code}</pre>
    <div class="doc-links">
      {doc_links_html}
    </div>
  </div>

  <div class="cta-box">
    <a href="https://github.com/{github_name}" target="_blank">⭐ 去 GitHub 看看</a>
  </div>

  <div class="footer">
    © 2026 <a href="https://github.com/leapord/agent" target="_blank">leapord/agent</a> ·
    <a href="/agent/index.html">Dashboard</a> ·
    <a href="/agent/curated.html">每日精选</a> ·
    报告生成时间: {timestamp}
  </div>
</div>
</body>
</html>"""


def tag_html(tags):
    return ''.join(f"<span class='tag'>{t}</span>" for t in tags)

def li_html(items):
    return ''.join(f"<li>{i}</li>" for i in items)

def meta_html(info):
    parts = []
    if info.get('created'): parts.append(f"<span>📅 创建于 {info['created']}</span>")
    if info.get('topics'): parts.append(f"<span>🏷️ {', '.join(info['topics'][:5])}</span>")
    return '<br>'.join(parts)

def generate_detail(name, info, out_dir):
    slug = name.replace('/', '-')
    out_path = os.path.join(out_dir, f"{slug}.html")

    stars = info.get('stars', 'N/A')
    forks = info.get('forks', 'N/A')
    language = info.get('language', 'N/A')
    license_ = info.get('license', 'N/A')
    eval_text = info.get('eval', '')
    what_text = info.get('what', '')
    why_items = info.get('why', [])
    cons_text = info.get('cons', [])
    who_text = info.get('who', '')
    install_code = info.get('install', '')
    doc_links = info.get('doc_links', [])
    tags = info.get('tags', [])

    # 合并 pro/con 到 pro-con 结构
    pro_items = info.get('why', [])[:5]
    con_items = info.get('cons', [])

    # 简单的模板替换（不用 jinja2，减少依赖）
    html = DETAIL_TEMPLATE
    replacements = {
        '{name}': name,
        '{meta_desc}': eval_text[:120],
        '{eval_text}': eval_text,
        '{tags_html}': tag_html(tags),
        '{stars}': stars,
        '{forks}': forks,
        '{language}': language,
        '{license}': license_,
        '{meta_html}': meta_html(info),
        '{what_text}': what_text,
        '{why_list}': li_html(why_items) if why_items else '<li>暂无信息</li>',
        '{who_text}': who_text,
        '{install_code}': install_code,
        '{doc_links_html}': ''.join(f"<a class='doc-link' href='{url}' target='_blank'>• {label}</a>" for label, url in doc_links),
        '{github_name}': name,
        '{timestamp}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '{pro_item}': '<br>'.join(f'· {p}' for p in pro_items),
        '{con_text}': '<br>'.join(f'· {c}' for c in con_items) if con_items else '暂无已知的局限性',
    }
    for k, v in replacements.items():
        html = html.replace(k, v)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    detail_dir = os.path.join(script_dir, 'detail')
    os.makedirs(detail_dir, exist_ok=True)

    # 切换到脚本目录（确保能找到 curated.json）
    os.chdir(script_dir)

    print(f"📦 共 {len(PROJECTS)} 个项目，开始生成深度 detail 页面 ...")
    count = 0
    for name, info in PROJECTS.items():
        if generate_detail(name, info, detail_dir):
            count += 1
            print(f"  ✅ {name} ({info.get('stars','?')} ⭐)")
        else:
            print(f"  ⏭️  跳过: {name}")

    print(f"\n✅ 完成！生成了 {count} 个 detail 页面 → {detail_dir}/")

if __name__ == '__main__':
    main()
