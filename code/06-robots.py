#!/usr/bin/env python3
"""
第6关：协议礼仪 - robots.txt 与伦理
学会遵守规矩，做个文明的爬虫！
"""

import requests
from urllib import robotparser
import time

print("=" * 40)
print("📜 爬虫礼仪课")
print("=" * 40)

# 1️⃣ 查看网站的"家规"
rp = robotparser.RobotFileParser()

# 检查某个网站是否允许爬取
url = "https://www.baidu.com/robots.txt"
rp.set_url(url)
rp.read()

print("\n1️⃣ 百度允许爬虫吗?")
print(f"   📋 允许爬取 /index.html: {rp.can_fetch('*', '/index.html')}")
print(f"   📋 允许爬取 /search: {rp.can_fetch('*', '/search')}")
print(f"   📋 允许爬取 /sh古人: {rp.can_fetch('*', '/sh古人')}")

# 2️⃣ 正确的请求姿势
print("\n2️⃣ 文明爬虫的正确姿势:")

url = "https://httpbin.org/delay/1"

# ❌ 不礼貌：连续狂请求
# for i in range(10):
#     requests.get(url)

# ✅ 礼貌：每次间隔一下
print("   ⏳ 每次请求间隔 1 秒...")
for i in range(3):
    start = time.time()
    # requests.get(url)  # 取消注释实际执行
    elapsed = time.time() - start
    print(f"   ✅ 第{i+1}次请求完成，耗时{elapsed:.2f}s")
    time.sleep(1)  # 等待1秒再下一次

# 3️⃣ 设置合理的请求间隔
print("\n3️⃣ 设置延迟（用 Session）:")
session = requests.Session()

# 爬虫中间件可以设置默认延迟（演示）
print("   💡 requests-rate limiter 可以控制频率")
print("   💡 建议: 每秒不超过 3-5 个请求")

# 4️⃣ 识别反爬信号
print("\n4️⃣ 常见反爬信号:")
print("   🚫 403 Forbidden - 不让进")
print("   🚫 429 Too Many Requests - 请求太多")
print("   🚫 验证码 - 怀疑你是机器人")
print("   💡 遇到这些，该换代理或停停了！")
