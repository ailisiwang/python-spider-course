#!/usr/bin/env python3
"""
第3章：精准定位 - XPath

本章目标：
1. 理解 XPath 的语法和概念
2. 掌握常用的 XPath 表达式
3. 学会使用 lxml 解析 HTML

运行方式：python 03-xpath.py
"""

from lxml import etree
import logging
from typing import List

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


# 示例 HTML（稍微复杂一些）
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>电商网站 - 商品搜索结果</title>
</head>
<body>
    <div id="app">
        <header class="site-header">
            <div class="logo">ShopMall</div>
            <nav class="main-nav">
                <ul>
                    <li><a href="/">首页</a></li>
                    <li><a href="/products">商品</a></li>
                    <li><a href="/brands">品牌</a></li>
                </ul>
            </nav>
            <div class="search-box">
                <input type="text" name="q" placeholder="搜索商品">
                <button type="submit">搜索</button>
            </div>
        </header>

        <main class="content">
            <aside class="sidebar">
                <div class="filter-group">
                    <h3>分类</h3>
                    <ul>
                        <li><a href="/cat/phone">手机</a></li>
                        <li><a href="/cat/computer">电脑</a></li>
                        <li><a href="/cat/tablet">平板</a></li>
                    </ul>
                </div>
                <div class="filter-group">
                    <h3>价格区间</h3>
                    <ul>
                        <li><a href="/price/0-1000">0-1000元</a></li>
                        <li><a href="/price/1000-5000">1000-5000元</a></li>
                        <li><a href="/price/5000+">5000元以上</a></li>
                    </ul>
                </div>
            </aside>

            <section class="product-area">
                <div class="toolbar">
                    <span class="result-count">共找到 42 个商品</span>
                    <select class="sort-select">
                        <option value="default">默认排序</option>
                        <option value="price-asc">价格从低到高</option>
                        <option value="price-desc">价格从高到低</option>
                    </select>
                </div>

                <div class="product-grid">
                    <div class="product-item" data-id="101" data-category="phone">
                        <div class="product-image">
                            <img src="/img/phone1.jpg" alt="iPhone 15 Pro">
                        </div>
                        <div class="product-info">
                            <h3 class="product-title">iPhone 15 Pro 256GB</h3>
                            <p class="product-desc">A17 Pro 芯片，钛金属设计</p>
                            <div class="product-meta">
                                <span class="price">¥7999</span>
                                <span class="sales">月销 1000+</span>
                            </div>
                            <div class="product-tags">
                                <span class="tag tag-hot">热卖</span>
                                <span class="tag tag-new">新品</span>
                            </div>
                        </div>
                    </div>

                    <div class="product-item" data-id="102" data-category="computer">
                        <div class="product-image">
                            <img src="/img/laptop1.jpg" alt="MacBook Pro">
                        </div>
                        <div class="product-info">
                            <h3 class="product-title">MacBook Pro 14寸 M3</h3>
                            <p class="product-desc">专业性能，绝佳体验</p>
                            <div class="product-meta">
                                <span class="price">¥14999</span>
                                <span class="sales">月销 500+</span>
                            </div>
                            <div class="product-tags">
                                <span class="tag tag-hot">热卖</span>
                            </div>
                        </div>
                    </div>

                    <div class="product-item" data-id="103" data-category="tablet">
                        <div class="product-image">
                            <img src="/img/tablet1.jpg" alt="iPad Air">
                        </div>
                        <div class="product-info">
                            <h3 class="product-title">iPad Air 5 M1芯片</h3>
                            <p class="product-desc">全能平板，轻薄便携</p>
                            <div class="product-meta">
                                <span class="price">¥4799</span>
                                <span class="sales">月销 2000+</span>
                            </div>
                            <div class="product-tags">
                                <span class="tag tag-recommend">推荐</span>
                            </div>
                        </div>
                    </div>

                    <div class="product-item" data-id="104" data-category="phone">
                        <div class="product-image">
                            <img src="/img/phone2.jpg" alt="华为 Mate 60">
                        </div>
                        <div class="product-info">
                            <h3 class="product-title">华为 Mate 60 Pro</h3>
                            <p class="product-desc">卫星通信，超光变摄像头</p>
                            <div class="product-meta">
                                <span class="price">¥6999</span>
                                <span class="sales">月销 3000+</span>
                            </div>
                            <div class="product-tags">
                                <span class="tag tag-hot">热卖</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="pagination">
                    <a class="page active">1</a>
                    <a class="page" href="?page=2">2</a>
                    <a class="page" href="?page=3">3</a>
                    <a class="page" href="?page=4">4</a>
                    <a class="next" href="?page=2">下一页</a>
                </div>
            </section>
        </main>

        <footer class="site-footer">
            <p>&copy; 2024 ShopMall 版权所有</p>
        </footer>
    </div>
