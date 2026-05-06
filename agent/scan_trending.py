#!/usr/bin/env python3
"""
AI Agent GitHub Trending 趋势分析脚本
每天扫描 GitHub Trending AI Agent 项目，生成全中文行业趋势分析报告
生成文件：trending.json（项目列表）+ trend_report.json（趋势分析）
"""

import json
import re
import os
import time
import subprocess
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# ── AI Agent 过滤关键词 ────────────────────────────────────────────────────────
FILTER_KEYWORDS = [
    'agent', 'AI agent', 'llm agent', 'autonomous', 'multi-agent',
    'multi agent', 'tool use', 'rag', 'vector db', 'langchain',
    'dify', 'crewai', 'autogen', 'metagpt', 'mem0', 'deer-flow',
    'ragflow', 'openagents', 'agentic', 'memfree', 'llamaindex',
    'flowise', 'cherry-studio', 'agentgpt', 'openagent', 'chatbot'
]

# ── 中文行业趋势分析（静态洞察库）────────────────────────────────────────────
TREND_ANALYSIS = {
    "多智能体协作": {
        "icon": "🤝",
        "summary": "多智能体框架热度持续攀升，MetaGPT、CrewAI、AutoGen 三足鼎立",
        "detail": "2024 年是多智能体（Multi-Agent）元年。以 MetaGPT、CrewAI、AutoGen 为代表的多智能体框架正在重塑 AI 应用开发范式。MetaGPT 通过模拟软件公司 SOP 流程让 Agent 协作更规范；CrewAI 以极低上手门槛吸引入门用户；AutoGen 凭借微软背书在企业场景快速落地。三者各有优势：MetaGPT 适合复杂任务分解，CrewAI 适合快速原型，AutoGen 适合企业集成。预计 2025 年多智能体将深入业务流程自动化领域。",
        "technologies": ["MetaGPT", "CrewAI", "AutoGen", "ChatDev"],
        "star_range": "30k-67k ⭐"
    },
    "Agent 开发平台": {
        "icon": "🛠️",
        "summary": "低代码/零代码 Agent 平台爆发，Dify 14万 Stars 领跑",
        "detail": "Dify 和 Flowise 的崛起标志着 AI 应用开发进入「全民时代」。Dify 以 14 万 Stars 成为最热门 AI 应用开发平台，其工作流编排、RAG 引擎、Agent 模式三位一体，解决了从原型到生产的全链路需求。Flowise 以拖拽式低代码降低门槛，适合非技术背景用户。这一趋势说明：AI 应用开发正在从「高度定制」走向「标准化平台」，未来更多业务人员将直接参与 AI 应用搭建。",
        "technologies": ["Dify", "Flowise", "LangChain", "LangServe"],
        "star_range": "30k-140k ⭐"
    },
    "RAG 与知识检索": {
        "icon": "📚",
        "summary": "RAG 持续进化，从简单检索走向深度文档理解",
        "detail": "RAG（检索增强生成）依然是 AI Agent 的核心技术方向。2024 年的 RAG 不再是简单的向量相似度匹配，而是向「深度文档理解」演进。RAGFlow 通过复杂 PDF 解析、多跳问答能力超越传统 RAG；LlamaIndex 专注文档理解，提供多种索引策略；Dify 内置的 RAG 引擎则覆盖大多数标准场景。随着企业私有知识库需求爆发，RAG 技术将继续在「理解深度」和「检索效率」两个方向突破。",
        "technologies": ["RAGFlow", "LlamaIndex", "Dify RAG", "Quivr"],
        "star_range": "10k-79k ⭐"
    },
    "Agent 记忆架构": {
        "icon": "🧠",
        "summary": "记忆能力成为 Agent 差异化核心，Mem0 开辟新赛道",
        "detail": "「记不住」是 Agent 落地最大痛点之一。Mem0 针对性解决跨会话记忆、用户偏好存储、事实遗忘等问题，开辟了「Agent 记忆层」这一新赛道。Claude-mem 则为 Claude 用户提供会话压缩和长期上下文保持。记忆架构的重要性在于：真正有价值的 AI 助手必须「认识用户」，而非每次从零开始。随着 Agent 向个人助理场景渗透，记忆能力将成为标配。",
        "technologies": ["Mem0", "claude-mem", "LangChain Memory", "Context7"],
        "star_range": "5k-72k ⭐"
    },
    "Dev Agent": {
        "icon": "⚡",
        "summary": "Dev Agent 重塑软件开发，Dify、LangChain 分列一二",
        "detail": "Dev Agent（AI 编程 Agent）今年大爆发。Dify 和 LangChain 分别代表两种路线：Dify 以可视化工作流让产品经理也能搭建 AI 流程；LangChain 以高度定制化满足复杂 AI 流水线的技术需求。在 GitHub Trending 上，Dev Agent 类项目长期占据高位，说明市场对「用 AI 提升开发效率」的需求极为旺盛。2025 年预计更多 Dev Agent 将整合代码审查、自动化测试、CI/CD 等环节。",
        "technologies": ["Dify", "LangChain", "Devin", "GitHub Copilot"],
        "star_range": "135k-140k ⭐"
    },
    "工具调用与函数执行": {
        "icon": "🔧",
        "summary": "Tool Use/Function Calling 成为 Agent 与外界交互的标准接口",
        "detail": "Function Calling（函数调用）是 Agent 调用外部工具（搜索引擎、数据库、API）的主流方案。OpenAI、Anthropic、Google 都推出了各自的 Function Calling 规范，形成了事实标准。开源社区在此基础上构建了强大的工具生态：SerpAPI 搜索、Tavily 网页搜索、Browserbase 自动化浏览等。这一方向的竞争焦点在于：工具调用的稳定性、工具组合的灵活性、以及多步推理能力。",
        "technologies": ["OpenAI Function Calling", "LangChain Tools", "Semantic Kernel", "AgentSDK"],
        "star_range": "框架内置"
    }
}

