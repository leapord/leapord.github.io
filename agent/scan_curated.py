#!/usr/bin/env python3
"""
AI Agent 每日精选脚本
从 trending.json 筛选 1k+ Stars 项目，通过 GitHub API 获取信息，
结合静态中文解读库生成精选项目列表 + 深度分析报告
生成文件：curated.json + curated.html
"""

import json
import re
import os
import time
import subprocess
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# ── 精选项目中文深度解读库 ───────────────────────────────────────────────────
CURATED_ANALYSIS = {
    "langgenius/dify": {
        "digest": "Dify 是当前最热门的一站式 AI 应用开发平台，14万 Stars。工作流编排+RAG+Agent 三位一体，零基础也能快速上线生产级 AI 应用。Docker 一键部署，文档完善，中文社区活跃。适合想快速搭建智能客服、私有知识库、AI 助手的团队，无需大量代码即可完成从原型到生产。",
        "highlights": ["14万 Stars，TypeScript+Python 双技术栈", "可视化工作流编排，零代码也能用", "RAG 引擎支持多数据源接入", "支持 Agent 模式（ReAct/Function Call）", "日志、监控、多模型切换开箱即用"],
        "use_cases": ["企业智能客服机器人", "私有文档知识库问答", "AI 助手/ Copilot", "内容审核与分类"],
        "vs_alternatives": "vs LangChain：Dify 上手门槛极低，5分钟可跑通；LangChain 适合深度定制。vs Flowise：Dify 功能更完整（报表、权限），Flowise 更轻量。"
    },
    "langchain-ai/langchain": {
        "digest": "LangChain 是生态最成熟的 LLM 应用开发框架，135k Stars，提供 Chains、Agents、Tools、Memory 四大核心组件。Python+TypeScript 双版本，学术认可度高。适合有编程基础、需要构建复杂 LLM 流水线的开发者，以及需要快速验证 LLM 新想法的 AI 研究者。",
        "highlights": ["135k Stars，生态最成熟", "Chains+Agents+Tools+Memory 全组件", "LangSmith 观测平台、LangServe 部署工具", "Python+TypeScript 双版本", "大量第三方集成和社区教程"],
        "use_cases": ["复杂多步推理系统", "自定义工具调用链", "对话式知识库", "AI 研究实验平台"],
        "vs_alternatives": "vs Dify：LangChain 灵活度高但门槛也高；Dify 适合快速出活。vs LlamaIndex：LangChain 覆盖更广，LlamaIndex 专注文档检索。"
    },
    "FoundationAgents/MetaGPT": {
        "digest": "MetaGPT 是首个将软件公司 SOP 映射到多 Agent 协作的开源框架，67k Stars。输入「写一个 2048 小游戏」，它会自动输出 PRD→架构设计→代码→测试完整流程。学术影响力极大，引领了 2024 年多智能体研究热潮。",
        "highlights": ["67k Stars，多 Agent 领域标杆", "将软件工程 SOP 映射到 Agent 协作", "PRD→设计→代码→测试完整流程", "学术论文引用量极高", "角色扮演设计符合人类组织逻辑"],
        "use_cases": ["AI 软件公司（自主完成完整项目）", "多 Agent 任务分解研究", "复杂协作流程原型验证", "软件工程自动化"],
        "vs_alternatives": "vs CrewAI：MetaGPT 适合复杂研究场景，CrewAI 适合快速入门。vs AutoGen：MetaGPT 有 SOP 流程保障质量，AutoGen 对话式更灵活。"
    },
    "microsoft/autogen": {
        "digest": "AutoGen 是微软研究院开源的多 Agent 协作框架，45k Stars。通过多 Agent 对话让不同 LLM 协作，支持人机协同（Human-in-the-loop）。企业背书强，适合在企业内部快速搭建 AI 原型。",
        "highlights": ["微软研究院背书，企业认可度高", "多 Agent 对话式协作设计", "支持人类在关键步骤介入", "企业级应用快速原型首选", "与微软生态深度集成"],
        "use_cases": ["企业 AI 客服团队", "代码审查自动化", "多角色数据分析", "人机协同工作流"],
        "vs_alternatives": "vs MetaGPT：AutoGen 对话式更灵活，MetaGPT SOP 流程质量更有保障。vs CrewAI：AutoGen 企业背书更强，CrewAI 上手更简单。"
    },
    "crewAIInc/crewAI": {
        "digest": "CrewAI 是当前入门多智能体协作最简单的框架，30k Stars。通过「Crew（团队）+ Agent（角色）+ Task（任务）」让多个 Agent 分工协作。支持 YAML 或代码定义 Agent，上手极简，适合快速构建自动化工作流。",
        "highlights": ["30k Stars，入门门槛最低的多 Agent 框架", "Crew+Agent+Task 三层抽象", "YAML/代码都能定义 Agent", "研究员+写手+审核等角色开箱即用", "学习资源丰富，社区活跃"],
        "use_cases": ["市场调研自动化", "报告撰写工作流", "多角度数据分析", "内容创作流水线"],
        "vs_alternatives": "vs MetaGPT：CrewAI 上手极简，MetaGPT 适合复杂任务。vs AutoGen：CrewAI 概念更直观，AutoGen 灵活性更高。"
    },
    "mem0ai/mem0": {
        "digest": "Mem0 是 AI Agent 的通用记忆层，解决 Agent「记不住」的根本痛点。API 简单，可接入任何框架（Dify、LangChain、CrewAI），支持用户偏好存储、对话历史摘要、跨会话记忆。",
        "highlights": ["解决 Agent 记不住的核心痛点", "API 简单，框架无关", "支持向量数据库、Redis、内存多种存储", "用户偏好+对话历史+事实三重记忆", "国内 AI 应用需求旺盛"],
        "use_cases": ["AI Tutor（记住学习进度）", "私人 AI 管家", "AI Copilot（记住工作习惯）", "个性化推荐系统"],
        "vs_alternatives": "vs LangChain Memory：Mem0 更通用，不绑定框架。vs claude-mem：Mem0 跨框架，claude-mem 专精 Claude 生态。"
    },
    "infiniflow/ragflow": {
        "digest": "RAGFlow 是深度文档理解 RAG 引擎，79k Stars。能处理复杂 PDF（含表格、图表、多列排版），通过 Agent 做多跳推理，适合有大量内部文档（合同、报告、论文）需要智能问答的企业。中文支持优秀。",
        "highlights": ["79k Stars，深度文档理解领先", "复杂 PDF 多列表格解析", "多跳问答（Multi-hop QA）", "RAG + Agent 融合不是简单检索", "中文文档处理优化"],
        "use_cases": ["合同智能问答", "论文研究助手", "财务报表分析", "企业内部知识库"],
        "vs_alternatives": "vs Dify RAG：RAGFlow 文档理解深度更强，Dify RAG 适合标准场景。vs LlamaIndex：RAGFlow 端到端更完整，LlamaIndex 可定制性更高。"
    },
    "run-llama/llama_index": {
        "digest": "LlamaIndex 是文档智能理解与 RAG 框架，38k Stars。专注「让 LLM 理解私有数据」，提供丰富的数据连接器和多层次索引（Summary、Vector、KG、Recursive）。构建私有知识库的主流选择之一。",
        "highlights": ["38k Stars，专注文档理解", "PDF、Notion、SQL、API 丰富连接器", "Summary/Vector/KG 等多索引策略", "与 LangChain、AutoGPT 深度集成", "文档详尽，学习曲线平滑"],
        "use_cases": ["私有知识库问答", "文档摘要与总结", "复杂检索场景", "多数据源聚合查询"],
        "vs_alternatives": "vs LangChain：LlamaIndex 更专注知识检索，LangChain 覆盖更广。vs RAGFlow：LlamaIndex 可定制性高，RAGFlow 开箱即用更简单。"
    },
    "FlowiseAI/Flowise": {
        "digest": "Flowise 是零编码门槛的拖拽式 AI Flow 构建器，30k Stars。拖拽即可搭建完整 AI 流水线，完全不需要写代码，可导出 LangChain 代码继续开发。适合产品经理和独立创业者快速验证 AI 产品想法。",
        "highlights": ["30k Stars，门槛最低的可视化 AI 工具", "纯拖拽，零代码基础也能用", "所见即所得，组件一目了然", "可导出 LangChain 代码深度开发", "Docker 一键部署"],
        "use_cases": ["快速验证 AI 产品想法", "非技术团队搭建 AI 流程", "AI 应用原型开发", "AI 培训演示"],
        "vs_alternatives": "vs Dify：Dify 功能更完整，Flowise 更轻量简单。vs LangChain：Flowise 零编码，LangChain 可深度定制。"
    },
    "Shubhamsaboo/awesome-llm-apps": {
        "digest": "awesome-llm-apps 精选 100+ 可直接运行的 AI Agent 和 RAG 应用集合，108k Stars。每个都有完整代码，涵盖聊天机器人、RAG 知识库、代码助手、多模态等多个方向，是 AI 应用开发最佳参考集合。",
        "highlights": ["108k Stars，最大 AI 应用参考集合", "100+ 可直接运行的项目", "覆盖 Agent、RAG、多模态全方向", "每个项目含完整代码和说明", "更新频繁，持续有新项目加入"],
        "use_cases": ["AI 应用开发参考", "直接基于项目二开", "学习不同 AI 应用架构", "快速出 MVP"],
        "vs_alternatives": "vs LangChain Examples：awesome-llm-apps 都是可直接运行的应用，LangChain 示例偏底层代码。"
    }
}

