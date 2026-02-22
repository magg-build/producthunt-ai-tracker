# Product Hunt AI Tracker 快速部署指南

## 部署步骤

### 方式一：使用 OpenClaw 自动部署（推荐）

1. **获取 Product Hunt Developer Token**
   - 访问 https://www.producthunt.com/v2/oauth/applications
   - 登录账号 → Create Application
   - 复制 Developer Token

2. **获取 GitHub Personal Access Token**
   - 访问 https://github.com/settings/tokens
   - 生成新 Token，勾选 `repo` 和 `workflow` 权限

3. **（可选）获取飞书 Webhook URL**
   - 在飞书群组中添加自定义机器人
   - 复制 Webhook 地址

4. **运行部署命令**
   ```bash
   export PRODUCTHUNT_DEVELOPER_TOKEN="你的PH Token"
   export GITHUB_USERNAME="你的GitHub用户名"
   export PAT="你的GitHub Token"
   export FEISHU_WEBHOOK_URL="你的飞书Webhook（可选）"
   
   ./deploy.sh
   ```

### 方式二：手动部署

1. **Fork 或创建仓库**
   ```bash
   # 在 GitHub 上创建新仓库 producthunt-ai-tracker
   ```

2. **上传代码**
   ```bash
   git clone https://github.com/你的用户名/producthunt-ai-tracker.git
   cd producthunt-ai-tracker
   
   # 复制所有项目文件到该目录
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **配置 Secrets**
   进入仓库 Settings → Secrets and variables → Actions → New repository secret
   
   添加以下 secrets：
   - `PRODUCTHUNT_DEVELOPER_TOKEN` - Product Hunt API Token
   - `PAT` - GitHub Personal Access Token
   - `FEISHU_WEBHOOK_URL` - 飞书机器人 Webhook（可选）

4. **启用 Actions**
   - 进入 Actions 页面
   - 点击 "I understand my workflows, go ahead and enable them"

5. **测试运行**
   - 进入 Actions → Product Hunt AI Daily Report
   - 点击 "Run workflow" → 选择榜单类型 → Run

---

## 使用说明

### 自动运行
- **每日6:00**（北京时间）自动生成日报
- **周末**自动使用 Weekly 榜单
- **首次运行**使用 Weekly 榜单

### 手动触发
进入 Actions 页面，选择工作流，点击 "Run workflow"，可选择：
- Daily - 日榜（前5个AI项目）
- Weekly - 周榜（前5个AI项目）
- Monthly - 月榜（前20个AI项目）
- Yearly - 年榜（前20个AI项目）

### 查看报告
- 报告保存在 `data/` 目录
- 文件名格式：`PH-AI-{period}-{YYYY-MM-DD}.md`
- 每次运行后自动提交到仓库

---

## 报告内容示例

```markdown
# 🔥 Product Hunt AI 项目日报 - 2026年02月22日

> 📊 榜单类型：**日榜**
> ⏰ 生成时间：2026-02-22 06:00:00
> 🤖 筛选条件：AI / ML / LLM 相关项目

---

## 📈 今日精选（Top 5）

### 1. AI Product Name

**🏷️ 项目类型**：企业服务 | 营销增长

**👥 使用人群**：企业团队、营销人员

**📝 核心功能**：使用 AI 自动生成营销文案和广告创意

**🔗 项目地址**：
- Product Hunt: https://www.producthunt.com/posts/xxx
- 官方网站: https://example.com

**📊 数据表现**：
- 👍 投票数：523
- 💬 评论数：45
- 🏷️ 相关标签：AI, Marketing, Copywriting

---
```

---

## 故障排除

### API 返回错误
- 检查 `PRODUCTHUNT_DEVELOPER_TOKEN` 是否正确
- 确认 Token 没有过期

### 推送失败
- 检查 `PAT` 是否有 `repo` 和 `workflow` 权限
- 确认仓库 Settings → Actions → General → Workflow permissions 设置为 "Read and write permissions"

### 飞书推送失败
- 检查 Webhook URL 是否正确
- 确认飞书机器人在群组中且没有被禁言

---

## 自定义配置

### 修改运行时间
编辑 `.github/workflows/daily-report.yml`：
```yaml
on:
  schedule:
    - cron: '0 22 * * *'  # UTC 22:00 = 北京时间 6:00
```

### 修改筛选关键词
编辑 `scripts/tracker.py` 中的 `AI_KEYWORDS` 列表

### 修改项目分类
编辑 `CATEGORY_RULES` 字典

---

## 项目文件说明

```
producthunt-ai-tracker/
├── .github/workflows/
│   └── daily-report.yml      # GitHub Actions 工作流配置
├── scripts/
│   ├── tracker.py            # 核心追踪脚本
│   ├── feishu_notifier.py    # 飞书通知模块
│   └── send_to_feishu.py     # 发送脚本
├── data/                     # 报告输出目录
├── README.md                 # 项目说明
├── requirements.txt          # Python 依赖
├── deploy.sh                 # 部署脚本
└── DEPLOY.md                 # 本文件
```
