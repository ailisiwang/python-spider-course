#!/usr/bin/env python3
"""
第1关：爬虫入门 - 了解网页结构
就像去房产中介看房子
"""

import requests

# 就像你去房产中介看房子info
url = "https://example.com"

# 发送请求，获取网页内容
response = requests.get(url)

# 打印网页的"骨架"（HTML）
print("🏠 网页内容：")
print(response.text[:500])  # 只看前500个字符，就像看房型图