def parse_stars(stars_str):
    """解析 stars 字符串为整数"""
    if not stars_str or stars_str == '—':
        return 0
    stars_str = stars_str.strip().lower()
    multiplier = 1000
    if 'k' in stars_str:
        stars_str = stars_str.replace('k', '')
        multiplier = 1000
    elif 'm' in stars_str:
        stars_str = stars_str.replace('m', '')
        multiplier = 1000000
    try:
        return int(float(stars_str.replace(',', '')) * multiplier)
    except:
        return 0

def fetch_github_api(path):
    """通过 GitHub API 获取仓库信息"""
    import urllib.request
    url = f"https://api.github.com{path}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'AI-Agent-Scanner/1.0'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None

def web_search(query, num_results=3):
    """通过 curl 调用 Google 搜索（可选功能）"""
    import urllib.request
    import urllib.parse
    
    # 尝试使用 SerpAPI 或直接搜索
    # 这里用简单的 Bing 搜索作为降级方案
    encoded = urllib.parse.quote(query)
    url = f"https://ddg-api.herokuapp.com/search?q={encoded}&limit={num_results}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = []
            for item in data[:num_results]:
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('description', item.get('snippet', '')),
                    'url': item.get('url', '')
                })
            return results
    except Exception:
        return []

def generate_curated_projects(trending_projects):
    """从 trending 项目中筛选 1k+ Stars 生成精选列表"""
    today = datetime.now().strftime("%Y-%m-%d")
    selected = []
    
    # 优先选择有详细解读库的项目（高可信度）
    for name, analysis in CURATED_ANALYSIS.items():
        for p in trending_projects:
            if p['name'] == name:
                stars = parse_stars(p.get('stars', '0'))
                selected.append({
                    "date": today,
                    "name": p['name'],
                    "description": p.get('description', ''),
                    "language": p.get('language', ''),
                    "stars": p.get('stars', ''),
                    "stars_num": stars,
                    "forks": p.get('forks', ''),
                    "tags": p.get('tags', []),
                    "url": p.get('url', f"https://github.com/{name}"),
                    "digest": analysis['digest'],
                    "highlights": analysis['highlights'],
                    "use_cases": analysis['use_cases'],
                    "vs_alternatives": analysis['vs_alternatives'],
                    "trend": "稳定热门" if stars > 50000 else ("快速上升" if stars > 10000 else "稳步增长"),
                    "analysis_date": today
                })
                break
    
    # 从 trending 中补充未收录但 stars 高的项目
    trending_sorted = sorted(trending_projects, key=lambda x: parse_stars(x.get('stars', '0')), reverse=True)
    for p in trending_sorted:
        if len(selected) >= 12:
            break
        name = p['name']
        stars = parse_stars(p.get('stars', '0'))
        if stars < 1000:
            continue
        if any(s['name'] == name for s in selected):
            continue
        
        # 生成简要 digest
        desc = p.get('description', '')
        tags = p.get('tags', [])
        tag_str = '、'.join(tags[:3]) if tags else 'AI Agent'
        digest = f"GitHub Stars {p.get('stars', '')}，{tag_str}方向热门项目。{desc}" if desc else f"GitHub Stars {p.get('stars', '')}，{tag_str}方向值得关注的项目。"
        
        selected.append({
            "date": today,
            "name": name,
            "description": desc,
            "language": p.get('language', ''),
            "stars": p.get('stars', ''),
            "stars_num": stars,
            "forks": p.get('forks', ''),
            "tags": tags,
            "url": p.get('url', f"https://github.com/{name}"),
            "digest": digest,
            "highlights": [],
            "use_cases": [],
            "vs_alternatives": "",
            "trend": "快速上升" if stars > 50000 else ("稳步增长" if stars > 10000 else "新晋热门"),
            "analysis_date": today
        })
    
    return selected

