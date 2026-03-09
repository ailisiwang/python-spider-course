#!/usr/bin/env python3
"""
第7章：动态网页渲染

本章目标：
1. 理解动态网页的加载原理
2. 掌握 Selenium 的基本用法
3. 学会使用 Playwright
4. 了解如何直接请求后端 API

运行方式：python 07-dynamic-page.py

依赖安装:
    pip install selenium webdriver-manager playwright
    playwright install
"""

import time
import json
import logging
from typing import List, Dict, Optional

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


# ============ 检测网页类型 ============

def detect_page_type(url: str) -> Dict:
    """检测网页类型（静态/动态）"""
    print_section("1. 检测网页类型")

    import requests
    from bs4 import BeautifulSoup

    result = {
        'url': url,
        'is_dynamic': False,
        'requires_js': False,
        'has_api': False,
    }

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 检查是否有动态加载的迹象
        scripts = soup.find_all('script')
        result['script_count'] = len(scripts)

        # 检查常见前端框架
        frameworks = []
        for script in scripts:
            src = script.get('src', '').lower()
            if any(fw in src for fw in ['react', 'vue', 'angular', 'jquery']):
                frameworks.append(src)

        result['frameworks'] = frameworks
        result['requires_js'] = len(frameworks) > 0

        # 检查是否有空的内容容器
        empty_containers = soup.find_all(attrs={'class': lambda x: x and ('loading' in x.lower() or 'content' in x.lower())})
        for container in empty_containers:
            if not container.text.strip() and container.get('data-src') or container.get('data-url'):
                result['is_dynamic'] = True
                break

        print(f"\n📊 网页分析结果:")
        print(f"   URL: {url}")
        print(f"   Script 数量: {result['script_count']}")
        print(f"   前端框架: {frameworks if frameworks else '未检测到'}")
        print(f"   可能是动态页面: {'是' if result['is_dynamic'] or result['requires_js'] else '否'}")

    except Exception as e:
        logger.error(f"检测失败: {e}")

    return result


# ============ Selenium 示例 ============

def selenium_basic_demo() -> None:
    """Selenium 基础示例"""
    print_section("2. Selenium 基础用法")

    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        print("\n🚗 启动 Chrome 浏览器...")

        # 使用 webdriver-manager 自动管理驱动
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()

        # 添加一些选项
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        driver = webdriver.Chrome(service=service, options=options)

        try:
            # 访问网页
            url = "https://httpbin.org/html"
            print(f"📍 访问: {url}")
            driver.get(url)

            # 获取页面标题
            title = driver.title
            print(f"📄 页面标题: {title}")

            # 查找元素
            try:
                # 等待元素加载
                wait = WebDriverWait(driver, 10)
                h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                print(f"🔍 找到标题: {h1.text}")

            except Exception as e:
                print(f"⚠️  查找元素超时: {e}")

            # 获取页面长度
            page_length = len(driver.page_source)
            print(f"📏 页面内容长度: {page_length} 字符")

            # 执行 JavaScript
            result = driver.execute_script("return document.documentElement.scrollHeight;")
            print(f"📜 页面高度: {result} 像素")

        finally:
            driver.quit()
            print("\n✅ 浏览器已关闭")

    except ImportError as e:
        print(f"\n⚠️  缺少依赖: {e}")
        print("   请运行: pip install selenium webdriver-manager")
    except Exception as e:
        logger.error(f"Selenium 演示失败: {e}")


def selenium_interactions_demo() -> None:
    """Selenium 交互演示"""
    print_section("3. Selenium 用户交互")

    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service

        print("\n🚗 启动浏览器...")

        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(service=service, options=options)

        try:
            # 访问一个有表单的页面
            url = "https://httpbin.org/forms/post"
            print(f"📍 访问表单页面: {url}")
            driver.get(url)

            # 填写表单
            print("\n📝 填写表单:")

            # 输入文本
            try:
                # 查找输入框并输入
                wait = WebDriverWait(driver, 10)

                # 尝试查找各种输入元素
                inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"   找到 {len(inputs)} 个输入框")

                # 输入文本到第一个输入框
                if inputs:
                    inputs[0].clear()
                    inputs[0].send_keys("测试用户")
                    print("   ✅ 已输入用户名")

            except Exception as e:
                print(f"   ⚠️  表单操作: {e}")

            # 截图
            screenshot_path = "/tmp/selenium_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 截图已保存: {screenshot_path}")

            # 获取 Cookie
            cookies = driver.get_cookies()
            print(f"\n🍪 Cookie 数量: {len(cookies)}")

        finally:
            driver.quit()

    except Exception as e:
        logger.error(f"交互演示失败: {e}")


# ============ Playwright 示例 ============

def playwright_basic_demo() -> None:
    """Playwright 基础示例"""
    print_section("4. Playwright 基础用法")

    try:
        from playwright.sync_api import sync_playwright

        print("\n🎭 启动 Playwright...")

        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 访问网页
            url = "https://httpbin.org/html"
            print(f"📍 访问: {url}")
            page.goto(url, wait_until="networkidle")

            # 获取页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")

            # 查找元素
            try:
                h1 = page.locator("h1").first
                if h1:
                    text = h1.text_content()
                    print(f"🔍 找到标题: {text}")
            except Exception as e:
                print(f"⚠️  查找元素: {e}")

            # 等待选择器
            try:
                page.wait_for_selector("h1", timeout=5000)
                print("✅ 元素已加载")
            except Exception as e:
                print(f"⏰ 等待超时: {e}")

            # 执行 JavaScript
            result = page.evaluate("() => document.documentElement.scrollHeight")
            print(f"📜 页面高度: {result} 像素")

            # 获取页面内容
            content = page.content()
            print(f"📏 页面长度: {len(content)} 字符")

            browser.close()

    except ImportError as e:
        print(f"\n⚠️  缺少依赖: {e}")
        print("   请运行: pip install playwright && playwright install")
    except Exception as e:
        logger.error(f"Playwright 演示失败: {e}")


