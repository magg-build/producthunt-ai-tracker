#!/bin/bash
# Product Hunt AI Tracker 部署脚本

set -e

echo "🚀 Product Hunt AI Tracker 部署脚本"
echo "===================================="

# 检查必要的环境变量
if [ -z "$PRODUCTHUNT_DEVELOPER_TOKEN" ]; then
    echo "❌ 错误: 未设置 PRODUCTHUNT_DEVELOPER_TOKEN 环境变量"
    echo "请访问 https://www.producthunt.com/v2/oauth/applications 获取"
    exit 1
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ 错误: 未设置 GITHUB_USERNAME 环境变量"
    exit 1
fi

REPO_NAME="${REPO_NAME:-producthunt-ai-tracker}"

echo ""
echo "📦 配置信息:"
echo "  GitHub 用户名: $GITHUB_USERNAME"
echo "  仓库名称: $REPO_NAME"
echo ""

# 创建临时目录
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# 克隆当前仓库
echo "📥 准备仓库文件..."
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"

# 复制项目文件（假设在 workspace 目录）
WORKSPACE_DIR="${WORKSPACE_DIR:-/root/.openclaw/workspace/producthunt-ai-tracker}"
cp -r "$WORKSPACE_DIR"/* .

# 初始化 git
git init
git add .
git commit -m "Initial commit: Product Hunt AI Tracker"

# 创建 GitHub 仓库并推送
echo ""
echo "📤 创建 GitHub 仓库..."

# 使用 GitHub CLI 或 API 创建仓库
if command -v gh &> /dev/null; then
    # 使用 GitHub CLI
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
else
    # 使用 GitHub API
    curl -X POST \
        -H "Authorization: token $PAT" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"$REPO_NAME\",\"private\":false}"
    
    # 添加远程并推送
    git remote add origin "https://$GITHUB_USERNAME:$PAT@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    git branch -M main
    git push -u origin main
fi

echo ""
echo "✅ 仓库创建成功!"
echo "  URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# 设置 Secrets
echo "🔐 配置 GitHub Secrets..."

# Product Hunt Token
gh secret set PRODUCTHUNT_DEVELOPER_TOKEN -b"$PRODUCTHUNT_DEVELOPER_TOKEN" || echo "请手动在 GitHub 设置 PRODUCTHUNT_DEVELOPER_TOKEN"

# GitHub PAT
if [ -n "$PAT" ]; then
    gh secret set PAT -b"$PAT" || echo "请手动在 GitHub 设置 PAT"
fi

# 飞书 Webhook（可选）
if [ -n "$FEISHU_WEBHOOK_URL" ]; then
    gh secret set FEISHU_WEBHOOK_URL -b"$FEISHU_WEBHOOK_URL" || echo "请手动在 GitHub 设置 FEISHU_WEBHOOK_URL"
fi

echo ""
echo "🎉 部署完成!"
echo ""
echo "下一步:"
echo "  1. 访问 https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo "  2. 点击 'Product Hunt AI Daily Report' 工作流"
echo "  3. 点击 'Run workflow' 进行测试"
echo ""

# 清理
cd /
rm -rf "$TEMP_DIR"
