#!/usr/bin/env python3
"""
第9章：反爬虫对抗进阶

本章目标：
1. 了解高级反爬机制
2. 掌握代理池的使用
3. 学会处理验证码
4. 实现完整的反反爬策略

运行方式：python 09-anti-advanced.py

依赖安装:
    pip install fake-useragent retrying requests
"""

import requests
import time
import random
import json
import logging
from typing import Dict, List, Optional, Callable
from abc import ABC, abstractmethod
from enum import Enum

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


# ============ 反爬虫类型枚举 ============

class AntiCrawlType(Enum):
    """反爬虫类型"""
    USER_AGENT_CHECK = "User-Agent 检测"
    IP_RATE_LIMIT = "IP 访问频率限制"
    IP_BLOCK = "IP 封禁"
    COOKIE_CHECK = "Cookie 验证"
    REFERER_CHECK = "Referer 验证"
    CAPTCHA = "验证码"
    JS_CHALLENGE = "JavaScript 挑战"
    ENCRYPTED_PARAMS = "参数加密"
    BEHAVIOR_ANALYSIS = "行为分析"
    FINGERPRINT = "浏览器指纹"


# ============ User-Agent 池 ============

class UserAgentPool:
    """User-Agent 池"""

    DEFAULT_AGENTS = [
        # Chrome Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',

        # Chrome Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',

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

    def __init__(self, agents: List[str] = None):
        self.agents = agents or self.DEFAULT_AGENTS
        self.current_index = 0

    def get_random(self) -> str:
        """获取随机 UA"""
        return random.choice(self.agents)

    def get_next(self) -> str:
        """按顺序获取下一个 UA"""
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)
        return agent

    def add_agent(self, agent: str) -> None:
        """添加 UA"""
        self.agents.append(agent)


def ua_pool_demo() -> None:
    """UA 池演示"""
    print_section("1. User-Agent 池")

    pool = UserAgentPool()

    print("\n🔀 随机获取 UA:")
    for i in range(3):
        ua = pool.get_random()
        print(f"   {i+1}. {ua[:60]}...")

    print("\n🔄 按顺序获取 UA:")
    for i in range(3):
        ua = pool.get_next()
        print(f"   {i+1}. {ua[:60]}...")


# ============ 代理池管理 ============

class ProxyPool:
    """代理池管理"""

    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.failed_proxies: Dict[str, int] = {}
        self.max_failures = 3

    def load_from_list(self, proxy_list: List[str]) -> None:
        """从列表加载代理"""
        for proxy in proxy_list:
            self.add_proxy(proxy.strip())

    def add_proxy(self, proxy: str) -> None:
        """添加代理"""
        if ':' in proxy:
            host, port = proxy.split(':')
            self.proxies.append({
                'http': f'http://{host}:{port}',
                'https': f'http://{host}:{port}'
            })

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取可用代理"""
        available = [p for p in self.proxies
                     if self.failed_proxies.get(str(p), 0) < self.max_failures]

        if not available:
            return None

        return random.choice(available)

    def mark_failed(self, proxy: Dict[str, str]) -> None:
        """标记代理失败"""
        proxy_str = str(proxy)
        self.failed_proxies[proxy_str] = self.failed_proxies.get(proxy_str, 0) + 1

    def mark_success(self, proxy: Dict[str, str]) -> None:
        """标记代理成功"""
        proxy_str = str(proxy)
        if proxy_str in self.failed_proxies:
            del self.failed_proxies[proxy_str]

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total': len(self.proxies),
            'available': len([p for p in self.proxies
                            if self.failed_proxies.get(str(p), 0) < self.max_failures]),
            'failed': len(self.failed_proxies)
        }


def proxy_pool_demo() -> None:
    """代理池演示"""
    print_section("2. 代理池管理")

    pool = ProxyPool()

    # 加载示例代理
    example_proxies = [
        'proxy1.example.com:8080',
        'proxy2.example.com:8080',
        'proxy3.example.com:8080',
    ]

    pool.load_from_list(example_proxies)

    print(f"\n📊 代理池状态:")
    stats = pool.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n🔄 获取代理:")
    for i in range(5):
        proxy = pool.get_proxy()
        if proxy:
            print(f"   请求 {i+1}: {proxy}")


# ============ 重试机制 ============

class RetryStrategy(ABC):
    """重试策略抽象基类"""

    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """判断是否应该重试"""
        pass

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """获取重试延迟"""
        pass


class ExponentialBackoff(RetryStrategy):
    """指数退避策略"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self.max_retries

    def get_delay(self, attempt: int) -> float:
        return self.base_delay * (2 ** attempt)


