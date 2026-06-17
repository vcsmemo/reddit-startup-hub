# Reddit API 配置指南

## 为什么需要配置 Reddit API

当前 MVP 使用模拟数据展示功能。要接入真实 Reddit 数据，需要配置 Reddit OAuth API。

Reddit 的公开 JSON API（`reddit.com/r/xxx.json`）已被限制，返回 403。必须使用官方 OAuth API。

---

## 步骤 1：注册 Reddit App

1. 访问 https://www.reddit.com/prefs/apps
2. 点击 "create another app..."
3. 选择类型：**script**
4. 填写信息：
   - **name**: `reddit-startup-hub`（或其他）
   - **description**: 自动抓取创业 subreddit
   - **about url**: 你的站点 URL（或留空）
   - **redirect uri**: `http://localhost:8080`（script 类型不需要实际回调）
5. 点击 "create app"
6. 记下：
   - **client id**（在 app 名称下方的一串字符）
   - **client secret**（点击 "edit" 后可见）

---

## 步骤 2：创建环境变量

在项目根目录创建 `.env` 文件：

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=reddit-startup-hub/1.0 by u/your_username
```

---

## 步骤 3：修改 fetcher.py 使用 OAuth

当前 `fetcher.py` 使用公开 JSON API（已被封）。需要改为 OAuth 方式。

安装依赖：

```bash
pip3 install praw python-dotenv
```

然后修改 `fetcher.py` 的 `fetch_subreddit_posts` 函数：

```python
import praw
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

def fetch_subreddit_posts(subreddit: str, limit: int = 25, sort: str = "hot"):
    sub = reddit.subreddit(subreddit)
    method = getattr(sub, sort, sub.hot)
    posts = []
    for post in method(limit=limit):
        posts.append({
            "id": post.id,
            "subreddit": post.subreddit.display_name,
            "title": post.title,
            "author": str(post.author) if post.author else None,
            "score": post.score,
            "num_comments": post.num_comments,
            "upvote_ratio": post.upvote_ratio,
            "url": post.url,
            "selftext": post.selftext,
            "created_utc": post.created_utc,
            "permalink": f"https://www.reddit.com{post.permalink}",
        })
    return posts
```

---

## 步骤 4：自动化更新

### 本地 Cron（Linux/macOS）

```bash
# 每 4 小时运行一次
0 */4 * * * cd /path/to/reddit-startup-hub && ./update.sh >> /var/log/reddit-hub.log 2>&1
```

### GitHub Actions（免费，推荐）

创建 `.github/workflows/update.yml`：

```yaml
name: Update Reddit Data

on:
  schedule:
    - cron: '0 */4 * * *'  # 每 4 小时
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install praw python-dotenv
      - run: python src/fetcher.py
        env:
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
          REDDIT_USERNAME: ${{ secrets.REDDIT_USERNAME }}
          REDDIT_PASSWORD: ${{ secrets.REDDIT_PASSWORD }}
      - run: python src/build_site.py
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./static
```

---

## 速率限制

Reddit OAuth API 限制：
- 未认证：10 requests/minute
- 认证（OAuth）：60 requests/minute
- 8 个 subreddit × 25 posts = 8 请求，远低于限制

---

## 替代方案（无需 Reddit 账号）

如果你不想注册 Reddit App，可以使用以下替代方案：

1. **使用 kimi_search_v2** 定期搜索 Reddit 创业帖子，解析后存入数据库
2. **使用第三方 Reddit API**（如 `https://www.reddit.com/r/SaaS/hot.json` 偶尔可用，但不稳定）
3. **使用 RSS 订阅**（Reddit 提供 RSS feed：`https://www.reddit.com/r/SaaS/hot/.rss`）

当前 MVP 已使用模拟数据完整展示了所有功能，接入真实数据只是替换数据源的问题。
