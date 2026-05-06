#!/usr/bin/env python3
"""
AI Agent GitHub Scanner & Report Generator
每天扫描 GitHub 热门 AI Agent 项目，生成静态报告并同步到双仓
"""

import json
import re
import os
import sys
import time
import subprocess
from datetime import datetime, timezone, timedelta

# ── 中文解读库：项目名 → (是什么, 为什么热, 适合谁) ────────────────────────
PROJECT_ANALYSIS = {
    "langgenius/dify": (
        "一站式 AI 应用开发平台，支持工作流编排、RAG、Agent 等多种开发模式，",
        "目前最火的 AI 应用开发平台之一，Stars 突破 14 万，文档完善、部署简单，",
        "适合想快速搭建 AI 应用（客服、文档助手、数据分析）但不想写太多代码的团队"
    ),
    "langchain-ai/langchain": (
        "LLM 应用开发框架，提供 Chains、Agents、Tools、Memory 等丰富组件，",
        "生态最成熟，Stars 排名第二，有大量第三方集成和社区教程，",
        "适合有编程基础、需要构建复杂 LLM 流水线的开发者"
    ),
    "Shubhamsaboo/awesome-llm-apps": (
        "收录了 100+ 可直接运行的 AI Agent 和 RAG 应用集合，含完整代码，",
        "精选高质量项目，每个都可以直接 clone 并自定义，二次开发门槛低，",
        "适合想快速参考成熟案例、或直接基于现有项目改造的开发者"
    ),
    "infiniflow/ragflow": (
        "深度文档理解 RAG 引擎，支持非结构化文档智能解析和多跳问答，",
        "在 RAG 基础上融合 Agent 能力，能处理复杂 PDF、表格等长文档，",
        "适合有大量内部文档（合同、报告、论文）需要构建智能问答的企业"
    ),
    "dair-ai/Prompt-Engineering-Guide": (
        "提示工程权威指南，收录最新提示技术、RAG、Agent 研究资料和实战教程，",
        "内容更新快、覆盖全面，包含论文解读和代码示例，",
        "适合想系统学习提示工程和 LLM 最佳实践的研究者和开发者"
    ),
    "thedotmack/claude-mem": (
        "Claude Code 记忆插件，自动记录编码会话并压缩存储相关上下文，",
        "突破性解决 AI 编程上下文丢失问题，让 Claude 每次都能「记住」之前的工作，",
        "适合重度使用 Claude Code 进行开发的工程师"
    ),
    "FoundationAgents/MetaGPT": (
        "多智能体框架，模拟软件公司组织架构让多个 Agent 协作完成复杂任务，",
        "首个将 Agent 团队协作理念落地的开源框架，引发多 Agent 研究热潮，",
        "适合研究多 Agent 协作、想让多个 AI 角色分工完成复杂任务（如写完整项目）的团队"
    ),
    "bytedance/deer-flow": (
        "字节开源的超级 Agent 测试框架，支持长周期研究和代码自动化生成，",
        "采用模块化设计，可评估 Agent 在复杂任务中的推理和工具使用能力，",
        "适合 AI 研究者和企业用于评估和基准测试 Agent 系统的能力上限"
    ),
    "microsoft/autogen": (
        "微软开源的多 Agent 编程框架，支持多 Agent 对话协作完成任务，",
        "背靠微软研究院，学术影响力大，适合企业级 AI 应用快速原型开发，",
        "适合想在企业场景中搭建多 Agent 协作系统（客服、代码审查、数据分析）的团队"
    ),
    "mem0ai/mem0": (
        "AI Agent 的通用记忆层，为各类 AI 助手提供持久化、跨会话的记忆能力，",
        "解决了 Agent 「记不住」的核心痛点，支持多种后端存储，",
        "适合需要构建真正「认识用户」的个性化 AI 助手（如 AI Tutor、AI Copilot）的开发者"
    ),
    "FlowiseAI/Flowise": (
        "低代码/无代码可视化 AI Flow 构建器，拖拽即可搭建完整 AI 流水线，",
        "零编码门槛，界面友好，支持一键部署，降低了 LLM 应用开发的入门难度，",
        "适合非技术背景用户、产品经理、或想快速验证想法的创业团队"
    ),
    "crewAIInc/crewAI": (
        "角色扮演多智能体编排框架，让多个 Agent 各司其职（如研究员+写手+审核），",
        "通过「Crew（团队）」概念让多 Agent 分工协作，支持复杂的层级任务分解，",
        "适合想构建自动化工作流（如市场调研、自动写报告）且有明确角色分工场景的团队"
    ),
    "run-llama/llama_index": (
        "文档智能理解与检索增强生成（RAG）框架，支持结构化和非结构化数据接入，",
        "Stars 排名靠前，生态成熟，与 LangChain 有深度集成，",
        "适合需要构建知识库问答、文档总结、数据分析代理的后端开发者"
    ),
    "CherryHQ/cherry-studio": (
        "AI 生产力工作室，内置 300+ 预设助手和自主 Agent，支持多模型切换，",
        "开箱即用，适合不想自己搭建、直接使用现成 AI 能力的用户，",
        "适合个人用户和中小企业快速使用 AI 能力（聊天、写作、代码助手）"
    ),
    "ruvnet/ruflo": (
        "面向 Claude 的多 Agent 编排平台，支持可视化流程设计和 Claude Opus 深度集成，",
        "新兴平台，主打 Claude 全生态，定位企业级 Agent 部署，",
        "适合已经在使用 Claude 的企业或开发者想搭建 Claude Agent 团队"
    ),
}

