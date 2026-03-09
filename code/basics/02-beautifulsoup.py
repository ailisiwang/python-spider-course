#!/usr/bin/env python3
"""
第2章：HTML 解析基础 - BeautifulSoup

本章目标：
1. 理解 BeautifulSoup 的基本用法
2. 掌握常用的查找方法
3. 学会使用 CSS 选择器

运行方式：python 02-beautifulsoup.py
"""

from bs4 import BeautifulSoup
import logging
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str) -> None:
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# 示例 HTML
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>示例网页 - 商品列表</title>
</head>
<body>
    <div id="header">
        <h1 class="site-title">在线商城</h1>
        <nav class="main-nav">
            <a href="/home">首页</a>
            <a href="/products">商品</a>
            <a href="/about">关于</a>
        </nav>
    </div>

    <div id="container">
        <div class="product-list">
            <div class="product" data-id="1">
                <h3 class="product-name">iPhone 15 Pro</h3>
                <p class="description">最新款 iPhone，钛金属边框</p>
                <span class="price">¥7999</span>
                <span class="stock">有货</span>
                <a href="/product/1" class="btn">查看详情</a>
            </div>

            <div class="product" data-id="2">
                <h3 class="product-name">MacBook Pro 16寸</h3>
                <p class="description">M3 Max 芯片，性能怪兽</p>
                <span class="price">¥19999</span>
                <span class="stock out">缺货</span>
                <a href="/product/2" class="btn">查看详情</a>
            </div>

            <div class="product" data-id="3">
                <h3 class="product-name">AirPods Pro 2</h3>
                <p class="description">主动降噪，空间音频</p>
                <span class="price">¥1899</span>
                <span class="stock">有货</span>
                <a href="/product/3" class="btn">查看详情</a>
            </div>

            <div class="product" data-id="4">
                <h3 class="product-name">iPad Air 5</h3>
                <p class="description">M1 芯片，全面屏设计</p>
                <span class="price">¥4799</span>
                <span class="stock">有货</span>
                <a href="/product/4" class="btn">查看详情</a>
            </div>
        </div>

        <div class="pagination">
            <a href="?page=1" class="active">1</a>
            <a href="?page=2">2</a>
            <a href="?page=3">3</a>
            <a href="?page=2" class="next">下一页</a>
        </div>
    </div>

    <div id="footer">
        <p>&copy; 2024 在线商城 版权所有</p>
    </div>