def generate_curated_html(projects):
    """生成精选项目详情页 HTML"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    cards_html = ""
    for p in projects:
        tags_html = "".join(f"<span class='curated-tag'>{t}</span>" for t in (p.get('tags', [])[:4]))
        highlights_html = ""
        if p.get('highlights'):
            highlights_html = "<ul class='hl-list'>" + "".join(f"<li>✅ {h}</li>" for h in p['highlights']) + "</ul>"
        
        cards_html += f"""
        <div class="curated-card" id="{p['name'].replace('/', '-')}">
          <div class="cc-header">
            <div class="cc-name">
              <a href="https://github.com/{p['name']}" target="_blank">{p['name']}</a>
              <span class="cc-trend trend-{p.get('trend', 'stable')}">{p.get('trend', 'stable')}</span>
            </div>
            <div class="cc-meta">
              <span>⭐ {p.get('stars', '')}</span>
              <span v-if="p.get('language')">{p.get('language')}</span>
              <span v-if="p.get('forks')">🍴 {p.get('forks')}</span>
            </div>
          </div>
          <div class="cc-desc">{p.get('description', '')}</div>
          <div class="cc-digest">{p.get('digest', '')}</div>
          {highlights_html}
          <div class="cc-footer">
            <div class="cc-tags">{tags_html}</div>
            <a class="detail-btn" href="detail/{p['name'].replace('/', '-')}.html" target="_blank">深度解读 →</a>
          </div>
        </div>"""
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>每日精选 · AI Agent 1k+ Stars 项目</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Inter','PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.6}}
    .container{{max-width:1100px;margin:0 auto;padding:24px}}
    .back-btn{{display:inline-flex;align-items:center;gap:6px;color:#409EFF;font-size:13px;text-decoration:none;margin-bottom:20px;padding:6px 14px;background:#fff;border:1px solid #409EFF;border-radius:7px;transition:all .2s}}
    .back-btn:hover{{background:#409EFF;color:#fff}}
    .page-header{{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:14px;padding:32px;color:#fff;margin-bottom:24px}}
    .page-header h1{{font-size:22px;font-weight:700;margin-bottom:8px}}
    .page-header h1 span{{color:#409EFF}}
    .page-header p{{color:rgba(255,255,255,.6);font-size:13px}}
    .page-header .stats{{display:flex;gap:20px;margin-top:16px;flex-wrap:wrap}}
    .page-header .stat{{}}
    .page-header .stat .n{{font-size:20px;font-weight:700;color:#409EFF}}
    .page-header .stat .l{{font-size:11px;color:rgba(255,255,255,.5)}}
    .curated-card{{background:#fff;border-radius:12px;border:1px solid #f0f0f0;padding:18px;margin-bottom:14px;transition:border-color .2s}}
    .curated-card:hover{{border-color:#409EFF}}
    .cc-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}}
    .cc-name{{font-size:14px;font-weight:700;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
    .cc-name a{{color:#409EFF}}
    .cc-trend{{font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px}}
    .trend-稳定热门{{background:#e6f4ea;color:#1e7e34}}
    .trend-快速上升{{background:#fff3e0;color:#e65100}}
    .trend-稳步增长{{background:#ecf5ff;color:#409EFF}}
    .trend-新晋热门{{background:#fce4ec;color:#c2185b}}
    .cc-meta{{display:flex;gap:10px;font-size:11px;color:#7a8ba8;flex-shrink:0}}
    .cc-desc{{font-size:12px;color:#7a8ba8;margin-bottom:8px}}
    .cc-digest{{font-size:13px;color:#1a1a2e;line-height:1.7;background:#f8fafc;padding:10px 12px;border-radius:8px;border-left:3px solid #409EFF;margin-bottom:10px}}
    .hl-list{{list-style:none;padding:0;margin:0 0 10px 0;display:flex;flex-direction:column;gap:4px}}
    .hl-list li{{font-size:12px;color:#555;padding-left:12px;position:relative}}
    .hl-list li::before{{content:'✅';position:absolute;left:0;color:#409EFF}}
    .cc-footer{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}}
    .cc-tags{{display:flex;gap:5px;flex-wrap:wrap}}
    .curated-tag{{padding:2px 8px;background:#ecf5ff;color:#409EFF;border-radius:10px;font-size:10px}}
    .detail-btn{{display:inline-block;background:#f0f9ff;color:#409EFF;border:1px solid #409EFF;font-size:11px;padding:3px 9px;border-radius:5px;transition:all .2s;white-space:nowrap}}
    .detail-btn:hover{{background:#409EFF;color:#fff}}
    .footer{{text-align:center;padding:24px;color:#b0c4de;font-size:12px}}
    .footer a{{color:#409EFF}}
  </style>
</head>
<body>
<div class="container">
  <a class="back-btn" href="index.html">← 返回 Dashboard</a>
  
  <div class="page-header">
    <h1>⭐ 每日精选 · <span>1k+ Stars AI Agent 项目</span></h1>
    <p>每日自动筛选 GitHub Stars 超过 1000 的优质 AI Agent 项目，提供深度中文解读和分析报告</p>
    <div class="stats">
      <div class="stat"><div class="n">{len(projects)}</div><div class="l">精选项目</div></div>
      <div class="stat"><div class="n">{today}</div><div class="l">更新日期</div></div>
    </div>
  </div>
  
  {cards_html}
  
  <div class="footer">
    <p>© {datetime.now().year} AI Agent 前沿追踪 · 每日 09:00 自动更新</p>
  </div>
</div>
</body>
</html>"""