</body>
</html>
"""


def basic_xpath() -> None:
    """基础 XPath 语法"""
    print_section("1. XPath 基础语法")

    tree = etree.HTML(SAMPLE_HTML)

    # 绝对路径
    print("\n📍 绝对路径:")
    title = tree.xpath('/html/head/title/text()')
    print(f"   /html/head/title/text(): {title}")

    # 相对路径
    print("\n📍 相对路径:")
    h1 = tree.xpath('//h1/text()')
    print(f"   //h1/text(): {h1}")

    # 通配符
    print("\n📍 通配符 *:")
    all_headers = tree.xpath('//*/h3/text()')
    print(f"   所有 h3 文本: {all_headers}")


def select_by_tag() -> None:
    """通过标签选择"""
    print_section("2. 通过标签选择")

    tree = etree.HTML(SAMPLE_HTML)

    # 选择所有 div
    all_divs = tree.xpath('//div')
    print(f"\n📦 所有 div 数量: {len(all_divs)}")

    # 选择所有 a 标签
    all_links = tree.xpath('//a')
    print(f"🔗 所有 a 标签数量: {len(all_links)}")

    # 选择所有 img 标签的 src 属性
    img_srcs = tree.xpath('//img/@src')
    print(f"🖼️  所有图片 src:")
    for src in img_srcs:
        print(f"   - {src}")


def select_by_attribute() -> None:
    """通过属性选择"""
    print_section("3. 通过属性选择")

    tree = etree.HTML(SAMPLE_HTML)

    # 通过 id 选择
    app = tree.xpath('//div[@id="app"]')
    print(f"\n🎯 找到 id='app': {len(app)} 个")

    # 通过 class 选择
    products = tree.xpath('//div[@class="product-item"]')
    print(f"📦 找到 class='product-item': {len(products)} 个")

    # 属性包含特定值
    phone_products = tree.xpath('//div[contains(@data-category, "phone")]')
    print(f"📱 data-category 包含 'phone': {len(phone_products)} 个")

    # 多属性条件
    hot_items = tree.xpath('//div[@class="product-item" and contains(@data-category, "phone")]')
    print(f"🔥 手机类商品: {len(hot_items)} 个")

    # 属性值以特定字符串开头
    img_with_alt = tree.xpath('//img[starts-with(@alt, "iPhone")]')
    print(f"🍎 alt 以 'iPhone' 开头的图片: {len(img_with_alt)} 个")


def select_by_position() -> None:
    """通过位置选择"""
    print_section("4. 通过位置选择")

    tree = etree.HTML(SAMPLE_HTML)

    # 选择第一个商品
    first_product = tree.xpath('(//div[@class="product-item"])[1]/div[@class="product-info"]/h3/text()')
    print(f"\n🥇 第一个商品: {first_product}")

    # 选择最后一个商品
    last_product = tree.xpath('(//div[@class="product-item"])[last()]/div[@class="product-info"]/h3/text()')
    print(f"📍 最后一个商品: {last_product}")

    # 选择前两个商品
    first_two = tree.xpath('(//div[@class="product-item"])[position()<=2]/div[@class="product-info"]/h3/text()')
    print(f"📊 前两个商品: {first_two}")

    # 选择偶数位置的商品
    even_products = tree.xpath('(//div[@class="product-item"])[position() mod 2 = 0]/div[@class="product-info"]/h3/text()')
    print(f"🔢 偶数位置商品: {even_products}")


def axis_selectors() -> None:
    """轴选择器"""
    print_section("5. 轴选择器（Axis）")

    tree = etree.HTML(SAMPLE_HTML)

    # ancestor - 所有祖先节点
    print("\n⬆️  ancestor (祖先):")
    first_img = tree.xpath('//img[1]')[0]
    ancestors = first_img.xpath('ancestor::div')
    print(f"   第一个图片的 div 祖先数: {len(ancestors)}")

    # parent - 父节点
    print("\n👆 parent (父节点):")
    parent_div = first_img.xpath('parent::div/@class')
    print(f"   图片父节点的 class: {parent_div}")

    # following-sibling - 后面的兄弟节点
    print("\n👉 following-sibling (后面的兄弟):")
    first_title = tree.xpath('(//h3[@class="product-title"])[1]')
    siblings = first_title[0].xpath('following-sibling::*')
    print(f"   第一个标题后的兄弟节点数: {len(siblings)}")

    # preceding-sibling - 前面的兄弟节点
    print("\n👈 preceding-sibling (前面的兄弟):")
    price = tree.xpath('(//span[@class="price"])[1]')
    preceding = price[0].xpath('preceding-sibling::*')
    print(f"   第一个价格前的兄弟节点数: {len(preceding)}")

    # descendant - 所有后代节点
    print("\n⬇️  descendant (后代):")
    product_grid = tree.xpath('//div[@class="product-grid"]')
    descendants = product_grid[0].xpath('descendant::div')
    print(f"   product-grid 下的 div 数量: {len(descendants)}")


def extract_text() -> None:
    """提取文本"""
    print_section("6. 提取文本内容")

    tree = etree.HTML(SAMPLE_HTML)

    # text() - 获取当前节点的文本
    print("\n📝 text() 函数:")
    page_title = tree.xpath('//title/text()')
    print(f"   页面标题: {page_title}")

    # . - 当前节点
    print("\n📍 获取所有文本（包含空文本）:")
    all_text = tree.xpath('//div[@class="product-info"]/text()')
    print(f"   原始文本节点数: {len(all_text)}")

    # string() - 获取所有文本合并
    print("\n📄 string() 函数:")
    first_info = tree.xpath('//div[@class="product-info"][1]/string()')
    print(f"   第一个商品信息的所有文本:")
    print(f"   {first_info[0].strip()[:80]}...")


def extract_data_example() -> None:
    """完整的数据提取示例"""
    print_section("7. 完整数据提取示例")

    tree = etree.HTML(SAMPLE_HTML)

    products = []

    # 获取所有商品
    product_divs = tree.xpath('//div[@class="product-item"]')

    for div in product_divs:
        product = {
            'id': div.xpath('./@data-id')[0],
            'category': div.xpath('./@data-category')[0],
            'title': div.xpath('.//h3[@class="product-title"]/text()')[0],
            'desc': div.xpath('.//p[@class="product-desc"]/text()')[0],
            'price': div.xpath('.//span[@class="price"]/text()')[0],
            'sales': div.xpath('.//span[@class="sales"]/text()')[0],
            'tags': div.xpath('.//span[@class="tag"]/text()'),
            'image_alt': div.xpath('.//img/@alt')[0],
        }
        products.append(product)

    print(f"\n📊 提取了 {len(products)} 个商品:")
    for p in products:
        print(f"\n   📦 [{p['id']}] {p['title']}")
        print(f"      💰 价格: {p['price']}")
        print(f"      📝 描述: {p['desc']}")
        print(f"      📊 销量: {p['sales']}")
        print(f"      🏷️  标签: {', '.join(p['tags'])}")


def xpath_functions() -> None:
    """XPath 常用函数"""
    print_section("8. XPath 常用函数")

    tree = etree.HTML(SAMPLE_HTML)

    # contains() - 包含
    print("\n🔍 contains() - 包含匹配:")
    contains_iphone = tree.xpath('//h3[contains(text(), "iPhone")]/text()')
    print(f"   标题包含 'iPhone': {contains_iphone}")

    # starts-with() - 以...开头
    print("\n🔤 starts-with() - 开头匹配:")
    starts_with_iphone = tree.xpath('//img[starts-with(@alt, "iPhone")]/@alt')
    print(f"   alt 以 'iPhone' 开头: {starts_with_iphone}")

    # text() - 文本内容
    print("\n📝 text() - 文本长度:")
    long_desc = tree.xpath('//p[string-length(text()) > 10]/text()')
    print(f"   文本长度>10的描述: {len(long_desc)} 个")

    # normalize-space() - 去除空白
    print("\n✂️ normalize-space() - 标准化空白:")
    messy_text = "  hello   world  "
    normalized = tree.xpath(f'normalize-space("{messy_text}")')
    print(f"   原始: '{messy_text}'")
    print(f"   标准化: '{normalized}'")

    # count() - 计数
    print("\n🔢 count() - 计数:")
    div_count = tree.xpath('count(//div[@class="product-item"])')
    print(f"   product-item 数量: {int(div_count)}")

    # sum() - 求和
    print("\n➕ sum() - 求和:")
    numbers = tree.xpath('sum(//span[@class="sales"]/substring-after(text(), "月销 "))')
    print(f"   销量之和（解析后）: 需要进一步处理数字")


def real_world_example() -> None:
    """真实网页示例"""
    print_section("9. 真实网页 XPath 示例")

    import requests

    try:
        # 使用 httpbin 的 HTML 页面
        url = "https://httpbin.org/html"
        response = requests.get(url, timeout=10)

        tree = etree.HTML(response.text)

        # 提取标题
        h1 = tree.xpath('//h1/text()')
        print(f"\n📌 页面标题: {h1}")

        # 提取所有段落
        paragraphs = tree.xpath('//p/text()')
        print(f"\n📝 段落数量: {len(paragraphs)}")
        for i, p in enumerate(paragraphs, 1):
            print(f"   {i}. {p.strip()}")

    except requests.RequestException as e:
        logger.error(f"请求失败: {e}")


def performance_tip() -> None:
    """性能提示"""
    print_section("10. 性能对比与最佳实践")

    import time

    tree = etree.HTML(SAMPLE_HTML)

    # 测试1: 使用 // 从根搜索
    start = time.time()
    for _ in range(1000):
        _ = tree.xpath('//span[@class="price"]')
    time1 = time.time() - start

    # 测试2: 使用相对路径
    start = time.time()
    products = tree.xpath('//div[@class="product-info"]')
    for _ in range(100):
        for p in products:
            _ = p.xpath('.//span[@class="price"]')
    time2 = time.time() - start

    print(f"\n⚡ 性能测试:")
    print(f"   全局搜索 (//) 1000次: {time1:.4f}秒")
    print(f"   相对搜索 (./) 100次: {time2:.4f}秒")

    print(f"\n💡 最佳实践:")
    print(f"   1. 尽量使用具体的路径，避免 //")
    print(f"   2. 使用 @属性 而不是文本内容定位")
    print(f"   3. 善用 contains() 和 starts-with()")
    print(f"   4. 复杂场景可以结合 BeautifulSoup 使用")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🕷️ XPath - 精准定位 HTML 元素                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    basic_xpath()
    select_by_tag()
    select_by_attribute()
    select_by_position()
    axis_selectors()
    extract_text()
    extract_data_example()
    xpath_functions()
    real_world_example()
    performance_tip()

    print_section("完成")
    print("💡 XPath 常用语法速查:")
    print("   //div[@class='xxx']      - class 为 xxx 的 div")
    print("   //div[@id='xxx']         - id 为 xxx 的 div")
    print("   //a/@href                - 所有 a 的 href 属性")
    print("   //text()                 - 所有文本节点")
    print("   //div[contains(text(), 'keyword')]")
    print("                            - 包含关键词的 div")
    print("   (//div)[1]               - 第一个 div")
    print("   //div[last()]            - 最后一个 div")
    print("\n📚 练习:")
    print("   1. 使用 XPath 爬取一个网站的新闻列表")
    print("   2. 尝试提取嵌套很深的元素")
    print("   3. 对比 BeautifulSoup 和 XPath 的用法差异")


if __name__ == "__main__":
    main()
