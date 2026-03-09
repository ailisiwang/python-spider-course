#!/usr/bin/env python3
"""
综合实战项目：多源新闻聚合爬虫

项目目标：
1. 综合运用课程所有知识点
2. 爬取多个新闻源的数据
3. 使用异步并发提升效率
4. 数据持久化到数据库
5. 完整的错误处理和日志
6. 数据去重和更新检测

涉及技术：
- 异步爬虫 (aiohttp)
- HTML 解析 (BeautifulSoup/XPath)
- 数据存储 (SQLite)
- 请求伪装 (User-Agent/Headers)
- 并发控制 (Semaphore)
- 错误处理和重试
- 日志记录
- 进度显示

数据源（示例）：
- 使用 httpbin.org 作为演示源

运行方式：python news_aggregator.py
"""

import asyncio
import aiohttp
import sqlite3
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# 尝试导入 BeautifulSoup
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logging.warning("BeautifulSoup 未安装，HTML 解析功能将受限")

# 配置日志
def setup_logger(name: str, log_file: str) -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if not logger.handlers:
        # 文件处理器
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)

        # 控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


# 创建目录
Path('data').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)

# 初始化日志
logger = setup_logger('NewsAggregator', 'logs/news_aggregator.log')


# ============ 数据模型 ============

class NewsSource(Enum):
    """新闻来源枚举"""
    DEMO = "demo_source"
    SOURCE_A = "source_a"
    SOURCE_B = "source_b"


@dataclass
class NewsItem:
    """新闻条目数据模型"""
    title: str                    # 标题
    url: str                      # 链接
    content: str                  # 内容
    source: str                   # 来源
    category: str                 # 分类
    publish_time: str             # 发布时间
    author: str = ""              # 作者
    tags: List[str] = None        # 标签
    crawled_at: str = ""          # 爬取时间

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.crawled_at:
            self.crawled_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['tags'] = json.dumps(self.tags)  # 标签转 JSON 字符串
        return data

    def get_hash(self) -> str:
        """获取唯一标识（用于去重）"""
        content = f"{self.url}_{self.title}"
        return hashlib.md5(content.encode()).hexdigest()


# ============ 数据库管理 ============

