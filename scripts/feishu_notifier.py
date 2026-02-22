#!/usr/bin/env python3
"""
发送 Product Hunt 报告到飞书
"""

import os
import sys
import json
import re
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def parse_markdown_report(file_path):
    """解析 Markdown 报告，提取产品信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    products = []
    
    # 按 ### 分割，提取每个产品
    sections = content.split('###')[1:]  # 跳过第一个（标题部分）
    
    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        # 第一行是产品名称
        name = lines[0].strip()
        
        # 提取信息
        product_type = ""
        audience = ""
        features = ""
        ph_url = ""
        votes = "0"
        
        for line in lines:
            if '项目类型' in line:
                product_type = line.split('**：')[-1].strip() if '**：' in line else ""
            elif '使用人群' in line:
                audience = line.split('**：')[-1].strip() if '**：' in line else ""
            elif '核心功能' in line:
                features = line.split('**：')[-1].strip() if '**：' in line else ""
            elif 'Product Hunt:' in line:
                ph_url = line.split('：')[-1].strip()
            elif '投票数' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    votes = match.group(1)
        
        products.append({
            'name': name,
            'type': product_type,
            'audience': audience,
            'features': features[:100] + '...' if len(features) > 100 else features,
            'url': ph_url,
            'votes': votes
        })
    
    return products

def send_to_feishu(products, period="daily"):
    """发送产品列表到飞书"""
    
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        print("❌ 未设置 FEISHU_WEBHOOK_URL 环境变量")
        return False
    
    period_names = {
        "daily": "日榜",
        "weekly": "周榜",
        "monthly": "月榜",
        "yearly": "年榜"
    }
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    period_name = period_names.get(period, "榜单")
    
    # 构建卡片内容
    content_lines = [f"📊 **Product Hunt AI 项目 {period_name}** | {date_str}\n"]
    
    for i, product in enumerate(products[:5], 1):
        content_lines.append(f"**{i}. {product['name']}**")
        content_lines.append(f"🏷️ {product['type']} | 👥 {product['audience']}")
        content_lines.append(f"📝 {product['features']}")
        content_lines.append(f"👍 {product['votes']} votes | [查看详情]({product['url']})")
        content_lines.append("")
    
    # 飞书文本消息
    message = {
        "msg_type": "text",
        "content": {
            "text": "\n".join(content_lines)
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=message,
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

def main():
    """主函数"""
    # 查找最新的报告文件
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print(f"❌ 目录不存在: {data_dir}")
        sys.exit(1)
    
    files = [f for f in os.listdir(data_dir) if f.startswith('PH-AI-') and f.endswith('.md')]
    if not files:
        print("❌ 未找到报告文件")
        sys.exit(1)
    
    # 按时间排序，取最新的
    files.sort(reverse=True)
    latest_file = os.path.join(data_dir, files[0])
    
    print(f"📄 读取报告: {latest_file}")
    
    # 解析报告
    products = parse_markdown_report(latest_file)
    print(f"✅ 解析到 {len(products)} 个产品")
    
    # 提取榜单类型
    period = "daily"
    if 'weekly' in files[0]:
        period = "weekly"
    elif 'monthly' in files[0]:
        period = "monthly"
    elif 'yearly' in files[0]:
        period = "yearly"
    
    # 发送到飞书
    if products:
        send_to_feishu(products, period)
    else:
        print("⚠️ 没有产品数据可发送")

if __name__ == "__main__":
    main()
