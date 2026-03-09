#!/usr/bin/env python3
"""
第3关：织网技术 - BeautifulSoup 解析
织一张网，去捕捞数据！
"""

from bs4 import BeautifulSoup

# 模拟一个网页的 HTML（就像捕捞上来的海草）
html = """
<html>
    <head>
        <title>钓鱼岛主的主页</title>
    </head>
    <body>
        <h1 class="title">欢迎来到钓鱼岛</h1>
        <div class="content">
            <p>今天钓到了很多鱼！</p>
            <a href="/fish/1">查看大黄鱼</a>
            <a href="/fish/2">查看石斑鱼</a>
        </div>
        <ul class="fish-list">
            <li class="fish">金枪鱼</li>
            <li class="fish">三文鱼</li>
            <li class="fish">鳕鱼</li>
        </ul>
    </body>
</html>
"""

# 🕸️ 织网（解析 HTML）
soup = BeautifulSoup(html, 'html.parser')

print("=" * 40)
print("🎣 BeautifulSoup 捕捞演示")
print("=" * 40)

# 1. 通过标签捕捞
title = soup.find('title')
print(f"\n1️⃣ 捕捞标题: {title.text}")

# 2. 通过 class 捕捞
content = soup.find(class_='content')
print(f"2️⃣ 捕捞内容区域: {content.text.strip()}")

# 3. 批量捕捞所有链接
links = soup.find_all('a')
print(f"\n3️⃣ 捕捞到 {len(links)} 条链接:")
for link in links:
    print(f"   🔗 {link.text}: {link['href']}")

# 4. 批量捕捞所有鱼
fishes = soup.find_all(class_='fish')
print(f"\n4️⃣ 捕捞到 {len(fishes)} 条鱼:")
for fish in fishes:
    print(f"   🐟 {fish.text}")

# 5. 进阶：用 CSS 选择器（像精准钓鱼）
links_via_css = soup.select('div.content a')
print(f"\n5️⃣ 用 CSS 选择器精准捕捞: {len(links_via_css)} 个")
