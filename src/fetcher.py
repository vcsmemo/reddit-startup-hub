"""
HackerNews + TechMeme 创业情报站 — 核心抓取 + 提取模块
完全免费，不需要任何 API 认证
"""
import requests
import json
import time
import sqlite3
import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from html import unescape

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DATA_DIR, "posts.db")

# HackerNews 官方 API 端点
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ITEM = f"{HN_API_BASE}/item/{{id}}.json"
HN_TOP_STORIES = f"{HN_API_BASE}/topstories.json"
HN_NEW_STORIES = f"{HN_API_BASE}/newstories.json"
HN_BEST_STORIES = f"{HN_API_BASE}/beststories.json"

# TechMeme RSS
TECHMEME_RSS = "https://www.techmeme.com/feed.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json, application/xml",
}


# 创业/tech 关键词过滤（用于筛选帖子）
STARTUP_KEYWORDS = [
    "startup", "saas", "api", "ai", "llm", "open source", "bootstrapped", "mrr", "revenue",
    "profit", "founder", "launch", "product", "tool", "platform", "framework", "library",
    "deployment", "hosting", "pricing", "acquisition", "funding", "vc", "angel", "investor",
    "side project", "side project", "indie", "solo founder", "remote", "devops", "kubernetes",
    "docker", "postgres", "redis", "react", "next.js", "typescript", "python", "golang", "rust",
    "stripe", "vercel", "supabase", "firebase", "openai", "gpt", "claude", "langchain",
    "rag", "vector", "embeddings", "machine learning", "deep learning", "automation",
    "chatbot", "agent", "workflow", "email", "marketing", "analytics", "seo", "content",
    "no-code", "low-code", "nocode", "lowcode", "bubble", "webflow", "zapier", "make",
    "b2b", "b2c", "enterprise", "small business", "freelancer", "consultant", "agency",
    "chrome extension", "browser extension", "mobile app", "web app", "desktop app",
    "open source", "github", "source code", "repository", "self-hosted", "self hosted",
]


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
            source TEXT NOT NULL,
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


def clean_html(text: str) -> str:
    """清理 HTML 实体和标签"""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:5000]


def is_startup_related(title: str, text: str = "") -> bool:
    """判断帖子是否与创业/tech 相关"""
    combined = (title + " " + text).lower()
    return any(kw in combined for kw in STARTUP_KEYWORDS)


def fetch_hn_item(item_id: int) -> Optional[Dict]:
    """获取单个 HackerNews 帖子详情"""
    try:
        url = HN_ITEM.format(id=item_id)
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  [WARN] Failed to fetch item {item_id}: {e}")
    return None


def fetch_hn_stories(list_type: str = "top", limit: int = 100) -> List[Dict]:
    """从 HackerNews 获取帖子列表，不做关键词过滤，让提取器自动分类"""
    if list_type == "top":
        list_url = HN_TOP_STORIES
    elif list_type == "new":
        list_url = HN_NEW_STORIES
    elif list_type == "best":
        list_url = HN_BEST_STORIES
    else:
        list_url = HN_TOP_STORIES

    try:
        r = requests.get(list_url, timeout=15)
        r.raise_for_status()
        story_ids = r.json()[:limit]
    except Exception as e:
        print(f"[ERROR] Failed to fetch HN story list: {e}")
        return []

