"""
飞书消息推送模块
用于将 Product Hunt 报告推送到飞书群组
"""

import os
import requests
import json
from typing import List, Dict
from datetime import datetime

class FeishuNotifier:
    """飞书消息通知器"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get('FEISHU_WEBHOOK_URL')
    
    def format_product_card(self, product: Dict, index: int) -> Dict:
        """格式化单个产品为卡片元素"""
        node = product.get("node", {})
        
        # 获取分类和受众
        from scripts.tracker import ProductHuntAITracker
        tracker = ProductHuntAITracker()
        categories = tracker.categorize_project(product)
        audience = tracker.analyze_target_audience(product)
        
        # 截断描述
        description = node.get('description', '')[:100] + '...' if len(node.get('description', '')) > 100 else node.get('description', '')
        
        return {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{index}. [{node.get('name')}]({node.get('url')})**\n"
                          f"📝 {node.get('tagline')}\n"
                          f"🏷️ {' | '.join(categories)}\n"
                          f"👥 {audience}\n"
                          f"👍 {node.get('votesCount', 0)} votes | [官网]({node.get('website', node.get('url'))})"
            }
        }
    
    def send_daily_report(self, products: List[Dict], period: str = "daily") -> bool:
        """发送日报到飞书"""
        
        if not self.webhook_url:
            print("❌ 未配置飞书 Webhook URL")
            return False
        
        period_names = {
            "daily": "日榜",
            "weekly": "周榜",
            "monthly": "月榜", 
            "yearly": "年榜"
        }
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        period_name = period_names.get(period, "榜单")
        
        # 构建卡片元素
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"📊 **{period_name}** | {date_str}"
                }
            },
            {"tag": "hr"}
        ]
        
        # 添加产品信息
        for i, product in enumerate(products[:5], 1):
            elements.append(self.format_product_card(product, i))
            elements.append({"tag": "hr"})
        
        # 添加页脚
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "_数据来源：Product Hunt_"
            }
        })
        
        # 构建卡片消息
        card = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🔥 Product Hunt AI 项目日报"
                    },
                    "template": "blue"
                },
                "elements": elements
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=card,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("✅ 飞书消息发送成功")
                    return True
                else:
                    print(f"❌ 飞书 API 错误: {result}")
                    return False
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            return False


def send_simple_text(products: List[Dict], webhook_url: str = None) -> bool:
    """发送简单文本消息（备用方案）"""
    
    webhook_url = webhook_url or os.environ.get('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        return False
    
    lines = ["🔥 Product Hunt AI 项目日报\n"]
    
    for i, product in enumerate(products[:5], 1):
        node = product.get("node", {})
        lines.append(f"{i}. {node.get('name')}")
        lines.append(f"   {node.get('tagline')}")
        lines.append(f"   👍 {node.get('votesCount')} | {node.get('url')}\n")
    
    message = {
        "msg_type": "text",
        "content": {
            "text": "\n".join(lines)
        }
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        return response.status_code == 200 and response.json().get("code") == 0
    except:
        return False


if __name__ == "__main__":
    # 测试代码
    print("飞书通知模块测试")
    print("请设置 FEISHU_WEBHOOK_URL 环境变量后使用")
