"""
Reddit Startup Hub — Reddit API Fetcher (PRAW-ready)
Fetches posts from Reddit startup communities using PRAW (Reddit API wrapper).
Requires: pip install praw
Environment: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD

Fallback: Uses seed_mock.py data if Reddit API is not configured.
"""
import os
import sqlite3
import json
import time
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "posts.db")

# Target subreddits for startup/SaaS/AI content
TARGET_SUBREDDITS = [
    "SaaS", "startups", "indiehackers", "Entrepreneur",
    "SideProject", "bootstrapped", "Startup_Ideas", "ExperiencedDevs",
    "SaaS_Chat", "buildinpublic", "microsaas",
]

# Keywords for startup relevance detection
STARTUP_KEYWORDS = [
    "startup", "saas", "mrr", "arr", "revenue", "profit", "launch", "shipped",
    "bootstrapped", "bootstrap", "funding", "vc", "angel", "investor", "pitch",
    "product", "mvp", "prototype", "validation", "feedback", "users", "customers",
    "growth", "marketing", "seo", "traffic", "acquisition", "retention", "churn",
    "pricing", "monetization", "subscription", "freemium", "trial", "stripe",
    "tech stack", "stack", "framework", "database", "hosting", "architecture",
    "open source", "github", "api", "webhook", "integration",
    "ai", "llm", "gpt", "claude", "openai", "machine learning", "automation",
    "side project", "side hustle", "passive income", "indie hacker", "solopreneur",
    "founder", "co-founder", "team", "hiring", "remote", "freelancer", "consultant",
    "agency", "developer", "engineer", "designer", "product manager",
    "lessons learned", "mistake", "regret", "what i wish", "post-mortem", "reflection",
    "burnout", "struggle", "failed", "quit", "shut down", "closed",
]

