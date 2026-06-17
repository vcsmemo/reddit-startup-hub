# Reddit 创业情报站

自动抓取 Reddit 创业社区（SaaS / startups / indiehackers / Entrepreneur 等），提取结构化创业信息，生成可浏览的情报站。

## 技术栈

- **Python 3.11** — 数据抓取 + 结构化提取
- **SQLite** — 本地数据存储
- **HTML/CSS/JS** — 静态前端（无需服务器）
- **Cloudflare Workers** — Reddit 代理（绕过 403/429 限制）
- **GitHub Actions** — 自动定时更新
- **GitHub Pages** — 免费静态站点托管

**总成本：$0 / 月**

---

## 快速部署（5 分钟）

### 步骤 1：创建 Cloudflare Worker（2 分钟）

1. 访问 [dash.cloudflare.com](https://dash.cloudflare.com) 注册/登录
2. 左侧菜单 → **Workers & Pages** → **Create**
3. 点击 **Create Worker**（保留默认名称，如 `reddit-proxy-xxx`）
4. 在编辑器中，删除默认代码，**粘贴 `proxy/cloudflare-worker.js` 中的代码**
5. 点击 **Deploy**
6. 获得 Worker URL：`https://reddit-proxy-xxx.your-subdomain.workers.dev`
7. **复制这个 URL**

### 步骤 2：创建 GitHub 仓库（1 分钟）

1. 访问 [github.com/new](https://github.com/new) 创建新仓库
2. 名称：`reddit-startup-hub`（或其他）
3. 设置为 **Public**（GitHub Pages 免费需要公开仓库）
4. 点击 **Create repository**

### 步骤 3：上传代码到 GitHub（1 分钟）

```bash
# 在本地项目目录执行
cd /path/to/reddit-startup-hub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/reddit-startup-hub.git
git push -u origin main
```

### 步骤 4：配置 GitHub Secrets（1 分钟）

1. 打开 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. **Name**: `CF_WORKER_URL`
4. **Value**: 你复制的 Cloudflare Worker URL（如 `https://reddit-proxy-xxx.your-subdomain.workers.dev`）
5. 点击 **Add secret**

### 步骤 5：启用 GitHub Pages（1 分钟）

1. 仓库 → **Settings** → **Pages**
2. **Source**: 选择 **GitHub Actions**
3. 完成！

---

## 验证部署

### 手动触发第一次运行

1. 仓库 → **Actions** → **Update Reddit Data & Deploy Site**
2. 点击右侧 **Run workflow** → **Run workflow**
3. 等待 2-3 分钟，查看运行日志

### 访问站点

- 站点地址：`https://YOUR_USERNAME.github.io/reddit-startup-hub/`
- 每次运行后自动更新（每 4 小时）

---

## 数据抓取方式

### 方式 1：Cloudflare Worker 代理（推荐，零 Reddit 注册）

- 通过 Cloudflare CDN 代理 Reddit JSON API
- 绕过 IP 限制，完全免费
- 需要配置 `CF_WORKER_URL` 环境变量
- 已在 GitHub Actions 中配置

### 方式 2：自有 VPS（备选）

- 购买 $5/月 VPS（Vultr / DigitalOcean / Hetzner）
- 干净 IP 直接访问 Reddit RSS/JSON 不会被限制
- 在 VPS 上运行 `update.sh` 定时任务
- 推送到 GitHub Pages 或部署到自有服务器

### 方式 3：Reddit 官方 API（最稳定，但需要注册）

- 访问 https://www.reddit.com/prefs/apps 注册 App
- 获得 `client_id` + `client_secret`
- 详见 `REDDIT_API_SETUP.md`

---

## 本地开发

```bash
# 1. 安装依赖
pip install requests

# 2. 生成模拟数据（演示模式，不需要 Reddit）
python src/seed_mock.py

# 3. 构建静态站点
python src/build_site.py

# 4. 本地预览
open static/index.html

# 5. 接入真实数据（需要配置 CF Worker）
export CF_WORKER_URL="https://your-worker.workers.dev"
python src/fetcher.py
python src/build_site.py
```

---

## 目录结构

```
reddit-startup-hub/
├── .github/workflows/
│   └── update.yml         # GitHub Actions 自动更新
├── src/
│   ├── fetcher.py         # 核心抓取脚本（支持 CF Worker 代理）
│   ├── build_site.py      # 构建静态站点
│   └── seed_mock.py       # 模拟数据（演示用）
├── proxy/
│   └── cloudflare-worker.js  # CF Worker 代理代码
├── data/
│   ├── posts.db           # SQLite 数据库
│   └── posts.json         # 前端数据（自动导出）
├── static/
│   └── index.html         # 静态站点（自动构建）
├── README.md              # 本文件
└── REDDIT_API_SETUP.md    # Reddit 官方 API 配置说明
```

---

## 功能特性

- **自动抓取**：8 个核心创业 subreddit，每 4 小时更新
- **结构化提取**：收入/MRR、技术栈、目标受众、痛点、情绪、分类
- **今日简报**：Top 10 高价值帖子，按互动量排序
- **多维筛选**：按 subreddit / 分类 / 情绪 / 含收入数据 / 关键词搜索
- **响应式前端**：暗色主题，桌面和移动端自适应
- **零成本部署**：完全免费（Cloudflare + GitHub）

---

## 数据来源

| Subreddit | 成员数 | 适合内容 |
|-----------|--------|----------|
| r/SaaS | 200K+ | SaaS 运营、定价、增长策略 |
| r/startups | 1.5M+ | 通用创业讨论、反馈 |
| r/indiehackers | 100K+ | Building in public、收入里程碑 |
| r/Entrepreneur | 3M+ | 创业经验、商业故事 |
| r/SideProject | 150K+ | 项目展示、MVP 反馈 |
| r/bootstrapped | 50K+ | 自举创业经验 |
| r/Startup_Ideas | 80K+ | 创业想法验证 |
| r/ExperiencedDevs | 200K+ | 技术架构决策 |

---

## 商业化路径

- **订阅制**：高级搜索、数据导出、行业报告
- **数据 API**：为其他工具提供 Reddit 创业情报
- **Affiliate**：推荐创业工具（Stripe、Vercel 等）
- **赞助**：B2B SaaS 工具推广

---

## 成本分析

| 方案 | 注册成本 | 运行成本 | 维护成本 | 推荐度 |
|------|----------|----------|----------|--------|
| **CF Worker + GitHub Actions** | CF 账号（免费） | **$0** | 低 | ⭐⭐⭐ 推荐 |
| 自有 VPS + 定时任务 | 无需注册 | $5/月 | 低 | ⭐⭐ 备选 |
| Reddit OAuth API | Reddit App 注册 | 免费 | 中 | ⭐⭐ 备选 |