# ── 项目详细中文解读库 ────────────────────────────────────────────────────────
PROJECT_ANALYSIS_DETAIL = {
    "langgenius/dify": {
        "title": "Dify · 一站式 AI 应用开发平台",
        "summary": "当前最热门的 AI 应用开发平台，支持工作流编排、RAG、Agent，Stars 突破 14 万，零基础也能快速上线生产级 AI 应用。",
        "what": "Dify 是一个开源的 AI 应用开发平台，核心理念是让 AI 应用开发变得像搭积木一样简单。它将常见的 AI 开发模式封装成可复用的模块，开发者无需从零编写复杂的 LLM 调度逻辑，通过可视化界面或 YAML 配置即可完成 AI 应用的构建。支持三大核心能力：工作流编排（可视化 DAG）、RAG 引擎（多数据源）、Agent 模式（ReAct/Function Call）。",
        "why": [
            "门槛极低：有手就会用，无需深入了解 LLM 底层原理",
            "功能完备：内置日志、监控、多模型切换、API 发布等企业级功能",
            "部署简单：支持 Docker 一键部署，也有云端 SaaS 版本",
            "社区活跃：14 万 Stars，贡献者众多，插件生态丰富",
            "中文友好：文档完善，有活跃的中文社区",
        ],
        "competitors": [
            ("Dify", "低", "中", "完善", "140k ⭐"),
            ("LangChain", "高", "高", "需自行封装", "135k ⭐"),
            ("Flowise", "极低", "低", "基础", "~30k ⭐"),
        ],
        "who": [
            ("强烈推荐", "想快速上线 AI 应用（智能客服、私有知识库、AI 助手）但不想写太多代码的团队"),
            ("中小企业", "需要快速验证 AI 能力、自建 AI 应用、且没有专职 AI 工程师的产品团队"),
            ("需评估", "需要极深度定制（自定义训练模型、超复杂 Agent 逻辑）的场景"),
        ],
        "links": [
            ("官方文档", "https://docs.dify.ai"),
            ("GitHub", "https://github.com/langgenius/dify"),
            ("在线体验", "https://dify.ai"),
        ],
    },
    "langchain-ai/langchain": {
        "title": "LangChain · Agent 工程平台",
        "summary": "生态最成熟的 LLM 应用开发框架，Stars 排名第二，提供 Chains、Agents、Tools、Memory 等丰富组件，适合构建复杂 LLM 流水线。",
        "what": "LangChain 是一个全方位 LLM 应用开发框架，核心抽象包括：Chains（调用序列）、Agents（自主决策）、Tools（外部能力）、Memory（对话记忆）。它既是 Python 库也是 TypeScript 库，生态极其丰富，有 LangSmith（观测平台）、LangServe（部署工具）等官方配套工具。",
        "why": [
            "生态最成熟：Stars 排名第二，大量第三方集成和社区教程",
            "灵活性最高：几乎所有组件都支持深度定制和替换",
            "学术认可度高：大量 AI 论文基于 LangChain 做实验",
            "配套完善：LangSmith 观测平台、LangServe 一键部署",
            "多语言：Python + TypeScript双版本，企业选用多",
        ],
        "competitors": [
            ("LangChain", "高", "高", "需自行封装", "135k ⭐"),
            ("LlamaIndex", "中", "高", "基础", "~38k ⭐"),
            ("Dify", "低", "中", "完善", "140k ⭐"),
        ],
        "who": [
            ("强烈推荐", "有编程基础、需要构建复杂 LLM 流水线（如多步推理、复杂工具调用）的高级开发者"),
            ("强烈推荐", "AI 研究者、需要快速验证 LLM 新想法的学术人员"),
            ("需评估", "纯业务团队、快速出活优先的场景——门槛较高，建议用 Dify/Flowise"),
        ],
        "links": [
            ("官方文档", "https://python.langchain.com"),
            ("GitHub", "https://github.com/langchain-ai/langchain"),
            ("LangSmith", "https://smith.langchain.com"),
        ],
    },
    "FoundationAgents/MetaGPT": {
        "title": "MetaGPT · 多智能体框架",
        "summary": "首个将 Agent 团队协作理念落地的开源框架，模拟软件公司组织架构让多个 Agent 协作完成复杂任务，引发多 Agent 研究热潮。",
        "what": "MetaGPT 是一个多智能体框架，创新性地让多个 Agent 各扮演软件公司中的角色（产品经理、架构师、工程师、测试），通过协作完成复杂任务。例如输入「写一个 2048 小游戏」，MetaGPT 会自动输出完整的产品需求文档（PRD）、架构设计、代码实现。它是目前多 Agent 协作领域最具影响力的开源项目之一。",
        "why": [
            "创新性极强：首个将软件工程流程映射到多 Agent 协作的项目",
            "学术影响力大：引发了大量多 Agent 系统的研究热潮",
            "任务分解自然：用「角色+ SOP」的方式让 Agent 协作更符合人类组织逻辑",
            "代码质量较高：生成代码经过评审和测试流程，而非一次性输出",
        ],
        "competitors": [
            ("MetaGPT", "高", "PRD→设计→代码→测试", "学术影响力大", "67k ⭐"),
            ("CrewAI", "低", "角色+任务分配", "易上手", "~30k ⭐"),
            ("AutoGen", "中", "多 Agent 对话", "微软背书", "~45k ⭐"),
        ],
        "who": [
            ("强烈推荐", "AI 研究者、研究多 Agent 协作、任务分解与规划的学术团队"),
            ("强烈推荐", "想探索「AI 软件公司」概念、让 AI 自主完成完整项目的先锋团队"),
            ("需评估", "只想做简单客服/问答的场景——过于重量，建议用 Dify"),
        ],
        "links": [
            ("官方文档", "https://docs.deepwisdom.ai/metagpt"),
            ("GitHub", "https://github.com/FoundationAgents/MetaGPT"),
            ("论文", "https://arxiv.org/abs/2308.00352"),
        ],
    },
    "microsoft/autogen": {
        "title": "AutoGen · 微软多 Agent 编程框架",
        "summary": "微软开源的多 Agent 编程框架，支持多 Agent 对话协作，背靠微软研究院，适合企业级 AI 应用快速原型开发。",
        "what": "AutoGen 是微软研究院开源的多 Agent 协作框架，核心是通过多 Agent 对话让不同的 LLM Agent 相互协作完成任务。它支持灵活的 Agent 定义（可带工具、可带记忆）、对话式协作、以及人机协同（Human-in-the-loop）。适合需要多角色分工、长流程协作的企业场景。",
        "why": [
            "微软背书：背靠微软研究院，学术和企业认可度高",
            "对话式设计：Agent 之间通过自然语言对话协作，易于理解",
            "人机协同：支持人类在关键步骤介入，适合需要审核的流程",
            "企业友好：适合在企业内部快速搭建 AI 原型",
        ],
        "competitors": [
            ("AutoGen", "中", "对话式协作", "微软背书", "~45k ⭐"),
            ("MetaGPT", "高", "SOP 流程", "学术影响力大", "67k ⭐"),
            ("CrewAI", "低", "角色+任务", "易上手", "~30k ⭐"),
        ],
        "who": [
            ("强烈推荐", "企业开发者、需要快速在内部搭建多 Agent AI 原型的团队"),
            ("推荐", "需要人类在流程中审核把关（如审批、客服升级）的场景"),
            ("需评估", "简单场景下 CrewAI 上手更快；复杂研究场景 MetaGPT 能力上限更高"),
        ],
        "links": [
            ("官方文档", "https://microsoft.github.io/autogen"),
            ("GitHub", "https://github.com/microsoft/autogen"),
        ],
    },
    "crewAIInc/crewAI": {
        "title": "CrewAI · 角色扮演多智能体编排",
        "summary": "通过「Crew（团队）」概念让多个 Agent 分工协作，支持复杂任务分解，适合构建自动化工作流（市场调研、自动写报告）。",
        "what": "CrewAI 是一个角色扮演多智能体编排框架，核心概念是 Crew（团队）+ Agent（角色）+ Task（任务）。你可以定义多个 Agent（如研究员、写手、审核），给每个 Agent 分配具体任务，Crew 负责协调它们按顺序或并行执行。上手极简，是目前多 Agent 入门最友好的框架。",
        "why": [
            "入门最简单：概念清晰，YAML 或代码都能定义 Agent",
            "角色分工自然：「研究员+写手+审核」符合人类工作习惯",
            "支持任务依赖：可以定义任务之间的顺序和依赖关系",
            "学习资源丰富：官方教程详细，社区活跃",
        ],
        "competitors": [
            ("CrewAI", "低", "角色+任务", "易上手", "~30k ⭐"),
            ("MetaGPT", "高", "SOP 流程", "学术影响力大", "67k ⭐"),
            ("AutoGen", "中", "对话式协作", "微软背书", "~45k ⭐"),
        ],
        "who": [
            ("强烈推荐", "想入门多 Agent 协作、需要构建自动化工作流（市场调研、报告撰写、数据分析）的团队"),
            ("强烈推荐", "个人开发者、快速验证多 Agent 想法的独立创业者"),
            ("需评估", "极复杂任务（完整软件工程）→ MetaGPT；企业级大规模部署 → AutoGen"),
        ],
        "links": [
            ("官方文档", "https://docs.crewai.com"),
            ("GitHub", "https://github.com/crewAIInc/crewAI"),
        ],
    },
    "mem0ai/mem0": {
        "title": "Mem0 · AI Agent 记忆层",
        "summary": "为 AI Agent 提供跨会话持久化记忆能力，解决 Agent「记不住」的核心痛点，让 AI 助手真正「认识用户」。",
        "what": "Mem0 是 AI Agent 的通用记忆层，核心理念是给任何 AI 助手加上持久化、跨会话的记忆能力。它支持用户偏好记忆、对话历史摘要、事实存储，提供 API 接入任何 Agent（LangChain、LlamaIndex、Dify 都能对接）。解决了 Agent「每次对话都从零开始」的根本痛点。",
        "why": [
            "解决核心痛点：Agent 「记不住」是实际落地最大障碍之一",
            "通用适配：API 简单，能接入任何框架（LangChain、Dify、CrewAI 等）",
            "多种存储后端：支持向量数据库、Redis、内存等多种存储方式",
            "国内关注度高：记忆能力在国内 AI 应用中需求旺盛",
        ],
        "competitors": [
            ("Mem0", "低（API）", "跨会话记忆", "通用适配", "~15k ⭐"),
            ("dotmac/claude-mem", "中（插件）", "Claude 专用", "Claude 生态", "72k ⭐"),
            ("LangChain Memory", "中", "对话内记忆", "LangChain 绑定", "内置"),
        ],
        "who": [
            ("强烈推荐", "想构建真正「认识用户」的 AI 助手（AI Tutor、AI Copilot、私人 AI 管家）的开发者"),
            ("推荐", "有用户个性化需求（记住用户偏好、习惯、历史）的产品团队"),
            ("不推荐", "不需要跨会话记忆的简单一次性问答场景"),
        ],
        "links": [
            ("官方文档", "https://docs.mem0.ai"),
            ("GitHub", "https://github.com/mem0ai/mem0"),
        ],
    },
    "FlowiseAI/Flowise": {
        "title": "Flowise · 低代码 AI Flow 构建器",
        "summary": "零编码门槛的可视化 AI Flow 构建器，拖拽即可搭建完整 AI 流水线，适合非技术背景用户快速验证 AI 想法。",
        "what": "Flowise 是一个低代码/无代码可视化 AI Flow 构建器，核心理念是「拖拽即用」，通过图形界面串联 LLM、向量数据库、工具等组件。完全不需要写代码，但也可以在需要时写 JavaScript 自定义逻辑。上手极简，适合产品经理和独立创业者快速验证 AI 产品想法。",
        "why": [
            "门槛最低：纯拖拽，零代码基础也能用",
            "界面友好：所见即所得，组件一目了然",
            "可导出代码：复杂需求可以导出 LangChain 代码继续开发",
            "部署简单：Docker 一键部署或使用官方云版",
        ],
        "competitors": [
            ("Flowise", "极低", "极低", "仅支持简单流水线", "~30k ⭐"),
            ("Dify", "低", "低", "功能完善", "140k ⭐"),
            ("LangChain", "高", "高", "无限灵活", "135k ⭐"),
        ],
        "who": [
            ("强烈推荐", "非技术背景用户（产品经理、运营、创业者）想快速验证 AI 产品想法"),
            ("推荐", "技术团队快速出原型，验证可行性后再决定是否用代码重写"),
            ("不推荐", "需要深度定制、超复杂逻辑的场景——建议直接上 LangChain"),
        ],
        "links": [
            ("官方文档", "https://flowiseai.com"),
            ("GitHub", "https://github.com/FlowiseAI/Flowise"),
        ],
    },
    "infiniflow/ragflow": {
        "title": "RAGFlow · 深度文档理解 RAG 引擎",
        "summary": "在 RAG 基础上融合 Agent 能力，支持复杂 PDF、表格等长文档的智能解析和多跳问答，适合有大量内部文档的企业。",
        "what": "RAGFlow 是一个深度文档理解 RAG 引擎，主打「深度理解」而非简单关键词匹配。它能处理复杂的非结构化文档（PDF、Word、表格、图片），通过 Agent 做多跳推理（Multi-hop QA），适合需要从大量内部文档中提取信息并回答复杂问题的企业场景。",
        "why": [
            "深度文档理解：能解析表格、图表、复杂版式的 PDF",
            "多跳问答：支持复杂推理问题（如「A 和 B 的差异是什么然后得出结论」）",
            "RAG + Agent 融合：不是简单检索，是真正理解文档结构后回答",
            "中文支持好：国内开源，对中文文档处理优化较多",
        ],
        "competitors": [
            ("RAGFlow", "中", "深度文档理解", "中文优化", "79k ⭐"),
            ("Dify", "低", "标准 RAG", "功能完善", "140k ⭐"),
            ("LlamaIndex", "高", "基础 RAG", "高度可定制", "~38k ⭐"),
        ],
        "who": [
            ("强烈推荐", "有大量内部文档（合同、报告、论文）需要构建智能问答的企业"),
            ("强烈推荐", "需要处理复杂 PDF（含表格、图表）而非纯文本的团队"),
            ("需评估", "简单 Q&A 场景 Dify 更轻量；极复杂推理场景可能需要配合 LangChain"),
        ],
        "links": [
            ("官方文档", "https://ragflow.io"),
            ("GitHub", "https://github.com/infiniflow/ragflow"),
        ],
    },
    "run-llama/llama_index": {
        "title": "LlamaIndex · 文档智能理解框架",
        "summary": "与 LangChain 并列的文档理解与 RAG 框架，Stars 靠前，生态成熟，特别擅长知识库构建和文档代理。",
        "what": "LlamaIndex（又称 GPT Index）是文档智能理解与检索增强生成（RAG）框架，专注于「让 LLM 理解私有数据」。提供丰富的数据连接器（PDF、Notion、SQL、API），支持多层次索引（Summary Index、Vector Index、Knowledge Graph Index），是构建私有知识库的首选框架之一。",
        "why": [
            "专注文档理解：比 LangChain 更聚焦在知识检索和理解领域",
            "索引类型丰富：Summary、Vector、KG、Recursive 等多种索引策略",
            "生态成熟：与 LangChain、AutoGPT 等主流框架深度集成",
            "文档详尽：官方文档质量高，学习曲线相对平滑",
        ],
        "competitors": [
            ("LlamaIndex", "中", "文档+检索", "专注知识库", "~38k ⭐"),
            ("LangChain", "高", "通用框架", "生态最广", "135k ⭐"),
            ("Dify", "低", "RAG 引擎", "开箱即用", "140k ⭐"),
        ],
        "who": [
            ("强烈推荐", "需要构建私有知识库问答、文档总结、复杂检索场景的后端开发者"),
            ("推荐", "需要在现有 LangChain 项目中加强 RAG 能力的团队"),
            ("不推荐", "只想快速上线简单 AI 应用——Dify/Flowise 更适合"),
        ],
        "links": [
            ("官方文档", "https://docs.llamaindex.ai"),
            ("GitHub", "https://github.com/run-llama/llama_index"),
        ],
    },
    "Shubhamsaboo/awesome-llm-apps": {
        "title": "awesome-llm-apps · 100+ 可运行 AI 应用集合",
        "summary": "精选 100+ 可直接运行的 AI Agent 和 RAG 应用集合，每个都有完整代码，适合快速参考或直接二开。",
        "what": "awesome-llm-apps 是一个精选 AI 应用集合，收录了 100+ 个可以直接运行的 AI Agent 和 RAG 应用，每个应用都配有完整代码和详细说明。涵盖聊天机器人、RAG 知识库、代码助手、多模态应用等多个方向，是目前最全面的 AI 应用参考集合之一。",
        "why": [
            "精选高质量：每个项目都经过筛选，不是简单罗列",
            "可直接运行：clone 后按文档配置即可运行，二次开发门槛低",
            "覆盖面广：Agent、RAG、多模态、代码助手等各种场景都有",
            "更新频繁：作者持续维护，不断有新项目加入",
        ],
        "competitors": [
            ("awesome-llm-apps", "低", "应用集合", "可直接运行", "108k ⭐"),
            ("LangChain Examples", "中", "代码示例", "偏底层", "官方示例"),
            ("Dify 社区", "低", "应用模板", "需在 Dify 内使用", "社区"),
        ],
        "who": [
            ("强烈推荐", "想参考成熟 AI 应用案例、直接基于现有项目改造的开发者"),
            ("强烈推荐", "创业团队想快速出 MVP，选择现成应用改造而非从零开发"),
            ("不推荐", "需要深度定制核心算法——这只是应用层参考，不是底层框架"),
        ],
        "links": [
            ("GitHub", "https://github.com/Shubhamsaboo/awesome-llm-apps"),
        ],
    },
}

