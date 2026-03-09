#!/usr/bin/env python3
"""
第10关：反爬对抗 - 实战案例
反反爬虫实战
"""

import requests
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class AntiCrawlSpider:
    """反反爬虫 Spider"""
    
    def __init__(self):
        self.session = self._create_session()
        self.proxies = []  # 代理池
        
    def _create_session(self):
        """创建带重试机制的 Session"""
        session = requests.Session()
        
        # 设置重试策略（指数退避）
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def get_headers(self):
        """随机生成请求头"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def fetch(self, url, use_proxy=False):
        """带反反爬措施的请求"""
        
        headers = self.get_headers()
        
        # 随机延迟（模拟人类）
        time.sleep(random.uniform(0.5, 2.0))
        
        # 选择代理
        proxies = None
        if use_proxy and self.proxies:
            proxies = random.choice(self.proxies)
        
        try:
            response = self.session.get(
                url, 
                headers=headers,
                proxies=proxies,
                timeout=10
            )
            
            # 检查状态码
            if response.status_code == 403:
                print(f"   🚫 403 被禁止! 换代理...")
                # 切换代理重试
            elif response.status_code == 429:
                print(f"   ⏳ 429 请求过多! 等待更久...")
                time.sleep(10)
                
            return response
            
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            return None

# 使用演示
print("=" * 40)
print("⚔️ 反反爬虫实战")
print("=" * 40)

spider = AntiCrawlSpider()

# 爬取示例
urls = [
    "https://httpbin.org/get",
    "https://httpbin.org/ip",
    "https://httpbin.org/headers"
]

for url in urls:
    print(f"\n🔄 爬取: {url}")
    # response = spider.fetch(url)
    print(f"   ✅ 模拟请求已发送")
    time.sleep(1)

print("\n🛡️ 反爬应对策略总结:")
print("   1. User-Agent 轮换")
print("   2. 请求延迟（随机 1-3 秒）")
print("   3. 代理池（多个 IP 轮换）")
print("   4. 失败重试（指数退避）")
print("   5. 分布式（多机器低频率）")
