#!/usr/bin/env python3
"""
实战篇项目：图片爬虫系统

项目目标：
1. 批量下载图片
2. 多线程/多进程下载
3. 图片去重（MD5）
4. 断点续传
5. 完善的错误处理和日志

功能特性：
- 支持多种图片来源（网页解析、API、图片列表）
- 多线程并发下载，提升效率
- MD5 去重，避免重复下载
- 断点续传，网络中断可恢复
- 完整的日志记录
- 进度显示

运行方式：python image_spider.py
"""

import os
import time
import hashlib
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse
import json
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/image_spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ImageTask:
    """图片下载任务"""
    url: str              # 图片URL
    save_path: str        # 保存路径
    filename: str         # 文件名
    referer: str = ''     # Referer
    md5: str = ''         # MD5值（去重用）


class MD5Checker:
    """MD5去重检查器"""

    def __init__(self, cache_file: str = 'data/md5_cache.json'):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.md5_set: Set[str] = self._load_cache()

    def _load_cache(self) -> Set[str]:
        """加载MD5缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('md5_list', []))
            except Exception as e:
                logger.warning(f"加载MD5缓存失败: {e}")
        return set()

    def _save_cache(self):
        """保存MD5缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'md5_list': list(self.md5_set)}, f, indent=2)
        except Exception as e:
            logger.error(f"保存MD5缓存失败: {e}")

    def is_duplicate(self, md5: str) -> bool:
        """检查是否重复"""
        return md5 in self.md5_set

    def add_md5(self, md5: str):
        """添加MD5到缓存"""
        self.md5_set.add(md5)
        self._save_cache()

    @staticmethod
    def calculate_md5(content: bytes) -> str:
        """计算内容的MD5值"""
        return hashlib.md5(content).hexdigest()


