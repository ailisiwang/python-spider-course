#!/usr/bin/env python3
"""
第2关：下竿试试 - 发送第一次请求
第一次"钓鱼"，把杆甩出去！
"""

import requests

# 🐟 目标鱼塘（网站）
url = "https://httpbin.org/get"

print("🎣 正在甩竿...")

# 发送 GET 请求
response = requests.get(url)

# 看看钓到了什么
print(f"✅ 钓到了！状态码: {response.status_code}")
print(f"📏 鱼的长度: {len(response.text)} 字符")
print(f"\n🐟 鱼的内容:\n{response.text}")
