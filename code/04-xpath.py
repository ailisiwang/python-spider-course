#!/usr/bin/env python3
"""
第4关：精准捕捞 - XPath 高手
用 XPath 精准定位，就像用 GPS 导航！
"""

from lxml import etree

html = """
<html>
    <body>
        <div class="container">
            <h1 class="title">商品列表</h1>
            <div class="product" id="p1">
                <span class="name">iPhone 15</span>
                <span class="price">6999</span>
            </div>
            <div class="product" id="p2">
                <span class="name">MacBook Pro</span>
                <span class="price">19999</span>
            </div>
            <div class="product" id="p3">
                <span class="name">AirPods Pro</span>
                <span class="price">1999</span>
            </div>
        </div>
    </body>
</html>
"""

# 解析 HTML
tree = etree.HTML(html)

print("=" * 40)
print("🗺️ XPath 精准定位演示")
print("=" * 40)

# 1. 定位所有商品名称
names = tree.xpath('//span[@class="name"]/text()')
print(f"\n1️⃣ 所有商品名称: {names}")

# 2. 获取所有价格
prices = tree.xpath('//span[@class="price"]/text()')
print(f"2️⃣ 所有价格: {prices}")

# 3. 配对商品名和价格
print("\n3️⃣ 商品清单:")
for name, price in zip(names, prices):
    print(f"   📱 {name}: ¥{price}")

# 4. 找到特定商品（id="p2"）
p2_name = tree.xpath('//div[@id="p2"]/span[@class="name"]/text()')[0]
print(f"\n4️⃣ p2商品名称: {p2_name}")

# 5. 获取第二个商品的名称（索引从1开始）
second_name = tree.xpath('(//span[@class="name"])[2]/text()')[0]
print(f"5️⃣ 第二个商品: {second_name}")