# ── 扫描 GitHub Trending ────────────────────────────────────────────────────
def fetch_github_trending(language='', since='daily'):
    """抓取 GitHub Trending 页面"""
    url = f"https://github.com/trending?since={since}"
    if language:
        url += f"&l={language}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8')
        return html
    except Exception as e:
        print(f"  ⚠️ 抓取 GitHub Trending 失败: {e}")
        return ""

def parse_trending(html):
    """解析 GitHub Trending HTML，提取项目信息"""
    projects = []

    # 匹配每个项目块
    article_pattern = r'class="Box-row">(.*?)</article>'
    articles = re.findall(article_pattern, html, re.DOTALL)

    for article in articles:
        try:
            # ── 项目名：从 h2 中提取 ──────────────────────────
            name = ""
            h2_match = re.search(r'<h2 class="h3[^\"]*"[^>]*>(.*?)</h2>', article, re.DOTALL)
            if h2_match:
                h2 = h2_match.group(1)
                # owner/name 来自 href
                href_match = re.search(r'<a[^>]+href="(/[^"]+)"[^>]*>', h2)
                if href_match:
                    name = href_match.group(1).lstrip('/')
                else:
                    # 纯文本提取
                    name = re.sub(r'<[^>]+>', '', h2).strip()
            if not name:
                continue

            # ── 描述 ─────────────────────────────────────────
            desc_match = re.search(r'<p class="col-9[^\"]*"[^>]*>(.*?)</p>', article, re.DOTALL)
            description = ""
            if desc_match:
                description = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()

            # ── 编程语言 ─────────────────────────────────────
            lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>([^<]+)</span>', article)
            language = lang_match.group(1).strip() if lang_match else ""

            # ── Stars（SVG path L8 2.694Z 是 star 图标唯一特征）───
            stars = "0"
            star_match = re.search(r'L8 2\.694Z\"></path>\s*</svg>\s*([\d,]+)\s*</a>', article)
            if star_match:
                stars = star_match.group(1).strip()

            # ── Forks（SVG path 0 0 1.5 0Z 是 fork 图标唯一特征）───
            forks = "0"
            fork_match = re.search(r'0 0 1\.5 0Z\"></path>\s*</svg>\s*([\d,]+)\s*</a>', article)
            if fork_match:
                forks = fork_match.group(1).strip()

            # ── 今日新增 Stars ───────────────────────────────
            today_match = re.search(r'([\d,]+)\s+stars today', article)
            today_stars = today_match.group(1).strip() if today_match else "—"

            # ── 自动打标签 ───────────────────────────────────
            tags = auto_tag(name, description)

            projects.append({
                "rank": len(projects) + 1,
                "name": name,
                "description": description,
                "language": language,
                "stars": stars,
                "todayStars": today_stars,
                "forks": forks,
                "tags": tags,
                "url": f"https://github.com/{name}"
            })
        except Exception:
            continue

    return projects

