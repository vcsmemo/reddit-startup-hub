"""
构建静态站点 — 从 posts.json 生成 index.html
"""
import json
import os
import html
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HN TechHub · HackerNews + TechMeme 科技情报站</title>
<style>
:root {
  --bg: #0f172a;
  --card: #1e293b;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --accent: #3b82f6;
  --accent2: #10b981;
  --accent3: #f59e0b;
  --danger: #ef4444;
  --radius: 12px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
header {
  padding: 48px 0 24px;
  border-bottom: 1px solid #334155;
}
header h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
header p { color: var(--muted); margin-top: 8px; font-size: 0.95rem; }
.stats-bar {
  display: flex; gap: 32px; padding: 20px 0;
  border-bottom: 1px solid #334155; flex-wrap: wrap;
}
.stat { text-align: center; }
.stat .num { font-size: 1.5rem; font-weight: 700; color: var(--accent); }
.stat .label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
.filters {
  display: flex; gap: 12px; padding: 20px 0; flex-wrap: wrap; align-items: center;
}
.filters label { color: var(--muted); font-size: 0.85rem; }
.filters select, .filters input {
  background: var(--card); color: var(--text); border: 1px solid #334155;
  padding: 8px 12px; border-radius: 8px; font-size: 0.9rem; cursor: pointer;
}
.filters select:hover, .filters input:hover { border-color: var(--accent); }
.filter-btn {
  background: var(--accent); color: white; border: none; padding: 8px 16px;
  border-radius: 8px; cursor: pointer; font-size: 0.85rem; font-weight: 600;
}
.filter-btn:hover { background: #2563eb; }
.clear-btn {
  background: transparent; color: var(--muted); border: 1px solid #334155;
}
.grid { display: grid; gap: 16px; padding: 16px 0 48px; }
.card {
  background: var(--card); border-radius: var(--radius); padding: 20px;
  border: 1px solid #334155; transition: transform 0.15s, border-color 0.15s;
}
.card:hover { transform: translateY(-2px); border-color: #475569; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.card-title { font-size: 1.05rem; font-weight: 600; line-height: 1.4; }
.card-title a { color: var(--text); text-decoration: none; }
.card-title a:hover { color: var(--accent); }
.card-meta { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.badge {
  display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
}
.badge-sub { background: #1e3a5f; color: #60a5fa; }
.badge-cat { background: #1e3a5f; color: #a78bfa; }
.badge-sent-pos { background: #064e3b; color: #34d399; }
.badge-sent-neg { background: #450a0a; color: #f87171; }
.badge-sent-neu { background: #374151; color: #9ca3af; }
.badge-revenue { background: #451a03; color: #fbbf24; }
.badge-tech { background: #1e293b; color: #38bdf8; border: 1px solid #0ea5e9; }
.card-body { margin-top: 12px; color: var(--muted); font-size: 0.9rem; line-height: 1.6; }
.card-body p { margin-bottom: 8px; }
.card-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }
.card-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 16px; padding-top: 12px; border-top: 1px solid #334155;
  font-size: 0.8rem; color: var(--muted);
}
.score { display: flex; gap: 12px; }
.score span { display: flex; align-items: center; gap: 4px; }
.daily-brief {
  background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%);
  border-radius: var(--radius); padding: 24px; margin: 20px 0;
  border: 1px solid #334155;
}
.daily-brief h2 { font-size: 1.2rem; margin-bottom: 16px; color: var(--accent); }
.brief-list { display: flex; flex-direction: column; gap: 8px; }
.brief-item { display: flex; gap: 12px; align-items: center; padding: 8px 12px; border-radius: 6px; background: rgba(15,23,42,0.5); }
.brief-item .rank { font-weight: 700; color: var(--accent); min-width: 24px; }
.brief-item a { color: var(--text); text-decoration: none; font-size: 0.9rem; }
.brief-item a:hover { color: var(--accent); }
.brief-item .meta { margin-left: auto; font-size: 0.75rem; color: var(--muted); white-space: nowrap; }
footer { text-align: center; padding: 32px 0; color: var(--muted); font-size: 0.8rem; border-top: 1px solid #334155; }
@media (max-width: 768px) {
  .stats-bar { gap: 16px; }
  .filters { gap: 8px; }
  .card-header { flex-direction: column; }
  .score { gap: 8px; }
}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>HN TechHub</h1>
    <p>自动追踪 HackerNews 热门帖子 + TechMeme 科技新闻，提取结构化科技情报</p>
  </header>

  <div class="stats-bar">
    <div class="stat"><div class="num" id="stat-total">0</div><div class="label">帖子总数</div></div>
    <div class="stat"><div class="num" id="stat-subs">0</div><div class="label">Sources</div></div>
    <div class="stat"><div class="num" id="stat-revenue">0</div><div class="label">含收入数据</div></div>
    <div class="stat"><div class="num" id="stat-today">0</div><div class="label">今日更新</div></div>
    <div class="stat"><div class="num" id="stat-categories">0</div><div class="label">分类</div></div>
  </div>

  <div class="daily-brief" id="daily-brief">
    <h2>今日简报 · Top 10 高价值帖子</h2>
    <div class="brief-list" id="brief-list"></div>
  </div>

  <div class="filters">
    <label>筛选：</label>
    <select id="filter-source"><option value="">全部 Source</option></select>
    <select id="filter-category"><option value="">全部分类</option></select>
    <select id="filter-sentiment"><option value="">全部情绪</option><option value="positive">积极</option><option value="negative">消极</option><option value="neutral">中性</option></select>
    <select id="filter-revenue"><option value="">全部</option><option value="1">含收入数据</option></select>
    <input type="text" id="search-input" placeholder="搜索关键词..." style="width: 200px;">
    <button class="filter-btn" onclick="applyFilters()">应用</button>
    <button class="filter-btn clear-btn" onclick="clearFilters()">重置</button>
  </div>

  <div class="grid" id="post-grid"></div>

  <footer>
    <p>数据自动抓取于 HackerNews 官方 API + TechMeme RSS · 更新频率：每 4 小时 · 构建时间：{BUILD_TIME}</p>
  </footer>
</div>

<script>
const POSTS = {POSTS_JSON};

function init() {
  populateFilters();
  renderStats();
  renderBrief();
  renderPosts(POSTS);
}

function populateFilters() {
  const sources = [...new Set(POSTS.map(p => p.source))].sort();
  const cats = [...new Set(POSTS.map(p => p.category))].sort();
  const srcSel = document.getElementById('filter-source');
  const catSel = document.getElementById('filter-category');
  sources.forEach(s => srcSel.add(new Option(s, s)));
  cats.forEach(c => catSel.add(new Option(c.replace(/_/g, ' '), c)));
}

function renderStats() {
  const total = POSTS.length;
  const sources = new Set(POSTS.map(p => p.source)).size;
  const revenue = POSTS.filter(p => p.has_revenue_info === 1).length;
  const today = new Date().toISOString().slice(0, 10);
  const todayCount = POSTS.filter(p => p.created_date === today).length;
  const cats = new Set(POSTS.map(p => p.category)).size;
  document.getElementById('stat-total').textContent = total;
  document.getElementById('stat-subs').textContent = sources;
  document.getElementById('stat-revenue').textContent = revenue;
  document.getElementById('stat-today').textContent = todayCount;
  document.getElementById('stat-categories').textContent = cats;
}

function renderBrief() {
  const top = [...POSTS]
    .filter(p => p.score >= 20)
    .sort((a, b) => (b.score + b.num_comments) - (a.score + a.num_comments))
    .slice(0, 10);
  const el = document.getElementById('brief-list');
  el.innerHTML = top.map((p, i) => `
    <div class="brief-item">
      <span class="rank">${i+1}</span>
      <a href="${p.permalink}" target="_blank">${truncate(p.title, 60)}</a>
      <span class="meta">${p.source} · ${p.score}↑ · ${p.num_comments}💬</span>
    </div>
  `).join('');
}

function renderPosts(posts) {
  const el = document.getElementById('post-grid');
  if (posts.length === 0) {
    el.innerHTML = '<p style="text-align:center;color:var(--muted);padding:40px 0">没有找到匹配的帖子</p>';
    return;
  }
  el.innerHTML = posts.map(p => `
    <div class="card" data-sub="${p.source}" data-cat="${p.category}" data-sent="${p.sentiment}" data-rev="${p.has_revenue_info}">
      <div class="card-header">
        <div class="card-title"><a href="${p.permalink}" target="_blank">${escapeHtml(p.title)}</a></div>
      </div>
      <div class="card-meta">
        <span class="badge badge-sub">${p.source}</span>
        <span class="badge badge-cat">${p.category.replace(/_/g, ' ')}</span>
        <span class="badge badge-sent-${p.sentiment}">${p.sentiment}</span>
        ${p.has_revenue_info ? '<span class="badge badge-revenue">$ Revenue</span>' : ''}
      </div>
      <div class="card-body">
        <p>${escapeHtml(p.extracted_summary)}</p>
        ${p.tech_stack ? `<p><strong>Tech:</strong> ${escapeHtml(p.tech_stack)}</p>` : ''}
        ${p.target_audience ? `<p><strong>Audience:</strong> ${escapeHtml(p.target_audience)}</p>` : ''}
        ${p.pain_point ? `<p><strong>Pain:</strong> ${escapeHtml(p.pain_point)}</p>` : ''}
        ${p.revenue_pattern ? `<p><strong>Revenue:</strong> ${escapeHtml(p.revenue_pattern)}</p>` : ''}
      </div>
      <div class="card-footer">
        <div class="score">
          <span>👤 ${p.author || 'unknown'}</span>
          <span>📅 ${p.created_date}</span>
        </div>
        <div class="score">
          <span>⬆ ${p.score}</span>
          <span>💬 ${p.num_comments}</span>
          <span>📊 ${(p.upvote_ratio * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  `).join('');
}

function applyFilters() {
  const src = document.getElementById('filter-source').value;
  const cat = document.getElementById('filter-category').value;
  const sent = document.getElementById('filter-sentiment').value;
  const rev = document.getElementById('filter-revenue').value;
  const query = document.getElementById('search-input').value.toLowerCase();
  const filtered = POSTS.filter(p => {
    if (src && p.source !== src) return false;
    if (cat && p.category !== cat) return false;
    if (sent && p.sentiment !== sent) return false;
    if (rev && p.has_revenue_info !== 1) return false;
    if (query) {
      const text = (p.title + ' ' + p.selftext + ' ' + p.tech_stack + ' ' + p.target_audience).toLowerCase();
      if (!text.includes(query)) return false;
    }
    return true;
  });
  renderPosts(filtered);
}

function clearFilters() {
  document.getElementById('filter-source').value = '';
  document.getElementById('filter-category').value = '';
  document.getElementById('filter-sentiment').value = '';
  document.getElementById('filter-revenue').value = '';
  document.getElementById('search-input').value = '';
  renderPosts(POSTS);
}

function truncate(str, len) {
  if (!str) return '';
  return str.length > len ? str.slice(0, len) + '...' : str;
}
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

init();
</script>
</body>
</html>
"""


def build_site():
    """从 posts.json 构建静态 index.html"""
    json_path = os.path.join(DATA_DIR, "posts.json")
    if not os.path.exists(json_path):
        print(f"[ERROR] {json_path} not found. Run fetcher first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    posts_json_str = json.dumps(posts, ensure_ascii=False)

    html_content = TEMPLATE.replace("{POSTS_JSON}", posts_json_str)
    html_content = html_content.replace("{BUILD_TIME}", build_time)

    output_path = os.path.join(STATIC_DIR, "index.html")
    os.makedirs(STATIC_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[BUILD] Static site generated: {output_path}")
    print(f"[BUILD] Total posts: {len(posts)}")


if __name__ == "__main__":
    build_site()
