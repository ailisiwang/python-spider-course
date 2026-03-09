#!/usr/bin/env python3
"""
第5章：请求伪装与反爬基础

本章目标：
1. 理解常见的反爬机制
2. 掌握请求头伪装技巧
3. 学会使用代理 IP
4. 实现合理的请求频率控制

运行方式：python 05-request-disguise.py
"""

import requests
import time
import random
import logging
from typing import Dict, List, Optional
from fake_useragent import UserAgent

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


# ============ 常用 User-Agent 列表 ============

USER_AGENTS = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',

    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',

    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',

    # Mobile
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
]


# ============ 请求头生成器 ============

class HeaderGenerator:
    """请求头生成器"""

    def __init__(self, use_fake_ua: bool = True):
        self.use_fake_ua = use_fake_ua
        try:
            self.ua = UserAgent()
        except Exception:
            logger.warning("fake_useragent 不可用，使用内置 UA 列表")
            self.use_fake_ua = False
            self.ua = None

    def get_random_ua(self) -> str:
        """获取随机 User-Agent"""
        if self.use_fake_ua and self.ua:
            try:
                return self.ua.random
            except Exception:
                pass
        return random.choice(USER_AGENTS)

    def get_desktop_headers(self) -> Dict[str, str]:
        """获取桌面浏览器请求头"""
        return {
            'User-Agent': self.get_random_ua(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def get_mobile_headers(self) -> Dict[str, str]:
        """获取移动设备请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def get_api_headers(self) -> Dict[str, str]:
        """获取 API 请求头"""
        return {
            'User-Agent': self.get_random_ua(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Origin': 'https://example.com',
            'Referer': 'https://example.com/',
        }


def header_generator_demo() -> None:
    """请求头生成器演示"""
    print_section("1. 请求头生成器")

    generator = HeaderGenerator()

    print("\n🖥️  桌面浏览器请求头:")
    desktop_headers = generator.get_desktop_headers()
    for key, value in desktop_headers.items():
        print(f"   {key}: {value[:60]}..." if len(value) > 60 else f"   {key}: {value}")

    print("\n📱 移动设备请求头:")
    mobile_headers = generator.get_mobile_headers()
    for key, value in mobile_headers.items():
        print(f"   {key}: {value}")


# ============ 请求延迟控制 ============

class RequestLimiter:
    """请求频率限制器"""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0

    def wait(self) -> None:
        """等待随机时间"""
        delay = random.uniform(self.min_delay, self.max_delay)
        elapsed = time.time() - self.last_request_time

        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.info(f"⏳ 等待 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def __call__(self, func):
        """装饰器用法"""
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


def request_limiter_demo() -> None:
    """请求限制器演示"""
    print_section("2. 请求频率控制")

    limiter = RequestLimiter(min_delay=0.5, max_delay=1.5)

    print("\n⏱️  发送 3 个请求（带随机延迟）:")
    for i in range(3):
        limiter.wait()
        print(f"   ✅ 请求 {i+1} 发送完成")


# ============ 代理管理 ============

class ProxyManager:
    """代理管理器"""

    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.current_index = 0
        self.failed_proxies: Dict[str, int] = {}

    def add_proxy(self, proxy: str, proxy_type: str = 'http') -> None:
        """添加代理"""
        self.proxies.append({proxy_type: proxy})

    def load_from_list(self, proxy_list: List[str]) -> None:
        """从列表加载代理"""
        for proxy in proxy_list:
            self.add_proxy(proxy.strip())

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取下一个可用代理"""
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def mark_failed(self, proxy_str: str) -> None:
        """标记代理失败"""
        self.failed_proxies[proxy_str] = self.failed_proxies.get(proxy_str, 0) + 1

    def get_stats(self) -> Dict:
        """获取代理统计"""
        return {
            'total': len(self.proxies),
            'failed': len(self.failed_proxies),
            'available': len(self.proxies) - len(self.failed_proxies)
        }


def proxy_demo() -> None:
    """代理演示"""
    print_section("3. 代理 IP 使用")

    # 示例代理列表（实际使用时需要有效的代理）
    example_proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
        'http://proxy3.example.com:8080',
    ]

    proxy_manager = ProxyManager()
    proxy_manager.load_from_list(example_proxies)

    print(f"\n📊 代理池信息:")
    stats = proxy_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 轮换代理:")
    for i in range(5):
        proxy = proxy_manager.get_proxy()
        print(f"   请求 {i+1}: {proxy}")


# ============ Session 管理器 ============

class SessionManager:
    """会话管理器"""

    def __init__(self):
        self.session = requests.Session()
        self.header_gen = HeaderGenerator()
        self.limiter = RequestLimiter()

    def get(self, url: str, **kwargs) -> requests.Response:
        """发送 GET 请求"""
        self.limiter.wait()

        # 默认请求头
        headers = kwargs.pop('headers', {})
        default_headers = self.header_gen.get_desktop_headers()
        default_headers.update(headers)

        kwargs['headers'] = default_headers
        kwargs.setdefault('timeout', 10)

        try:
            response = self.session.get(url, **kwargs)
            logger.info(f"✅ GET {url} - {response.status_code}")
            return response

        except requests.RequestException as e:
            logger.error(f"❌ GET {url} 失败: {e}")
            raise

    def post(self, url: str, **kwargs) -> requests.Response:
        """发送 POST 请求"""
        self.limiter.wait()

        headers = kwargs.pop('headers', {})
        default_headers = self.header_gen.get_desktop_headers()
        default_headers.update(headers)

        kwargs['headers'] = default_headers
        kwargs.setdefault('timeout', 10)

        try:
            response = self.session.post(url, **kwargs)
            logger.info(f"✅ POST {url} - {response.status_code}")
            return response

        except requests.RequestException as e:
            logger.error(f"❌ POST {url} 失败: {e}")
            raise


def session_manager_demo() -> None:
    """会话管理器演示"""
    print_section("4. Session 管理")

    session_mgr = SessionManager()

    print("\n🔍 使用 Session 管理器发送请求:")

    try:
        # 第一个请求
        response1 = session_mgr.get('https://httpbin.org/get')
        print(f"   请求1: {response1.status_code}")

        # 第二个请求（会自动带 Cookie）
        response2 = session_mgr.get('https://httpbin.org/cookies/set/test/value')
        print(f"   请求2: {response2.status_code}")

        # 第三个请求（检查 Cookie）
        response3 = session_mgr.get('https://httpbin.org/cookies')
        cookies = response3.json()
        print(f"   请求3 Cookies: {cookies}")

    except Exception as e:
        logger.error(f"请求失败: {e}")


# ============ 完整的反反爬虫类 ============

class SmartSpider:
    """智能爬虫类"""

    def __init__(self):
        self.session_mgr = SessionManager()
        self.proxy_manager = ProxyManager()
        self.max_retries = 3

    def fetch(self, url: str, use_proxy: bool = False) -> Optional[requests.Response]:
        """智能请求"""
        proxies = None

        if use_proxy:
            proxies = self.proxy_manager.get_proxy()

        for attempt in range(self.max_retries):
            try:
                response = self.session_mgr.get(url, proxies=proxies)

                # 检查状态码
                if response.status_code == 200:
                    return response

                elif response.status_code == 403:
                    logger.warning("🚫 403 禁止访问，可能被识别为机器人")

                elif response.status_code == 429:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"⏳ 429 请求过多，等待 {wait_time} 秒...")
                    time.sleep(wait_time)

            except requests.RequestException as e:
                logger.error(f"❌ 请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")

        return None


