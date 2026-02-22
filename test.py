#!/usr/bin/env python3
"""
Product Hunt AI Tracker 测试脚本
用于验证配置和 API 连接
"""

import os
import sys

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_import():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    try:
        from tracker import ProductHuntAITracker
        from feishu_notifier import FeishuNotifier
        print("✅ 模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_api_connection():
    """测试 Product Hunt API 连接"""
    print("\n🧪 测试 Product Hunt API 连接...")
    
    token = os.environ.get('PRODUCTHUNT_DEVELOPER_TOKEN')
    if not token:
        print("❌ 未设置 PRODUCTHUNT_DEVELOPER_TOKEN 环境变量")
        print("   请访问 https://www.producthunt.com/v2/oauth/applications 获取")
        return False
    
    try:
        from tracker import ProductHuntAITracker
        tracker = ProductHuntAITracker()
        
        # 尝试获取少量数据测试连接
        posts = tracker.fetch_posts("daily", 2)
        
        if posts:
            print(f"✅ API 连接成功，获取到 {len(posts)} 个项目")
            # 显示第一个项目
            node = posts[0].get("node", {})
            print(f"   示例项目: {node.get('name')} - {node.get('tagline')[:50]}...")
            return True
        else:
            print("⚠️ API 连接成功但未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False

def test_ai_filter():
    """测试 AI 项目筛选功能"""
    print("\n🧪 测试 AI 项目筛选...")
    
    try:
        from tracker import ProductHuntAITracker
        tracker = ProductHuntAITracker()
        
        # 模拟测试数据
        test_posts = [
            {
                "node": {
                    "name": "AI Writer Pro",
                    "tagline": "AI-powered content generation tool",
                    "description": "Use GPT-4 to write blog posts"
                }
            },
            {
                "node": {
                    "name": "Task Manager",
                    "tagline": "Simple todo list app",
                    "description": "Manage your daily tasks"
                }
            },
            {
                "node": {
                    "name": "ChatBot Builder",
                    "tagline": "Build LLM chatbots without code",
                    "description": "Create AI assistants for your business"
                }
            }
        ]
        
        ai_posts = [p for p in test_posts if tracker.is_ai_project(p)]
        print(f"✅ 筛选测试通过，识别出 {len(ai_posts)}/3 个 AI 项目")
        
        for post in ai_posts:
            print(f"   🤖 {post['node']['name']}")
        
        return len(ai_posts) >= 2
        
    except Exception as e:
        print(f"❌ 筛选测试失败: {e}")
        return False

def test_categorization():
    """测试项目分类功能"""
    print("\n🧪 测试项目分类...")
    
    try:
        from tracker import ProductHuntAITracker
        tracker = ProductHuntAITracker()
        
        test_cases = [
            ({"node": {"tagline": "CRM for sales teams", "description": ""}}, "企业服务"),
            ({"node": {"tagline": "SEO optimization tool", "description": ""}}, "营销增长"),
            ({"node": {"tagline": "Personal note taking app", "description": ""}}, "个人生产力"),
        ]
        
        passed = 0
        for post, expected in test_cases:
            categories = tracker.categorize_project(post)
            if expected in categories:
                passed += 1
                print(f"   ✅ '{post['node']['tagline']}' → {categories}")
            else:
                print(f"   ⚠️ '{post['node']['tagline']}' → {categories} (期望: {expected})")
        
        print(f"✅ 分类测试: {passed}/{len(test_cases)} 通过")
        return passed >= 2
        
    except Exception as e:
        print(f"❌ 分类测试失败: {e}")
        return False

def test_feishu_notifier():
    """测试飞书通知配置"""
    print("\n🧪 测试飞书通知配置...")
    
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ 未设置 FEISHU_WEBHOOK_URL（可选配置）")
        return None
    
    print(f"✅ 飞书 Webhook 已配置: {webhook_url[:30]}...")
    return True

def main():
    """运行所有测试"""
    print("=" * 50)
    print("🚀 Product Hunt AI Tracker 测试套件")
    print("=" * 50)
    
    results = {
        "模块导入": test_import(),
        "API 连接": test_api_connection(),
        "AI 筛选": test_ai_filter(),
        "项目分类": test_categorization(),
        "飞书配置": test_feishu_notifier()
    }
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    for name, result in results.items():
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️ 跳过"
        print(f"{name}: {status}")
    
    # 统计
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")
    
    if failed == 0:
        print("\n🎉 所有关键测试通过！可以开始使用了。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
