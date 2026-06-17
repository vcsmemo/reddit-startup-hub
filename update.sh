#!/bin/bash
# Reddit 创业情报站 — 自动更新脚本
# 用法：./update.sh

set -e

echo "=== Reddit 创业情报站 自动更新 ==="

cd "$(dirname "$0")"

# 1. 抓取数据（需要配置 Reddit API 后启用）
# echo "[1/3] 抓取 Reddit 数据..."
# python3 src/fetcher.py

echo "[1/2] 生成模拟数据（开发阶段使用，生产环境替换为真实抓取）..."
python3 src/seed_mock.py

# 2. 构建静态站点
echo "[2/2] 构建静态站点..."
python3 src/build_site.py

echo "✅ 更新完成！静态站点在 static/index.html"
echo "📦 部署: npx vercel --prod static/"