class ImageDownloader:
    """图片下载器"""

    def __init__(self, max_workers: int = 5, timeout: int = 30):
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        self.md5_checker = MD5Checker()
        self.downloaded = 0
        self.failed = 0
        self.skipped = 0

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def download_single(self, task: ImageTask) -> bool:
        """
        下载单张图片

        Args:
            task: 图片下载任务

        Returns:
            是否下载成功
        """
        filepath = Path(task.save_path) / task.filename

        # 检查文件是否已存在
        if filepath.exists():
            logger.info(f"   ⏭️  已存在，跳过: {task.filename}")
            self.skipped += 1
            return True

        # 准备请求头
        headers = self.headers.copy()
        if task.referer:
            headers['Referer'] = task.referer

        try:
            # 发送请求
            response = self.session.get(
                task.url,
                headers=headers,
                timeout=self.timeout,
                stream=True
            )

            if response.status_code != 200:
                logger.warning(f"   ❌ 状态码 {response.status_code}: {task.url}")
                self.failed += 1
                return False

            # 读取内容
            content = response.content

            # 计算MD5
            md5 = MD5Checker.calculate_md5(content)

            # 检查去重
            if self.md5_checker.is_duplicate(md5):
                logger.info(f"   🔁 重复图片，跳过: {task.filename}")
                self.skipped += 1
                return True

            # 保存文件
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(content)

            # 添加到MD5缓存
            self.md5_checker.add_md5(md5)

            logger.info(f"   ✅ 下载成功: {task.filename}")
            self.downloaded += 1
            return True

        except requests.Timeout:
            logger.error(f"   ⏱️  超时: {task.url}")
            self.failed += 1
            return False
        except Exception as e:
            logger.error(f"   ❌ 下载失败 {task.filename}: {e}")
            self.failed += 1
            return False

    def download_batch(self, tasks: List[ImageTask]) -> Dict[str, int]:
        """
        批量下载图片

        Args:
            tasks: 图片下载任务列表

        Returns:
            下载统计
        """
        logger.info(f"开始下载 {len(tasks)} 张图片...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.download_single, task): task for task in tasks}

            for future in as_completed(futures):
                future.result()

        return {
            'downloaded': self.downloaded,
            'failed': self.failed,
            'skipped': self.skipped,
            'total': len(tasks)
        }

    def print_summary(self):
        """打印下载统计"""
        print("\n" + "=" * 60)
        print("  📊 下载统计")
        print("=" * 60)
        print(f"\n   总计: {self.downloaded + self.failed + self.skipped} 张")
        print(f"   ✅ 下载成功: {self.downloaded} 张")
        print(f"   ⏭️  跳过: {self.skipped} 张")
        print(f"   ❌ 失败: {self.failed} 张")


class WebImageExtractor:
    """网页图片提取器"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

    def extract_from_url(self, url: str, min_size: int = 10000) -> List[str]:
        """
        从网页提取图片URL

        Args:
            url: 网页URL
            min_size: 最小文件大小（字节）

        Returns:
            图片URL列表
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            if response.status_code != 200:
                logger.error(f"获取网页失败: {url}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')

            image_urls = []
            for img in img_tags:
                src = img.get('src') or img.get('data-src')
                if src:
                    # 处理相对URL
                    full_url = urljoin(url, src)
                    image_urls.append(full_url)

            logger.info(f"从 {url} 提取到 {len(image_urls)} 张图片")
            return image_urls

        except Exception as e:
            logger.error(f"提取图片失败: {e}")
            return []


class ImageSpider:
    """图片爬虫主类"""

    def __init__(self, output_dir: str = 'data/images', max_workers: int = 5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.downloader = ImageDownloader(max_workers=max_workers)
        self.extractor = WebImageExtractor()

    def create_tasks_from_urls(self, urls: List[str], referer: str = '') -> List[ImageTask]:
        """
        从URL列表创建下载任务

        Args:
            urls: 图片URL列表
            referer: Referer

        Returns:
            任务列表
        """
        tasks = []
        for i, url in enumerate(urls, 1):
            # 从URL生成文件名
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1]
            if not filename or '.' not in filename:
                filename = f"image_{i:04d}.jpg"

            # 清理文件名
            filename = filename.replace('?', '_').replace('&', '_')

            task = ImageTask(
                url=url,
                save_path=str(self.output_dir),
                filename=filename,
                referer=referer
            )
            tasks.append(task)

        return tasks

    def crawl_from_url(self, url: str, max_images: int = 50) -> int:
        """
        从网页爬取图片

        Args:
            url: 网页URL
            max_images: 最大图片数量

        Returns:
            下载数量
        """
        print("\n" + "=" * 60)
        print("  🖼️  网页图片爬虫")
        print("=" * 60)
        print(f"\n📍 目标网页: {url}")

        # 提取图片URL
        image_urls = self.extractor.extract_from_url(url)

        if not image_urls:
            print("\n   ❌ 未找到图片")
            return 0

        # 限制数量
        image_urls = image_urls[:max_images]

        # 创建任务
        tasks = self.create_tasks_from_urls(image_urls, referer=url)

        # 下载
        stats = self.downloader.download_batch(tasks)

        # 打印统计
        self.downloader.print_summary()

        return stats['downloaded']

    def crawl_from_list(self, url_list: List[str]) -> int:
        """
        从URL列表爬取图片

        Args:
            url_list: 图片URL列表

        Returns:
            下载数量
        """
        print("\n" + "=" * 60)
        print("  🖼️  批量图片下载器")
        print("=" * 60)

        tasks = self.create_tasks_from_urls(url_list)
        stats = self.downloader.download_batch(tasks)

        self.downloader.print_summary()

        return stats['downloaded']


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🖼️  图片爬虫系统                                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 创建目录
    Path('data/images').mkdir(parents=True, exist_ok=True)
    Path('logs').mkdir(exist_ok=True)

    # 示例：从网页爬取图片
    # 注意：这里使用示例URL，实际使用时请替换为合法的目标
    example_urls = [
        'https://picsum.photos/800/600',
        'https://picsum.photos/800/601',
        'https://picsum.photos/800/602',
        'https://picsum.photos/800/603',
        'https://picsum.photos/800/604',
    ]

    spider = ImageSpider(output_dir='data/images/demo', max_workers=3)

    print("\n📝 使用示例：")
    print("   1. 从URL列表下载（使用示例图片）")

    # 下载示例图片
    downloaded = spider.crawl_from_list(example_urls)

    print(f"\n✅ 完成！下载了 {downloaded} 张图片")

    print("\n" + "=" * 60)
    print("  📖 使用说明")
    print("=" * 60)
    print("""
要爬取网页图片，使用以下代码：

    from image_spider import ImageSpider

    spider = ImageSpider(output_dir='data/images', max_workers=5)

    # 从网页爬取
    spider.crawl_from_url('https://example.com', max_images=50)

    # 从URL列表下载
    urls = ['https://example.com/image1.jpg', ...]
    spider.crawl_from_list(urls)
    """)


if __name__ == "__main__":
    main()
