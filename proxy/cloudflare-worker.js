// Cloudflare Workers 代理 — 绕过 Reddit 403/429 限制
// 部署: 复制到 Cloudflare Workers 编辑器，保存并部署
// 免费额度: 100K 请求/天

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // 只代理 Reddit 相关请求
    const targetUrl = url.searchParams.get('url');
    if (!targetUrl) {
      return new Response('Usage: ?url=https://www.reddit.com/r/SaaS/hot.json', { status: 400 });
    }
    
    if (!targetUrl.includes('reddit.com')) {
      return new Response('Only reddit.com URLs allowed', { status: 403 });
    }

    try {
      const response = await fetch(targetUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
          'Accept': 'application/json, text/html, application/xml',
          'Accept-Language': 'en-US,en;q=0.9',
          'Referer': 'https://www.google.com/',
        },
        cf: {
          cacheEverything: true,
          cacheTtl: 600, // 缓存 10 分钟
        }
      });

      // 复制响应并添加 CORS 头
      const newHeaders = new Headers(response.headers);
      newHeaders.set('Access-Control-Allow-Origin', '*');
      newHeaders.set('Access-Control-Allow-Methods', 'GET, OPTIONS');
      newHeaders.set('Cache-Control', 'public, max-age=600');

      return new Response(response.body, {
        status: response.status,
        headers: newHeaders,
      });
    } catch (e) {
      return new Response(`Error: ${e.message}`, { status: 500 });
    }
  }
};

/* 
部署步骤:
1. 访问 https://workers.cloudflare.com/
2. 创建 Worker
3. 复制上述代码，粘贴到编辑器
4. 保存并部署
5. 获得 URL: https://your-worker.your-subdomain.workers.dev
6. 使用: https://your-worker.your-subdomain.workers.dev/?url=https://www.reddit.com/r/SaaS/hot.json

Python 调用:
import requests
PROXY = "https://your-worker.your-subdomain.workers.dev"
url = f"{PROXY}/?url=https://www.reddit.com/r/SaaS/hot.json"
r = requests.get(url)
data = r.json()
*/
