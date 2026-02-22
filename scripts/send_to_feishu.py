#!/usr/bin/env python3
"""
发送 Product Hunt 报告到飞书
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_notifier import FeishuNotifier, send_simple_text

def load_products_from_report(report_file):
    """从报告文件解析产品信息（简化版）"""
    # 实际使用时，可以从 tracker 直接获取数据
    # 这里简化处理，直接读取 tracker 生成的 JSON 数据
    json_file = report_file.replace('.md', '.json')
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def main():
    parser = argparse.ArgumentParser(description='Send Product Hunt report to Feishu')
    parser.add_argument('--period', default='daily', help='Report period (daily/weekly/monthly/yearly)')
    parser.add_argument('--file', help='Specific report file to send')
    args = parser.parse_args()
    
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        print("❌ 未设置 FEISHU_WEBHOOK_URL 环境变量")
        sys.exit(1)
    
    # 如果没有指定文件，查找最新的报告
    if not args.file:
        data_dir = 'data'
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.startswith('PH-AI-') and f.endswith('.md')]
            if files:
                files.sort(reverse=True)
                args.file = os.path.join(data_dir, files[0])
    
    if not args.file or not os.path.exists(args.file):
        print(f"❌ 未找到报告文件")
        sys.exit(1)
    
    print(f"📄 读取报告: {args.file}")
    
    # 读取 Markdown 内容并发送
    with open(args.file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构建简单文本消息
    notifier = FeishuNotifier(webhook_url)
    
    # 由于无法直接获取 products 列表，发送文本格式
    message = {
        "msg_type": "text",
        "content": {
            "text": f"🔥 Product Hunt AI 项目日报\n\n{content[:3000]}...\n\n完整报告请查看 GitHub Actions 产物"
        }
    }
    
    import requests
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        if response.status_code == 200 and response.json().get("code") == 0:
            print("✅ 飞书消息发送成功")
        else:
            print(f"❌ 发送失败: {response.text}")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
