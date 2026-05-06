#!/usr/bin/env python3
"""为 trending 和 curated 项目生成 detail 分析报告页面"""
import json, os, sys
from datetime import datetime

# 项目中文解读库（可扩展）
KNOWLEDGE = {
    "Hmbown/DeepSeek-TUI": {
        "eval": "DeepSeek 官方出品的大模型终端界面，通过 TUI 方式让你在命令行里直接和 DeepSeek 聊天，支持多轮对话、代码高亮、Markdown 渲染，体验接近 ChatGPT 但完全本地运行。",
        "what": "DeepSeek 官方推出的终端聊天界面，基于 Rich TUI 框架构建，提供沉浸式命令行 AI 对话体验。支持 DeepSeek-V3/R1 等模型，多轮对话、代码块高亮、Markdown 格式渲染是核心亮点。",
        "why": "轻量快速：无需浏览器，直接在终端运行；资源占用低；支持 DeepSeek 全系列模型；交互体验流畅；Markdown 代码块渲染美观。",
        "tags": ["LLM Chat", "TUI", "DeepSeek", "CLI"],
        "pros": ["轻量快速", "无需浏览器", "支持 DeepSeek 全系模型", "Markdown 渲染"],
        "cons": ["纯命令行界面", "不适合新手"],
        "who": "开发者、数据科学家、喜欢终端操作的极客用户",
    },
    "ruvnet/ruflo": {
        "eval": "ruflo 是一个开源的 AI 代码助手 CLI 工具，可以无缝对接 Code Agent，帮助你自动补全、代码审查、Bug 修复，适合追求高效编码体验的开发者。",
        "what": "ruflo 是一个面向 AI 原生开发的命令行工具，集成 Code Agent 能力，支持代码补全、审查、重构、多语言切换。定位类似 GitHub Copilot CLI 但是完全开源可自托管。",
        "why": "完全开源可自托管；多模型支持（Claude/GPT/本地模型）；支持 50+ 编程语言；可集成到现有 CI/CD 工作流。",
        "tags": ["Code Agent", "CLI", "AI Coding", "开源 Copilot"],
        "pros": ["完全开源", "自托管", "多模型", "CI/CD 集成"],
        "cons": ["配置有一定门槛"],
        "who": "追求代码隐私和可控性的开发团队",
    },
    "virattt/dexter": {
        "eval": "Dexter 是一个 AI Agent 框架，专注于自动化测试和代码质量分析，可以自动发现 Bug、性能瓶颈，并给出修复建议，是工程团队提升代码质量的好帮手。",
        "what": "Dexter 是一个 AI Agent 开发框架，重点应用于自动化代码审查、测试生成和 Bug 检测。核心基于 LangChain + Claude API，支持多 Agent 协作处理复杂代码分析任务。",
        "why": "自动化代码审查节省人工成本；支持测试生成 + Bug 检测双模式；可集成 GitHub Actions；中文社区活跃。",
        "tags": ["Code Agent", "代码审查", "Bug 检测", "测试生成"],
        "pros": ["自动化测试生成", "Bug 检测", "GitHub Actions 集成"],
        "cons": ["依赖外部 API"],
        "who": "软件工程团队、DevOps 工程师",
    },
    "msitarzewski/agency-agents": {
        "eval": "agency-agents 是一个多 Agent 协作框架，可以让多个 AI Agent 分工合作完成复杂任务，适合研究多 Agent 系统的开发者。",
        "what": "agency-agents 是一个轻量级多 Agent 协作框架，核心是让多个专业化 Agent 通过消息传递协作完成任务。支持自定义 Agent 角色、工具调用和长程记忆。",
        "why": "架构简单易上手；支持自定义 Agent；多 Agent 协作模式灵活；适合研究实验。",
        "tags": ["Multi-Agent", "Agent 协作", "框架"],
        "pros": ["轻量简单", "多 Agent 协作", "可自定义角色"],
        "cons": ["生态较小"],
        "who": "AI 研究者、多 Agent 系统探索者",
    },
}

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
  <a class="back-btn" href="/agent/index.html">← Dashboard</a>
  <a class="back-btn" href="/agent/curated.html" style="margin-left:12px">← 每日精选</a>

  <div class="hero">
    <div class="badge">⭐ AI Agent 精选</div>
    <h1>{name}</h1>
    <p class="desc">{description}</p>
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
      <p>{eval_text}</p>
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">🔍</span> 是什么</h2>
    <p>{what_text}</p>
  </div>

  <div class="section">
    <h2><span class="icon">📈</span> 为什么值得关注</h2>
    <ul>{why_list}</ul>
  </div>

  <div class="section">
    <h2><span class="icon">👥</span> 适合谁用</h2>
    <div class="who-card">
      <div class="title">✅ 推荐</div>
      <div class="text">{who_text}</div>
    </div>
  </div>

  <div class="section">
    <h2><span class="icon">🚀</span> 快速上手</h2>
    <ul>
      <li><a href="https://github.com/{name}" target="_blank" style="color:#409EFF">GitHub 仓库</a></li>
      {doc_link}
    </ul>
  </div>

  <div class="cta-box">
    <a href="https://github.com/{name}" target="_blank">⭐ 去 GitHub 看看</a>
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

