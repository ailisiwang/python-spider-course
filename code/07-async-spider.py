#!/usr/bin/env python3
"""
第7关：加速快艇 - 异步爬虫
异步爬虫，就像快艇一样快！
"""

import asyncio
import aiohttp
import time
import requests  # 同步版本对比用

async def fetch(session, url):
    """异步获取一个网页"""
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1", 
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]
    
    print("=" * 40)
    print("🚀 异步爬虫 vs 同步爬虫")
    print("=" * 40)
    
    # 🐢 同步版本（串行）
    print("\n🐢 同步版本（一个个来）:")
    start = time.time()
    for url in urls:
        requests.get(url)
    sync_time = time.time() - start
    print(f"   ⏱️ 耗时: {sync_time:.2f}秒")
    
    # 🚀 异步版本（并行）
    print("\n🚀 异步版本（一起上）:")
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        await asyncio.gather(*tasks)
    async_time = time.time() - start
    print(f"   ⏱️ 耗时: {async_time:.2f}秒")
    
    # 对比
    print(f"\n📊 提升: {sync_time/async_time:.1f}倍!")
    
    # 完整示例：爬取多个页面
    print("\n" + "=" * 40)
    print("📖 异步爬虫实战")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # 爬取多个 URL
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json", 
            "https://httpbin.org/headers"
        ]
        
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        print(f"\n✅ 成功爬取 {len(results)} 个页面:")
        for i, (url, result) in enumerate(zip(urls, results), 1):
            print(f"   {i}. {url[:30]}... ({len(result)} 字符)")

if __name__ == "__main__":
    asyncio.run(main())
