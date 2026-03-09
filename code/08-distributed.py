#!/usr/bin/env python3
"""
第8关：分布式舰队 - 规模爬取
分布式爬虫架构演示
"""

import hashlib
from collections import deque
import time

class DistributedSpiderDemo:
    """分布式爬虫演示（单机版模拟）"""
    
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.visited = set()  # 已访问 URL
        self.queue = deque()  # 待爬队列
        self.stats = {"success": 0, "failed": 0}
    
    def url_hash(self, url):
        """URL 去重（用 MD5）"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def add_url(self, url):
        """添加 URL（自动去重）"""
        url_hash = self.url_hash(url)
        if url_hash not in self.visited:
            self.queue.append(url)
            self.visited.add(url_hash)
            return True
        return False
    
    def crawl(self, url):
        """模拟爬取一个页面"""
        # 模拟网络请求
        time.sleep(0.1)
        
        # 模拟提取新链接
        new_urls = [
            f"http://example.com/page{i}" 
            for i in range(3)
        ]
        
        return new_urls

# 使用示例
print("=" * 40)
print("🏗️ 分布式爬虫演示")
print("=" * 40)

# 模拟 3 个爬虫 worker
workers = [
    DistributedSpiderDemo(f"worker-{i+1}") 
    for i in range(3)
]

# 添加初始 URL
seed_url = "http://example.com"
for worker in workers:
    worker.add_url(seed_url)

print(f"\n📥 初始 URL: {seed_url}")
print(f"👥 爬虫数量: {len(workers)}")

# 模拟爬取几轮
for round_num in range(3):
    print(f"\n🔄 第 {round_num + 1} 轮:")
    
    new_urls = []
    for worker in workers:
        if worker.queue:
            url = worker.queue.popleft()
            print(f"   {worker.worker_id} 爬取: {url}")
            
            # 模拟提取新链接
            found = worker.crawl(url)
            new_urls.extend(found)
            worker.stats["success"] += 1
    
    # 分配新链接给各个 worker（负载均衡）
    for i, url in enumerate(new_urls):
        workers[i % len(workers)].add_url(url)

print("\n📊 最终统计:")
for worker in workers:
    print(f"   {worker.worker_id}: 成功 {worker.stats['success']} 次")
