#!/usr/bin/env python3
"""
第6章：异步爬虫

本章目标：
1. 理解异步编程的概念
2. 掌握 asyncio 和 aiohttp 的使用
3. 学会并发控制和错误处理
4. 对比同步和异步的性能差异

运行方式：python 06-async-spider.py
"""

import asyncio
import aiohttp
import requests
import time
import logging
from typing import List, Optional, Callable, Any
from datetime import datetime

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


# ============ 同步 vs 异步对比 ============

def sync_fetch(urls: List[str]) -> float:
    """同步请求"""
    print("\n🐢 同步爬虫:")
    start = time.time()

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"   ✅ {url[:40]}... - {len(response.text)} 字符")
        except Exception as e:
            print(f"   ❌ {url[:40]}... - {e}")

    elapsed = time.time() - start
    print(f"   ⏱️  总耗时: {elapsed:.2f} 秒")
    return elapsed


async def async_fetch(session: aiohttp.ClientSession, url: str) -> dict:
    """异步请求单个 URL"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            text = await response.text()
            return {
                'url': url,
                'status': response.status,
                'length': len(text),
                'success': True
            }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'success': False
        }


async def async_fetch_all(urls: List[str]) -> float:
    """异步请求所有 URL"""
    print("\n🚀 异步爬虫:")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [async_fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result['success']:
                print(f"   ✅ {result['url'][:40]}... - {result['length']} 字符")
            else:
                print(f"   ❌ {result['url'][:40]}... - {result.get('error', 'Unknown')}")

    elapsed = time.time() - start
    print(f"   ⏱️  总耗时: {elapsed:.2f} 秒")
    return elapsed


def sync_vs_async() -> None:
    """同步 vs 异步对比"""
    print_section("1. 同步 vs 异步性能对比")

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    # 同步请求
    sync_time = sync_fetch(urls)

    # 异步请求
    async_time = asyncio.run(async_fetch_all(urls))

    # 性能对比
    print(f"\n📊 性能对比:")
    print(f"   同步耗时: {sync_time:.2f} 秒")
    print(f"   异步耗时: {async_time:.2f} 秒")
    print(f"   🚀 提升: {sync_time / async_time:.1f}x")


# ============ 并发控制 ============

class AsyncSemaphore:
    """异步并发控制"""

    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> dict:
        """带并发控制的请求"""
        async with self.semaphore:
            logger.info(f"🔓 获取信号量: {url[:40]}")

            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    text = await response.text()
                    logger.info(f"🔓 释放信号量: {url[:40]}")
                    return {
                        'url': url,
                        'status': response.status,
                        'length': len(text),
                        'success': True
                    }
            except Exception as e:
                logger.error(f"❌ 请求失败: {url} - {e}")
                return {
                    'url': url,
                    'error': str(e),
                    'success': False
                }


async def fetch_with_limit(urls: List[str], max_concurrent: int = 3) -> List[dict]:
    """限制并发数的请求"""
    print(f"\n⚙️  并发控制（最大 {max_concurrent} 个并发）")

    limiter = AsyncSemaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [limiter.fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        success_count = sum(1 for r in results if r['success'])
        print(f"   ✅ 成功: {success_count}/{len(urls)}")

        return results


def semaphore_demo() -> None:
    """信号量演示"""
    print_section("2. 并发控制")

    urls = [f"https://httpbin.org/delay/1" for _ in range(10)]

    # 不同并发数测试
    for concurrency in [2, 5, 10]:
        print(f"\n🔢 并发数: {concurrency}")
        start = time.time()
        results = asyncio.run(fetch_with_limit(urls, concurrency))
        elapsed = time.time() - start
        print(f"   ⏱️  耗时: {elapsed:.2f} 秒")


# ============ 超时和重试 ============

class AsyncFetcher:
    """带超时和重试的异步获取器"""

    def __init__(self,
                 max_retries: int = 3,
                 timeout: int = 10,
                 retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.timeout = timeout
        self.retry_delay = retry_delay

    async def fetch_with_retry(self, session: aiohttp.ClientSession, url: str) -> Optional[dict]:
        """带重试的请求"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    text = await response.text()

                    if response.status == 200:
                        logger.info(f"✅ 成功: {url}")
                        return {
                            'url': url,
                            'status': response.status,
                            'text': text,
                            'success': True
                        }
                    else:
                        logger.warning(f"⚠️  状态码 {response.status}: {url}")

            except asyncio.TimeoutError:
                last_error = "超时"
                logger.warning(f"⏰ 请求超时 (尝试 {attempt + 1}/{self.max_retries}): {url}")

            except aiohttp.ClientError as e:
                last_error = str(e)
                logger.warning(f"❌ 请求错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")

            # 重试前等待
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        logger.error(f"❌ 最终失败: {url}")
        return {
            'url': url,
            'error': last_error,
            'success': False
        }

    async def fetch_all(self, urls: List[str]) -> List[dict]:
        """获取所有 URL"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_with_retry(session, url) for url in urls]
            return await asyncio.gather(*tasks)


def retry_demo() -> None:
    """重试演示"""
    print_section("3. 超时和重试")

    fetcher = AsyncFetcher(max_retries=3, timeout=5, retry_delay=1.0)

    urls = [
        "https://httpbin.org/delay/2",  # 正常
        "https://httpbin.org/status/200",  # 正常
        "https://httpbin.org/delay/10",  # 会超时
        "https://this-url-does-not-exist-12345.com",  # 不存在的域名
    ]

    print(f"\n🔄 测试重试机制:")
    results = asyncio.run(fetcher.fetch_all(urls))

    for result in results:
        if result['success']:
            print(f"   ✅ {result['url'][:40]}...")
        else:
            print(f"   ❌ {result['url'][:40]}... - {result.get('error', 'Unknown')}")


# ============ 进度显示 ============

class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()

    def update(self, success: bool):
        """更新进度"""
        if success:
            self.completed += 1
        else:
            self.failed += 1

        self.print_progress()

    def print_progress(self):
        """打印进度"""
        elapsed = time.time() - self.start_time
        progress = (self.completed + self.failed) / self.total * 100

        print(f"\r   📊 进度: {self.completed + self.failed}/{self.total} "
              f"({progress:.1f}%) | ✅ {self.completed} | ❌ {self.failed} | "
              f"⏱️  {elapsed:.1f}s", end='')

        if self.completed + self.failed >= self.total:
            print()  # 换行


async def fetch_with_progress(urls: List[str]) -> List[dict]:
    """带进度显示的异步请求"""
    print(f"\n📊 带进度显示的请求 ({len(urls)} 个 URL)")

    tracker = ProgressTracker(len(urls))

    async def fetch_and_track(session: aiohttp.ClientSession, url: str) -> dict:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                text = await response.text()
                tracker.update(True)
                return {'url': url, 'success': True, 'length': len(text)}
        except Exception as e:
            tracker.update(False)
            return {'url': url, 'success': False, 'error': str(e)}

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_track(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        return results


def progress_demo() -> None:
    """进度演示"""
    print_section("4. 进度显示")

    urls = [f"https://httpbin.org/delay/1" for _ in range(20)]

    results = asyncio.run(fetch_with_progress(urls))

    success_count = sum(1 for r in results if r['success'])
    print(f"   ✅ 完成: {success_count}/{len(urls)} 成功")


# ============ 异步上下文管理器 ============

class AsyncSpider:
    """异步爬虫类"""

    def __init__(self,
                 max_concurrent: int = 5,
                 max_retries: int = 3,
                 timeout: int = 10):
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore: Optional[asyncio.Semaphore] = None

    async def __aenter__(self):
        """进入上下文"""
        self.session = aiohttp.ClientSession()
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> Optional[dict]:
        """获取单个 URL"""
        if not self.session or not self.semaphore:
            raise RuntimeError("请使用 async with 语句")

        async with self.semaphore:
            for attempt in range(self.max_retries):
                try:
                    async with self.session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        text = await response.text()

                        if response.status == 200:
                            return {
                                'url': url,
                                'text': text,
                                'status': response.status,
                                'success': True
                            }

                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                    continue

                except Exception as e:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(1)
                    continue

            return {'url': url, 'success': False}

    async def fetch_all(self, urls: List[str]) -> List[dict]:
        """获取所有 URL"""
        tasks = [self.fetch(url) for url in urls]
        return await asyncio.gather(*tasks)


def async_spider_demo() -> None:
    """异步爬虫类演示"""
    print_section("5. 异步爬虫类")

    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/headers",
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
    ]

    async def main():
        async with AsyncSpider(max_concurrent=3, max_retries=2) as spider:
            print(f"\n🕷️  使用 AsyncSpider 爬取 {len(urls)} 个页面:")
            results = await spider.fetch_all(urls)

            for result in results:
                if result['success']:
                    print(f"   ✅ {result['url'][:40]}...")
                else:
                    print(f"   ❌ {result['url'][:40]}...")

    asyncio.run(main())


# ============ 批量处理 ============

async def batch_process(items: List[Any],
                       processor: Callable,
                       batch_size: int = 10) -> List[Any]:
    """批量处理"""
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        print(f"\n📦 处理批次 {i // batch_size + 1}: {len(batch)} 项")

        batch_results = await asyncio.gather(*[processor(item) for item in batch])
        results.extend(batch_results)

    return results


def batch_demo() -> None:
    """批量处理演示"""
    print_section("6. 批量处理")

    async def process_url(url: str) -> dict:
        """处理单个 URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    text = await response.text()
                    return {'url': url, 'length': len(text), 'success': True}
        except Exception as e:
            return {'url': url, 'error': str(e), 'success': False}

    urls = [f"https://httpbin.org/delay/1" for _ in range(15)]

    print(f"\n🔄 批量处理 {len(urls)} 个 URL（批次大小 5）:")
    results = asyncio.run(batch_process(urls, process_url, batch_size=5))

    success_count = sum(1 for r in results if r['success'])
    print(f"\n   ✅ 总计: {success_count}/{len(urls)} 成功")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🚀 异步爬虫 - 高效并发处理                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    sync_vs_async()
    semaphore_demo()
    retry_demo()
    progress_demo()
    async_spider_demo()
    batch_demo()

    print_section("完成")
    print("💡 异步爬虫最佳实践:")
    print("   1. 🎯 使用 Semaphore 控制并发数")
    print("   2. ⏰ 设置合理的超时时间")
    print("   3. 🔄 实现重试机制处理临时错误")
    print("   4. 📊 添加进度显示")
    print("   5. 🔍 使用上下文管理器管理 Session")
    print("   6. 📦 大批量数据使用分批处理")
    print("\n📚 练习:")
    print("   1. 将之前的同步爬虫改写为异步版本")
    print("   2. 实现一个带进度条的异步爬虫")
    print("   3. 对比不同并发数的性能表现")


if __name__ == "__main__":
    main()
