import os
import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class ProductHuntAITracker:
    """Product Hunt AI 项目追踪器"""
    
    # AI 相关关键词
    AI_KEYWORDS = [
        'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
        'gpt', 'llm', 'large language model', 'chatbot', 'agent', 'automation',
        'neural', 'generative', 'genai', 'copilot', 'assistant', 'claude',
        'openai', 'anthropic', 'gemini', 'midjourney', 'stable diffusion',
        'vector', 'embedding', 'rag', 'fine-tuning', 'prompt', 'workflow',
        'no-code', 'low-code', 'api', 'saas', 'b2b', 'b2c'
    ]
    
    # 项目类型分类规则
    CATEGORY_RULES = {
        '企业服务': ['b2b', 'enterprise', 'business', 'company', 'team', 'workspace', 'collaboration', 'crm', 'erp'],
        '营销增长': ['marketing', 'sales', 'seo', 'ads', 'advertising', 'growth', 'lead', 'conversion', 'analytics'],
        '开发者工具': ['developer', 'dev', 'api', 'sdk', 'code', 'programming', 'github', 'deployment', 'testing'],
        '个人生产力': ['productivity', 'personal', 'individual', 'todo', 'note', 'writing', 'reading', 'learning'],
        '内容创作': ['content', 'video', 'image', 'photo', 'design', 'creative', 'editing', 'generation', 'media'],
        '客户服务': ['support', 'customer', 'service', 'chat', 'helpdesk', 'ticket', 'feedback'],
        '数据分析': ['data', 'analytics', 'insight', 'dashboard', 'report', 'visualization', 'bi'],
        '人力资源': ['hr', 'hiring', 'recruitment', 'talent', 'interview', 'resume', 'candidate'],
        '金融科技': ['finance', 'fintech', 'payment', 'crypto', 'blockchain', 'trading', 'investment'],
        '教育学习': ['education', 'learning', 'course', 'tutorial', 'study', 'student', 'teacher'],
        '健康医疗': ['health', 'medical', 'healthcare', 'fitness', 'wellness', 'therapy'],
        '社交社区': ['social', 'community', 'network', 'communication', 'messaging', 'connection']
    }
    
    def __init__(self):
        self.token = os.environ.get('PRODUCTHUNT_DEVELOPER_TOKEN')
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def should_use_weekly(self) -> bool:
        """判断是否使用 Weekly 榜单（第一次运行或周末）"""
        today = datetime.now()
        
        # 周末（周六=5, 周日=6）
        if today.weekday() >= 5:
            return True
        
        # 检查是否是第一次运行（data 目录为空）
        data_dir = "data"
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.md')]
            if not files:
                return True
        else:
            return True
        
        return False
    
    def get_posts_query(self, period: str = "daily", first: int = 10) -> str:
        """构建 GraphQL 查询"""
        
        # 根据周期计算日期
        now = datetime.now()
        if period == "daily":
            posted_after = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        elif period == "weekly":
            posted_after = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        elif period == "monthly":
            posted_after = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        elif period == "yearly":
            posted_after = (now - timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            posted_after = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        
        query = f"""
        query {{
          posts(order: RANKING, first: {first}, postedAfter: "{posted_after}T00:00:00Z") {{
            edges {{
              node {{
                id
                name
                tagline
                description
                url
                website
                votesCount
                commentsCount
                createdAt
                topics {{
                  edges {{
                    node {{
                      name
                    }}
                  }}
                }}
                makers {{
                  username
                  name
                  headline
                }}
                thumbnail {{
                  url
                }}
                user {{
                  username
                  name
                }}
              }}
            }}
          }}
        }}
        """
        return query
    
    def fetch_posts(self, period: str = "daily", first: int = 10) -> List[Dict]:
        """获取帖子列表"""
        query = self.get_posts_query(period, first)
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"GraphQL Errors: {data['errors']}")
                    return []
                
                posts = data.get("data", {}).get("posts", {}).get("edges", [])
                print(f"✅ 成功获取 {len(posts)} 个项目")
                return posts
            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
                return []
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
            return []
    
    def is_ai_project(self, post: Dict) -> bool:
        """判断是否是 AI 项目"""
        node = post.get("node", {})
        
        # 合并所有文本
        text = f"{node.get('name', '')} {node.get('tagline', '')} {node.get('description', '')}".lower()
        
        # 获取标签
        topics = [t.get("node", {}).get("name", "").lower() 
                  for t in node.get("topics", {}).get("edges", [])]
        
        # 检查关键词
        for keyword in self.AI_KEYWORDS:
            if keyword in text or any(keyword in t for t in topics):
                return True
        
        return False
    
    def categorize_project(self, post: Dict) -> List[str]:
        """对项目进行分类，返回标签列表"""
        node = post.get("node", {})
        text = f"{node.get('name', '')} {node.get('tagline', '')} {node.get('description', '')}".lower()
        topics = [t.get("node", {}).get("name", "").lower() 
                  for t in node.get("topics", {}).get("edges", [])]
        
        categories = []
        
        for category, keywords in self.CATEGORY_RULES.items():
            for keyword in keywords:
                if keyword in text or any(keyword in t for t in topics):
                    categories.append(category)
                    break
        
        # 如果没有匹配到，根据其他特征判断
        if not categories:
            if any(kw in text for kw in ['app', 'mobile', 'ios', 'android']):
                categories.append('移动应用')
            if any(kw in text for kw in ['web', 'browser', 'extension']):
                categories.append('Web工具')
            if any(kw in text for kw in ['chrome', 'plugin', 'addon']):
                categories.append('浏览器插件')
        
        return categories if categories else ['其他']
    
    def analyze_target_audience(self, post: Dict) -> str:
        """分析目标使用人群"""
        node = post.get("node", {})
        text = f"{node.get('tagline', '')} {node.get('description', '')}".lower()
        categories = self.categorize_project(post)
        
        # 根据分类和描述推断用户群体
        audience_signals = {
            '企业团队': ['enterprise', 'business', 'company', 'team', 'organization', 'corporate', 'startup', 'b2b'],
            '开发者': ['developer', 'engineer', 'programmer', 'coder', 'technical', 'dev', 'api', 'sdk'],
            '营销人员': ['marketer', 'marketing', 'growth', 'seo', 'sales', 'advertiser'],
            '设计师': ['designer', 'design', 'creative', 'ui', 'ux', 'graphic'],
            '内容创作者': ['creator', 'content creator', 'youtuber', 'blogger', 'influencer', 'writer'],
            '学生/学习者': ['student', 'learner', 'education', 'study', 'academic'],
            '个人用户': ['individual', 'personal', 'consumer', 'user', 'everyone', 'anyone']
        }
        
        audiences = []
        for audience, keywords in audience_signals.items():
            if any(kw in text for kw in keywords):
                audiences.append(audience)
        
        # 根据分类补充
        if '企业服务' in categories and '企业团队' not in audiences:
            audiences.append('企业团队')
        if '开发者工具' in categories and '开发者' not in audiences:
            audiences.append('开发者')
        if '营销增长' in categories and '营销人员' not in audiences:
            audiences.append('营销人员')
        if '内容创作' in categories and '内容创作者' not in audiences:
            audiences.append('内容创作者')
        
        return '、'.join(audiences) if audiences else '通用用户'
    
    def extract_core_features(self, post: Dict) -> str:
        """提取核心功能场景"""
        node = post.get("node", {})
        description = node.get('description', '')
        tagline = node.get('tagline', '')
        
        # 优先使用 tagline，通常更简洁
        if tagline:
            return tagline
        
        # 否则截取描述的前两句
        if description:
            sentences = re.split(r'[.!?。！？]+', description)
            core = ' '.join(s.strip() for s in sentences[:2] if s.strip())
            return core[:200] + '...' if len(core) > 200 else core
        
        return '暂无描述'
    
    def generate_report(self, posts: List[Dict], period: str = "daily") -> str:
        """生成日报报告"""
        date_str = datetime.now().strftime("%Y年%m月%d日")
        period_names = {
            "daily": "日榜",
            "weekly": "周榜", 
            "monthly": "月榜",
            "yearly": "年榜"
        }
        period_name = period_names.get(period, "榜单")
        
        report = f"""# 🔥 Product Hunt AI 项目日报 - {date_str}

> 📊 榜单类型：**{period_name}**
> ⏰ 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> 🤖 筛选条件：AI / ML / LLM 相关项目

---

## 📈 今日精选（Top {len(posts)}）

"""
        
        for i, post in enumerate(posts, 1):
            node = post.get("node", {})
            categories = self.categorize_project(post)
            audience = self.analyze_target_audience(post)
            features = self.extract_core_features(post)
            
            # 获取话题标签
            topics = [t.get("node", {}).get("name", "") 
                     for t in node.get("topics", {}).get("edges", [])]
            
            report += f"""### {i}. {node.get('name', 'Unknown')}

**🏷️ 项目类型**：{' | '.join(categories)}

**👥 使用人群**：{audience}

**📝 核心功能**：{features}

**🔗 项目地址**：
- Product Hunt: {node.get('url', 'N/A')}
- 官方网站: {node.get('website', 'N/A')}

**📊 数据表现**：
- 👍 投票数：{node.get('votesCount', 0)}
- 💬 评论数：{node.get('commentsCount', 0)}
- 🏷️ 相关标签：{', '.join(topics[:5]) if topics else 'N/A'}

---

"""
        
        # 添加页脚
        report += f"""
## 📌 说明

- 本报告由 AI 自动生成，每日筛选 Product Hunt 热门 AI 项目
- 数据来源：Product Hunt API
- 筛选逻辑：基于关键词匹配和话题标签识别 AI 相关项目

---
*Generated by Product Hunt AI Tracker*
"""
        
        return report
    
    def run(self, force_period: Optional[str] = None) -> tuple:
        """主运行函数"""
        print("🚀 启动 Product Hunt AI 项目追踪...")
        print(f"📅 当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 确定使用哪个榜单
        if force_period:
            period = force_period
        elif self.should_use_weekly():
            period = "weekly"
        else:
            period = "daily"
        
        # 根据周期确定获取数量
        fetch_counts = {
            "daily": 15,      # 日榜多获取一些，过滤后保留5个
            "weekly": 25,     # 周榜获取更多
            "monthly": 30,    # 月榜
            "yearly": 50      # 年榜
        }
        first = fetch_counts.get(period, 15)
        
        print(f"📋 使用榜单：{period.upper()}，获取前 {first} 个项目")
        
        # 获取数据
        posts = self.fetch_posts(period, first)
        if not posts:
            print("❌ 未获取到数据")
            return None, []
        
        # 过滤 AI 项目
        ai_posts = [p for p in posts if self.is_ai_project(p)]
        print(f"🤖 识别到 {len(ai_posts)} 个 AI 相关项目")
        
        # 如果 AI 项目不足，补充其他热门项目
        if len(ai_posts) < 5:
            remaining = [p for p in posts if p not in ai_posts]
            ai_posts.extend(remaining[:5 - len(ai_posts)])
        
        # 只保留前5个
        ai_posts = ai_posts[:5]
        
        print(f"✅ 最终筛选：{len(ai_posts)} 个项目")
        
        # 生成报告
        report = self.generate_report(ai_posts, period)
        
        # 保存文件
        os.makedirs("data", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"data/PH-AI-{period}-{date_str}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"💾 报告已保存：{filename}")
        
        return filename, ai_posts


if __name__ == "__main__":
    # 支持命令行参数
    import sys
    force_period = sys.argv[1] if len(sys.argv) > 1 else None
    
    tracker = ProductHuntAITracker()
    tracker.run(force_period)