class LinearBackoff(RetryStrategy):
    """线性退避策略"""

    def __init__(self, max_retries: int = 3, delay: float = 1.0, increment: float = 0.5):
        self.max_retries = max_retries
        self.delay = delay
        self.increment = increment

    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self.max_retries

    def get_delay(self, attempt: int) -> float:
        return self.delay + (attempt * self.increment)


def retry_demo() -> None:
    """重试机制演示"""
    print_section("3. 重试机制")

    # 指数退避
    print("\n📈 指数退避策略:")
    exponential = ExponentialBackoff(max_retries=5, base_delay=1.0)

    for attempt in range(5):
        delay = exponential.get_delay(attempt)
        print(f"   第 {attempt + 1} 次重试延迟: {delay:.1f} 秒")

    # 线性退避
    print("\n📊 线性退避策略:")
    linear = LinearBackoff(max_retries=5, delay=1.0, increment=0.5)

    for attempt in range(5):
        delay = linear.get_delay(attempt)
        print(f"   第 {attempt + 1} 次重试延迟: {delay:.1f} 秒")


# ============ 完整的反反爬虫类 ============

class SmartSpider:
    """智能爬虫 - 综合反反爬虫策略"""

    def __init__(self,
                 max_retries: int = 3,
                 min_delay: float = 1.0,
                 max_delay: float = 3.0):
        self.session = requests.Session()
        self.ua_pool = UserAgentPool()
        self.proxy_pool = ProxyPool()
        self.retry_strategy = ExponentialBackoff(max_retries=max_retries)
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.request_count = 0

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'User-Agent': self.ua_pool.get_random(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _random_delay(self) -> None:
        """随机延迟"""
        if self.request_count > 0:
            delay = random.uniform(self.min_delay, self.max_delay)
            logger.info(f"⏳ 延迟 {delay:.2f} 秒...")
            time.sleep(delay)

    def fetch(self, url: str, use_proxy: bool = False) -> Optional[requests.Response]:
        """智能请求"""
        for attempt in range(self.retry_strategy.max_retries):
            try:
                # 随机延迟
                self._random_delay()

                # 获取代理
                proxies = None
                if use_proxy:
                    proxies = self.proxy_pool.get_proxy()

                # 发送请求
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    proxies=proxies,
                    timeout=10
                )

                self.request_count += 1

                # 检查状态码
                if response.status_code == 200:
                    if proxies:
                        self.proxy_pool.mark_success(proxies)
                    logger.info(f"✅ 成功: {url}")
                    return response

                elif response.status_code == 403:
                    logger.warning("🚫 403 禁止访问")

                elif response.status_code == 429:
                    wait_time = self.retry_strategy.get_delay(attempt)
                    logger.warning(f"⏳ 429 请求过多，等待 {wait_time:.1f} 秒...")
                    time.sleep(wait_time)

                else:
                    logger.warning(f"⚠️  状态码: {response.status_code}")

            except requests.Timeout:
                logger.warning(f"⏰ 请求超时 (尝试 {attempt + 1}/{self.retry_strategy.max_retries})")

            except requests.ProxyError:
                logger.warning(f"🔌 代理错误 (尝试 {attempt + 1}/{self.retry_strategy.max_retries})")
                if proxies:
                    self.proxy_pool.mark_failed(proxies)

            except requests.RequestException as e:
                logger.error(f"❌ 请求失败 (尝试 {attempt + 1}/{self.retry_strategy.max_retries}): {e}")

            # 重试前等待
            if attempt < self.retry_strategy.max_retries - 1:
                delay = self.retry_strategy.get_delay(attempt)
                logger.info(f"🔄 {delay:.1f} 秒后重试...")
                time.sleep(delay)

        logger.error(f"❌ 最终失败: {url}")
        return None


