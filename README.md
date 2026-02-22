# Product Hunt AI 项目追踪器

自动追踪 Product Hunt 热门 AI 项目，每日生成精选报告。

## 功能特性

- 🤖 **AI 智能筛选** - 自动识别 AI/ML/LLM 相关项目
- 📊 **智能榜单切换** - 第一次运行 + 每周末使用 Weekly 榜单，日常使用 Daily 榜单
- 🏷️ **项目分类** - 自动标注项目类型（企业服务、营销增长、个人生产力等）
- 👥 **用户分析** - 推断目标使用人群
- 📝 **核心功能** - 提取项目核心场景描述
- ⏰ **定时推送** - 每天早上6点自动生成报告

## 报告内容

每个项目包含：
1. **项目地址** - Product Hunt 链接 + 官方网站
2. **简要描述** - 核心功能场景
3. **使用人群** - 目标用户群体
4. **项目类型** - 自动分类标签（ToB/ToC 等）
5. **数据表现** - 投票数、评论数、相关标签

## 快速开始

### 1. Fork 本仓库

点击右上角的 "Fork" 按钮，将仓库复制到你的账号下。

### 2. 配置 Secrets

在仓库 Settings -> Secrets and variables -> Actions 中添加以下 secrets：

| Secret Name | 说明 | 获取方式 |
|------------|------|---------|
| `PRODUCTHUNT_DEVELOPER_TOKEN` | Product Hunt API Token | [开发者设置](https://www.producthunt.com/v2/oauth/applications) |
| `PAT` | GitHub Personal Access Token | Settings -> Developer settings -> Personal access tokens |

### 3. 获取 Product Hunt Developer Token

1. 访问 https://www.producthunt.com/v2/oauth/applications
2. 登录你的 Product Hunt 账号
3. 点击 "Create Application"
4. 填写应用名称和描述
5. 获取 `Developer Token`

### 4. 手动测试

进入 Actions 页面，选择 "Product Hunt AI Daily Report"，点击 "Run workflow" 进行测试。

## 工作流说明

### 自动触发
- **每日6:00**（北京时间）自动生成日报
- **周末**自动切换为 Weekly 榜单
- **首次运行**使用 Weekly 榜单

### 手动触发
支持手动选择榜单类型：
- Daily - 日榜
- Weekly - 周榜
- Monthly - 月榜
- Yearly - 年榜

## 项目分类标签

| 标签 | 说明 |
|-----|------|
| 企业服务 | B2B 企业级应用、团队协作工具 |
| 营销增长 | SEO、广告、销售、增长工具 |
| 开发者工具 | API、SDK、代码工具、部署平台 |
| 个人生产力 | 效率工具、笔记、待办、学习 |
| 内容创作 | 视频、图片、设计、创意工具 |
| 客户服务 | 客服、工单、反馈系统 |
| 数据分析 | BI、可视化、报表工具 |
| 人力资源 | 招聘、面试、简历工具 |
| 金融科技 | 支付、加密、投资工具 |
| 教育学习 | 在线课程、学习平台 |
| 健康医疗 | 健康、医疗、健身应用 |
| 社交社区 | 社交、社区、通讯工具 |

## 目录结构

```
.
├── .github/workflows/
│   └── daily-report.yml    # GitHub Actions 工作流
├── scripts/
│   └── tracker.py          # 核心追踪脚本
├── data/                   # 生成的报告存储目录
│   └── PH-AI-daily-YYYY-MM-DD.md
├── README.md
└── .gitignore
```

## 自定义配置

### 修改筛选关键词

编辑 `scripts/tracker.py` 中的 `AI_KEYWORDS` 列表：

```python
AI_KEYWORDS = [
    'ai', 'machine learning', 'gpt', 'llm',
    # 添加你的关键词
]
```

### 修改分类规则

编辑 `CATEGORY_RULES` 字典：

```python
CATEGORY_RULES = {
    '新分类': ['keyword1', 'keyword2'],
    # ...
}
```

### 修改定时时间

编辑 `.github/workflows/daily-report.yml` 中的 cron 表达式：

```yaml
on:
  schedule:
    # UTC 时间，北京时间 = UTC + 8
    - cron: '0 22 * * *'  # 每天 UTC 22:00 = 北京时间 6:00
```

## 贡献

欢迎提交 Issue 和 PR！

## License

MIT
