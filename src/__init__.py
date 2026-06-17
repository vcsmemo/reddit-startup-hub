"""
Reddit 创业情报站 — 抓取器架构说明

## 为什么直接请求 Reddit 会被 403/429

当前环境 IP 被 Reddit 限制（可能是共享 IP 或请求频率过高）。
但通过浏览器（WebBridge）可以正常访问 — 因为浏览器有真实的用户行为。

## redditalpha 可能使用的数据获取方式

### 方案 1: Reddit 官方 API (OAuth)
- 需要注册 App: https://www.reddit.com/prefs/apps
- 最稳定、最可靠
- 速率限制: 60 req/min (OAuth)
- redditalpha 几乎肯定使用此方案（长期产品）
- 我们已在 fetcher.py 中预留了此接口

### 方案 2: 浏览器自动化 (Puppeteer/Playwright/Selenium)
- 完全绕过 IP 限制（因为行为像真实用户）
- 抓取 JSON 端点: https://www.reddit.com/r/SaaS/hot.json?limit=25
- 获取完整数据: score, comments, upvote_ratio, selftext
- 适合在自有服务器上运行
- 资源消耗略高于 API，但完全免费

### 方案 3: 自有服务器 + RSS
- 在干净的 VPS/服务器上运行 Python 脚本
- 每 4 小时请求一次 RSS feed
- Reddit 对个人服务器 IP 限制更宽松
- 成本: $5/月 (Vultr/DigitalOcean/Linode)

### 方案 4: Cloudflare Workers 代理
- 通过 Cloudflare 的 CDN 网络转发请求
- Reddit 无法封锁所有 Cloudflare IP
- 免费额度: 100K 请求/天
- 无服务器，完全免费

## 当前 MVP 推荐方案

### 开发阶段 (现在)
- 使用 seed_mock.py 生成的模拟数据
- 展示完整功能和用户体验
- 无需任何 Reddit 配置

### 生产部署 (推荐: 方案 1 + 方案 3)
1. 注册 Reddit App，获取 OAuth 凭证
2. 部署到自有 VPS 或 GitHub Actions
3. 每 4 小时运行一次抓取脚本
4. 自动构建静态站点并部署到 Vercel/GitHub Pages

### 极简方案 (推荐: 方案 3)
1. 购买 $5/月 VPS (Vultr, DigitalOcean, Hetzner)
2. 在 VPS 上运行 Python 抓取脚本
3. 使用 RSS 或 JSON 端点（VPS IP 通常不会被限制）
4. 自动生成静态站点并推送到 GitHub Pages

## 关键结论

- 直接请求: 在当前环境 IP 被限制，但在干净 VPS 上通常没问题
- Reddit 官方 API: 需要注册，但最稳定，redditalpha 很可能使用此方案
- 浏览器自动化: 完全绕过限制，但资源消耗更高
- 推荐生产环境: Reddit OAuth API + 自有 VPS 定时任务
"""

from fetcher import fetch_subreddit_rss, fetch_all, export_json, demo_single_subreddit
from fetcher import extract_structured_info, store_posts
from seed_mock import seed_mock_data, MOCK_POSTS
from build_site import build_site

__all__ = [
    "fetch_subreddit_rss",
    "fetch_all",
    "export_json",
    "demo_single_subreddit",
    "extract_structured_info",
    "store_posts",
    "seed_mock_data",
    "MOCK_POSTS",
    "build_site",
]