def smart_spider_demo() -> None:
    """智能爬虫演示"""
    print_section("5. 智能爬虫")

    spider = SmartSpider()

    print("\n🕷️  使用智能爬虫获取网页:")

    try:
        response = spider.fetch('https://httpbin.org/get')
        if response:
            print(f"   ✅ 成功获取: {len(response.text)} 字符")

    except Exception as e:
        logger.error(f"获取失败: {e}")


# ============ 实战：获取网站信息 ============

def detect_anti_crawl(url: str) -> Dict:
    """检测网站的反爬措施"""
    print_section("6. 检测网站反爬措施")

    results = {
        'url': url,
        'user_agent_check': False,
        'cookie_check': False,
        'rate_limit': False,
        'javascript_required': False,
    }

    session_mgr = SessionManager()

    # 1. 检查 User-Agent 检测
    print("\n🔍 检查 User-Agent 检测...")

    # 不带 UA 的请求
    try:
        response1 = requests.get(url, timeout=10)
        if response1.status_code != 200:
            results['user_agent_check'] = True
            print("   ⚠️  可能存在 User-Agent 检测")
    except Exception as e:
        logger.warning(f"   无 UA 请求失败: {e}")

    # 带 UA 的请求
    try:
        response2 = session_mgr.get(url)
        if response2.status_code == 200:
            print("   ✅ 正常请求成功")
    except Exception as e:
        logger.warning(f"   带 UA 请求失败: {e}")

    return results


def real_world_example() -> None:
    """真实世界示例"""
    print_section("7. 真实网站爬取示例")

    # 使用 httpbin 作为示例
    test_url = "https://httpbin.org/html"

    spider = SmartSpider()

    print(f"\n🕷️  爬取: {test_url}")

    response = spider.fetch(test_url)

    if response:
        print(f"   ✅ 成功！")
        print(f"   📏 内容长度: {len(response.text)} 字符")
        print(f"   🏷️  Content-Type: {response.headers.get('Content-Type')}")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🕷️ 请求伪装与反爬基础                                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    header_generator_demo()
    request_limiter_demo()
    proxy_demo()
    session_manager_demo()
    smart_spider_demo()
    detect_anti_crawl("https://httpbin.org/get")
    real_world_example()

    print_section("完成")
    print("💡 反反爬虫最佳实践:")
    print("   1. 🎭 随机化 User-Agent，模拟真实浏览器")
    print("   2. ⏳ 添加随机延迟，避免请求过快")
    print("   3. 🔄 使用代理 IP 池，避免 IP 被封")
    print("   4. 🍪 使用 Session 管理 Cookie")
    print("   5. 🔁 实现重试机制，处理临时错误")
    print("   6. 📊 监控请求状态，及时调整策略")
    print("\n📚 练习:")
    print("   1. 实现一个带代理池的爬虫")
    print("   2. 分析一个网站的反爬机制并应对")
    print("   3. 实现指数退避的重试策略")


if __name__ == "__main__":
    main()