def fetch_hn_stories(list_type: str = "top", limit: int = 50, max_workers: int = 10) -> List[Dict]:
    """从 HackerNews 获取帖子列表，并行请求加速"""
    if list_type == "top":
        list_url = HN_TOP_STORIES
    elif list_type == "new":
        list_url = HN_NEW_STORIES
    elif list_type == "best":
        list_url = HN_BEST_STORIES
    else:
        list_url = HN_TOP_STORIES

    try:
        r = requests.get(list_url, timeout=15)
        r.raise_for_status()
        story_ids = r.json()[:limit]
    except Exception as e:
        print(f"[ERROR] Failed to fetch HN story list: {e}")
        return []

    posts = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_hn_item, sid): sid for sid in story_ids}
        for future in as_completed(future_to_id):
            item = future.result()
            if item and item.get("type") == "story":
                title = item.get("title", "")
                text = item.get("text", "")
                posts.append({
                    "id": str(item.get("id")),
                    "source": "hackernews",
                    "title": title,
                    "author": item.get("by", ""),
                    "score": item.get("score", 0),
                    "num_comments": item.get("descendants", 0),
                    "upvote_ratio": 0,
                    "url": item.get("url", ""),
                    "selftext": clean_html(text) if text else "",
                    "created_utc": item.get("time", 0),
                    "permalink": f"https://news.ycombinator.com/item?id={item.get('id')}",
                })
    return posts


