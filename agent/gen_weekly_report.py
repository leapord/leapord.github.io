#!/usr/bin/env python3
import glob
from datetime import datetime, timedelta
from collections import Counter

today = datetime.now()
week_start = today - timedelta(days=today.weekday())
week_num = today.strftime('%W')
week_id = f'{today.year}-W{week_num}'
week_dates = [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

# 收集本周所有日报
reports = []
for d in week_dates:
    path = f'daily-{d}.html'
    if glob.glob(path):
        reports.append((d, path))

# 统计项目出现次数
project_counter = Counter()
for d, path in reports:
    with open(path) as f:
        content = f.read()
    # 提取项目名（简化版）
    import re
    names = re.findall(r'>#(\d+)\s+<a href="detail/([^"]+)"', content)
    for rank, slug in names:
        project_counter[slug] += 1

top_projects = project_counter.most_common(10)

# 生成周报
html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Agent 周报 {week_id}</title>
<style>
body{{font-family:system-ui;max-width:900px;margin:0 auto;padding:2rem;background:#0f172a;color:#e2e8f0}}
h1{{color:#38bdf8}}
.card{{background:#1e293b;border-radius:12px;padding:1.2rem;margin:1rem 0;border-left:4px solid #f59e0b}}
.day-link{{background:#1e3a5f;color:#38bdf8;padding:.5rem 1rem;border-radius:8px;text-decoration:none;margin:.3rem;display:inline-block}}
.top-item{{display:flex;align-items:center;gap:1rem;padding:.8rem 0;border-bottom:1px solid #334155}}
.top-num{{font-size:1.5rem;font-weight:bold;color:#f59e0b;width:2rem}}
</style>
</head>
<body>
<h1>📊 AI Agent 周报 {week_id}</h1>
<p>📅 {week_start.strftime('%Y-%m-%d')} ~ {(week_start+timedelta(days=6)).strftime('%Y-%m-%d')} | 📝 {len(reports)} 份日报</p>
<hr style="border-color:#334155">

<h2>📅 本周日报</h2>
<div>
'''
for d, path in reports:
    html += f'  <a class="day-link" href="{path}">{d}</a>\n'

html += '</div>\n'

if top_projects:
    html += '''
<h2>🏆 本周项目热度 TOP10</h2>
'''
    for i, (slug, count) in enumerate(top_projects, 1):
        name = slug.replace('-', '/')
        html += f'''
<div class="top-item">
<div class="top-num">#{i}</div>
<div>
<div style="font-size:1.1rem;font-weight:bold">{name.split('/')[-1]}</div>
<div style="color:#94a3b8">出现 {count} 次</div>
</div>
<div><a href="detail/{slug}.html" style="color:#38bdf8">深度解读 →</a></div>
</div>'''

html += f'''
<hr style="border-color:#334155">
<p style="color:#94a3b8;text-align:center">
📊 <a href="index.html" style="color:#38bdf8">Dashboard</a> · 
📝 <a href="daily-{today.strftime('%Y-%m-%d')}.html" style="color:#38bdf8">今日日报</a>
</p>
</body></html>'''

with open(f'weekly-{week_id}.html', 'w') as f:
    f.write(html)
print(f'✅ 生成周报: weekly-{week_id}.html ({len(reports)} 份日报, {len(top_projects)} 个热门项目)')
