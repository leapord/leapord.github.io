#!/usr/bin/env python3
import json
from datetime import datetime

with open('trending.json') as f:
    trending = json.load(f)

today = datetime.now().strftime('%Y-%m-%d')
week = datetime.now().strftime('%Y-W%W')

html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Agent 日报 {today}</title>
<style>
body{{font-family:system-ui;max-width:900px;margin:0 auto;padding:2rem;background:#0f172a;color:#e2e8f0}}
h1{{color:#38bdf8}}
.card{{background:#1e293b;border-radius:12px;padding:1.2rem;margin:1rem 0;border-left:4px solid #38bdf8}}
.card h3{{margin:0 0 .5rem;color:#f8fafc}}
.card p{{margin:0;color:#94a3b8}}
.card a{{color:#38bdf8;text-decoration:none}}
.stars{{color:#f59e0b}}
.tag{{display:inline-block;background:#1e3a5f;color:#38bdf8;padding:.1rem .5rem;border-radius:4px;font-size:.75rem;margin:.2rem .1rem}}
</style>
</head>
<body>
<h1>🤖 AI Agent 日报 {today}</h1>
<p>📅 本周第{week.split("W")[1]}周 | 🔥 {len(trending)} 个热门项目</p>
<hr style="border-color:#334155">
'''

for p in trending[:15]:
    name = p.get('name','')
    slug = name.replace('/','-')
    desc = p.get('description','') or '暂无描述'
    stars = p.get('stars','')
    url = p.get('url','')
    rank = p.get('rank',0)
    html += f'''
<div class="card">
<h3>#{rank} <a href="detail/{slug}.html">{name.split('/')[-1]}</a></h3>
<p>{desc}</p>
<p><span class="stars">⭐ {stars}</span> · <a href="{url}">GitHub</a> · <a href="detail/{slug}.html">深度解读 →</a></p>
</div>'''

html += f'''
<hr style="border-color:#334155">
<p style="color:#94a3b8;text-align:center">
📊 <a href="index.html" style="color:#38bdf8">Dashboard</a> · 
📝 <a href="weekly-{week}.html" style="color:#38bdf8">本周周报</a> · 
📧 每日 09:00 自动更新
</p>
</body></html>'''

with open(f'daily-{today}.html', 'w') as f:
    f.write(html)
print(f'✅ 生成日报: daily-{today}.html ({len(trending)} 个项目)')