def fetch_techmeme_rss(limit: int = 20) -> List[Dict]:
    """从 TechMeme RSS 获取科技新闻"""
    try:
        r = requests.get(TECHMEME_RSS, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  [WARN] TechMeme RSS returned {r.status_code}")
            return []

        root = ET.fromstring(r.text)
        items = root.findall(".//item")
        posts = []

        for item in items[:limit]:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_date_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            url = link_el.text if link_el is not None else ""
            desc = desc_el.text if desc_el is not None and desc_el.text else ""
            pub_date = pub_date_el.text if pub_date_el is not None else ""

            # 只保留与 tech/创业 相关的新闻
            if is_startup_related(title, desc):
                # 解析日期
                created_utc = 0
                if pub_date:
                    try:
                        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                        created_utc = dt.timestamp()
                    except ValueError:
                        pass

                # 生成唯一 ID
                post_id = re.sub(r'[^a-zA-Z0-9]', '_', title[:30]) + str(int(created_utc))[:6]

                posts.append({
                    "id": post_id,
                    "source": "techmeme",
                    "title": title,
                    "author": "techmeme",
                    "score": 0,
                    "num_comments": 0,
                    "upvote_ratio": 0,
                    "url": url,
                    "selftext": clean_html(desc)[:1000],
                    "created_utc": created_utc,
                    "permalink": url,
                })

        return posts
    except Exception as e:
        print(f"  [ERROR] Failed to fetch TechMeme: {e}")
        return []


def extract_structured_info(title: str, body: str, source: str = "") -> Dict[str, Any]:
    """用规则 + 关键词匹配做结构化提取"""
    text = f"{title} {body}".lower()
    full_text = f"{title} {body}"

    # 1. 检测收入/MRR 信息
    revenue_patterns = re.findall(
        r"\$[\d,.]+[kmb]?\s*(?:/month|mrr|monthly|revenue|arr|year|mo|annual|month)",
        full_text,
        re.IGNORECASE,
    )
    has_revenue = len(revenue_patterns) > 0

    # 2. 检测技术栈关键词
    tech_keywords = [
        "react", "next.js", "vue", "angular", "svelte", "solidjs",
        "python", "django", "flask", "fastapi", "nodejs", "node.js", "express", "typescript",
        "go", "golang", "rust", "c++", "c#", "java", "kotlin", "swift", "ruby", "rails", "php", "laravel",
        "aws", "gcp", "azure", "cloudflare", "vercel", "netlify", "heroku", "railway", "digitalocean", "hetzner", "vultr", "linode",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "pulumi",
        "postgres", "postgresql", "mysql", "mariadb", "mongodb", "redis", "sqlite", "dynamodb", "cockroachdb", "planetscale", "supabase", "firebase", "faunadb", "cassandra",
        "stripe", "paddle", "lemonsqueezy", "chargebee", "paypal", "square", "braintree",
        "tailwind", "bootstrap", "material-ui", "chakra-ui", "shadcn", "radix",
        "openai", "gpt", "gpt-4", "gpt-3", "claude", "anthropic", "llama", "llama2", "llama3", "mistral", "mixtral", "gemini", "groq",
        "langchain", "llamaindex", "crewai", "haystack", "embedchain", "auto-gpt", "babyagi",
        "vector", "embedding", "embedding", "transformer", "huggingface", "transformers",
        "nextauth", "auth0", "clerk", "supabase auth", "firebase auth",
        "plausible", "fathom", "mixpanel", "amplitude", "segment", "posthog", "umami",
        "postmark", "resend", "mailgun", "sendgrid", "twilio", "sendgrid",
        "cloudflare workers", "serverless", "lambda", "edge function",
        "websocket", "graphql", "rest", "grpc", "tRPC", "tRPC", "openapi", "swagger",
    ]
    tech_stack = [kw for kw in tech_keywords if kw.lower() in text]

    # 3. 检测痛点关键词
    pain_keywords = [
        "pain point", "painpoint", "frustrated", "struggling", "annoying", "hate", "wish there was", "tired of",
        "problem", "challenge", "difficult", "hard to", "tricky", "painful", "tedious", "manual",
        "waste time", "wasting time", "inefficient", "bottleneck", "headache", "nightmare",
        "can't find", "hard to find", "no good way", "no easy way", "too complicated", "too complex",
        "slow", "unreliable", "broken", "buggy", "outdated", "legacy", "technical debt",
    ]
    pain_point = [kw for kw in pain_keywords if kw in text]

    # 4. 目标受众检测
    audience_keywords = [
        "developer", "dev", "engineer", "programmer", "coder",
        "founder", "co-founder", "cofounder", "entrepreneur", "startup founder",
        "freelancer", "consultant", "contractor",
        "agency", "studio", "shop",
        "marketer", "growth", "sales", "pm", "product manager",
        "designer", "ux designer", "ui designer",
        "content creator", "youtuber", "blogger", "writer",
        "small business", "smb", "sme",
        "ecommerce", "e-commerce", "shopify", "woocommerce",
        "saas", "b2b", "b2c", "enterprise", "team", "remote team", "distributed team",
        "indie hacker", "indie maker", "solopreneur", "solo founder",
        "data scientist", "ml engineer", "ai researcher",
        "student", "learner", "beginner",
    ]
    target_audience = [kw for kw in audience_keywords if kw in text]

    # 5. 情绪判断
    positive_words = [
        "launch", "launched", "shipped", "release", "released", "announcing", "introducing", "proud to",
        "revenue", "mrr", "arr", "profit", "profitable", "growth", "growing", "scaling", "scale",
        "success", "successful", "milestone", "achievement", "breakthrough", "momentum",
        "built", "created", "made", "built this", "i made", "we built",
        "thank you", "grateful", "appreciate", "excited", "thrilled", "proud", "happy", "love",
        "bootstrapped", "self-funded", " ramen profitable", " ramen profitable",
        "free", "open source", "open-source", "community", "contributors",
    ]
    negative_words = [
        "failed", "failure", "shut down", "shutdown", "closed", "closing", "winding down",
        "burnout", "burn out", "burnt out", "struggling", "struggle", "frustrated", "frustrating",
        "depressed", "depression", "anxiety", "anxious", "stress", "stressed", "overwhelmed",
        "quit", "quitting", "resigned", "fired", "layoff", "laid off", "laid off",
        "bankrupt", "bankruptcy", "insolvent", "dead", "killed", "died",
        "no customers", "zero revenue", "zero mrr", "no sales", "no traction", "no users",
        "wasted", "waste of", "regret", "regretting", "mistake", "mistaken", "wrong",
        "burned", "burned out", "exhausted", "tired", "hate this", "hate my job",
        "rejected", "rejection", "denied", "declined", "turned down", "no",
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
        "show_hn": ["show hn", "show-hn", "showhn", "launched", "i built", "i made", "we built", "we launched"],
        "ask_hn": ["ask hn", "ask-hn", "askhn", "how do i", "how can i", "should i", "advice", "feedback", "question"],
        "revenue": ["mrr", "revenue", "arr", "profit", "income", "earnings", "sales", "paid", "pricing", "monetization", "subscription", "pricing model"],
        "growth": ["growth", "marketing", "seo", "traffic", "acquisition", "conversion", "retention", "churn", "users", "user acquisition", "customer acquisition"],
        "tech_stack": ["stack", "technology", "framework", "database", "hosting", "infrastructure", "architecture", "tech stack", "built with", "using"],
        "hiring": ["hiring", "we're hiring", "join us", "careers", "job opening", "looking for", "co-founder", "cofounder", "partner"],
        "funding": ["funding", "raised", "seed", "series", "investor", "investment", "vc", "venture capital", "angel", "y combinator", "yc", "accelerator"],
        "lessons": ["lessons", "learned", "mistake", "regret", "what i wish", "reflection", "post-mortem", "postmortem", "post mortem", "retrospective"],
        "open_source": ["open source", "open-source", "github", "source code", "repository", "repo", "self-hosted", "self hosted"],
        "ai_ml": ["ai", "machine learning", "deep learning", "llm", "gpt", "claude", "openai", "langchain", "vector", "embedding", "rag", "fine-tuning", "fine tuning"],
    }
    matched_cats = []
    for cat, words in categories.items():
        if any(w in text for w in words):
            matched_cats.append(cat)
    category = matched_cats[0] if matched_cats else "general"

    # 7. 生成摘要
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
        info = extract_structured_info(post["title"], post["selftext"], post.get("source", ""))
        c.execute(
            """
            INSERT OR REPLACE INTO posts VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """,
            (
                post["id"],
                post.get("source", "hackernews"),
                post["title"],
                post["author"],
                post["score"],
                post["num_comments"],
                post.get("upvote_ratio", 0),
                post.get("url", ""),
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
    c.execute(
        """
        SELECT * FROM posts
        ORDER BY score DESC, num_comments DESC
        LIMIT 500
    """
    )
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


def fetch_all(hn_limit: int = 20, techmeme_limit: int = 5):
    """抓取所有数据，增加超时处理"""
    init_db()
    total = 0

    # 1. 抓取 HackerNews
    print(f"[FETCH] HackerNews top stories (limit={hn_limit})...")
    try:
        hn_posts = fetch_hn_stories(list_type="top", limit=hn_limit)
        if hn_posts:
            store_posts(hn_posts)
            total += len(hn_posts)
        print(f"[HN] Fetched {len(hn_posts)} posts")
    except Exception as e:
        print(f"[ERROR] HN fetch failed: {e}")

    # 2. 抓取 TechMeme（可选，设置 >0 时启用）
    if techmeme_limit > 0:
        print(f"[FETCH] TechMeme RSS (limit={techmeme_limit})...")
        try:
            tm_posts = fetch_techmeme_rss(limit=techmeme_limit)
            if tm_posts:
                store_posts(tm_posts)
                total += len(tm_posts)
            print(f"[TechMeme] Fetched {len(tm_posts)} posts")
        except Exception as e:
            print(f"[ERROR] TechMeme fetch failed: {e}")

    print(f"[DONE] Total fetched: {total} posts")
    return total


def demo_hn(limit: int = 10):
    """演示模式：抓取 HackerNews 并展示"""
    print(f"\n=== Demo: Fetching HackerNews top stories (limit={limit}) ===")
    posts = fetch_hn_stories(list_type="top", limit=limit)
    for p in posts:
        print(f"\n--- [{p['source']}] {p['title'][:80]}...")
        print(f"Author: {p['author']} | Score: {p['score']}↑ | Comments: {p['num_comments']}💬")
        print(f"Permalink: {p['permalink']}")
        if p["selftext"]:
            print(f"Text: {p['selftext'][:200]}...")
        elif p["url"]:
            print(f"URL: {p['url'][:80]}...")
    print(f"\nFetched {len(posts)} startup-related posts from HackerNews")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        demo_hn(limit)
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        export_json()
    else:
        fetch_all(hn_limit=50, techmeme_limit=10)
        export_json()
