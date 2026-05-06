#!/usr/bin/env python3
import glob, re, json, os
from datetime import datetime

logs = []
for lf in sorted(glob.glob('/opt/data/home/agent/logs/deploy-*.log'), reverse=True)[:30]:
    fname = os.path.basename(lf)
    with open(lf) as f:
        content = f.read()
    started = re.search(r'开始\s*\|\s*(.+)', content)
    github_count = re.search(r'获取\s*(\d+)\s*个热门', content)
    arxiv_count = re.search(r'ArXiv\s*论文:\s*(\d+)\s*篇', content)
    pushed = 'Y' if '已提交推送' in content else 'N'
    logs.append({
        'date': fname.replace('deploy-','').replace('.log',''),
        'started': started.group(1).strip() if started else '—',
        'github': int(github_count.group(1)) if github_count else 0,
        'arxiv': int(arxiv_count.group(1)) if arxiv_count else 0,
        'pushed': pushed,
        'status': 'OK' if pushed == 'Y' else 'WARN'
    })

success_rate = f"{sum(1 for l in logs if l['pushed']=='Y')}/{len(logs)}" if logs else "—"

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>Agent 系统监控</title>
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
.ok{{color:#67c23a;font-weight:600}}.err{{color:#f56c6c;font-weight:600}}
tr:last-child td{{border-bottom:none}}
.back{{display:inline-block;margin-top:20px;font-size:13px;color:#409EFF}}
</style></head><body>
<div id="app"><h1>🤖 Agent 系统监控</h1>
<div class="summary">
<div class="sum-card"><div class="num">{len(logs)}</div><div class="label">执行记录</div></div>
<div class="sum-card"><div class="num">{success_rate}</div><div class="label">推送成功率</div></div>
<div class="sum-card"><div class="num">{datetime.now().strftime('%H:%M')}</div><div class="label">最后检查</div></div>
</div>
<table><tr><th>日期</th><th>开始时间</th><th>GitHub 项目</th><th>ArXiv 论文</th><th>Git 推送</th><th>状态</th></tr>"""
for log in logs[:20]:
    sc = 'ok' if log['pushed'] == 'Y' else 'err'
    icon = '✅' if log['pushed'] == 'Y' else '⚠️'
    html += f"<tr><td>{log['date']}</td><td>{log['started']}</td><td>{log['github']}</td><td>{log['arxiv']}</td><td class='{sc}'>{icon}</td><td class='{sc}'>{log['status']}</td></tr>\n"
html += f"""</table>
<a class="back" href="index.html">← 返回 Dashboard</a>
</div><script>createApp({{}}).use(ElementPlus).mount("#app")</script></body></html>"""

with open('/opt/data/home/agent/monitor.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/data/home/agent/monitor.json', 'w', encoding='utf-8') as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)
print(f'monitor.html + monitor.json generated ({len(logs)} entries)')