def main():
    print("=" * 50)
    print("⭐ AI Agent 每日精选生成器")
    print("=" * 50)
    
    trending_path = os.path.join(REPO_DIR, "trending.json")
    if not os.path.exists(trending_path):
        print("  ⚠️  trending.json 不存在，先运行 scan_trending.py")
        return
    
    with open(trending_path, 'r', encoding='utf-8') as f:
        trending_projects = json.load(f)
    print(f"  📦 从 trending.json 加载了 {len(trending_projects)} 个项目")
    
    # 生成精选列表
    print("\n🎯 正在筛选 1k+ Stars 项目并生成深度分析 ...")
    curated = generate_curated_projects(trending_projects)
    print(f"  ✅ 精选了 {len(curated)} 个优质项目")
    
    # 保存 curated.json
    curated_path = os.path.join(REPO_DIR, "curated.json")
    with open(curated_path, 'w', encoding='utf-8') as f:
        json.dump(curated, f, ensure_ascii=False, indent=2)
    print(f"  ✅ curated.json 已保存 → {curated_path}")
    
    # 生成 curated.html 详情页
    print("\n📄 正在生成 curated.html 详情页 ...")
    curated_html = generate_curated_html(curated)
    curated_html_path = os.path.join(REPO_DIR, "curated.html")
    with open(curated_html_path, 'w', encoding='utf-8') as f:
        f.write(curated_html)
    print(f"  ✅ curated.html 已生成 → {curated_html_path}")
    
    print("\n✅ scan_curated.py 完成！")
    return curated

if __name__ == "__main__":
    main()