def generate_detail(name, data, out_dir):
    slug = name.replace('/', '-')
    out_path = os.path.join(out_dir, f"{slug}.html")

    # 如果已有 detail 页面且不想覆盖，跳过
    # if os.path.exists(out_path):
    #     return False

    k = KNOWLEDGE.get(name, {})
    tags = k.get('tags', data.get('tags', ['AI Agent']))
    stars = data.get('stars', 'N/A')
    forks = data.get('forks', 'N/A')
    language = data.get('language', 'N/A')
    description = data.get('description', data.get('digest', '暂无描述'))
    eval_text = k.get('eval', description)
    what_text = k.get('what', description)
    why_items = k.get('pros', ['值得关注'])
    who_text = k.get('who', 'AI 开发者和研究者')

    html = DETAIL_TEMPLATE.format(
        name=name,
        meta_desc=description[:100],
        description=description,
        stars=stars,
        forks=forks,
        language=language,
        tags_html=tag_html(tags),
        eval_text=eval_text,
        what_text=what_text,
        why_list=li_html(why_items),
        who_text=who_text,
        doc_link="",
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )

    with open(out_path, 'w') as f:
        f.write(html)
    return True

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    detail_dir = os.path.join(out_dir, 'detail')
    os.makedirs(detail_dir, exist_ok=True)

    projects = []

    # 从 trending.json 加载
    try:
        with open('trending.json') as f:
            trending = json.load(f)
            if isinstance(trending, list):
                projects.extend(trending)
            elif isinstance(trending, dict):
                projects.extend(trending.get('projects', trending.get('items', [])))
    except Exception as e:
        print(f"⚠️ trending.json 读取失败: {e}")

    # 从 curated.json 加载
    try:
        with open('curated.json') as f:
            curated = json.load(f)
            if isinstance(curated, list):
                projects.extend(curated)
            elif isinstance(curated, dict):
                projects.extend(curated.get('projects', []))
    except Exception as e:
        print(f"⚠️ curated.json 读取失败: {e}")

    # 去重
    seen = set()
    unique = []
    for p in projects:
        name = p.get('name', '')
        if name and name not in seen:
            seen.add(name)
            unique.append(p)

    print(f"📦 共 {len(unique)} 个唯一项目，开始生成 detail 页面 ...")
    count = 0
    for p in unique:
        name = p.get('name', '')
        if not name:
            continue
        if generate_detail(name, p, detail_dir):
            count += 1
            print(f"  ✅ {name}")
        else:
            print(f"  ⏭️  跳过（已存在）: {name}")

    print(f"\n✅ 完成！生成了 {count} 个 detail 页面 → {detail_dir}/")

if __name__ == '__main__':
    main()