def smart_spider_demo() -> None:
    """智能爬虫演示"""
    print_section("4. 智能爬虫")

    spider = SmartSpider(max_retries=3, min_delay=0.5, max_delay=1.5)

    test_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/ip",
        "https://httpbin.org/headers",
    ]

    print(f"\n🕷️  使用智能爬虫爬取 {len(test_urls)} 个页面:")

    for url in test_urls:
        response = spider.fetch(url)
        if response:
            print(f"   ✅ {url[:40]}... - {len(response.text)} 字符")


# ============ 反爬虫检测与应对 ============

class AntiCrawlDetector:
    """反爬虫检测器"""

    @staticmethod
    def detect(response: requests.Response) -> List[AntiCrawlType]:
        """检测反爬虫机制"""
        detected = []

        # 检查状态码
        if response.status_code == 403:
            detected.append(AntiCrawlType.IP_BLOCK)

        elif response.status_code == 429:
            detected.append(AntiCrawlType.IP_RATE_LIMIT)

        # 检查内容
        content = response.text.lower()

        if 'captcha' in content or '验证码' in content:
            detected.append(AntiCrawlType.CAPTCHA)

        if 'access denied' in content or 'forbidden' in content:
            detected.append(AntiCrawlType.USER_AGENT_CHECK)

        if 'javascript' in content and 'enable' in content:
            detected.append(AntiCrawlType.JS_CHALLENGE)

        return detected


def detector_demo() -> None:
    """检测器演示"""
    print_section("5. 反爬虫检测")

    # 模拟检测
    print("\n🔍 检测反爬虫机制:")

    # 403 响应
    print("\n   场景1: 收到 403 响应")
    mock_response = type('Response', (), {
        'status_code': 403,
        'text': 'Access Denied'
    })()
    detected = AntiCrawlDetector.detect(mock_response)
    for item in detected:
        print(f"      - {item.value}")

    # 验证码响应
    print("\n   场景2: 页面包含验证码")
    mock_response = type('Response', (), {
        'status_code': 200,
        'text': 'Please complete the captcha to continue'
    })()
    detected = AntiCrawlDetector.detect(mock_response)
    for item in detected:
        print(f"      - {item.value}")


# ============ 应对策略指南 ============

def countermeasures_guide() -> None:
    """应对策略指南"""
    print_section("6. 反爬虫应对策略")

    guide = """
    🛡️  常见反爬虫应对策略:

    1️⃣  User-Agent 检测
       ✅ 随机切换 User-Agent
       ✅ 使用真实的浏览器 UA
       ✅ 保持 UA 与其他头部的协调

    2️⃣  IP 频率限制/封禁
       ✅ 使用代理 IP 池
       ✅ 控制请求频率
       ✅ 分布式爬虫（多机器低频率）

    3️⃣  Cookie 验证
       ✅ 使用 Session 管理 Cookie
       ✅ 先访问首页获取初始 Cookie
       ✅ 保持 Cookie 的时效性

    4️⃣  Referer 验证
       ✅ 设置正确的 Referer
       ✅ 从真实访问流程中获取 Referer

    5️⃣  验证码
       ⚠️  图形验证码: OCR / 打码平台
       ⚠️  滑动验证: 模拟轨迹
       ⚠️  点选验证: 图像识别
       💡 避免触发验证码是最好的策略

    6️⃣  JavaScript 挑战
       ✅ 使用 Selenium/Playwright
       ✅ 分析 JS 逻辑，直接计算

    7️⃣  参数加密
       ✅ 逆向分析 JS 代码
       ✅ 执行加密函数
       ✅ 使用 execjs 执行 JS

    ⚠️  法律和伦理提醒:
       - 遵守 robots.txt
       - 不要对服务器造成压力
       - 尊重数据版权
       - 仅用于学习和研究
    """
    print(guide)


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        ⚔️ 反爬虫对抗进阶                                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    ua_pool_demo()
    proxy_pool_demo()
    retry_demo()
    smart_spider_demo()
    detector_demo()
    countermeasures_guide()

    print_section("完成")
    print("💡 反反爬虫核心原则:")
    print("   1. 🎭 模拟真实用户行为")
    print("   2. ⏳ 控制请求频率")
    print("   3. 🔄 使用重试机制")
    print("   4. 🌐 使用代理 IP")
    print("   5. 🔍 及时检测和调整")
    print("\n📚 练习:")
    print("   1. 实现一个完整的代理池")
    print("   2. 分析一个网站的反爬机制")
    print("   3. 实现指数退避的重试策略")


if __name__ == "__main__":
    main()
