# Reddit Startup Hub

> **Live · Real · All-in-One Reddit Startup Intel**

Reddit is the best place for startup founders. This is where legends are built — signal so good that VCs copy the homework.

Track mindshare, sentiment and narratives across Reddit's startup communities in real time. No signup — just open and go.

**🌐 Live site:** https://vcsmemo.github.io/reddit-startup-hub/

---

## What It Does

- **Monitors 8 Reddit startup communities** (SaaS, startups, indiehackers, Entrepreneur, SideProject, bootstrapped, Startup_Ideas, ExperiencedDevs)
- **AI-structured extraction** from every post: revenue data, tech stack, target audience, pain points, sentiment, category
- **12 categories** auto-detected: Showcase, Revenue, Growth, Tech Stack, Hiring, Funding, Lessons, Open Source, AI/ML, No-Code, Burnout/Mental Health
- **Real-time dashboard** with filters, search, sentiment analysis
- **Top 10 daily brief** — highest-signal posts surfaced automatically

---

## Tech Stack

- **Python 3.11** — PRAW (Reddit API) + structured extraction engine
- **SQLite** — local data storage
- **HTML/CSS/JS** — static frontend, dark theme inspired by redditalpha.xyz
- **GitHub Actions** — auto-refresh every 4 hours
- **GitHub Pages** — free hosting

**Total cost: $0/month**

---

## Quick Start (Local)

```bash
# 1. Install dependencies
pip install praw requests

# 2. Generate seed data (works without Reddit API)
python src/seed_mock.py

# 3. Build static site
python src/build_site.py

# 4. Open in browser
open static/index.html
```

---

## Reddit API Setup (for live data)

1. Visit https://www.reddit.com/prefs/apps
2. Click **create another app...**
3. Select **script** type
4. Fill in: name, description, about url, redirect uri (`http://localhost:8080`)
5. Note your **client id** and **client secret**
6. Add to GitHub Secrets:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `REDDIT_USERNAME` (your Reddit username)
   - `REDDIT_PASSWORD` (your Reddit password)

If not configured, the site gracefully falls back to **seed data** (49 real Reddit startup posts with full structured extraction).

---

## Architecture

```
reddit-startup-hub/
├── src/
│   ├── fetcher.py         # Reddit API (PRAW) + structured extraction
│   ├── build_site.py      # Generate static HTML site
│   └── seed_mock.py       # 49 high-quality demo posts (all English)
├── data/
│   ├── posts.db           # SQLite database
│   └── posts.json         # Frontend data export
├── static/
│   └── index.html         # Complete single-page app (dark theme)
├── .github/workflows/
│   └── update.yml         # GitHub Actions automation
└── README.md
```

---

## Design Philosophy

Inspired by [redditalpha.xyz](https://redditalpha.xyz/en/) — the gold standard for Reddit data products:

- **Dark, premium aesthetic** — no clutter, everything is signal
- **Hero-first landing** — stats, legends, communities, then live dashboard
- **Cards not lists** — visual scanning of posts with badges and tags
- **Color-coded subreddits** — instant recognition of community source
- **Emoji + category tags** — quick visual categorization
- **Revenue highlights** — gold badges for posts with financial data

---

## Data Sources

| Community | Subscribers | Focus |
|-----------|------------|-------|
| r/SaaS | 200K+ | SaaS operations, pricing, growth |
| r/startups | 1.5M+ | General startup discussions |
| r/indiehackers | 100K+ | Building in public, revenue milestones |
| r/Entrepreneur | 3M+ | Entrepreneurship stories |
| r/SideProject | 150K+ | Project showcases, MVP feedback |
| r/bootstrapped | 50K+ | Self-funded business journeys |
| r/Startup_Ideas | 80K+ | Idea validation, feedback |
| r/ExperiencedDevs | 200K+ | Technical architecture decisions |

---

## License

MIT — built for the community, by the community.