</body>
</html>
"""


def basic_parsing() -> None:
    """基础解析示例"""
    print_section("1. BeautifulSoup 基础解析")

    # 创建 BeautifulSoup 对象
    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # 获取标题
    title = soup.title
    print(f"\n📄 页面标题: {title.text}")

    # 格式化输出 HTML
    print(f"\n🏷️  标题标签 HTML:")
    print(title.prettify()[:100])


def find_by_tag() -> None:
    """通过标签查找"""
    print_section("2. 通过标签查找")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # 查找第一个 h1 标签
    h1 = soup.find('h1')
    print(f"\n🔍 找到第一个 h1: {h1.text}")

    # 查找所有 a 标签
    all_links = soup.find_all('a')
    print(f"\n🔗 所有链接数量: {len(all_links)}")

    # 查找前 3 个 a 标签
    first_three_links = soup.find_all('a', limit=3)
    print(f"🔗 前 3 个链接:")
    for link in first_three_links:
        print(f"   - {link.text.strip()}: {link.get('href')}")


def find_by_class_and_id() -> None:
    """通过 class 和 id 查找"""
    print_section("3. 通过 Class 和 ID 查找")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # 通过 class 查找
    site_title = soup.find(class_='site-title')
    print(f"\n📌 找到 .site-title: {site_title.text}")

    # 通过 id 查找
    header = soup.find(id='header')
    print(f"📌 找到 #header: {header.h1.text}")

    # 查找所有带有 product class 的元素
    products = soup.find_all(class_='product')
    print(f"\n📦 找到 {len(products)} 个商品")


def find_by_attributes() -> None:
    """通过属性查找"""
    print_section("4. 通过属性查找")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # 通过 data-id 属性查找
    product_1 = soup.find(attrs={'data-id': '1'})
    print(f"\n🏷️  data-id='1' 的商品: {product_1.h3.text}")

    # 查找所有有 href 属性的 a 标签
    all_links_with_href = soup.find_all('a', href=True)
    print(f"\n🔗 带 href 的链接数: {len(all_links_with_href)}")


def css_selectors() -> None:
    """CSS 选择器"""
    print_section("5. CSS 选择器")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # ID 选择器
    header = soup.select_one('#header')
    print(f"\n🎯 #header: {header.h1.text}")

    # 类选择器
    products = soup.select('.product')
    print(f"📦 .product 数量: {len(products)}")

    # 后代选择器
    product_names = soup.select('.product .product-name')
    print(f"\n📝 商品名称:")
    for name in product_names:
        print(f"   - {name.text}")

    # 组合选择器
    in_stock_items = soup.select('.stock:not(.out)')
    print(f"\n✅ 有货商品数: {len(in_stock_items)}")

    # 属性选择器
    products_with_id = soup.select('div[data-id]')
    print(f"🏷️  带 data-id 的商品: {len(products_with_id)}")


def extract_data() -> None:
    """提取数据示例"""
    print_section("6. 提取结构化数据")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    products = []

    for product_div in soup.select('.product'):
        # 提取商品信息
        product = {
            'id': product_div.get('data-id'),
            'name': product_div.select_one('.product-name').text,
            'description': product_div.select_one('.description').text,
            'price': product_div.select_one('.price').text,
            'in_stock': 'out' not in product_div.select_one('.stock')['class'],
            'url': product_div.select_one('a')['href']
        }
        products.append(product)

    print(f"\n📊 提取了 {len(products)} 个商品:")
    for p in products:
        stock_status = "✅ 有货" if p['in_stock'] else "❌ 缺货"
        print(f"\n   📦 {p['name']}")
        print(f"      💰 价格: {p['price']}")
        print(f"      📝 描述: {p['description']}")
        print(f"      📦 库存: {stock_status}")
        print(f"      🔗 链接: {p['url']}")


def navigation_methods() -> None:
    """节点导航方法"""
    print_section("7. 节点导航")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # 获取第一个商品
    first_product = soup.find(class_='product')

    # .contents - 直接子节点
    print(f"\n📍 第一个商品的直接子节点数: {len(first_product.contents)}")

    # .children - 子节点迭代器
    print(f"📍 使用 .children 遍历:")
    for i, child in enumerate(first_product.children):
        if hasattr(child, 'name') and child.name:
            print(f"   {i+1}. <{child.name}>")

    # .parent - 父节点
    print(f"\n⬆️  商品父节点: {first_product.parent.get('class')}")

    # .parents - 所有祖先
    print(f"⬆️  到达根节点的路径:")
    for i, parent in enumerate(first_product.parents):
        if parent.name:
            print(f"   {i+1}. <{parent.name}>")

    # .next_sibling 和 .previous_sibling
    nav = soup.find(class_='main-nav')
    first_link = nav.find('a')
    print(f"\n🔗 第一个链接: {first_link.text}")
    print(f"   下一个兄弟: {first_link.next_sibling.next_sibling.text}")


def extract_links_and_images() -> None:
    """提取链接和图片"""
    print_section("8. 提取链接和图片")

    # 创建包含图片的 HTML
    html_with_images = SAMPLE_HTML + """
    <div class="gallery">
        <img src="/images/1.jpg" alt="商品图1" class="product-img">
        <img src="/images/2.jpg" alt="商品图2" class="product-img">
        <img src="https://example.com/banner.jpg" alt="横幅" class="banner">
    </div>
    """

    soup = BeautifulSoup(html_with_images, 'html.parser')

    # 提取所有链接
    print("\n🔗 所有链接:")
    links = soup.find_all('a')
    for link in links:
        text = link.text.strip()
        href = link.get('href')
        print(f"   [{text}]({href})")

    # 提取所有图片
    print("\n🖼️  所有图片:")
    images = soup.find_all('img')
    for img in images:
        src = img.get('src')
        alt = img.get('alt', '无描述')
        print(f"   <{alt}>: {src}")

    # 只提取特定类名的图片
    product_imgs = soup.find_all('img', class_='product-img')
    print(f"\n📦 商品图片数: {len(product_imgs)}")


def modify_html() -> None:
    """修改 HTML"""
    print_section("9. 修改 HTML")

    soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

    # 修改文本
    title = soup.find('title')
    title.string = "修改后的标题"
    print(f"✏️  修改标题: {title.text}")

    # 添加新元素
    new_div = soup.new_tag('div', attrs={'class': 'announcement'})
    new_div.string = "🎉 新年促销活动开始啦！"
    soup.find(id='header').insert_after(new_div)
    print(f"➕ 添加了公告栏")

    # 删除元素
    footer = soup.find(id='footer')
    footer.decompose()
    print(f"🗑️  删除了页脚")

    # 包装元素
    first_p = soup.find('p')
    new_wrapper = soup.new_tag('div', attrs={'class': 'highlight'})
    first_p.wrap(new_wrapper)
    print(f"📦 包装了第一个 p 标签")


def real_world_example() -> None:
    """真实网页示例（使用 httpbin）"""
    print_section("10. 真实网页解析示例")

    import requests

    try:
        # 获取一个真实网页
        url = "https://httpbin.org/html"
        response = requests.get(url, timeout=10)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找标题
        h1 = soup.find('h1')
        print(f"\n📌 页面标题: {h1.text if h1 else '未找到'}")

        # 查找所有段落
        paragraphs = soup.find_all('p')
        print(f"\n📝 段落数量: {len(paragraphs)}")
        for i, p in enumerate(paragraphs[:3], 1):
            print(f"   {i}. {p.text[:60]}...")

    except requests.RequestException as e:
        logger.error(f"请求失败: {e}")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🕷️ BeautifulSoup - HTML 解析入门                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    basic_parsing()
    find_by_tag()
    find_by_class_and_id()
    find_by_attributes()
    css_selectors()
    extract_data()
    navigation_methods()
    extract_links_and_images()
    modify_html()
    real_world_example()

    print_section("完成")
    print("💡 提示:")
    print("   - find() 返回第一个匹配的元素")
    print("   - find_all() 返回所有匹配的元素列表")
    print("   - select() 使用 CSS 选择器，更灵活")
    print("\n📚 练习:")
    print("   1. 爬取一个真实网站，提取文章标题和链接")
    print("   2. 使用不同的方法提取相同元素，对比差异")
    print("   3. 处理嵌套的 HTML 结构")


if __name__ == "__main__":
    main()
