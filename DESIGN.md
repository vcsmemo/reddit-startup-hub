# Design Spec — Reddit Startup Hub (learning from redditalpha.xyz)

## Product Positioning
**Tagline**: "Live · real · all-in-one Reddit startup intel"
**Mission**: Reddit is where SaaS founders are forged. Track mindshare, sentiment and narratives across Reddit's startup communities in real time.

## Page Structure (single-scroll, full-bleed sections)

### 1. Hero Section (100vh, dark)
- Background: #0a0a0a with subtle gradient
- Headline: "Reddit is the best place for startup founders."
- Subhead: "This is where legends are built — signal so good that VCs copy the homework."
- CTA: "Enter live dashboard" → scroll to dashboard
- Stats bar (5 cards, large numbers):
  - 8 startup communities
  - 3.2M+ total subscribers
  - 1,200+ live posts tracked
  - 50+ SaaS tools discovered
  - 400+ active founders

### 2. Legends Section (dark, full-width)
- Title: "Legends forged on Reddit"
- Subtitle: "Real people · real track records"
- Horizontal scrollable cards (time-line style):
  - Pieter Levels (2019) — PhotoAI, $132K MRR, solo founder
  - Tyler (2023) — AI wrapper, $40K MRR, no-code builder
  - Marc Lou (2023) — Cal.com, open source, $1M+ ARR
  - Pieter Levels (2022) — Nomad List, $3M+/year
  - Solo dev agency (2024) — $1.5M ARR, one person
- Each card: avatar, year badge, name, handle, key metric, category, brief bio

### 3. Communities Section (dark, compact)
- Grid of subreddit logos/badges with subscriber counts
- r/SaaS, r/startups, r/indiehackers, r/Entrepreneur, r/SideProject, r/bootstrapped, r/Startup_Ideas, r/ExperiencedDevs

### 4. Live Dashboard (dark, the main content)
- Top bar: filters + search + sentiment toggle
- Stats mini-bar: total posts, revenue mentions, tech stacks, positive sentiment
- Card grid (3-column desktop, 1-column mobile)
- Each card:
  - Subreddit badge (colored)
  - Title + link to Reddit
  - Author + date
  - Sentiment badge (positive/neutral/negative)
  - Category badge (Launch, Revenue, Growth, Tech Stack, Lessons, etc.)
  - Revenue badge if detected ($)
  - Tech stack tags
  - Upvote score + comment count
  - Brief excerpt (first 200 chars)

### 5. Footer (dark, minimal)
- "Data auto-fetched from Reddit public API · refreshed every 4 hours"
- Links: GitHub, About

## Color Palette
- Background: #0a0a0a (hero), #0f0f0f (content)
- Card: #111111 with #1a1a1a border
- Text primary: #ffffff
- Text secondary: #888888
- Text muted: #555555
- Accent: #f5a623 (amber/gold for highlights)
- Accent secondary: #10b981 (emerald for positive)
- Accent negative: #ef4444 (red for negative)
- Accent neutral: #6b7280 (gray for neutral)
- Subreddit colors:
  - r/SaaS: #3b82f6 (blue)
  - r/startups: #10b981 (emerald)
  - r/indiehackers: #f59e0b (amber)
  - r/Entrepreneur: #8b5cf6 (violet)
  - r/SideProject: #ec4899 (pink)
  - r/bootstrapped: #14b8a6 (teal)
  - r/Startup_Ideas: #f97316 (orange)
  - r/ExperiencedDevs: #6366f1 (indigo)

## Typography
- Headline: 64px / 700 / -1.5px letter-spacing
- Section title: 48px / 700
- Stats number: 48px / 700 / accent color
- Card title: 18px / 600
- Body: 16px / 400 / 1.6 line-height
- Tags/badges: 12px / 600 / uppercase / 0.5px letter-spacing

## Interactions
- Smooth scroll on CTA click
- Card hover: lift + border glow
- Filter buttons: active state with accent border
- Search: real-time filtering (client-side)
- Legends: horizontal scroll with drag
- Cards: staggered fade-in on load
