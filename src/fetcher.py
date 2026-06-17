"""
Reddit 创业情报站 — 基于 RSS 的抓取器
完全不需要 Reddit API 认证
数据源: Reddit 公开 RSS feed (https://www.reddit.com/r/{sub}/hot/.rss)
"""
import requests
import xml.etree.ElementTree as ET
import json
import time
import sqlite3
import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any

# 目标 subreddit 列表（SaaS/AI/bootstrap 创业相关）
TARGET_SUBREDDITS = [
    "SaaS",
    "startups",
    "indiehackers",
    "Entrepreneur",
    "SideProject",
    "bootstrapped",
    "Startup_Ideas",
    "ExperiencedDevs",
]

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DATA_DIR, "posts.db")

RSS_BASE = "https://www.reddit.com/r/{subreddit}/hot/.rss"
RSS_NS = {"": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/atom+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Cloudflare Worker 代理（可选，用于绕过 Reddit 403/429 限制）
CF_WORKER_URL = os.environ.get("CF_WORKER_URL", "").rstrip("/")


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def init_db():
    """初始化 SQLite 数据库"""
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            score INTEGER,
            num_comments INTEGER,
            upvote_ratio REAL,
            url TEXT,
            selftext TEXT,
            created_utc REAL,
            permalink TEXT,
            extracted_summary TEXT,
            has_revenue_info INTEGER,
            revenue_pattern TEXT,
            tech_stack TEXT,
            target_audience TEXT,
            pain_point TEXT,
            sentiment TEXT,
            category TEXT,
            fetched_at TEXT,
            extracted_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def extract_text_from_html(html_content: str) -> str:
    """从 Reddit RSS 的 HTML 内容中提取纯文本"""
    if not html_content:
        return ""
    # 移除 <div class="md"> 等标签，保留文本
    text = re.sub(r"<[^>]+>", " ", html_content)
    # 解码 HTML 实体
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = re.sub(r"\s+", " ", text).strip()
    return text[:5000]


def extract_post_id_from_permalink(permalink: str) -> str:
    """从 Reddit permalink 提取帖子 ID"""
    # e.g., https://www.reddit.com/r/SaaS/comments/1u0z4vz/new_rule_banning/
    match = re.search(r"/comments/([a-z0-9]+)/", permalink)
    if match:
        return match.group(1)
    return permalink.replace("https://www.reddit.com/r/", "").replace("/", "_")


def try_get_post_score(post_id: str) -> tuple:
    """
    尝试获取帖子的分数和评论数
    使用 Reddit info.json 端点（通过 CF Worker 代理）
    """
    try:
        base = "https://www.reddit.com/api/info.json"
        if CF_WORKER_URL:
            url = f"{CF_WORKER_URL}/?url={base}?id=t3_{post_id}&raw_json=1"
        else:
            url = f"{base}?id=t3_{post_id}&raw_json=1"
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code == 200:
            data = r.json()
            children = data.get("data", {}).get("children", [])
            if children:
                post = children[0].get("data", {})
                return post.get("score", 0), post.get("num_comments", 0), post.get("upvote_ratio", 0)
    except Exception:
        pass
    return 0, 0, 0


def fetch_subreddit_json(subreddit: str, limit: int = 25, sort: str = "hot") -> List[Dict]:
    """
    通过 Reddit JSON API 抓取帖子（支持 CF Worker 代理）
    获取完整数据：score, num_comments, upvote_ratio, selftext
    """
    base = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    if CF_WORKER_URL:
        url = f"{CF_WORKER_URL}/?url={base}?limit={limit}&raw_json=1"
    else:
        url = f"{base}?limit={limit}&raw_json=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        if r.status_code != 200:
            print(f"  [WARN] r/{subreddit} JSON returned {r.status_code}")
            return []
        data = r.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append(
                {
                    "id": post.get("id", ""),
                    "subreddit": post.get("subreddit", subreddit),
                    "title": post.get("title", ""),
                    "author": post.get("author", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "upvote_ratio": post.get("upvote_ratio", 0),
                    "url": post.get("url", ""),
                    "selftext": post.get("selftext", ""),
                    "created_utc": post.get("created_utc", 0),
                    "permalink": f"https://www.reddit.com{post.get('permalink', '')}",
                }
            )
        return posts
    except Exception as e:
        print(f"  [ERROR] r/{subreddit} JSON: {e}")
        return []


def fetch_subreddit_rss(subreddit: str, limit: int = 25) -> List[Dict]:
    """从 Reddit RSS 抓取帖子，完全不需要 API 认证"""
    url = f"{RSS_BASE.format(subreddit=subreddit)}?limit={limit}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"  [WARN] r/{subreddit} RSS returned {r.status_code}")
            return []

        root = ET.fromstring(r.text)
        entries = root.findall("entry", RSS_NS)
        posts = []

        for entry in entries:
            title_el = entry.find("title", RSS_NS)
            link_el = entry.find("link", RSS_NS)
            author_el = entry.find("author", RSS_NS)
            updated_el = entry.find("updated", RSS_NS)
            content_el = entry.find("content", RSS_NS)

            title = title_el.text if title_el is not None else ""
            permalink = link_el.get("href") if link_el is not None else ""
            author = ""
            if author_el is not None:
                name_el = author_el.find("name", RSS_NS)
                author = name_el.text if name_el is not None else ""

            updated_dt = updated_el.text if updated_el is not None else ""
            # 解析为 UTC 时间戳
            created_utc = 0
            if updated_dt:
                try:
                    dt = datetime.fromisoformat(updated_dt.replace("Z", "+00:00"))
                    created_utc = dt.timestamp()
                except ValueError:
                    pass

            # 提取内容文本
            content_html = content_el.text if content_el is not None and content_el.text else ""
            selftext = extract_text_from_html(content_html)

            post_id = extract_post_id_from_permalink(permalink)

            # 尝试获取分数（可选，带延迟）
            score, num_comments, upvote_ratio = try_get_post_score(post_id)
            if score == 0 and num_comments == 0:
                # 回退：从 RSS 中偶尔能获取评分，但这里没有，暂时用 0
                pass

            posts.append(
                {
                    "id": post_id,
                    "subreddit": subreddit,
                    "title": title,
                    "author": author.replace("/u/", ""),
                    "score": score or 0,
                    "num_comments": num_comments or 0,
                    "upvote_ratio": upvote_ratio or 0,
                    "url": permalink,  # 对于文本帖子，URL 就是 permalink
                    "selftext": selftext,
                    "created_utc": created_utc,
                    "permalink": permalink,
                }
            )

        return posts

    except Exception as e:
        print(f"  [ERROR] r/{subreddit}: {e}")
        return []


def extract_structured_info(title: str, body: str) -> Dict[str, Any]:
    """用规则 + 关键词匹配做结构化提取"""
    text = f"{title} {body}".lower()
    full_text = f"{title} {body}"

    # 1. 检测收入/MRR 信息
    revenue_patterns = re.findall(
        r"\$[\d,.]+[kmb]?\s*(?:/month|mrr|monthly|revenue|arr|year|mo)",
        full_text,
        re.IGNORECASE,
    )
    has_revenue = len(revenue_patterns) > 0

    # 2. 检测技术栈关键词
    tech_keywords = [
        "react", "next.js", "vue", "python", "django", "flask", "node.js", "typescript", "go", "rust", "php", "laravel", "ruby", "rails",
        "aws", "gcp", "azure", "docker", "kubernetes", "postgres", "mongodb", "mysql", "supabase", "firebase",
        "stripe", "vercel", "netlify", "cloudflare", "tailwind", "openai", "gpt", "claude", "llama", "langchain",
        "redis", "nginx", "heroku", "railway", "digitalocean", "hetzner", "vultr", "twilio", "resend", "postmark",
        "mailgun", "plausible", "fathom", "mixpanel", "amplitude", "airtable", "make", "bubble", "webflow", "carrd",
    ]
    tech_stack = [kw for kw in tech_keywords if kw.lower() in text]

    # 3. 检测痛点关键词
    pain_keywords = [
        "pain point", "frustrated", "struggling", "annoying", "hate", "wish there was", "tired of",
        "problem", "challenge", "difficult", "hard to", "manual", "waste time", "inefficient", "bottleneck",
        "headache", "tedious", "burnout", "failed", "quit", "rejected", "no customers", "zero revenue",
    ]
    pain_point = [kw for kw in pain_keywords if kw in text]

    # 4. 目标受众检测
    audience_keywords = [
        "developer", "founder", "startup", "freelancer", "agency", "marketer", "designer", "content creator",
        "small business", "ecommerce", "saas", "indie hacker", "solopreneur", "consultant", "team", "remote",
        "dentist", "lawyer", "photographer", "roofer", "contractor", "b2b", "b2c",
    ]
    target_audience = [kw for kw in audience_keywords if kw in text]

    # 5. 情绪判断
    positive_words = [
        "launch", "revenue", "mrr", "growth", "success", "profitable", "built", "shipping", "launched",
        "milestone", "celebrate", "thank you", "excited", "proud", "achieved", "bootstrapped", "profitable",
    ]
    negative_words = [
        "failed", "shut down", "burnout", "struggling", "frustrated", "depressed", "anxiety", "quit", "layoff",
        "bankrupt", "losing", "no customers", "zero revenue", "rejected",
    ]
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # 6. 分类
    categories = {
        "idea_validation": ["idea", "validate", "feedback", "would you use", "should i build", "mvp", "concept"],
        "launch": ["launch", "shipped", "released", "live", "announcing", "introducing"],
        "revenue_share": ["mrr", "revenue", "arr", "profit", "income", "earnings", "sales", "paid", "pricing", "monetization"],
        "growth_marketing": ["growth", "marketing", "seo", "traffic", "acquisition", "conversion", "retention", "churn", "users"],
        "tech_stack": ["stack", "technology", "framework", "database", "hosting", "infrastructure", "architecture"],
        "hiring_team": ["hiring", "team", "co-founder", "partner", "employee", "contractor", "freelancer"],
        "lessons_learned": ["lessons", "learned", "mistake", "regret", "what i wish", "reflection", "post-mortem"],
    }
    matched_cats = []
    for cat, words in categories.items():
        if any(w in text for w in words):
            matched_cats.append(cat)
    category = matched_cats[0] if matched_cats else "general"

    # 7. 生成简单摘要
    summary = full_text[:300].strip()

    return {
        "extracted_summary": summary,
        "has_revenue_info": has_revenue,
        "revenue_pattern": ", ".join(revenue_patterns[:3]) if revenue_patterns else "",
        "tech_stack": ", ".join(tech_stack) if tech_stack else "",
        "target_audience": ", ".join(target_audience) if target_audience else "",
        "pain_point": ", ".join(pain_point) if pain_point else "",
        "sentiment": sentiment,
        "category": category,
    }


def store_posts(posts: List[Dict]):
    """将帖子存入 SQLite 数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    for post in posts:
        info = extract_structured_info(post["title"], post["selftext"])
        c.execute(
            """
            INSERT OR REPLACE INTO posts VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """,
            (
                post["id"],
                post["subreddit"],
                post["title"],
                post["author"],
                post["score"],
                post["num_comments"],
                post["upvote_ratio"],
                post["url"],
                post["selftext"],
                post["created_utc"],
                post["permalink"],
                info["extracted_summary"],
                1 if info["has_revenue_info"] else 0,
                info["revenue_pattern"],
                info["tech_stack"],
                info["target_audience"],
                info["pain_point"],
                info["sentiment"],
                info["category"],
                now,
                now,
            ),
        )
    conn.commit()
    conn.close()
    print(f"[STORE] Stored {len(posts)} posts to DB")


def export_json():
    """导出为 JSON 供前端使用"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM posts
        ORDER BY score DESC, num_comments DESC
        LIMIT 500
    """)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    for row in rows:
        row["created_date"] = (
            datetime.fromtimestamp(row["created_utc"], tz=timezone.utc).strftime("%Y-%m-%d")
            if row["created_utc"] > 0
            else "unknown"
        )

    output_path = os.path.join(DATA_DIR, "posts.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"[EXPORT] {len(rows)} posts -> {output_path}")
    return rows


def fetch_all(limit_per_sub: int = 25, use_proxy: bool = True):
    """抓取所有目标 subreddit 的数据"""
    init_db()
    total = 0
    for sub in TARGET_SUBREDDITS:
        print(f"[FETCH] r/{sub} ...")
        if use_proxy and CF_WORKER_URL:
            posts = fetch_subreddit_json(sub, limit=limit_per_sub, sort="hot")
        else:
            posts = fetch_subreddit_rss(sub, limit=limit_per_sub)
        if posts:
            store_posts(posts)
            total += len(posts)
        time.sleep(2.5)  # 礼貌等待，避免触发速率限制
    print(f"[DONE] Total fetched: {total} posts")
    return total


def demo_single_subreddit(subreddit: str = "SaaS", limit: int = 5, use_proxy: bool = True):
    """演示模式：抓取单个 subreddit 并展示结果"""
    print(f"\n=== Demo: Fetching r/{subreddit} (limit={limit}) ===")
    if use_proxy and CF_WORKER_URL:
        posts = fetch_subreddit_json(subreddit, limit=limit)
    else:
        posts = fetch_subreddit_rss(subreddit, limit=limit)
    for p in posts:
        print(f"\n--- {p['subreddit']} ---")
        print(f"Title: {p['title'][:80]}...")
        print(f"Author: {p['author']}")
        print(f"Score: {p['score']}↑ | Comments: {p['num_comments']}💬")
        print(f"Permalink: {p['permalink']}")
        print(f"Content: {p['selftext'][:200]}..." if p["selftext"] else "Content: (link post or empty)")
    print(f"\nFetched {len(posts)} posts from r/{subreddit}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        sub = sys.argv[2] if len(sys.argv) > 2 else "SaaS"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        demo_single_subreddit(sub, limit)
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        export_json()
    else:
        fetch_all(limit_per_sub=25)
        export_json()