async def playwright_async_demo() -> None:
    """Playwright 异步示例"""
    print_section("5. Playwright 异步用法")

    try:
        from playwright.async_api import async_playwright

        print("\n🎭 启动 Playwright (异步)...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 访问网页
            url = "https://httpbin.org/html"
            print(f"📍 访问: {url}")
            await page.goto(url, wait_until="networkidle")

            # 多页面并行操作
            print("\n🔄 创建多个页面...")
            pages = []
            for i in range(3):
                new_page = await browser.new_page()
                await new_page.goto(url)
                pages.append(new_page)

            print(f"✅ 创建了 {len(pages)} 个页面")

            # 关闭所有页面
            for page in pages:
                await page.close()

            await browser.close()

    except ImportError as e:
        print(f"\n⚠️  缺少依赖: {e}")
        print("   请运行: pip install playwright && playwright install")
    except Exception as e:
        logger.error(f"Playwright 异步演示失败: {e}")


# ============ API 逆向示例 ============

def api_reverse_demo() -> None:
    """API 逆向示例"""
    print_section("6. 直接请求后端 API")

    import requests

    print("\n💡 很多动态网页的数据来自后端 API")
    print("   我们可以直接请求 API，而不需要渲染页面")

    # 示例：使用 httpbin 的 API
    api_urls = {
        'JSON 数据': 'https://httpbin.org/json',
        'UUID 生成': 'https://httpbin.org/uuid',
        'IP 信息': 'https://httpbin.org/ip',
        '请求头信息': 'https://httpbin.org/headers',
    }

    for name, url in api_urls.items():
        print(f"\n📡 {name}:")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 尝试解析 JSON
                try:
                    data = response.json()
                    print(f"   ✅ {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"   ✅ {response.text[:200]}...")
            else:
                print(f"   ⚠️  状态码: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {e}")


def find_api_lesson() -> None:
    """查找 API 的经验分享"""
    print_section("7. 如何找到后端 API")

    lessons = """
    🔍 查找动态网页 API 的方法:

    1. 📱 打开浏览器开发者工具 (F12)
       → 切换到 Network (网络) 标签
       → 刷新页面，观察网络请求

    2. 🔍 筛选 XHR/Fetch 请求
       → 这些通常是 API 请求
       → 查看请求的 URL、方法、参数

    3. 📋 分析请求详情
       → Request Headers: 需要哪些请求头
       → Request Payload: POST 数据
       → Response: 返回的数据格式

    4. 🧪 测试 API
       → 使用 curl 或 Postman 重现请求
       → 确认哪些参数是必需的

    5. 💡 常见 API 模式
       → /api/*  : RESTful API
       → /graphql : GraphQL API
       → JSON 数据返回

    6. ⚠️  注意事项
       → 有些 API 需要认证 Token
       → 可能有加密/签名参数
       → 遵守网站的使用条款
    """
    print(lessons)


# ============ 性能对比 ============

def performance_comparison() -> None:
    """性能对比"""
    print_section("8. 不同方案性能对比")

    import requests

    url = "https://httpbin.org/html"

    print("\n⚡ 方案对比:")

    # 方案 1: 直接 requests (最快)
    print("\n1️⃣  Requests (静态页面)")
    start = time.time()
    response = requests.get(url, timeout=10)
    time1 = time.time() - start
    print(f"   ⏱️  耗时: {time1:.2f} 秒")
    print(f"   📏 内容: {len(response.text)} 字符")

    # 方案 2: Selenium (最慢，但最可靠)
    print("\n2️⃣  Selenium (渲染页面)")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options

        start = time.time()

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        content = driver.page_source

        time2 = time.time() - start
        print(f"   ⏱️  耗时: {time2:.2f} 秒")
        print(f"   📏 内容: {len(content)} 字符")

        driver.quit()

        print(f"\n📊 性能对比:")
        print(f"   Selenium 比 Requests 慢: {time2 / time1:.1f}x")

    except Exception as e:
        print(f"   ⚠️  Selenium 测试失败: {e}")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🌐 动态网页渲染 - Selenium & Playwright            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    detect_page_type("https://httpbin.org/html")
    selenium_basic_demo()
    selenium_interactions_demo()
    playwright_basic_demo()
    # asyncio.run(playwright_async_demo())  # 异步示例
    api_reverse_demo()
    find_api_lesson()
    performance_comparison()

    print_section("完成")
    print("💡 动态网页处理建议:")
    print("   1. 🔍 优先分析是否可以直接请求 API")
    print("   2. 🚗 Selenium 兼容性好，但速度慢")
    print("   3. 🎭 Playwright 更快，功能更强大")
    print("   4. ⚙️  使用无头模式节省资源")
    print("   5. ⏰ 合理设置等待时间")
    print("\n📚 练习:")
    print("   1. 使用 Selenium 爬取一个动态加载的网站")
    print("   2. 尝试找到并直接请求后端 API")
    print("   3. 使用 Playwright 实现表单自动提交")


if __name__ == "__main__":
    main()