def auto_tag(name, description):
    """根据项目名和描述自动打中文标签"""
    text = (name + " " + description).lower()
    tags = []
    
    if any(k in text for k in ['multi-agent', 'multi agent', 'metagpt', 'crewai', 'autogen', 'chatdev']):
        tags.append("多智能体")
    if any(k in text for k in ['dify', 'flowise', 'langchain', 'langserve', 'llamaindex']):
        tags.append("开发平台")
    if any(k in text for k in ['rag', 'retrieval', 'vector', 'knowledge', 'quivr', 'ragflow']):
        tags.append("RAG检索")
    if any(k in text for k in ['mem0', 'memory', 'context', 'memfree', 'claude-mem']):
        tags.append("记忆架构")
    if any(k in text for k in ['dev', 'coding', 'code', 'git', 'swarm']):
        tags.append("Dev Agent")
    if any(k in text for k in ['tool', 'function', 'api', 'browser', 'search']):
        tags.append("工具调用")
    if any(k in text for k in ['autonomous', 'agentgpt', 'openagent', 'openagents']):
        tags.append("自主代理")
    if any(k in text for k in ['prompt', 'few-shot', 'fewshot', 'instruction']):
        tags.append("提示工程")
    if any(k in text for k in ['vision', 'multi-modal', 'multimodal', 'image']):
        tags.append("多模态")
    if any(k in text for k in ['safety', ' jailbreak', 'guardrail', 'moderation']):
        tags.append("安全治理")
    if any(k in text for k in ['evaluation', 'benchmark', 'testing', 'deer-flow']):
        tags.append("评测基准")
    
    # 默认标签
    if not tags:
        tags.append("AI Agent")
    
    return tags[:5]

def filter_ai_agent(projects):
    """过滤出 AI Agent 相关项目"""
    filtered = []
    for p in projects:
        name = p['name'].lower()
        desc = p.get('description', '').lower()
        text = name + " " + desc
        if any(kw in text for kw in FILTER_KEYWORDS):
            filtered.append(p)
        elif any(kw in name for kw in ['agent', 'llm', 'rag', 'ai-app']):
            filtered.append(p)
    return filtered