class Database:
    """数据库管理类"""

    def __init__(self, db_path: str = 'data/news_aggregator.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            # 创建新闻表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    content TEXT,
                    source TEXT,
                    category TEXT,
                    publish_time TEXT,
                    author TEXT,
                    tags TEXT,
                    crawled_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON news(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON news(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_crawled_at ON news(crawled_at)")

            # 创建爬取日志表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    status TEXT,
                    items_count INTEGER,
                    error_message TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            conn.commit()
            logger.info(f"数据库初始化完成: {self.db_path}")

    def save_news(self, items: List[NewsItem]) -> int:
        """保存新闻条目"""
        saved_count = 0
        updated_count = 0

        with sqlite3.connect(self.db_path) as conn:
            for item in items:
                try:
                    data = item.to_dict()
                    conn.execute("""
                        INSERT OR REPLACE INTO news
                        (title, url, content, source, category, publish_time, author, tags, crawled_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        data['title'],
                        data['url'],
                        data['content'],
                        data['source'],
                        data['category'],
                        data['publish_time'],
                        data['author'],
                        data['tags'],
                        data['crawled_at']
                    ))

                    # 判断是新增还是更新
                    cursor = conn.execute(
                        "SELECT changes() FROM news WHERE url = ?",
                        (data['url'],)
                    )
                    if cursor.fetchone()[0] == 0:
                        updated_count += 1
                    else:
                        saved_count += 1

                except sqlite3.IntegrityError:
                    logger.debug(f"重复URL，跳过: {item.url}")
                except Exception as e:
                    logger.error(f"保存失败: {e}")

            conn.commit()

        logger.info(f"保存完成 - 新增: {saved_count}, 更新: {updated_count}")
        return saved_count + updated_count

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # 总数
            total = conn.execute("SELECT COUNT(*) as count FROM news").fetchone()['count']

            # 按来源统计
            by_source = conn.execute("""
                SELECT source, COUNT(*) as count
                FROM news
                GROUP BY source
            """).fetchall()

            # 按分类统计
            by_category = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM news
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()

            # 最新爬取时间
            latest = conn.execute("""
                SELECT MAX(crawled_at) as latest FROM news
            """).fetchone()['latest']

            return {
                'total': total,
                'by_source': {row['source']: row['count'] for row in by_source},
                'by_category': {row['category']: row['count'] for row in by_category},
                'latest_crawl': latest
            }

    def log_crawl(self, source: str, status: str, count: int, error: str = None, start_time: datetime = None):
        """记录爬取日志"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO crawl_logs (source, status, items_count, error_message, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                source,
                status,
                count,
                error,
                start_time.isoformat() if start_time else None,
                datetime.now().isoformat()
            ))
            conn.commit()


# ============ 爬虫基类 ============

class BaseCrawler:
    """爬虫基类"""

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.headers = self._get_headers()

    def _get_headers(self) -> Dict:
        """获取请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"[{self.name}] 状态码: {response.status} - {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"[{self.name}] 请求超时: {url}")
            return None
        except Exception as e:
            logger.error(f"[{self.name}] 请求失败: {url} - {e}")
            return None

    def parse(self, html: str) -> List[NewsItem]:
        """解析页面内容（子类实现）"""
        raise NotImplementedError

    async def crawl(self, session: aiohttp.ClientSession) -> List[NewsItem]:
        """执行爬取（子类实现）"""
        raise NotImplementedError


# ============ 演示爬虫 ============

class DemoCrawler(BaseCrawler):
    """演示用爬虫（使用 httpbin.org）"""

    def __init__(self):
        super().__init__("Demo Source", "https://httpbin.org")

    async def crawl(self, session: aiohttp.ClientSession) -> List[NewsItem]:
        """爬取演示数据"""
        logger.info(f"[{self.name}] 开始爬取...")

        items = []

        # 获取演示数据
        html = await self.fetch(session, f"{self.base_url}/html")
        if html:
            # 解析演示 HTML
            if BeautifulSoup:
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('h1')
                title_text = title.text if title else "Demo Page"

                # 创建演示新闻条目
                item = NewsItem(
                    title=f"[{self.name}] {title_text}",
                    url=f"{self.base_url}/html",
                    content=f"演示内容 - 爬取时间: {datetime.now().isoformat()}",
                    source=self.name,
                    category="演示",
                    publish_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    author="Demo Bot",
                    tags=["demo", "test"]
                )
                items.append(item)

        # 添加一些模拟数据
        for i in range(5):
            item = NewsItem(
                title=f"[{self.name}] 演示新闻 {i+1}",
                url=f"{self.base_url}/demo/{i+1}",
                content=f"这是第 {i+1} 条演示新闻内容。\n包含多行文本用于测试存储功能。",
                source=self.name,
                    category="演示分类" if i % 2 == 0 else "其他",
                publish_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                author=f"作者 {i+1}",
                tags=[f"tag{i}", "demo"]
            )
            items.append(item)

        logger.info(f"[{self.name}] 爬取完成，获取 {len(items)} 条")
        return items


# ============ 新闻聚合器 ============

class NewsAggregator:
    """新闻聚合器"""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.crawlers: List[BaseCrawler] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.db = Database()

    def add_crawler(self, crawler: BaseCrawler):
        """添加爬虫"""
        self.crawlers.append(crawler)
        logger.info(f"添加爬虫: {crawler.name}")

    async def crawl_single(self, session: aiohttp.ClientSession, crawler: BaseCrawler) -> List[NewsItem]:
        """爬取单个来源"""
        async with self.semaphore:
            start_time = datetime.now()
            logger.info(f"开始爬取: {crawler.name}")

            try:
                items = await crawler.crawl(session)

                # 记录日志
                self.db.log_crawl(
                    source=crawler.name,
                    status="success",
                    count=len(items),
                    start_time=start_time
                )

                return items

            except Exception as e:
                logger.error(f"爬取失败: {crawler.name} - {e}")
                self.db.log_crawl(
                    source=crawler.name,
                    status="error",
                    count=0,
                    error=str(e),
                    start_time=start_time
                )
                return []

    async def run(self) -> List[NewsItem]:
        """运行所有爬虫"""
        if not self.crawlers:
            logger.warning("没有配置爬虫")
            return []

        logger.info(f"开始运行新闻聚合器，共 {len(self.crawlers)} 个来源")

        all_items = []

        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self.crawl_single(session, crawler) for crawler in self.crawlers]
            results = await asyncio.gather(*tasks)

            for items in results:
                all_items.extend(items)

        # 保存到数据库
        if all_items:
            saved = self.db.save_news(all_items)
            logger.info(f"共保存 {saved} 条新闻到数据库")

        return all_items

    def print_report(self):
        """打印统计报告"""
        stats = self.db.get_stats()

        print("\n" + "=" * 60)
        print("  📊 新闻聚合报告")
        print("=" * 60)

        print(f"\n   总新闻数: {stats['total']}")
        print(f"   最新更新: {stats['latest_crawl'] or '暂无'}")

        if stats['by_source']:
            print(f"\n   📰 按来源统计:")
            for source, count in stats['by_source'].items():
                print(f"      {source}: {count}")

        if stats['by_category']:
            print(f"\n   📂 按分类统计:")
            for category, count in list(stats['by_category'].items())[:5]:
                print(f"      {category}: {count}")


# ============ 主程序 ============

async def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       📰 多源新闻聚合爬虫系统                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    start_time = time.time()

    # 创建聚合器
    aggregator = NewsAggregator(max_concurrent=3)

    # 添加爬虫（这里使用演示爬虫）
    # 实际使用时，可以添加真实的新闻源爬虫
    aggregator.add_crawler(DemoCrawler())

    # 运行爬取
    print("\n🚀 开始爬取新闻...")
    items = await aggregator.run()

    # 打印报告
    aggregator.print_report()

    # 显示部分新闻
    if items:
        print(f"\n   📝 最新 {min(5, len(items))} 条:")
        for item in items[:5]:
            print(f"      • {item.title}")
            print(f"        来源: {item.source} | 时间: {item.publish_time}")

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  ✅ 完成！")
    print("=" * 60)
    print(f"\n   耗时: {elapsed:.2f} 秒")
    print(f"   获取: {len(items)} 条新闻")
    print("\n📁 数据文件:")
    print("   - 数据库: data/news_aggregator.db")
    print("   - 日志: logs/news_aggregator.log")

    # 导出 JSON
    export_file = Path('data/news_export.json')
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump({
            'export_time': datetime.now().isoformat(),
            'total': len(items),
            'news': [item.to_dict() for item in items]
        }, f, ensure_ascii=False, indent=2)
    print(f"   - 导出: {export_file}")


if __name__ == "__main__":
    asyncio.run(main())