def slugify(name):
    """将 'owner/repo' 转为 'owner-repo' 用于 URL"""
    return name.replace("/", "-")

def generate_detail_pages(top_projects):
    """为热门项目生成详细解读页"""
    detail_dir = os.path.join(REPO_DIR, "detail")
    os.makedirs(detail_dir, exist_ok=True)
    count = 0
    for p in top_projects:
        name = p["name"]
        detail = PROJECT_ANALYSIS_DETAIL.get(name)
        slug = slugify(name)
        page_path = os.path.join(detail_dir, f"{slug}.html")
        html = _build_detail_html(p, detail, slug)
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(html)
        count += 1
    print(f"  ✅ 生成了 {count} 个详细解读页 → {detail_dir}/")
    return detail_dir

def _build_detail_html(p, detail, slug):
    """构建单个项目的详细解读 HTML"""
    title = detail["title"] if detail else p["name"]
    summary = detail["summary"] if detail else (p.get("description") or "暂无解读")
    what = detail["what"] if detail else (p.get("description") or "")
    rank = p.get("rank", 0)
    stars = p.get("stars", "")
    forks = p.get("forks", "")
    language = p.get("language", "")
    tags = p.get("tags", [])
    url = p.get("url", "")

    # 一句话评价
    one_liner = detail["summary"] if detail else summary

    # What is this
    what_html = f"<p>{what}</p>" if what else f"<p>{summary}</p>"

    # Why hot
    why_html = ""
    if detail and detail.get("why"):
        why_html = "<ul>" + "".join(f"<li>{r}</li>" for r in detail["why"]) + "</ul>"
    else:
        why_html = f"<p>近期在 GitHub 热度较高，受到开发者关注。Stars {stars}，Forks {forks}。</p>"

    # Competitors table
    comp_html = ""
    if detail and detail.get("competitors"):
        rows = ""
        for row in detail["competitors"]:
            rows += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        comp_html = f"""
    <table class="compare-table">
      <tr><th>方案</th><th>编程门槛</th><th>灵活性</th><th>企业特性</th><th>生态</th></tr>
      {rows}
    </table>"""

    # Who
    who_html = ""
    if detail and detail.get("who"):
        cards = ""
        for title, text in detail["who"]:
            emoji = "✅" if "强烈" in title or "推荐" in title else "⚠️"
            cards += f"""<div class="who-card">
          <div class="title">{emoji} {title}</div>
          <div class="text">{text}</div>
        </div>"""
        who_html = cards

    # Links
    links_html = ""
    if detail and detail.get("links"):
        links_html = "<ul>" + "".join(f"<li><a href='{url}' target='_blank' style='color:#409EFF'>{name}</a></li>" for name, url in detail["links"]) + "</ul>"
    else:
        links_html = f"<ul><li><a href='{url}' target='_blank' style='color:#409EFF'>GitHub 仓库</a></li></ul>"

    tags_html = "".join(f"<span class='tag'>{t}</span>" for t in tags[:5])

    today_short = datetime.now().strftime("%Y-%m-%d")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{title} | AI Agent 每日简报</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{summary[:100]}">
  <link rel="stylesheet" href="https://unpkg.com/element-plus@2.4.1/dist/index.css">
  <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
  <script src="https://unpkg.com/element-plus@2.4.1/dist/index.full.min.js"></script>
  <style>
   *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f7fa;color:#1a1a2e;line-height:1.8}}
    .container{{max-width:900px;margin:0 auto;padding:32px 24px}}
    .back-btn{{display:inline-flex;align-items:center;gap:6px;color:#409EFF;font-size:14px;text-decoration:none;margin-bottom:24px;padding:8px 16px;background:#fff;border:1px solid #409EFF;border-radius:8px;transition:all .2s}}
    .back-btn:hover{{background:#409EFF;color:#fff}}
    .hero{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:40px;color:#fff;margin-bottom:32px;position:relative;overflow:hidden}}
    .hero::before{{content:'';position:absolute;top:-50%;right:-20%;width:400px;height:400px;background:radial-gradient(circle,rgba(64,158,255,.15),transparent 70%);border-radius:50%}}
    .hero .badge{{display:inline-block;padding:4px 12px;background:rgba(64,158,255,.2);border:1px solid rgba(64,158,255,.4);border-radius:20px;font-size:12px;margin-bottom:12px}}
    .hero h1{{font-size:26px;font-weight:700;margin-bottom:8px}}
    .hero .desc{{color:rgba(255,255,255,.7);font-size:15px;margin-bottom:16px}}
    .hero .stats{{display:flex;gap:24px;flex-wrap:wrap;margin-top:20px}}
    .hero .stat{{text-align:center}}
    .hero .stat .num{{font-size:20px;font-weight:700;color:#409EFF}}
    .hero .stat .label{{font-size:11px;color:rgba(255,255,255,.5);text-transform:uppercase}}
    .section{{background:#fff;border-radius:12px;padding:28px;margin-bottom:20px;border:1px solid #f0f0f0}}
    .section h2{{font-size:17px;font-weight:700;color:#1a1a2e;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #409EFF;display:flex;align-items:center;gap:8px}}
    .section h2 .icon{{font-size:20px}}
    .section p,.section li{{color:#555;font-size:14px}}
    .section ul{{padding-left:20px}}
    .section li{{margin-bottom:8px}}
    .highlight-box{{background:linear-gradient(135deg,#ecf5ff,#f0f9ff);border-left:4px solid #409EFF;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0}}
    .highlight-box p{{color:#1a1a2e;font-size:14px}}
    .tag-list{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
    .tag{{padding:4px 12px;background:#ecf5ff;color:#409EFF;border-radius:20px;font-size:12px}}
    .compare-table{{width:100%;border-collapse:collapse;font-size:13px}}
    .compare-table th{{background:#f5f7fa;padding:10px 12px;text-align:left;font-weight:600;color:#606266;border-bottom:2px solid #e0e0e0}}
    .compare-table td{{padding:10px 12px;border-bottom:1px solid #f0f0f0;vertical-align:top}}
    .compare-table tr:hover{{background:#f5f7fa}}
    .who-card{{background:#fafafa;border-radius:8px;padding:16px;margin-bottom:12px;border:1px solid #f0f0f0}}
    .who-card .title{{font-weight:600;color:#1a1a2e;margin-bottom:4px;font-size:14px}}
    .who-card .text{{color:#7a8ba8;font-size:13px}}
    .cta-box{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;padding:24px;text-align:center;margin-top:24px}}
    .cta-box a{{display:inline-block;padding:12px 32px;background:#409EFF;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;transition:transform .2s}}
    .cta-box a:hover{{transform:scale(1.05)}}
    .footer{{text-align:center;padding:24px;color:#b0c4de;font-size:13px;margin-top:32px}}
    .footer a{{color:#409EFF}}
  </style>
</head>
<body>
<div id="app" class="container">
  <a class="back-btn" href="/agent/report-{today_short}.html">← 返回日报</a>
  <a class="back-btn" href="/agent/index.html" style="margin-left:12px">← Dashboard</a>

  <div class="hero">
    <div class="badge">🔥 GitHub Trending TOP {rank}</div>
    <h1>{p.get('name', '')}</h1>
    <p class="desc">{p.get('description', '')}</p>
    <div class="tag-list">{tags_html}</div>
    <div class="stats">
      <div class="stat"><div class="num">⭐ {stars}</div><div class="label">Stars</div></div>
      <div class="stat"><div class="num">{forks}</div><div class="label">Forks</div></div>
      <div class="stat"><div class="num">{language}</div><div class="label">语言</div></div>
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">💡</span> 一句话评价</h2>
    <div class="highlight-box">
      <p>{one_liner}</p>
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">🔍</span> 是什么</h2>
    {what_html}
  </div>

  <div class="section">
    <h2><span class="icon">📈</span> 为什么火</h2>
    {why_html}
  </div>

  <div class="section">
    <h2><span class="icon">⚔️</span> 竞品对比</h2>
    {comp_html}
  </div>

  <div class="section">
    <h2><span class="icon">👥</span> 适合谁用</h2>
    {who_html}
  </div>

  <div class="section">
    <h2><span class="icon">🚀</span> 快速上手</h2>
    {links_html}
  </div>

  <div class="cta-box">
    <a href="{url}" target="_blank">⭐ 去 GitHub 看看</a>
  </div>

  <div class="footer">
    © 2026 AI Agent 前沿追踪 ·
    <a href="/agent/index.html">Dashboard</a> ·
    <a href="/agent/report-{today_short}.html">日报</a> ·
    报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  </div>
</div>
</body>
</html>
"""


def get_analysis(name):
    """获取项目的中文解读，fallback 到通用描述"""
    if name in PROJECT_ANALYSIS:
        return PROJECT_ANALYSIS[name]
    return (f"一个优质的 {name.split('/')[-1]} 项目，", "近期热度较高，受到开发者关注，", "适合对 AI Agent 领域感兴趣的开发者探索研究")

# ── Config ──────────────────────────────────────────────────────────────────
REPO_DIR = "/opt/data/home/agent"
PAGES_REPO_DIR = "/opt/data/home/leapord.github.io"
AGENT_IN_PAGES = os.path.join(PAGES_REPO_DIR, "agent")

TODAY = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
TODAY_FILE = f"report-{TODAY}.html"
REPORT_PATH = os.path.join(REPO_DIR, TODAY_FILE)
TRENDING_JSON = os.path.join(REPO_DIR, "trending.json")
PAGES_JSON = os.path.join(REPO_DIR, "pages.json")
MONITOR_JSON = os.path.join(REPO_DIR, "monitor.json")

# GitHub API tokens (优先使用环境变量)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Agent-Scanner/1.0",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# ── AI Agent 关键词 ─────────────────────────────────────────────────────────
AGENT_KEYWORDS = [
    "AI agent", "LLM agent", "autonomous agent", "multi-agent",
    "tool use", "tool calling", "agent framework", "agentic",
    "reasoning agent", "agentic AI", "agent system", "agentic RAG",
    "single agent", "multi agent system", "AI assistant",
    "computer use", "web agent", "code agent", "software agent",
    "agentic workflow", "memory agent", "persistent agent",
    "crew AI", "crewai", "autogen", "langgraph", "smolagent",
    "agent protocol", "MCP server", "model context protocol",
]

# ── Helpers ─────────────────────────────────────────────────────────────────
def gh_api(url, params=None):
    """调用 GitHub API，带重试"""
    import urllib.request, urllib.parse
    for attempt in range(3):
        try:
            if params:
                encoded_params = "&".join(urllib.parse.urlencode({k: v}) for k, v in params.items())
                full_url = f"{url}?{encoded_params}"
            else:
                full_url = url
            req = urllib.request.Request(full_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                if isinstance(data, dict) and "items" in data:
                    return data
                elif isinstance(data, list):
                    return {"items": data}
                else:
                    return {"items": []}
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"  ⚠ API 失败: {url} → {e}")
                return {"items": []}
    return {"items": []}

def gh_trending(lang=None, since="daily"):
    """获取 GitHub Trending"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"AI agent OR LLM agent OR autonomous agent OR multi-agent{' language:'+lang if lang else ''}",
        "sort": "stars",
        "order": "desc",
        "per_page": 30
    }
    return gh_api(url, params)

def gh_search_agent(query, stars_min=10, per_page=20):
    """搜索 AI Agent 相关仓库"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"{query} stars:>{stars_min}",
        "sort": "stars",
        "order": "desc",
        "per_page": per_page
    }
    return gh_api(url, params)

def gh_repo(name):
    """获取单个仓库详情"""
    return gh_api(f"https://api.github.com/repos/{name}")

def classify_tags(name, desc, topics):
    """根据名称/描述/主题打标签"""
    tags = []
    name_lower = name.lower()
    desc_lower = (desc or "").lower()

    if any(k in name_lower or k in desc_lower for k in ["multi-agent", "multi_agent", "crew", "swarm", "multi agent"]):
        tags.append("Multi-Agent")
    if any(k in name_lower or k in desc_lower for k in ["single agent", "single-agent", "one agent"]):
        tags.append("Single Agent")
    if any(k in name_lower or k in desc_lower for k in ["tool", "plugin", "mcp", "function call", "tool-use", "toolcall"]):
        tags.append("Tool Calling")
    if any(k in name_lower or k in desc_lower for k in ["memory", "context", "long term", "persistent"]):
        tags.append("Memory")
    if any(k in name_lower or k in desc_lower for k in ["rag", "retrieval", "retriever"]):
        tags.append("RAG+Agent")
    if any(k in name_lower or k in desc_lower for k in ["code", "coder", "programming", "devin", "swe-agent", "aider"]):
        tags.append("Code Agent")
    if any(k in name_lower or k in desc_lower for k in ["research", "paper", "arxiv", "scientific", "benchmark"]):
        tags.append("Research Agent")
    if any(k in name_lower or k in desc_lower for k in ["dev", "developer", "engineering", "software", "build"]):
        tags.append("Dev Agent")
    if any(k in name_lower or k in desc_lower for k in ["langgraph", "langchain", "llamaindex", "dspy"]):
        tags.append("Framework")
    if any(k in name_lower or k in desc_lower for k in ["vision", "multimodal", "image", "video", "audio"]):
        tags.append("Multimodal")
    if any(k in name_lower or k in desc_lower for k in ["safety", "secure", "jailbreak", "protect", "guardrail"]):
        tags.append("Safety")
    if any(k in name_lower or k in desc_lower for k in ["evaluation", "benchmark", "measure", "metric"]):
        tags.append("Evaluation")

    # topics 中有价值的
    for t in (topics or []):
        if t not in tags and any(kw in t.lower() for kw in ["agent", "llm", "ai", "copilot", "assistant", "tool"]):
            tags.append(t.replace("-"," ").title()[:20])

    return tags[:4] if tags else ["AI Agent"]

def fmt_num(n):
    """格式化数字 1200 → 1.2k"""
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

# ── 核心扫描逻辑 ────────────────────────────────────────────────────────────
def scan_github():
    print("🔍 开始 GitHub 扫描...")
    projects = []
    seen = set()

    # 1. 搜索 AI Agent 核心框架
    print("  → 扫描 AI Agent 核心框架...")
    queries = [
        ("AI agent framework", 50),
        ("LLM autonomous agent", 30),
        ("multi-agent AI system", 30),
        ("tool calling agent", 20),
        ("agentic RAG", 20),
        ("AI agent memory", 15),
        ("code generation agent", 15),
    ]
    for query, per_page in queries:
        items = gh_search_agent(query, stars_min=10, per_page=per_page)
        for item in items.get("items", []):
            if item["full_name"] in seen:
                continue
            seen.add(item["full_name"])
            projects.append({
                "name": item["full_name"],
                "description": item.get("description") or "",
                "language": item.get("language") or "",
                "stars": fmt_num(item.get("stargazers_count", 0)),
                "stars_raw": item.get("stargazers_count", 0),
                "forks": fmt_num(item.get("forks_count", 0)),
                "forks_raw": item.get("forks_count", 0),
                "todayStars": "—",
                "url": item["html_url"],
                "tags": classify_tags(item["name"], item.get("description"), item.get("topics", [])),
                "updated": item.get("pushed_at", "")[:10],
            })
        time.sleep(1)

    # 2. 按 stars 排序，取前 20
    projects.sort(key=lambda x: x["stars_raw"], reverse=True)
    top_projects = projects[:20]

    # 3. 生成今日趋势
    trending = []
    for i, p in enumerate(top_projects):
        today_s = max(0, p["stars_raw"] - max(0, p["forks_raw"] * 3))
        trending.append({
            "rank": i + 1,
            "name": p["name"],
            "description": p["description"],
            "language": p["language"],
            "stars": p["stars"],
            "todayStars": p["todayStars"],
            "forks": p["forks"],
            "tags": p["tags"],
            "url": p["url"],
        })

    print(f"  ✅ 扫描完成，共获取 {len(trending)} 个热门项目")
    return trending, top_projects

# ── 报告生成 ─────────────────────────────────────────────────────────────────
# ── ArXiv 扫描 ──────────────────────────────────────────────────────────────
def _arxiv_query_with_backoff(url, max_retries=5):
    """带指数退避的 ArXiv 查询"""
    import urllib.request
    base_delay = 5
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "AI-Agent-Scanner/1.0 (mailto:leapord@example.com)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                delay = base_delay * (2 ** attempt)
                print(f"    ⏳ ArXiv 429限流，等待 {delay}s (重试 {attempt+1}/{max_retries})...")
                time.sleep(delay)
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"    ⏳ 请求超时，等待 {delay}s...")
                time.sleep(delay)
            else:
                raise
    return ""


def _generate_paper_digest(title, summary):
    """生成论文的中文摘要解读（一两句话，不重复不堆砌）"""
    # 简单规则化解读，避免大模型调用
    summary = summary[:400]
    key_words = []
    if any(w in summary.lower() for w in ['multi-agent', 'multi agent', 'agents']):
        key_words.append('多智能体')
    if any(w in summary.lower() for w in ['rag', 'retrieval', 'knowledge']):
        key_words.append('知识检索')
    if any(w in summary.lower() for w in ['planning', 'reasoning', 'chain-of-thought']):
        key_words.append('规划推理')
    if any(w in summary.lower() for w in ['tool', 'function', 'api']):
        key_words.append('工具调用')
    if any(w in summary.lower() for w in ['memory', 'context']):
        key_words.append('记忆管理')
    if any(w in summary.lower() for w in ['vision', 'multimodal', 'image']):
        key_words.append('多模态')
    if any(w in summary.lower() for w in ['fine-tune', 'training', 'learning']):
        key_words.append('模型训练')
    if any(w in summary.lower() for w in ['autonomous', 'robot']):
        key_words.append('自主行动')
    key_str = '、'.join(key_words[:3]) if key_words else 'AI Agent 应用'
    # 从 summary 提取核心句
    sentences = summary.replace('\n', ' ').split('. ')
    core = sentences[0][:120].strip() if sentences else summary[:120]
    return f"探讨{key_str}：{core}"


def scan_arxiv():
    """获取 ArXiv 上全新的 AI Agent 相关论文（去重 + 中文解读）"""
    import urllib.parse
    print("  → 扫描 ArXiv AI Agent 论文...")

    # 加载历史记录（跨运行去重）
    seen_file = os.path.join(REPO_DIR, "seen_papers.json")
    seen_ids = set()
    if os.path.exists(seen_file):
        try:
            with open(seen_file) as f:
                seen_ids = set(json.load(f))
            print(f"  📋 历史已收录 {len(seen_ids)} 篇论文")
        except Exception:
            pass

    queries = [
        ("AI agent", "cs.AI"),
        ("LLM agent", "cs.CL"),
        ("multi-agent system", "cs.MA"),
    ]
    papers = []
    new_ids = set()

    for q, cat in queries:
        try:
            params = {
                "search_query": f"all:{q} AND cat:{cat}",
                "start": 0,
                "max_results": 5,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
            url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
            xml_text = _arxiv_query_with_backoff(url)
            if not xml_text:
                continue

            entries = re.findall(r"<entry>(.*?)</entry>", xml_text, re.DOTALL)
            for entry in entries:
                arxiv_id = re.search(r"<id>(.*?)</id>", entry)
                title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
                summary_m = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
                author_m = re.findall(r"<name>(.*?)</name>", entry)
                published_m = re.search(r"<published>(.*?)</published>", entry)
                if not arxiv_id or not title_m:
                    continue
                aid = arxiv_id.group(1).split("/")[-1]
                if aid in seen_ids:
                    continue  # 已展示过，跳过
                seen_ids.add(aid)
                new_ids.add(aid)
                title = re.sub(r"\s+", " ", title_m.group(1)).strip()
                summary = re.sub(r"\s+", " ", (summary_m.group(1) or "")).strip()
                authors = ", ".join(author_m[:3]) + (" et al." if len(author_m) > 3 else "")
                published = (published_m.group(1)[:10]) if published_m else ""
                tags = classify_tags(title, summary, [])
                digest = _generate_paper_digest(title, summary)
                papers.append({
                    "id": aid,
                    "title": title,
                    "summary": summary[:300],
                    "digest": digest,
                    "authors": authors,
                    "published": published,
                    "url": f"https://arxiv.org/abs/{aid}",
                    "pdf": f"https://arxiv.org/pdf/{aid}.pdf",
                    "tags": tags,
                })
        except Exception as e:
            print(f"    ⚠️  ArXiv 查询失败 [{q}]: {e}")
        time.sleep(5)

    # 保存历史记录
    with open(seen_file, 'w') as f:
        json.dump(list(seen_ids), f)
    print(f"  ✅ 新论文 +{len(new_ids)} 篇 / 历史共 {len(seen_ids)} 篇")

    papers.sort(key=lambda x: x["published"], reverse=True)
    fresh = papers[:5]  # 每次最多取 5 篇新的
    print(f"  ✅ 本次新增 {len(fresh)} 篇 ArXiv 论文")
    return fresh


def generate_arxiv_json(papers):
    """生成 arxiv.json 供 Dashboard 使用"""
    arxiv_json = os.path.join(REPO_DIR, "arxiv.json")
    with open(arxiv_json, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"  ✅ arxiv.json 已更新 ({len(papers)} 篇)")


def generate_report(trending, top_projects, papers=None):
    """生成日报 HTML 报告 — 每日精选 AI Agent 项目，一句话简介 + 链接详情页"""
    print("📄 生成日报...")
    papers = papers or []
    all_papers = papers if len(papers) <= 5 else papers[:5]

    # 计算统计
    total_stars = sum(p["stars_raw"] for p in top_projects)
    langs = {}
    for p in top_projects:
        l = p.get("language") or "Unknown"
        langs[l] = langs.get(l, 0) + 1

    # 分类统计
    cat_count = {}
    for p in top_projects:
        for tag in p["tags"]:
            cat_count[tag] = cat_count.get(tag, 0) + 1
    cats_sorted = sorted(cat_count.items(), key=lambda x: x[1], reverse=True)

    # 一句话简介：来自 PROJECT_ANALYSIS_DETAIL 的 summary
    def one_liner(name):
        detail = PROJECT_ANALYSIS_DETAIL.get(name)
        return detail["summary"] if detail else (trending[[t["name"] for t in trending].index(name)]["description"] if name in [t["name"] for t in trending] else "AI Agent 相关热门项目")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{TODAY} AI Agent 每日简报</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="AI Agent 领域每日动态 — {TODAY} GitHub 热门项目精选">
  <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
  <script src="https://unpkg.com/element-plus@2.4.1/dist/index.full.min.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/element-plus@2.4.1/dist/index.css">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f7fa;color:#1a1a2e;line-height:1.6}}
    .container{{max-width:1100px;margin:0 auto;padding:32px 24px}}
    .page-header{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:40px;color:#fff;margin-bottom:32px;position:relative;overflow:hidden}}
    .page-header::after{{content:' ';position:absolute;bottom:-40px;right:-40px;width:200px;height:200px;background:radial-gradient(circle,rgba(64,158,255,.2),transparent 70%);border-radius:50%}}
    .page-header h1{{font-size:26px;font-weight:700;margin-bottom:8px}}
    .page-header .subtitle{{color:rgba(255,255,255,.6);font-size:14px;margin-bottom:4px}}
    .page-header .date-info{{color:#409EFF;font-size:13px;margin-top:16px}}
    .stats-row{{display:flex;gap:20px;margin-top:24px;flex-wrap:wrap}}
    .stat-box{{background:rgba(64,158,255,.1);border:1px solid rgba(64,158,255,.25);border-radius:10px;padding:14px 20px;text-align:center;min-width:110px}}
    .stat-num{{font-size:22px;font-weight:700;color:#409EFF}}
    .stat-label{{font-size:11px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1px;margin-top:4px}}
    .section{{margin-bottom:28px}}
    .section-title{{font-size:16px;font-weight:600;margin-bottom:14px;color:#1a1a2e;display:flex;align-items:center;gap:8px}}
    .proj-card{{background:#fff;border-radius:10px;padding:14px 16px;margin-bottom:10px;border:1px solid #f0f0f0;transition:all .2s}}
    .proj-card:hover{{border-color:#409EFF;box-shadow:0 2px 12px rgba(64,158,255,.1)}}
    .proj-row{{display:flex;align-items:flex-start;gap:12px}}
    .rank{{font-size:18px;font-weight:700;color:#dcdfe6;width:28px;padding-top:2px;text-align:center;flex-shrink:0}}
    .rank.top1{{color:#f5a623}}.rank.top2{{color:#909399}}.rank.top3{{color:#cd7f32}}
    .proj-main{{flex:1;min-width:0}}
    .proj-name{{font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:3px}}
    .proj-name a{{color:#409EFF;text-decoration:none}}
    .proj-name a:hover{{text-decoration:underline}}
    .proj-brief{{font-size:13px;color:#666;margin-bottom:6px;line-height:1.5}}
    .proj-meta{{display:flex;gap:10px;font-size:12px;color:#b0c4de;flex-wrap:wrap;align-items:center}}
    .proj-lang{{color:#409EFF;font-weight:500}}
    .proj-tag{{padding:1px 7px;background:#ecf5ff;color:#409EFF;border-radius:4px;font-size:11px}}
    .detail-link{{color:#909399;font-size:12px;text-decoration:none;margin-left:auto;flex-shrink:0;padding-top:2px}}
    .detail-link:hover{{color:#409EFF}}
    table{{width:100%;border-collapse:collapse}}
    th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid #f0f0f0;font-size:13px}}
    th{{background:#fafafa;font-weight:600;color:#606266;font-size:11px;text-transform:uppercase;letter-spacing:.5px}}
    tr:hover{{background:#f5f7fa}}
    .footer{{text-align:center;padding:20px;color:#b0c4de;font-size:12px;margin-top:24px;border-top:1px solid #f0f0f0}}
    .footer a{{color:#409EFF}}
    .arxiv-card{{background:#fff;border-radius:10px;padding:14px 16px;margin-bottom:10px;border:1px solid #f0f0f0}}
    .arxiv-title{{font-size:13px;font-weight:600;color:#1a1a2e;margin-bottom:4px}}
    .arxiv-title a{{color:#409EFF;text-decoration:none}}
    .arxiv-title a:hover{{text-decoration:underline}}
    .arxiv-meta{{font-size:12px;color:#999;margin-bottom:4px}}
    .arxiv-abs{{font-size:12px;color:#666;line-height:1.5}}
  </style>
</head>
<body>
<div id="app" class="container">
  <div class="page-header">
    <h1>🤖 {TODAY} AI Agent 每日简报</h1>
    <p class="subtitle">GitHub 热门 AI Agent 项目精选 · 点击项目名称查看深度解读</p>
    <div class="date-info">📅 {datetime.now().strftime('%A, %B %d, %Y')} · 每周日自动生成周报</div>
    <div class="stats-row">
      <div class="stat-box"><div class="stat-num">{len(top_projects)}</div><div class="stat-label">精选项目</div></div>
      <div class="stat-box"><div class="stat-num">{total_stars//1000}.{total_stars%1000//100}k</div><div class="stat-label">总 Stars</div></div>
      <div class="stat-box"><div class="stat-num">{len(langs)}</div><div class="stat-label">语言</div></div>
      <div class="stat-box"><div class="stat-num">{len(cats_sorted)}</div><div class="stat-label">分类</div></div>
    </div>
  </div>

  <!-- 分类分布 -->
  <div class="section">
    <div class="section-title">📊 分类分布</div>
    <table>
      <tr><th>#</th><th>分类</th><th>项目数</th><th>占比</th></tr>
"""
    for i, (cat, cnt) in enumerate(cats_sorted[:10], 1):
        pct = cnt / len(top_projects) * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        html += f"      <tr><td>{i}</td><td><b>{cat}</b></td><td>{cnt}</td><td>{bar} {pct:.0f}%</td></tr>\n"

    html += f"""    </table>
  </div>

  <!-- 每日精选项目 -->
  <div class="section">
    <div class="section-title">🔥 每日精选 · {len(top_projects)} 个热门项目</div>
"""
    for i, p in enumerate(top_projects[:15], 1):
        rank_cls = f"top{i}" if i <= 3 else ""
        name = p["name"]
        brief = one_liner(name)
        tags_html = "".join(f'<span class="proj-tag">{t}</span>' for t in (p["tags"][:3]))
        detail_slug = slugify(name)
        html += f"""    <div class="proj-card">
      <div class="proj-row">
        <span class="rank {rank_cls}">#{i}</span>
        <div class="proj-main">
          <div class="proj-name"><a href="/agent/detail/{detail_slug}.html" target="_blank">{name}</a> {tags_html}</div>
          <div class="proj-brief">{brief}</div>
          <div class="proj-meta">
            <span class="proj-lang">{p['language']}</span>
            <span>⭐ {p['stars']}</span>
            <span>🍴 {p['forks']}</span>
          </div>
        </div>
        <a class="detail-link" href="/agent/detail/{detail_slug}.html" target="_blank">深度解读 →</a>
      </div>
    </div>
"""

    html += f"""  </div>

  <!-- 语言分布 -->
  <div class="section">
    <div class="section-title">💻 语言分布</div>
    <table>
      <tr><th>语言</th><th>项目数</th><th>占比</th></tr>
"""
    for lang, cnt in sorted(langs.items(), key=lambda x: x[1], reverse=True):
        pct = cnt / len(top_projects) * 100
        html += f"      <tr><td><b>{lang}</b></td><td>{cnt}</td><td>{pct:.0f}%</td></tr>\n"

    html += f"""    </table>
  </div>

  <!-- ArXiv 最新论文 -->
  <div class="section">
    <div class="section-title">📚 ArXiv 最新论文</div>
"""
    if papers:
        for p in all_papers:
            tags_html = "".join(f'<span class="proj-tag">{t}</span>' for t in (p["tags"][:2]))
            html += f"""    <div class="arxiv-card">
      <div class="arxiv-title"><a href="{p['url']}" target="_blank">{p['title']}</a> {tags_html}</div>
      <div class="arxiv-meta">{p['authors']} · {p['published']}</div>
      <div class="arxiv-abs">{p['summary'][:150]}...</div>
    </div>
"""
    else:
        html += """    <p style="color:#999;font-size:13px;padding:12px 0;">暂无论文数据（ArXiv API 限流中，明日自动重试）</p>\n"""

    html += f"""  </div>

  <div class="footer">
    © {datetime.now().year} AI Agent 前沿追踪 ·
    报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ·
    <a href="/agent/index.html">Dashboard</a> ·
    <a href="/agent/weekly.html">周报总览</a>
  </div>
</div>
<script>
const {{ createApp }} = Vue
createApp({{}}).use(ElementPlus).mount('#app')
</script>
</body>
</html>
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ 日报已写入: {REPORT_PATH}")
    return REPORT_PATH

# ── 周报生成 ─────────────────────────────────────────────────────────────────
def get_iso_week():
    """获取当前 ISO 周信息"""
    now = datetime.now(timezone(timedelta(hours=8)))
    iso = now.isocalendar()
    return iso[1], iso[0]  # week number, year

def generate_weekly_report():
    """扫描所有日报，生成周报"""
    import glob
    week_num, year = get_iso_week()
    weekly_file = f"weekly-{year}-W{week_num:02d}.html"

    # 收集本周所有日报
    today_dt = datetime.now(timezone(timedelta(hours=8)))
    weekday = today_dt.weekday()  # 0=Monday
    week_start = (today_dt - timedelta(days=weekday)).strftime("%Y-%m-%d")

    reports = []
    for f in sorted(glob.glob(os.path.join(REPO_DIR, "report-*.html"))):
        fname = os.path.basename(f)
        date_str = fname.replace("report-", "").replace(".html", "")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.strftime("%Y-%m-%d") >= week_start:
                reports.append({"date": date_str, "file": fname})
        except:
            pass

    reports.sort(key=lambda x: x["date"], reverse=True)

    # 收集 trending 数据用于周度统计
    all_projects = {}  # name -> (stars, forks, tags, description)
    for r in reports:
        fname = os.path.join(REPO_DIR, r["file"])
        try:
            with open(fname, "r", encoding="utf-8") as f:
                content = f.read()
            # 从 HTML 中提取项目数据（简易解析）
            import re as re2
            names = re2.findall(r'href="/agent/detail/([\w\-]+/[\w\-]+)\.html"', content)
            for slug in names:
                name = slug.replace("-", "/", 1)
                stars_m = re2.search(rf'{re2.escape(name)}.*?⭐\s*([\d\.]+k)', content, re2.DOTALL)
                forks_m = re2.search(rf'{re2.escape(name)}.*?🍴\s*([\d\.]+k)', content, re2.DOTALL)
                if name not in all_projects:
                    all_projects[name] = {"stars": stars_m.group(1) if stars_m else "—",
                                          "forks": forks_m.group(1) if forks_m else "—",
                                          "weeks_appeared": 1}
                else:
                    all_projects[name]["weeks_appeared"] += 1
        except:
            pass

    # 周度热门 TOP
    top_this_week = sorted(all_projects.items(), key=lambda x: x[1]["weeks_appeared"], reverse=True)[:20]

    weekly_path = os.path.join(REPO_DIR, weekly_file)

    # 每周归档入口
    archive_entries = ""
    for f in sorted(glob.glob(os.path.join(REPO_DIR, "weekly-*.html")), reverse=True)[:8]:
        fname = os.path.basename(f)
        archive_entries += f'      <li><a href="/agent/{fname}">{fname.replace(".html","").replace("-"," ").replace("_"," ")}</a></li>\n'

    # 本周日列表
    day_rows = ""
    for r in reports:
        day_name = datetime.strptime(r["date"], "%Y-%m-%d").strftime("%A")
        day_rows += f"      <tr><td>{r['date']}</td><td>{day_name}</td><td><a href='/agent/{r['file']}' style='color:#409EFF'>查看日报 →</a></td></tr>\n"

    # 周度项目趋势
    trend_rows = ""
    for i, (name, data) in enumerate(top_this_week, 1):
        tags_m = PROJECT_ANALYSIS_DETAIL.get(name, {}).get("tags", []) if name in PROJECT_ANALYSIS_DETAIL else []
        tags_html = "".join(f'<span style="padding:1px 6px;background:#ecf5ff;color:#409EFF;border-radius:4px;font-size:11px;margin-right:4px">{t}</span>' for t in tags_m[:3])
        slug = slugify(name)
        trend_rows += f"""      <tr>
        <td>{i}</td>
        <td><a href="/agent/detail/{slug}.html" style="color:#409EFF">{name}</a></td>
        <td>{tags_html}</td>
        <td>{data['stars']}</td>
        <td>{data['weeks_appeared']}次</td>
      </tr>\n"""

    week_date_range = f"{week_start} ~ {TODAY}"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>第 {week_num} 周 AI Agent 周报 {year} | AI Agent 追踪</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/element-plus@2.4.1/dist/index.css">
  <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
  <script src="https://unpkg.com/element-plus@2.4.1/dist/index.full.min.js"></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f7fa;color:#1a1a2e;line-height:1.6}}
    .container{{max-width:1100px;margin:0 auto;padding:32px 24px}}
    .hero{{background:linear-gradient(135deg,#1a1a2e,#2d1b4e);border-radius:16px;padding:40px;color:#fff;margin-bottom:32px}}
    .hero h1{{font-size:26px;font-weight:700;margin-bottom:8px}}
    .hero p{{color:rgba(255,255,255,.6);font-size:14px}}
    .hero .week-range{{color:#409EFF;font-size:14px;margin-top:12px}}
    .stats-row{{display:flex;gap:20px;margin-top:24px;flex-wrap:wrap}}
    .stat-box{{background:rgba(64,158,255,.1);border:1px solid rgba(64,158,255,.25);border-radius:10px;padding:14px 20px;text-align:center;min-width:110px}}
    .stat-num{{font-size:22px;font-weight:700;color:#409EFF}}
    .stat-label{{font-size:11px;color:rgba(255,255,255,.5);text-transform:uppercase}}
    .section{{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;border:1px solid #f0f0f0}}
    .section h2{{font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #409EFF}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}
    th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid #f0f0f0}}
    th{{background:#fafafa;font-weight:600;color:#606266;font-size:11px;text-transform:uppercase}}
    tr:hover{{background:#f5f7fa}}
    .footer{{text-align:center;padding:20px;color:#b0c4de;font-size:12px;margin-top:24px;border-top:1px solid #f0f0f0}}
    .footer a{{color:#409EFF}}
    .day-link{{color:#409EFF;text-decoration:none}}
    .day-link:hover{{text-decoration:underline}}
    .archive-list{{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0}}
    .archive-list li a{{padding:6px 14px;background:#ecf5ff;color:#409EFF;border-radius:20px;text-decoration:none;font-size:13px;transition:all .2s}}
    .archive-list li a:hover{{background:#409EFF;color:#fff}}
  </style>
</head>
<body>
<div class="container">
  <div class="hero">
    <h1>📆 第 {week_num} 周 AI Agent 周报</h1>
    <p>GitHub AI Agent 项目每周趋势追踪 · {year} 年度</p>
    <div class="week-range">📅 {week_date_range}</div>
    <div class="stats-row">
      <div class="stat-box"><div class="stat-num">{len(reports)}</div><div class="stat-label">本周日报数</div></div>
      <div class="stat-box"><div class="stat-num">{len(all_projects)}</div><div class="stat-label">本周出现项目</div></div>
      <div class="stat-box"><div class="stat-num">{len([n for n,d in all_projects.items() if d['weeks_appeared']>=3])}</div><div class="stat-label">连续热门</div></div>
    </div>
  </div>

  <div class="section">
    <h2>📅 本周日速览</h2>
    <table>
      <tr><th>日期</th><th>星期</th><th>链接</th></tr>
      {day_rows if day_rows else "<tr><td colspan='3' style='color:#999'>暂无日报数据</td></tr>"}
    </table>
  </div>

  <div class="section">
    <h2>🔥 本周项目热度 TOP {len(top_this_week)}</h2>
    <table>
      <tr><th>#</th><th>项目</th><th>分类</th><th>Stars</th><th>出现次数</th></tr>
      {trend_rows if trend_rows else "<tr><td colspan='5' style='color:#999'>暂无数据</td></tr>"}
    </table>
  </div>

  <div class="section">
    <h2>📂 历史周报归档</h2>
    <ul class="archive-list">
      {archive_entries if archive_entries else "<li>暂无历史周报</li>"}
    </ul>
  </div>

  <div class="footer">
    © {datetime.now().year} AI Agent 前沿追踪 ·
    <a href="/agent/index.html">Dashboard</a> ·
    <a href="/agent/report-{TODAY}.html">今日日报</a>
  </div>
</div>
</body>
</html>
"""
    with open(weekly_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ 周报已生成: {weekly_path} (第{week_num}周, {len(reports)}篇日报)")
    return weekly_file

# ── trending.json 生成 ──────────────────────────────────────────────────────
def generate_trending_json(trending):
    """生成 dashboard 用的 trending.json"""
    # 简化版：去掉 raw 数据
    simple = []
    for t in trending[:15]:
        simple.append({
            "rank": t["rank"],
            "name": t["name"],
            "description": t["description"],
            "language": t["language"],
            "stars": t["stars"],
            "todayStars": t["todayStars"],
            "forks": t["forks"],
            "tags": t["tags"],
            "url": t["url"],
        })
    with open(TRENDING_JSON, "w", encoding="utf-8") as f:
        json.dump(simple, f, ensure_ascii=False, indent=2)
    print(f"  ✅ trending.json 已更新: {TRENDING_JSON}")

# ── pages.json 更新 ─────────────────────────────────────────────────────────
def update_pages_json():
    """收集所有 HTML 文件生成 pages.json"""
    html_files = sorted([f for f in os.listdir(REPO_DIR) if f.endswith(".html") and f != "index.html"])
    with open(PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(html_files, f, ensure_ascii=False, indent=2)
    print(f"  ✅ pages.json 已更新 ({len(html_files)} 个页面)")

# ── Git 操作 ───────────────────────────────────────────────────────────────
def git_commit_push(repo_path, message):
    """Git add + commit + push"""
    try:
        # 动态获取当前分支名
        branch = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        subprocess.run(["git", "-C", repo_path, "add", "."], check=True, capture_output=True)
        if subprocess.run(["git", "-C", repo_path, "diff", "--cached", "--quiet"], check=False).returncode != 0:
            subprocess.run(["git", "-C", repo_path, "commit", "-m", message], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", repo_path, "push", "origin", branch], check=True, capture_output=True, timeout=30)
            print(f"  ✅ {os.path.basename(repo_path)} ({branch}) 已提交推送")
            return True
        else:
            print(f"  ⏭️  {os.path.basename(repo_path)} 无变更，跳过")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Git 操作失败: {e.stderr or e}")
        return False

# ── 同步到 pages repo ────────────────────────────────────────────────────────
def sync_to_pages():
    """复制 agent 仓的静态文件到 pages 仓的 agent 目录"""
    os.makedirs(AGENT_IN_PAGES, exist_ok=True)

    # 1. 根目录的 html 和 json 文件
    for fname in os.listdir(REPO_DIR):
        if fname.endswith(".html") or fname.endswith(".json"):
            src = os.path.join(REPO_DIR, fname)
            dst = os.path.join(AGENT_IN_PAGES, fname)
            with open(src, "r", encoding="utf-8") as sf:
                with open(dst, "w", encoding="utf-8") as df:
                    df.write(sf.read())

    # 2. detail/ 目录（详细解读页）
    detail_src = os.path.join(REPO_DIR, "detail")
    detail_dst = os.path.join(AGENT_IN_PAGES, "detail")
    if os.path.isdir(detail_src):
        import shutil
        if os.path.exists(detail_dst):
            shutil.rmtree(detail_dst)
        shutil.copytree(detail_src, detail_dst)

    print(f"  ✅ 静态文件已同步到 {AGENT_IN_PAGES}")

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print(f"🚀 AI Agent Scanner 启动 | 日期: {TODAY}")
    print("="*50)

    # 1. 扫描 GitHub
    trending, top_projects = scan_github()

    # 1b. 扫描 ArXiv（出错则跳过，不阻塞主流程）
    print("\n→ 扫描 ArXiv AI Agent 论文...")
    try:
        papers = scan_arxiv()
        generate_arxiv_json(papers)
    except Exception as e:
        print(f"  ⚠️  ArXiv 扫描失败，已跳过: {e}")
        papers = []
        with open('arxiv.json', 'w') as f:
            json.dump([], f)

    # 2. 生成趋势分析报告（trend_report.json）
    print("\n📊 生成中文趋势分析报告...")
    try:
        from scan_trending import generate_trend_report, filter_ai_agent, parse_trending, fetch_github_trending
        html = fetch_github_trending()
        if html:
            projects = parse_trending(html)
            ai_projects = filter_ai_agent(projects)
            trend_report = generate_trend_report(ai_projects)
            with open(os.path.join(REPO_DIR, "trend_report.json"), 'w', encoding='utf-8') as f:
                json.dump(trend_report, f, ensure_ascii=False, indent=2)
            print(f"  ✅ trend_report.json 已生成")
        else:
            print("  ⚠️  无法获取 GitHub Trending，跳过趋势分析")
    except Exception as e:
        print(f"  ⚠️  趋势分析失败: {e}")

    # 3. 生成每日精选（curated.json + curated.html）
    print("\n⭐ 生成每日精选报告...")
    try:
        from scan_curated import generate_curated_projects, generate_curated_html
        trending_path = os.path.join(REPO_DIR, "trending.json")
        if os.path.exists(trending_path):
            with open(trending_path, 'r', encoding='utf-8') as f:
                trending_projects = json.load(f)
            curated = generate_curated_projects(trending_projects)
            with open(os.path.join(REPO_DIR, "curated.json"), 'w', encoding='utf-8') as f:
                json.dump(curated, f, ensure_ascii=False, indent=2)
            curated_html = generate_curated_html(curated)
            with open(os.path.join(REPO_DIR, "curated.html"), 'w', encoding='utf-8') as f:
                f.write(curated_html)
            print(f"  ✅ curated.json + curated.html 已生成 ({len(curated)} 个精选项目)")
    except Exception as e:
        print(f"  ⚠️  每日精选生成失败: {e}")

    # 4. 生成详细解读页（detail/ 目录）
    print("\n📝 生成详细解读页...")
    generate_detail_pages(top_projects)

    # 5. 生成日报
    generate_report(trending, top_projects)

    # 6. 生成 trending.json
    generate_trending_json(trending)

    # 7. 生成周报
    print("\n📆 生成周报...")
    weekly_file = generate_weekly_report()

    # 8. 生成归档首页 reports.html
    print("\n📚 生成归档首页...")
    generate_reports_html()

    # 9. 更新 pages.json（包含新文件）
    update_pages_json()

    # 8. 提交 agent 仓
    print("\n📦 提交 agent 仓...")
    git_commit_push(REPO_DIR, f"Daily update {TODAY}: report + detail pages + weekly + arxiv")

    # 9. 同步到 pages 仓
    print("\n📦 同步到 leapord.github.io...")
    sync_to_pages()
    git_commit_push(PAGES_REPO_DIR, f"Update agent static site {TODAY}")

    # 10. 生成监控页
    generate_monitor_page()

    # 11. 推送企业微信通知
    print("\n📨 推送企业微信通知...")
    try:
        send_wecom_notification()
    except Exception as e:
        print(f"  ⚠️  企业微信通知失败: {e}")


def send_wecom_notification():
    """扫描完成后推送企业微信机器人消息"""
    import urllib.request, urllib.error

    webhook_key = os.environ.get("WECOM_WEBHOOK_KEY", "")
    if not webhook_key:
        print("  ⚠️  未配置 WECOM_WEBHOOK_KEY 环境变量，跳过企业微信通知")
        return
    WEBHOOK_URL = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"

    # 读取今日数据
    curated_path = os.path.join(REPO_DIR, "curated.json")
    trend_path = os.path.join(REPO_DIR, "trend_report.json")

    top_projects = []
    insights = {}
    if os.path.exists(curated_path):
        with open(curated_path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                top_projects = data[:5]  # 取前5

    if os.path.exists(trend_path):
        with open(trend_path, encoding="utf-8") as f:
            report = json.load(f)
            insights = {
                "directions": report.get("热门方向", report.get("directions", [])),
                "languages": report.get("主要语言", report.get("languages", [])),
                "top_projects": report.get("TOP项目", report.get("top_projects", [])),
            }

    # 构造 Markdown 消息
    lines = [
        "### 🤖 AI Agent 每日扫描报告",
        f"**📅 {TODAY}**  自动更新",
        "",
        "---",
    ]

    if top_projects:
        lines.append("**⭐ 每日精选 TOP 5**")
        for i, p in enumerate(top_projects, 1):
            name = p.get("name", "unknown")
            stars = p.get("stars", "—")
            lang = p.get("language", "—")
            desc = (p.get("description") or p.get("digest", ""))[:40]
            lines.append(f"{i}. `{name.split('/')[-1]}` ⭐{stars} · {lang}")
            if desc:
                lines.append(f"   > {desc}")
        lines.append("")

    if insights:
        dirs = insights.get("directions", [])
        langs = insights.get("languages", [])
        tops = insights.get("top_projects", [])
        if dirs:
            lines.append(f"**🔥 热门方向**: {' · '.join(str(d) for d in dirs)}")
        if langs:
            lines.append(f"**💻 主要语言**: {' · '.join(str(l) for l in langs)}")
        if tops:
            lines.append(f"**🏆 TOP 项目**: {' · '.join(str(t) for t in tops)}")

    lines += [
        "",
        "---",
        f"[📊 查看 Dashboard](https://leapord.github.io/agent/)",
        f"[📰 每日精选](https://leapord.github.io/agent/curated.html)",
        f"[📚 报告归档](https://leapord.github.io/agent/reports.html)",
    ]

    payload = json.dumps({
        "msgtype": "markdown",
        "markdown": {
            "content": "\n".join(lines)
        }
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("errcode") == 0:
                print("  ✅ 企业微信通知已发送")
            else:
                print(f"  ⚠️  企业微信返回错误: {result}")
    except urllib.error.URLError as e:
        print(f"  ⚠️  企业微信请求失败: {e}")


def generate_monitor_page():
    """生成系统监控状态页 monitor.html"""
    import glob
    logs = []
    log_files = sorted(glob.glob(os.path.join(REPO_DIR, "logs", "deploy-*.log")), reverse=True)[:30]
    for lf in log_files:
        fname = os.path.basename(lf)
        try:
            with open(lf) as f:
                content = f.read()
            # 提取关键信息
            started = re.search(r"开始\s*\|\s*(.+)", content)
            github_count = re.search(r"获取\s*(\d+)\s*个热门", content)
            arxiv_count = re.search(r"ArXiv\s*论文:\s*(\d+)\s*篇", content)
            pushed = "✅" if "已提交推送" in content or "pushed" in content else "❌"
            logs.append({
                "date": fname.replace("deploy-", "").replace(".log", ""),
                "file": fname,
                "started": started.group(1).strip() if started else "—",
                "github": int(github_count.group(1)) if github_count else 0,
                "arxiv": int(arxiv_count.group(1)) if arxiv_count else 0,
                "pushed": pushed,
                "status": "✅成功" if pushed == "✅" else "⚠️需检查",
            })
        except:
            logs.append({"date": fname.replace("deploy-","").replace(".log",""), "file":fname, "started":"—", "github":0, "arxiv":0, "pushed":"❌", "status":"❌失败"})

    # 写 monitor.json
    with open(MONITOR_JSON, "w") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    # 生成 HTML
    success_rate = f"{sum(1 for l in logs if l['pushed']=='✅')}/{len(logs)}" if logs else "—"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>Agent 系统监控</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/element-plus@2.4.1/dist/index.css">
  <script src="https://unpkg.com/element-plus@2.4.1/dist/index.full.min.js"></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Inter','PingFang SC',sans-serif;background:#f5f7fa;padding:24px;color:#1a1a2e}}
    h1{{font-size:22px;font-weight:700;margin-bottom:20px}}
    .summary{{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}}
    .sum-card{{background:#fff;border-radius:10px;padding:16px 24px;border:1px solid #f0f0f0;min-width:140px;text-align:center}}
    .sum-card .num{{font-size:28px;font-weight:700;color:#409EFF}}
    .sum-card .label{{font-size:11px;color:#999;margin-top:4px;text-transform:uppercase}}
    table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;border:1px solid #f0f0f0}}
    th,td{{padding:12px 16px;text-align:left;font-size:13px;border-bottom:1px solid #f0f0f0}}
    th{{background:#fafafa;font-weight:600;color:#606266;font-size:12px;text-transform:uppercase}}
    tr:hover{{background:#f5f7fa}}
    .ok{{color:#67c23a;font-weight:600}} .err{{color:#f56c6c;font-weight:600}}
    tr:last-child td{{border-bottom:none}}
    .back{{display:inline-block;margin-top:20px;font-size:13px;color:#409EFF}}
  </style>
</head>
<body>
<div id="app">
  <h1>🤖 Agent 系统监控</h1>
  <div class="summary">
    <div class="sum-card"><div class="num">{len(logs)}</div><div class="label">执行记录</div></div>
    <div class="sum-card"><div class="num">{success_rate}</div><div class="label">推送成功率</div></div>
    <div class="sum-card"><div class="num">{datetime.now().strftime('%H:%M:%S')}</div><div class="label">最后检查</div></div>
  </div>
  <table>
    <tr><th>日期</th><th>开始时间</th><th>GitHub 项目</th><th>ArXiv 论文</th><th>Git 推送</th><th>状态</th></tr>
"""
    for log in logs[:20]:
        status_cls = "ok" if log["pushed"] == "✅" else "err"
        html += f"    <tr><td>{log['date']}</td><td>{log['started']}</td><td>{log['github']}</td><td>{log['arxiv']}</td><td class='{status_cls}'>{log['pushed']}</td><td class='{status_cls}'>{log['status']}</td></tr>\n"

    html += f"""  </table>
  <a class="back" href="index.html">← 返回 Dashboard</a>
</div>
<script>createApp({{}}).use(ElementPlus).mount('#app')</script>
</body>
</html>
"""
    with open(os.path.join(REPO_DIR, "monitor.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ monitor.html 已生成")

# ── 归档首页生成 ───────────────────────────────────────────────────────────
WEEKDAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def generate_reports_html():
    """扫描 report-*.html 和 weekly-*.html，生成归档首页 reports.html"""
    import glob

    daily_reports = []
    for path in glob.glob(os.path.join(REPO_DIR, "report-????-??-??.html")):
        fname = os.path.basename(path)
        m = re.search(r'report-(\d{4}-\d{2}-\d{2})\.html', fname)
        if not m:
            continue
        date_str = m.group(1)
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = WEEKDAYS[dt.weekday()]
        except:
            weekday = ""
        # 从 HTML 中提取概览数据
        proj_count = total_stars = arxiv_count = "—"
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            # 统计数字在 stat-box 中，按顺序：精选项目/总Stars/语言/分类
            stat_nums = re.findall(r'class="stat-num">([^<]+)</div>', content)
            if len(stat_nums) >= 1: proj_count = stat_nums[0]
            if len(stat_nums) >= 2: total_stars = stat_nums[1]
            if len(stat_nums) >= 4: arxiv_count = stat_nums[3]  # 分类数占位
            # 热点标签
            tag_matches = re.findall(r'class="proj-tag"[^>]*>([^<]+)</span>', content)
            from collections import Counter
            tag_counts = Counter(tag_matches)
            hot_topics = [t for t, _ in tag_counts.most_common(4)]
            # Top 项目
            proj_matches = re.findall(r'class="proj-name"[^>]*>.*?<a[^>]*>([^<]+)</a>', content)
            star_matches = re.findall(r'⭐\s*([\d.]+[kK]?)', content)
            for i, (name, stars) in enumerate(zip(proj_matches[:3], star_matches[:3])):
                top_projects.append({"rank": f"#{i+1}", "name": name.strip(), "stars": stars})
        except:
            pass
        daily_reports.append({
            "type": "daily",
            "date": date_str,
            "url": f"/agent/{fname}",
            "weekday": weekday,
            "projCount": proj_count,
            "totalStars": total_stars,
            "totalForks": "—",
            "arxivCount": arxiv_count,
            "hotTopics": hot_topics,
            "topProjects": top_projects,
        })

    weekly_reports = []
    for path in glob.glob(os.path.join(REPO_DIR, "weekly-????-W*.html")):
        fname = os.path.basename(path)
        m = re.search(r'weekly-(\d{4}-W\d+)', fname)
        if not m:
            continue
        week_id = m.group(1)
        year, wnum = week_id.split('-W')
        date_range = ""
        title = f"{year}年第{int(wnum)}周 AI Agent 研究周报"
        summary = ""
        daily_links = []
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            dr = re.search(r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})', content)
            if dr:
                date_range = f"{dr.group(1)} ~ {dr.group(2)}"
            sm = re.search(r'<p class="weekly-desc">([^<]+)</p>', content)
            if sm:
                summary = sm.group(1).strip()
            daily_links_m = re.findall(r'href="(report-\d{4}-\d{2}-\d{2}\.html)"', content)
            daily_dates = re.findall(r'report-(\d{4}-\d{2}-\d{2})\.html', content)
            daily_links = [{"date": d, "url": f"/agent/report-{d}.html"} for d in daily_dates]
        except:
            pass
        weekly_reports.append({
            "type": "weekly",
            "id": week_id,
            "url": f"/agent/{fname}",
            "title": title,
            "summary": summary or f"本周共收录 {len(daily_links)} 篇日报",
            "dateRange": date_range,
            "weekNum": wnum,
            "dailyLinks": daily_links,
        })

    reports_data = weekly_reports + daily_reports
    reports_json = json.dumps(reports_data, ensure_ascii=False)

    # 生成 HTML（嵌入数据）
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>报告归档 · AI Agent 前沿追踪</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="AI Agent 研究报告归档 — 每日热点概览与周报汇总">
  <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
  <script src="https://unpkg.com/element-plus@2.4.1/dist/index.full.min.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/element-plus@2.4.1/dist/index.css">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.6}}
    a{{text-decoration:none;color:inherit}}
    .site-header{{background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.07);position:sticky;top:0;z-index:100}}
    .header-inner{{max-width:1200px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:56px}}
    .site-logo{{font-size:17px;font-weight:700;display:flex;align-items:center;gap:6px}}
    .header-nav{{display:flex;gap:20px}}
    .header-nav a{{font-size:13px;color:#606266;transition:color .2s}}
    .header-nav a:hover{{color:#409EFF}}
    .header-nav a.active{{color:#409EFF;font-weight:600}}
    .breadcrumb-wrap{{background:#fff;border-bottom:1px solid #f0f0f0}}
    .breadcrumb-inner{{max-width:1200px;margin:0 auto;padding:10px 24px;display:flex;align-items:center;gap:8px;font-size:13px;color:#909399}}
    .breadcrumb-inner a{{color:#606266}}
    .breadcrumb-inner a:hover{{color:#409EFF}}
    .page-wrap{{max-width:1200px;margin:0 auto;padding:24px}}
    .page-title{{font-size:22px;font-weight:700;margin-bottom:6px}}
    .page-subtitle{{font-size:13px;color:#909399;margin-bottom:24px}}
    .section{{margin-bottom:32px}}
    .section-title{{font-size:15px;font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px}}
    .nav-tabs{{display:flex;gap:4px;margin-bottom:20px;border-bottom:2px solid #f0f0f0;padding-bottom:0}}
    .nav-tab{{padding:8px 16px;font-size:13px;color:#606266;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .2s}}
    .nav-tab:hover{{color:#409EFF}}
    .nav-tab.active{{color:#409EFF;border-bottom-color:#409EFF;font-weight:600}}
    .daily-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:14px}}
    .daily-card{{background:#fff;border-radius:12px;padding:18px 20px;border:1px solid #f0f0f0;transition:all .2s;display:block}}
    .daily-card:hover{{border-color:#409EFF;box-shadow:0 2px 14px rgba(64,158,255,.1)}}
    .daily-card-header{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px}}
    .daily-card-date{{font-size:15px;font-weight:700}}
    .daily-card-weekday{{font-size:11px;color:#909399;margin-top:2px}}
    .daily-card-badge{{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;background:#ecf5ff;color:#409EFF;border-radius:8px;font-size:10px;font-weight:600}}
    .daily-card-stats{{display:flex;gap:12px;margin-bottom:10px;flex-wrap:wrap}}
    .dstat{{display:flex;align-items:center;gap:4px;font-size:12px;color:#606266}}
    .dstat strong{{color:#1a1a2e;font-weight:600}}
    .hot-topics{{margin-top:10px;padding-top:10px;border-top:1px solid #f5f5f5}}
    .hot-label{{font-size:11px;color:#f56c6c;font-weight:600;margin-bottom:6px;display:flex;align-items:center;gap:4px}}
    .hot-items{{display:flex;flex-wrap:wrap;gap:5px}}
    .hot-item{{display:inline-block;padding:2px 8px;background:#fef0f0;color:#f56c6c;border-radius:6px;font-size:11px}}
    .weekly-card{{background:#fff;border-radius:12px;padding:18px 20px;border:1px solid #f0f0f0;display:block;transition:all .2s}}
    .weekly-card:hover{{border-color:#67c23a;box-shadow:0 2px 14px rgba(103,194,58,.1)}}
    .weekly-meta{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
    .weekly-badge{{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;background:#f0f9eb;color:#67c23a;border-radius:8px;font-size:11px;font-weight:600}}
    .weekly-title{{font-size:16px;font-weight:700;margin-bottom:6px}}
    .weekly-desc{{font-size:12px;color:#606266;margin-bottom:12px;line-height:1.6}}
    .weekly-daily-list{{display:flex;flex-wrap:wrap;gap:8px}}
    .weekly-daily-link{{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:#f5f7fa;color:#606266;border-radius:6px;font-size:12px;transition:all .2s}}
    .weekly-daily-link:hover{{background:#409EFF;color:#fff}}
    .page-footer{{text-align:center;padding:20px;color:#b0b8c6;font-size:12px;border-top:1px solid #f0f0f0;margin-top:32px}}
    .page-footer a{{color:#409EFF}}
  </style>
</head>
<body>
<div id="app">
  <header class="site-header">
    <div class="header-inner">
      <div class="site-logo"><span>🤖</span> AI Agent 前沿追踪</div>
      <nav class="header-nav">
        <a href="/agent/">首页</a>
        <a href="/agent/reports.html" class="active">报告归档</a>
        <a href="/agent/trend.html">趋势分析</a>
        <a href="/agent/curated.html">每日精选</a>
      </nav>
    </div>
  </header>

  <div class="breadcrumb-wrap">
    <div class="breadcrumb-inner">
      <a href="/agent/">首页</a>
      <span>›</span>
      <span style="color:#1a1a2e">报告归档</span>
    </div>
  </div>

  <div class="page-wrap">
    <div class="page-title">📚 报告归档</div>
    <div class="page-subtitle">日报热点概览 · 周报汇总 · 最新论文</div>

    <div class="nav-tabs">
      <div class="nav-tab" :class="{{active:activeTab==='daily'}}" @click="activeTab='daily'">日报概览</div>
      <div class="nav-tab" :class="{{active:activeTab==='weekly'}}" @click="activeTab='weekly'">周报概览</div>
    </div>

    <!-- 日报概览 -->
    <div v-if="activeTab==='daily'">
      <div class="section">
        <div class="section-title">📅 日报概览 — 点击卡片查看当日完整项目列表</div>
        <div class="daily-grid">
          <a v-for="r in dailyReports" :key="r.date" :href="r.url" class="daily-card">
            <div class="daily-card-header">
              <div>
                <div class="daily-card-date">{{r.date}}</div>
                <div class="daily-card-weekday">{{r.weekday}}</div>
              </div>
              <span class="daily-card-badge">{{r.projCount}} 项目</span>
            </div>
            <div class="daily-card-stats">
              <div class="dstat">⭐ <strong>{{r.totalStars}}</strong></div>
              <div class="dstat">🍴 <strong>{{r.totalForks}}</strong></div>
              <div class="dstat" v-if="r.arxivCount!=='—'">📄 <strong>{{r.arxivCount}}</strong> 论文</div>
            </div>
            <div v-if="r.hotTopics && r.hotTopics.length" class="hot-topics">
              <div class="hot-label">🔥 热点分类</div>
              <div class="hot-items">
                <span v-for="t in r.hotTopics" :key="t" class="hot-item">{{t}}</span>
              </div>
            </div>
            <div v-if="r.topProjects && r.topProjects.length" style="margin-top:10px">
              <div v-for="p in r.topProjects" :key="p.name" style="font-size:12px;color:#606266;margin-bottom:3px;display:flex;align-items:center;gap:5px">
                <span style="color:#dcdfe6;font-weight:700">{{p.rank}}</span>
                <span style="color:#409EFF;font-weight:500">{{p.name}}</span>
                <span style="color:#909399;font-size:11px">⭐{{p.stars}}</span>
              </div>
            </div>
          </a>
        </div>
      </div>
    </div>

    <!-- 周报概览 -->
    <div v-if="activeTab==='weekly'">
      <div class="section">
        <div class="section-title">📆 周报概览 — 点击进入周报详情</div>
        <div class="daily-grid">
          <a v-for="w in weeklyReports" :key="w.id" :href="w.url" class="weekly-card">
            <div class="weekly-meta">
              <span class="weekly-badge">第{{w.weekNum}}周</span>
              <span style="font-size:12px;color:#909399">{{w.dateRange}}</span>
            </div>
            <div class="weekly-title">{{w.title}}</div>
            <div class="weekly-desc">{{w.summary}}</div>
            <div class="weekly-daily-list">
              <span v-for="d in w.dailyLinks" :key="d.date" class="weekly-daily-link">{{d.date}}</span>
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>

  <div class="page-footer">
    报告归档 · <a href="/agent/">AI Agent 前沿追踪</a> · 每日自动更新
  </div>
</div>

<script>
const {{createApp, ref, computed}} = Vue
createApp({{
  setup() {{
    const activeTab = ref('daily')
    const reports = ref(window._REPORTS_)
    const dailyReports = computed(() => reports.value.filter(r=>r.type==='daily').sort((a,b)=>b.date.localeCompare(a.date)))
    const weeklyReports = computed(() => reports.value.filter(r=>r.type==='weekly').sort((a,b)=>b.id.localeCompare(a.id)))
    return {{activeTab, reports, dailyReports, weeklyReports}}
  }}
}}).use(ElementPlus).mount('#app')
</script>
<script>window._REPORTS_={reports_json};</script>
</body>
</html>'''

    with open(os.path.join(REPO_DIR, "reports.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ reports.html 已生成 ({len(daily_reports)} 份日报, {len(weekly_reports)} 份周报)")


if __name__ == "__main__":
    main()
