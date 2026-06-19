"""
Build static site — generates index.html from posts.json
Reddit Startup Hub style (inspired by redditalpha.xyz)
"""
import json
import os
import html as html_module
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Subreddit colors mapping
SUB_COLORS = {
    "SaaS": "#3b82f6",
    "startups": "#10b981",
    "indiehackers": "#f59e0b",
    "Entrepreneur": "#8b5cf6",
    "SideProject": "#ec4899",
    "bootstrapped": "#14b8a6",
    "Startup_Ideas": "#f97316",
    "ExperiencedDevs": "#6366f1",
}

# Category emoji mapping
CAT_EMOJI = {
    "showcase": "🚀",
    "ask_feedback": "❓",
    "revenue": "💰",
    "growth_marketing": "📈",
    "tech_stack": "⚙️",
    "hiring": "👥",
    "funding": "💵",
    "lessons": "📚",
    "open_source": "🔓",
    "ai_ml": "🤖",
    "no_code": "🧩",
    "burnout_mental": "🧠",
    "general": "📋",
}

# Sentiment colors
SENTIMENT_COLORS = {
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral": "#6b7280",
}


def build_site():
    json_path = os.path.join(DATA_DIR, "posts.json")
    if not os.path.exists(json_path):
        print(f"[ERROR] {json_path} not found. Run fetcher or seed_mock first.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Stats
    total_posts = len(posts)
    subreddits = sorted(set(p.get("subreddit", "") for p in posts if p.get("subreddit")))
    sources = len(set(p.get("source", "reddit") for p in posts))
    revenue_posts = len([p for p in posts if p.get("has_revenue_info") == 1])
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_posts = len([p for p in posts if p.get("created_date", "") == today_str])
    categories = sorted(set(p.get("category", "general") for p in posts))
    
    # Legends data (hardcoded for now, can be dynamic later)
    legends = [
        {
            "year": "2019",
            "name": "Pieter Levels",
            "handle": "@levelsio",
            "metric": "$3M+/year",
            "tagline": "Solo founder, 20+ products, nomad lifestyle",
            "bio": "Built Nomad List, Photo AI, and 20+ other products as a solo founder. Proves that indie hacking at scale is possible. Open about revenue, failures, and process.",
            "emoji": "👑",
        },
        {
            "year": "2023",
            "name": "Marc Lou",
            "handle": "@marc_lou",
            "metric": "$1M+ ARR",
            "tagline": "Cal.com, open-source scheduling",
            "bio": "Built Cal.com into a $1M+ ARR open-source scheduling platform. Transparent about fundraising, team building, and the challenges of open-source monetization.",
            "emoji": "📅",
        },
        {
            "year": "2023",
            "name": "Tyler",
            "handle": "u/tyler_scionti",
            "metric": "$40K MRR",
            "tagline": "AI wrapper, no-code builder",
            "bio": "Built an AI wrapper SaaS to $40K MRR with no coding knowledge. Uses Bubble, Make, and OpenAI. Proves that technical skills are not required to build a successful SaaS.",
            "emoji": "🤖",
        },
        {
            "year": "2022",
            "name": "Solo Dev Agency",
            "handle": "r/bootstrapped",
            "metric": "$1.5M ARR",
            "tagline": "Single-person agency, SEO for SaaS",
            "bio": "Runs a single-person agency doing SEO and content for B2B SaaS companies. $1.5M ARR with no employees. The ultimate example of productized services and niche focus.",
            "emoji": "💼",
        },
        {
            "year": "2024",
            "name": "Open Source Hero",
            "handle": "@open_source_founder",
            "metric": "12K stars",
            "tagline": "Open-sourced entire SaaS stack",
            "bio": "Open-sourced a full-stack SaaS starter kit and got 12K GitHub stars in 30 days. Turned open source into the top of the funnel, growing paid MRR from $15K to $28K.",
            "emoji": "🔓",
        },
    ]

    # Communities data
    communities = [
        ("r/SaaS", "200K+", "SaaS operations, pricing, growth"),
        ("r/startups", "1.5M+", "General startup discussions"),
        ("r/indiehackers", "100K+", "Building in public, revenue milestones"),
        ("r/Entrepreneur", "3M+", "Entrepreneurship stories"),
        ("r/SideProject", "150K+", "Project showcases, MVP feedback"),
        ("r/bootstrapped", "50K+", "Self-funded business journeys"),
        ("r/Startup_Ideas", "80K+", "Idea validation, feedback"),
        ("r/ExperiencedDevs", "200K+", "Technical architecture decisions"),
    ]

    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    # Convert posts to JSON string for embedding
    posts_json = json.dumps(posts, ensure_ascii=False)
    
    # Generate legends HTML
    legends_html = ""
    for i, leg in enumerate(legends):
        legends_html += f"""
        <div class="legend-card" style="animation-delay: {i * 0.1}s">
          <div class="legend-year">{leg['year']}★ Spotlight</div>
          <div class="legend-emoji">{leg['emoji']}</div>
          <div class="legend-name">{leg['name']}</div>
          <div class="legend-handle">{leg['handle']}</div>
          <div class="legend-metric">{leg['metric']}</div>
          <div class="legend-tagline">{leg['tagline']}</div>
          <div class="legend-bio">{leg['bio']}</div>
        </div>
        """

    # Generate communities HTML
    comms_html = ""
    for name, subs, desc in communities:
        short = name.replace("r/", "")
        color = SUB_COLORS.get(short, "#f5a623")
        comms_html += f"""
        <div class="comm-card">
          <div class="comm-icon" style="background: {color}20; color: {color}">{name[:2]}</div>
          <div class="comm-name">{name}</div>
          <div class="comm-subs">{subs}</div>
          <div class="comm-desc">{desc}</div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reddit Startup Hub — Live SaaS & AI Intel from Reddit</title>
<meta name="description" content="Track mindshare, sentiment and narratives across Reddit's startup communities in real time. No signup — just open and go.">
<style>
:root {{
  --bg: #0a0a0a;
  --bg-elevated: #111111;
  --card: #111111;
  --border: #1a1a1a;
  --text: #ffffff;
  --text-secondary: #888888;
  --text-muted: #555555;
  --accent: #f5a623;
  --accent-dim: #f5a62340;
  --positive: #10b981;
  --negative: #ef4444;
  --neutral: #6b7280;
  --radius: 12px;
  --radius-sm: 6px;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}

/* HERO */
.hero {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 80px 24px;
  position: relative;
  overflow: hidden;
}}
.hero::before {{
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 50% 50%, #f5a62308 0%, transparent 50%);
  pointer-events: none;
}}
.hero-tag {{
  display: inline-block;
  padding: 6px 16px;
  border: 1px solid #f5a62340;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 500;
  color: var(--accent);
  letter-spacing: 0.5px;
  margin-bottom: 32px;
  text-transform: uppercase;
}}
.hero h1 {{
  font-size: clamp(36px, 6vw, 72px);
  font-weight: 700;
  letter-spacing: -2px;
  line-height: 1.1;
  margin-bottom: 24px;
  max-width: 800px;
}}
.hero h1 .highlight {{ color: var(--accent); }}
.hero-sub {{
  font-size: clamp(16px, 2vw, 20px);
  color: var(--text-secondary);
  max-width: 600px;
  margin-bottom: 40px;
  line-height: 1.6;
}}
.hero-cta {{
  display: inline-block;
  padding: 14px 32px;
  background: var(--accent);
  color: #000;
  font-weight: 600;
  font-size: 15px;
  border-radius: 100px;
  text-decoration: none;
  transition: all 0.2s;
  margin-bottom: 64px;
}}
.hero-cta:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 30px #f5a62340;
}}

/* STATS BAR */
.stats-bar {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 24px;
  max-width: 900px;
  width: 100%;
}}
.stat-item {{
  text-align: center;
  padding: 20px;
  background: #ffffff05;
  border: 1px solid #ffffff08;
  border-radius: var(--radius);
  transition: all 0.2s;
}}
.stat-item:hover {{
  border-color: #f5a62330;
  background: #ffffff08;
}}
.stat-num {{
  font-size: 32px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 6px;
}}
.stat-label {{
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

/* SECTIONS */
.section {{
  padding: 80px 0;
  border-top: 1px solid var(--border);
}}
.section-title {{
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 700;
  letter-spacing: -1px;
  margin-bottom: 12px;
}}
.section-sub {{
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 48px;
  max-width: 600px;
}}

/* LEGENDS */
.legends-scroll {{
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 8px 4px 24px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}}
.legends-scroll::-webkit-scrollbar {{
  height: 4px;
}}
.legends-scroll::-webkit-scrollbar-track {{
  background: var(--border);
  border-radius: 2px;
}}
.legends-scroll::-webkit-scrollbar-thumb {{
  background: var(--accent);
  border-radius: 2px;
}}
.legend-card {{
  flex: 0 0 320px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px;
  scroll-snap-align: start;
  transition: all 0.3s;
  animation: fadeInUp 0.6s ease both;
}}
.legend-card:hover {{
  border-color: #f5a62330;
  transform: translateY(-4px);
}}
.legend-year {{
  font-size: 12px;
  color: var(--accent);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
}}
.legend-emoji {{
  font-size: 36px;
  margin-bottom: 12px;
}}
.legend-name {{
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}}
.legend-handle {{
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
}}
.legend-metric {{
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 8px;
}}
.legend-tagline {{
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 12px;
}}
.legend-bio {{
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}}

/* COMMUNITIES */
.comms-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}}
.comm-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.2s;
}}
.comm-card:hover {{
  border-color: #f5a62330;
}}
.comm-icon {{
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
}}
.comm-name {{
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}}
.comm-subs {{
  font-size: 13px;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 4px;
}}
.comm-desc {{
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}}

/* DASHBOARD */
.dashboard-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 32px;
}}
.dashboard-title {{
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}}
.dashboard-meta {{
  font-size: 13px;
  color: var(--text-muted);
}}

/* FILTERS */
.filters {{
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 32px;
  align-items: center;
}}
.filters select, .filters input {{
  background: var(--card);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}}
.filters select:hover, .filters input:hover {{
  border-color: var(--text-muted);
}}
.filters select:focus, .filters input:focus {{
  border-color: var(--accent);
}}
.filter-btn {{
  background: var(--accent);
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}}
.filter-btn:hover {{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px #f5a62330;
}}
.filter-btn.clear {{
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}}
.filter-btn.clear:hover {{
  border-color: var(--text-muted);
  color: var(--text);
}}

/* BRIEF */
.brief-section {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  margin-bottom: 32px;
}}
.brief-title {{
  font-size: 16px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.brief-list {{
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.brief-item {{
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: #ffffff04;
  transition: all 0.2s;
}}
.brief-item:hover {{
  background: #ffffff08;
}}
.brief-rank {{
  font-weight: 700;
  color: var(--accent);
  min-width: 24px;
  font-size: 14px;
}}
.brief-link {{
  color: var(--text);
  text-decoration: none;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.brief-link:hover {{
  color: var(--accent);
}}
.brief-meta {{
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}}

/* CARDS GRID */
.cards-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}}
@media (max-width: 768px) {{
  .cards-grid {{ grid-template-columns: 1fr; }}
  .hero h1 {{ font-size: 36px; }}
  .stats-bar {{ grid-template-columns: repeat(2, 1fr); }}
  .legends-scroll {{ flex-direction: column; flex: none; }}
  .legend-card {{ flex: none; width: 100%; }}
}}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}}
.card:hover {{
  border-color: #f5a62330;
  transform: translateY(-2px);
}}
.card-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}}
.card-title {{
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  flex: 1;
}}
.card-title a {{
  color: var(--text);
  text-decoration: none;
}}
.card-title a:hover {{
  color: var(--accent);
}}
.card-badges {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}}
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  line-height: 1;
}}
.badge-sub {{
  background: #1e3a5f;
  color: #60a5fa;
}}
.badge-cat {{
  background: #1e1a3f;
  color: #a78bfa;
}}
.badge-sent-pos {{ background: #064e3b; color: #34d399; }}
.badge-sent-neg {{ background: #450a0a; color: #f87171; }}
.badge-sent-neu {{ background: #374151; color: #9ca3af; }}
.badge-rev {{
  background: #451a03;
  color: #fbbf24;
}}
.card-excerpt {{
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
  flex: 1;
}}
.card-tags {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}}
.tag {{
  font-size: 11px;
  color: var(--text-muted);
  background: #ffffff08;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #ffffff08;
}}
.card-footer {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-muted);
}}
.card-stats {{
  display: flex;
  gap: 12px;
}}

/* FOOTER */
.footer {{
  text-align: center;
  padding: 48px 24px;
  border-top: 1px solid var(--border);
  font-size: 13px;
  color: var(--text-muted);
}}
.footer a {{
  color: var(--text-secondary);
  text-decoration: none;
}}
.footer a:hover {{
  color: var(--accent);
}}

/* ANIMATIONS */
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* SCROLL HINT */
.scroll-hint {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 12px;
}}
</style>
</head>
<body>

<!-- HERO -->
<section class="hero">
  <div class="hero-tag">Live · Real · All-in-One Reddit Startup Intel</div>
  <h1>Reddit is the best place for <span class="highlight">startup founders</span>.</h1>
  <p class="hero-sub">This is where legends are built — signal so good that VCs copy the homework. Track mindshare, sentiment and narratives across Reddit's startup communities in real time.</p>
  <a href="#dashboard" class="hero-cta">Enter live dashboard</a>
  
  <div class="stats-bar">
    <div class="stat-item"><div class="stat-num">{len(subreddits)}</div><div class="stat-label">Communities</div></div>
    <div class="stat-item"><div class="stat-num">3.2M+</div><div class="stat-label">Subscribers</div></div>
    <div class="stat-item"><div class="stat-num">{total_posts}</div><div class="stat-label">Live Posts</div></div>
    <div class="stat-item"><div class="stat-num">{revenue_posts}</div><div class="stat-label">Revenue Mentions</div></div>
    <div class="stat-item"><div class="stat-num">{len(categories)}</div><div class="stat-label">Categories</div></div>
  </div>
</section>

<!-- LEGENDS -->
<section class="section">
  <div class="container">
    <h2 class="section-title">Legends forged on Reddit</h2>
    <p class="section-sub">Real people · real track records. Reddit isn't just noise — here, deep public research and transparent sharing have built empires.</p>
    <div class="legends-scroll">
      {legends_html}
    </div>
    <div class="scroll-hint">← swipe · Reddit legends, past to present →</div>
  </div>
</section>

<!-- COMMUNITIES -->
<section class="section">
  <div class="container">
    <h2 class="section-title">Communities tracked</h2>
    <p class="section-sub">We monitor the best startup, SaaS, and indie hacker communities on Reddit for signal.</p>
    <div class="comms-grid">
      {comms_html}
    </div>
  </div>
</section>

<!-- DASHBOARD -->
<section class="section" id="dashboard">
  <div class="container">
    <div class="dashboard-header">
      <div>
        <h2 class="dashboard-title">Live Dashboard</h2>
        <div class="dashboard-meta">Daily refresh · {build_time} UTC</div>
      </div>
    </div>

    <div class="brief-section">
      <div class="brief-title">🔥 Top 10 High-Signal Posts</div>
      <div class="brief-list" id="brief-list"></div>
    </div>

    <div class="filters">
      <select id="filter-subreddit"><option value="">All Communities</option></select>
      <select id="filter-category"><option value="">All Categories</option></select>
      <select id="filter-sentiment"><option value="">All Sentiment</option><option value="positive">Positive</option><option value="negative">Negative</option><option value="neutral">Neutral</option></select>
      <select id="filter-revenue"><option value="">All Posts</option><option value="1">Revenue Data</option></select>
      <input type="text" id="search-input" placeholder="Search keywords..." style="width: 180px;">
      <button class="filter-btn" onclick="applyFilters()">Apply</button>
      <button class="filter-btn clear" onclick="clearFilters()">Reset</button>
    </div>

    <div class="cards-grid" id="post-grid"></div>
  </div>
</section>

<footer class="footer">
  <p>Data auto-fetched from Reddit communities · refreshed every 4 hours · <a href="https://github.com/vcsmemo/reddit-startup-hub">GitHub</a></p>
</footer>

<script>
const POSTS = {posts_json};
const CAT_EMOJI = {json.dumps(CAT_EMOJI)};
const SUB_COLORS = {json.dumps(SUB_COLORS)};
const SENTIMENT_COLORS = {json.dumps(SENTIMENT_COLORS)};

function init() {{
  populateFilters();
  renderBrief();
  renderPosts(POSTS);
}}

function populateFilters() {{
  const subs = [...new Set(POSTS.map(p => p.subreddit))].sort();
  const cats = [...new Set(POSTS.map(p => p.category))].sort();
  const subSel = document.getElementById('filter-subreddit');
  const catSel = document.getElementById('filter-category');
  subs.forEach(s => {{
    const color = SUB_COLORS[s] || '#f5a623';
    subSel.add(new Option(s, s));
  }});
  cats.forEach(c => {{
    const emoji = CAT_EMOJI[c] || '📋';
    catSel.add(new Option(emoji + ' ' + c.replace(/_/g, ' '), c));
  }});
}}

function renderBrief() {{
  const top = [...POSTS]
    .filter(p => p.score >= 50)
    .sort((a, b) => (b.score + b.num_comments) - (a.score + a.num_comments))
    .slice(0, 10);
  const el = document.getElementById('brief-list');
  el.innerHTML = top.map((p, i) => `
    <div class="brief-item">
      <span class="brief-rank">${{i+1}}</span>
      <a class="brief-link" href="${{p.permalink}}" target="_blank" title="${{escapeHtml(p.title)}}">${{truncate(p.title, 55)}}</a>
      <span class="brief-meta">${{p.subreddit}} · ${{p.score}}↑ · ${{p.num_comments}}💬</span>
    </div>
  `).join('');
}}

function renderPosts(posts) {{
  const el = document.getElementById('post-grid');
  if (posts.length === 0) {{
    el.innerHTML = '<p style="text-align:center;color:#555;padding:40px 0">No matching posts found</p>';
    return;
  }}
  el.innerHTML = posts.map(p => {{
    const subColor = SUB_COLORS[p.subreddit] || '#f5a623';
    const catEmoji = CAT_EMOJI[p.category] || '📋';
    const sentClass = 'badge-sent-' + p.sentiment;
    const sentLabel = p.sentiment.charAt(0).toUpperCase() + p.sentiment.slice(1);
    return `
    <div class="card" data-sub="${{p.subreddit}}" data-cat="${{p.category}}" data-sent="${{p.sentiment}}" data-rev="${{p.has_revenue_info}}">
      <div class="card-header">
        <div class="card-title"><a href="${{p.permalink}}" target="_blank">${{escapeHtml(p.title)}}</a></div>
      </div>
      <div class="card-badges">
        <span class="badge badge-sub" style="background:${{subColor}}20;color:${{subColor}}">${{p.subreddit}}</span>
        <span class="badge badge-cat">${{catEmoji}} ${{p.category.replace(/_/g, ' ')}}</span>
        <span class="badge ${{sentClass}}">${{sentLabel}}</span>
        ${{p.has_revenue_info ? '<span class="badge badge-rev">💰 Revenue</span>' : ''}}
      </div>
      <div class="card-excerpt">${{escapeHtml(p.extracted_summary)}}</div>
      ${{p.tech_stack ? `<div class="card-tags"><span class="tag">⚙️ ${{escapeHtml(p.tech_stack)}}</span></div>` : ''}}
      ${{p.revenue_pattern ? `<div class="card-tags"><span class="tag">💰 ${{escapeHtml(p.revenue_pattern)}}</span></div>` : ''}}
      <div class="card-footer">
        <div>👤 ${{p.author || 'unknown'}} · 📅 ${{p.created_date}}</div>
        <div class="card-stats">
          <span>⬆ ${{p.score}}</span>
          <span>💬 ${{p.num_comments}}</span>
          ${{p.upvote_ratio ? `<span>📊 ${{Math.round(p.upvote_ratio * 100)}}%</span>` : ''}}
        </div>
      </div>
    </div>
    `;
  }}).join('');
}}

function applyFilters() {{
  const sub = document.getElementById('filter-subreddit').value;
  const cat = document.getElementById('filter-category').value;
  const sent = document.getElementById('filter-sentiment').value;
  const rev = document.getElementById('filter-revenue').value;
  const query = document.getElementById('search-input').value.toLowerCase();
  const filtered = POSTS.filter(p => {{
    if (sub && p.subreddit !== sub) return false;
    if (cat && p.category !== cat) return false;
    if (sent && p.sentiment !== sent) return false;
    if (rev && p.has_revenue_info !== 1) return false;
    if (query) {{
      const text = (p.title + ' ' + p.selftext + ' ' + p.tech_stack + ' ' + p.target_audience + ' ' + p.pain_point).toLowerCase();
      if (!text.includes(query)) return false;
    }}
    return true;
  }});
  renderPosts(filtered);
}}

function clearFilters() {{
  document.getElementById('filter-subreddit').value = '';
  document.getElementById('filter-category').value = '';
  document.getElementById('filter-sentiment').value = '';
  document.getElementById('filter-revenue').value = '';
  document.getElementById('search-input').value = '';
  renderPosts(POSTS);
}}

function truncate(str, len) {{
  if (!str) return '';
  return str.length > len ? str.slice(0, len) + '...' : str;
}}
function escapeHtml(text) {{
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}}

init();
</script>

</body>
</html>
"""

    output_path = os.path.join(STATIC_DIR, "index.html")
    os.makedirs(STATIC_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[BUILD] Static site generated: {output_path}")
    print(f"[BUILD] Total posts: {len(posts)}")


if __name__ == "__main__":
    build_site()