# ── 生成行业趋势分析 ─────────────────────────────────────────────────────────
def generate_trend_report(projects):
    """根据扫描结果生成中文趋势分析报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 统计各分类数量
    category_count = {}
    language_count = {}
    total_stars = 0
    
    for p in projects:
        for tag in p.get('tags', []):
            category_count[tag] = category_count.get(tag, 0) + 1
        lang = p.get('language', '')
        if lang:
            language_count[lang] = language_count.get(lang, 0) + 1
        try:
            star_str = re.sub(r'[kKmM]', '', p.get('stars', '0'))
            total_stars += int(float(star_str.replace(',', '')) * 1000) if 'k' in p.get('stars', '').lower() else int(star_str.replace(',', ''))
        except:
            pass
    
    # 按分类数量排序
    top_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:8]
    top_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)[:6]
    
    # 生成趋势洞察
    insights = []
    
    if top_categories:
        cats_text = '、'.join([f"{cat}（{cnt}个项目）" for cat, cnt in top_categories[:3]])
        insights.append({
            "type": "技术方向",
            "icon": "🔥",
            "title": f"当前最热方向：{top_categories[0][0]}",
            "content": f"从今日 GitHub Trending 来看，{cats_text}，这三大方向持续吸引开发者关注。",
            "projects": [p['name'] for p in projects[:3]]
        })
    
    if top_languages:
        langs_text = '、'.join([f"{lang}" for lang, _ in top_languages[:3]])
        insights.append({
            "type": "语言趋势",
            "icon": "💻",
            "title": f"主流语言：{top_languages[0][0]} 领先",
            "content": f"项目语言分布：{langs_text}等，其中 {top_languages[0][0]} 项目数量最多，TypeScript 生态正在快速追赶 Python。",
            "projects": []
        })
    
    # 新兴方向分析
    emerging_tags = [cat for cat, cnt in top_categories if cat in TREND_ANALYSIS]
    if emerging_tags:
        emerging = emerging_tags[0]
        analysis = TREND_ANALYSIS.get(emerging, {})
        insights.append({
            "type": "深度解读",
            "icon": analysis.get("icon", "📊"),
            "title": f"行业趋势：{emerging}",
            "content": analysis.get("detail", ""),
            "projects": analysis.get("technologies", [])
        })
    
    # TOP 项目概览
    top_projects = []
    for p in projects[:5]:
        top_projects.append({
            "name": p['name'],
            "description": p.get('description', ''),
            "stars": p.get('stars', ''),
            "language": p.get('language', ''),
            "tags": p.get('tags', []),
            "why_hot": _explain_why_hot(p)
        })
    
    return {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "total_projects": len(projects),
        "total_stars": f"{total_stars//1000}k+",
        "top_categories": [{"name": n, "count": c} for n, c in top_categories],
        "top_languages": [{"name": n, "count": c} for n, c in top_languages],
        "insights": insights,
        "top_projects": top_projects,
        "trend_analysis": TREND_ANALYSIS
    }

def _explain_why_hot(project):
    """生成项目为什么热的中文解读"""
    name = project.get('name', '').lower()
    desc = project.get('description', '')
    tags = project.get('tags', [])
    stars = project.get('stars', '0')
    
    if 'dify' in name:
        return "Dify 是当前最火的一站式 AI 应用开发平台，工作流+RAG+Agent 三位一体，部署简单，文档完善。"
    elif 'langchain' in name:
        return "LangChain 是生态最成熟的 LLM 应用开发框架，Chains+Agents+Tools+Memory 组件丰富，适合复杂定制。"
    elif 'metagpt' in name:
        return "MetaGPT 创新性将软件公司 SOP 映射到多 Agent 协作，学术影响力大，是多 Agent 领域的标杆项目。"
    elif 'crewai' in name:
        return "CrewAI 以极低上手门槛让多 Agent 协作快速落地，角色+任务的概念符合人类工作习惯。"
    elif 'autogen' in name:
        return "AutoGen 背靠微软研究院，对话式多 Agent 协作设计优雅，企业级应用快速原型首选。"
    elif 'ragflow' in name:
        return "RAGFlow 在 RAG 基础上融合深度文档理解，支持复杂 PDF 解析和多跳问答，中文支持优秀。"
    elif 'llamaindex' in name or 'llama_index' in name:
        return "LlamaIndex 专注文档理解和知识检索，提供多种索引策略，是构建私有知识库的主流框架。"
    elif 'mem0' in name:
        return "Mem0 解决 Agent 「记不住」的核心痛点，跨会话记忆能力让 AI 助手真正「认识用户」。"
    elif 'flowise' in name:
        return "Flowise 拖拽式低代码可视化构建 AI 流程，零编码门槛，非技术背景用户也能快速上手。"
    elif 'awesome' in name:
        return "awesome-llm-apps 精选 100+ 可直接运行的 AI 应用，每个都有完整代码，是 AI 应用开发的最佳参考。"
    
    return f"GitHub Stars {stars}，在 {'/'.join(tags[:2])} 方向近期热度较高，受到开发者关注。"

# ── 主程序 ───────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("📊 AI Agent GitHub Trending 趋势分析")
    print("=" * 50)
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n🗓️  日期：{today}")
    
    # 抓取 Trending
    print("\n🌐 正在抓取 GitHub Trending ...")
    html = fetch_github_trending()
    if not html:
        print("  ⚠️  无法获取 GitHub Trending，使用缓存数据")
        cached = os.path.join(REPO_DIR, "trending.json")
        if os.path.exists(cached):
            with open(cached, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            print(f"  ✅ 从缓存加载了 {len(projects)} 个项目")
        else:
            projects = []
    else:
        print("  ✅ 抓取成功，解析中 ...")
        projects = parse_trending(html)
        print(f"  📦 共解析 {len(projects)} 个 Trending 项目")
    
    # 过滤 AI Agent 相关
    ai_projects = filter_ai_agent(projects)
    print(f"  🎯 过滤后 AI Agent 相关项目：{len(ai_projects)} 个")
    
    # 保存 trending.json（兼容原有格式）
    trending_path = os.path.join(REPO_DIR, "trending.json")
    with open(trending_path, 'w', encoding='utf-8') as f:
        json.dump(ai_projects, f, ensure_ascii=False, indent=2)
    print(f"  ✅ trending.json 已更新 → {trending_path}")
    
    # 生成趋势分析报告
    print("\n📝 正在生成中文趋势分析报告 ...")
    trend_report = generate_trend_report(ai_projects)
    trend_report_path = os.path.join(REPO_DIR, "trend_report.json")
    with open(trend_report_path, 'w', encoding='utf-8') as f:
        json.dump(trend_report, f, ensure_ascii=False, indent=2)
    print(f"  ✅ trend_report.json 已生成 → {trend_report_path}")
    
    print(f"\n📊 趋势分析摘要：")
    print(f"  - 热门方向：{[c['name'] for c in trend_report['top_categories'][:3]]}")
    print(f"  - 主要语言：{[l['name'] for l in trend_report['top_languages'][:3]]}")
    print(f"  - TOP 项目：{[p['name'] for p in trend_report['top_projects'][:3]]}")
    print("\n✅ scan_trending.py 完成！")
    return trend_report

if __name__ == "__main__":
    main()