# Revenue patterns
REVENUE_PATTERNS = re.compile(
    r"\$[\d,.]+[kmbKMB]?\s*(?:/month|mrr|monthly|revenue|arr|year|mo|annual|/mo|per month|/year|/yr)?",
    re.IGNORECASE,
)


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def init_db():
    """Initialize SQLite database with full schema."""
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
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
    """)
    conn.commit()
    conn.close()


def extract_structured_info(title: str, body: str, subreddit: str = "") -> Dict[str, Any]:
    """AI-style structured extraction from Reddit post text."""
    text = f"{title} {body}".lower()
    full_text = f"{title} {body}"

    # 1. Revenue detection
    revenue_matches = REVENUE_PATTERNS.findall(full_text)
    has_revenue = len(revenue_matches) > 0

    # 2. Tech stack keywords
    tech_keywords = [
        "react", "next.js", "vue", "svelte", "angular", "solidjs",
        "python", "django", "flask", "fastapi", "nodejs", "node.js", "express", "typescript", "javascript", "js",
        "go", "golang", "rust", "c++", "c#", "java", "kotlin", "swift", "ruby", "rails", "php", "laravel",
        "aws", "gcp", "azure", "cloudflare", "vercel", "netlify", "heroku", "railway", "digitalocean", "hetzner", "vultr", "linode",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "pulumi", "github actions", "ci/cd",
        "postgres", "postgresql", "mysql", "mariadb", "mongodb", "redis", "sqlite", "dynamodb", "cockroachdb", "planetscale", "supabase", "firebase", "faunadb", "cassandra", "clickhouse",
        "stripe", "paddle", "lemonsqueezy", "chargebee", "paypal", "square", "braintree", "paystack", "razorpay",
        "tailwind", "bootstrap", "material-ui", "chakra-ui", "shadcn", "radix",
        "openai", "gpt", "gpt-4", "gpt-3", "claude", "anthropic", "llama", "llama2", "llama3", "mistral", "mixtral", "gemini", "groq",
        "langchain", "llamaindex", "crewai", "haystack", "embedchain", "auto-gpt", "babyagi",
        "vector", "embedding", "transformer", "huggingface", "transformers", "ollama",
        "nextauth", "auth0", "clerk", "supabase auth", "firebase auth", "passport",
        "plausible", "fathom", "mixpanel", "amplitude", "segment", "posthog", "umami", "google analytics", "ga4",
        "postmark", "resend", "mailgun", "sendgrid", "twilio", "sendinblue", "brevo", "mailchimp",
        "cloudflare workers", "serverless", "lambda", "edge function", "cloud function",
        "websocket", "graphql", "rest", "grpc", "trpc", "openapi", "swagger", "fastapi",
        "bubble", "webflow", "carrd", "notion", "airtable", "make", "zapier", "n8n",
        "electron", "tauri", "flutter", "react native", "swiftui", "jetpack compose",
        "nginx", "caddy", "apache", "traefik", "haproxy",
        "prometheus", "grafana", "datadog", "new relic", "sentry", "logrocket", "bugsnag",
        "vite", "webpack", "rollup", "parcel", "esbuild", "turbopack", "bun",
        "redis", "memcached", "elasticsearch", "meilisearch", "algolia", "typesense",
        "ffmpeg", "opencv", "pytorch", "tensorflow", "jax", "scikit-learn", "pandas", "numpy",
    ]
    tech_stack = [kw for kw in tech_keywords if kw.lower() in text]

    # 3. Pain points
    pain_keywords = [
        "pain point", "painpoint", "frustrated", "frustrating", "struggling", "struggle",
        "annoying", "annoyed", "hate", "hated", "wish there was", "tired of", "sick of", "fed up with",
        "problem", "problems", "challenge", "challenging", "difficult", "difficulty", "hard to", "tricky", "painful", "tedious",
        "waste time", "wasting time", "wasted", "inefficient", "bottleneck", "headache", "nightmare", "horror story",
        "can't find", "hard to find", "no good way", "no easy way", "too complicated", "too complex", "overcomplicated", "overengineered",
        "slow", "unreliable", "broken", "buggy", "outdated", "legacy", "technical debt", "spaghetti code",
        "burnout", "burn out", "burnt out", "depressed", "depression", "anxiety", "anxious", "stress", "stressed", "overwhelmed",
        "failed", "failure", "shut down", "shutdown", "closed", "closing", "winding down", "bankrupt", "bankruptcy",
        "no customers", "zero revenue", "zero mrr", "no sales", "no traction", "no users", "no growth",
        "wasted", "waste of", "regret", "regretting", "mistake", "mistaken", "wrong", "bad decision",
        "rejected", "rejection", "denied", "declined", "turned down", "not enough", "insufficient",
    ]
    pain_point = [kw for kw in pain_keywords if kw in text]

    # 4. Target audience
    audience_keywords = [
        "developer", "dev", "engineer", "programmer", "coder", "software engineer", "backend", "frontend", "fullstack", "full-stack",
        "founder", "co-founder", "cofounder", "entrepreneur", "startup founder", "solopreneur", "indie hacker", "indie maker",
        "freelancer", "consultant", "contractor", "agency", "studio", "shop",
        "marketer", "growth hacker", "growth marketer", "sales", "pm", "product manager", "product owner",
        "designer", "ux designer", "ui designer", "graphic designer", "web designer",
        "content creator", "youtuber", "blogger", "writer", "podcaster", "influencer",
        "small business", "smb", "sme", "enterprise", "large company", "fortune 500",
        "ecommerce", "e-commerce", "shopify", "woocommerce", "dropshipper", "dropshipping",
        "saas", "b2b", "b2c", "team", "remote team", "distributed team", "hybrid team",
        "data scientist", "ml engineer", "ai researcher", "researcher", "analyst",
        "student", "learner", "beginner", "newbie", "junior", "senior", "lead", "staff", "principal",
        "non-technical", "no-code", "nocode", "citizen developer", "business user", "manager", "executive", "c-level", "cto", "ceo",
        "dentist", "lawyer", "accountant", "realtor", "photographer", "videographer", "musician", "artist",
        "teacher", "educator", "coach", "trainer", "therapist", "doctor", "nurse", "chef", "farmer",
    ]
    target_audience = [kw for kw in audience_keywords if kw in text]

    # 5. Sentiment analysis
    positive_words = [
        "launch", "launched", "shipped", "release", "released", "announcing", "introducing", "proud to", "excited to",
        "revenue", "mrr", "arr", "profit", "profitable", "growth", "growing", "scaling", "scale", "scaling up",
        "success", "successful", "milestone", "achievement", "breakthrough", "momentum", "traction",
        "built", "created", "made", "built this", "i made", "we built", "i created", "we created", "shipped this",
        "thank you", "grateful", "appreciate", "excited", "thrilled", "proud", "happy", "love", "loved", "amazing", "awesome", "incredible",
        "bootstrapped", "self-funded", "ramen profitable", "cash flow positive", "break even", "break-even",
        "free", "open source", "open-source", "community", "contributors", "stars", "forks",
        "hired", "hiring", "team", "growing team", "new member", "welcome", "joined",
        "acquired", "acquisition", "exit", "ipo", "sold", "deal", "partnership", "collaboration",
        "recommend", "highly recommend", "must try", "game changer", "life changing", "transformed",
    ]
    negative_words = [
        "failed", "failure", "shut down", "shutdown", "closed", "closing", "winding down", "wound down",
        "burnout", "burn out", "burnt out", "depressed", "depression", "anxiety", "anxious", "stress", "stressed", "overwhelmed",
        "quit", "quitting", "resigned", "fired", "layoff", "laid off", "laid off", "redundant", "let go",
        "bankrupt", "bankruptcy", "insolvent", "dead", "killed", "died", "crashed", "collapse", "collapsing",
        "no customers", "zero revenue", "zero mrr", "no sales", "no traction", "no users", "no growth", "stagnant", "flatlined",
        "wasted", "waste of", "regret", "regretting", "mistake", "mistaken", "wrong", "bad decision", "terrible idea", "worst",
        "rejected", "rejection", "denied", "declined", "turned down", "no", "not accepted", "not approved",
        "hate", "hated", "terrible", "awful", "horrible", "disgusting", "worst", "crap", "shit", "fuck", "damn",
        "scam", "fraud", "fake", "lie", "lying", "deceptive", "misleading", "dishonest",
    ]
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # 6. Category classification
    categories = {
        "showcase": ["show hn", "show-hn", "showhn", "launched", "shipped", "released", "live", "announcing", "introducing", "proud to", "excited to launch", "we launched", "i launched", "just launched"],
        "ask_feedback": ["ask hn", "ask-hn", "askhn", "how do i", "how can i", "should i", "advice", "feedback", "question", "thoughts", "opinions", "what do you think", "would you use", "would you pay"],
        "revenue": ["mrr", "revenue", "arr", "profit", "income", "earnings", "sales", "paid", "pricing", "monetization", "subscription", "charged", "billing", "pricing model", "price increase", "raised prices"],
        "growth_marketing": ["growth", "marketing", "seo", "traffic", "acquisition", "conversion", "retention", "churn", "users", "user acquisition", "customer acquisition", "viral", "word of mouth", "organic", "content marketing", "social media", "twitter", "linkedin", "product hunt"],
        "tech_stack": ["stack", "technology", "framework", "database", "hosting", "infrastructure", "architecture", "tech stack", "built with", "using", "migrated", "switched from", "moved to", "why we chose", "why i chose"],
        "hiring_team": ["hiring", "we're hiring", "join us", "careers", "job opening", "looking for", "co-founder", "cofounder", "partner", "team member", "employee", "contractor", "freelancer", "advisor"],
        "funding": ["funding", "raised", "seed", "series a", "series b", "angel", "investor", "investment", "vc", "venture capital", "y combinator", "yc", "accelerator", "bootstrapped vs", "raise or bootstrap", "valuation"],
        "lessons": ["lessons", "learned", "lesson", "mistake", "mistakes", "regret", "what i wish", "reflection", "post-mortem", "postmortem", "post mortem", "retrospective", "what went wrong", "what went right", "if i could do it again", "looking back"],
        "open_source": ["open source", "open-source", "github", "source code", "repository", "repo", "self-hosted", "self hosted", "contribute", "contributor", "license", "mit", "gpl", "apache"],
        "ai_ml": ["ai", "artificial intelligence", "machine learning", "deep learning", "llm", "gpt", "claude", "openai", "langchain", "vector", "embedding", "rag", "fine-tuning", "fine tuning", "fine-tune", "prompt engineering", "agents", "agentic"],
        "no_code": ["no-code", "no code", "low-code", "low code", "nocode", "lowcode", "bubble", "webflow", "carrd", "zapier", "make", "n8n", "glide", "softr", "flutterflow", "adalo"],
        "burnout_mental": ["burnout", "burn out", "burnt out", "mental health", "depression", "anxiety", "stress", "therapy", "work life balance", "work-life balance", "overworked", "exhausted", "imposter syndrome", "impostor syndrome"],
    }
    matched_cats = []
    for cat, words in categories.items():
        if any(w in text for w in words):
            matched_cats.append(cat)
    category = matched_cats[0] if matched_cats else "general"

    # 7. Summary generation
    summary = full_text[:280].strip()

    return {
        "extracted_summary": summary,
        "has_revenue_info": has_revenue,
        "revenue_pattern": ", ".join(revenue_matches[:3]) if revenue_matches else "",
        "tech_stack": ", ".join(tech_stack) if tech_stack else "",
        "target_audience": ", ".join(target_audience) if target_audience else "",
        "pain_point": ", ".join(pain_point) if pain_point else "",
        "sentiment": sentiment,
        "category": category,
    }


def store_posts(posts: List[Dict]):
    """Store posts into SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    for post in posts:
        info = extract_structured_info(post.get("title", ""), post.get("selftext", ""), post.get("subreddit", ""))
        c.execute("""
            INSERT OR REPLACE INTO posts VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            post["id"],
            post.get("source", "reddit"),
            post.get("subreddit", ""),
            post["title"],
            post.get("author", ""),
            post.get("score", 0),
            post.get("num_comments", 0),
            post.get("upvote_ratio", 0),
            post.get("url", ""),
            post.get("selftext", ""),
            post.get("created_utc", 0),
            post.get("permalink", ""),
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
        ))
    conn.commit()
    conn.close()
    print(f"[STORE] Stored {len(posts)} posts to DB")


def export_json() -> List[Dict]:
    """Export posts to JSON for frontend."""
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
            if row["created_utc"] and row["created_utc"] > 0
            else "unknown"
        )

    output_path = os.path.join(DATA_DIR, "posts.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"[EXPORT] {len(rows)} posts -> {output_path}")
    return rows


# ---------------------------------------------------------------------------
# Reddit PRAW Fetcher (requires API credentials)
# ---------------------------------------------------------------------------

def fetch_reddit_with_praw(limit_per_sub: int = 25, sort: str = "hot") -> int:
    """Fetch posts from Reddit using PRAW (official API). Requires env vars."""
    try:
        import praw
    except ImportError:
        print("[ERROR] praw not installed. Run: pip install praw")
        return 0

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    username = os.environ.get("REDDIT_USERNAME")
    password = os.environ.get("REDDIT_PASSWORD")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "RedditStartupHub/1.0")

    if not all([client_id, client_secret, username, password]):
        print("[ERROR] Reddit API credentials not configured. Set env vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
        return 0

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent,
    )

    init_db()
    total = 0

    for sub_name in TARGET_SUBREDDITS:
        print(f"[FETCH] r/{sub_name} ...")
        try:
            sub = reddit.subreddit(sub_name)
            method = getattr(sub, sort, sub.hot)
            posts = []
            for post in method(limit=limit_per_sub):
                posts.append({
                    "id": post.id,
                    "source": "reddit",
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
            if posts:
                store_posts(posts)
                total += len(posts)
            time.sleep(1)
        except Exception as e:
            print(f"  [ERROR] r/{sub_name}: {e}")

    print(f"[DONE] Total fetched: {total} posts")
    return total


def fetch_all():
    """Main entry point: try PRAW, fallback to seed data."""
    result = fetch_reddit_with_praw(limit_per_sub=25, sort="hot")
    if result == 0:
        print("[INFO] Reddit API not configured. Using seed data.")
        # Import and run seed_mock
        import sys
        sys.path.insert(0, os.path.join(BASE_DIR, "src"))
        from seed_mock import seed_mock_data
        seed_mock_data()
    export_json()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_json()
    else:
        fetch_all()
