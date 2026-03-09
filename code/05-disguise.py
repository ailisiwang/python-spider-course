#!/usr/bin/env python3
"""
第5关：伪装达人 - 请求头与代理
学会伪装，不被当作机器人！
"""

import requests

print("=" * 40)
print("🎭 伪装达人训练营")
print("=" * 40)

# 1️⃣ 基础伪装：穿上"人皮"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

url = "https://httpbin.org/headers"
response = requests.get(url, headers=headers)
print("\n1️⃣ 伪装后的请求头:")
print(response.json())

# 2️⃣ 高级伪装：全套礼仪
headers_advanced = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',  # 假装从谷歌点过来
}

response = requests.get(url, headers=headers_advanced)
print("\n2️⃣ 高级伪装（带 Referer）:")
print(response.json())

# 3️⃣ 使用代理（换马甲）
print("\n3️⃣ 代理示例（需要有效的代理服务器）:")
proxy = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
# response = requests.get(url, proxies=proxy)  # 取消注释启用
# print(response.json())

print("   💡 使用格式: requests.get(url, proxies=proxy)")

# 4️⃣ 设置超时和重试
print("\n4️⃣ 礼貌等待（设置超时）:")
try:
    response = requests.get('https://httpbin.org/delay/1', timeout=3)
    print(f"   ✅ 成功！耗时: {response.elapsed.total_seconds()}s")
except requests.Timeout:
    print("   ⏰ 等待太久，不等了！")
