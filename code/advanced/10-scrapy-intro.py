#!/usr/bin/env python3
"""
第10章：爬虫框架与分布式

本章目标：
1. 了解 Scrapy 框架的基本结构
2. 掌握 Scrapy Spider 的编写
3. 理解分布式爬虫的原理
4. 了解 Scrapy-Redis 的使用

运行方式:
    scrapy runspider 10-scrapy-intro.py

依赖安装:
    pip install scrapy scrapy-redis
"""

import scrapy
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
import logging

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


# ============ Scrapy 基础 Spider ============

class BasicSpider(Spider):
    """基础 Scrapy Spider"""

    name = 'basic_spider'
    start_urls = ['https://httpbin.org/html']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response: Response):
        """解析响应"""
        self.logger.info(f"正在解析: {response.url}")

        # 提取标题
        title = response.css('h1::text').get()
        if title:
            yield {
                'title': title,
                'url': response.url,
            }

        # 提取所有链接
        for link in response.css('a::attr(href)').getall():
            if link and link.startswith('/'):
                full_url = response.urljoin(link)
                yield Request(full_url, callback=self.parse_link)

    def parse_link(self, response: Response):
        """解析链接页面"""
        self.logger.info(f"解析链接: {response.url}")
        yield {
            'url': response.url,
            'status': response.status,
        }


def scrapy_basics_lesson() -> None:
    """Scrapy 基础教程"""
    print_section("1. Scrapy 框架基础")

    lesson = """
    🕷️  Scrapy 框架简介:

    ┌─────────────────────────────────────────────────────┐
    │                  Scrapy 架构                         │
    ├─────────────────────────────────────────────────────┤
    │                                                      │
    │   Engine ←→ Scheduler ←→ Downloader                 │
    │     ↓         ↓              ↓                       │
    │   Spider   Requests     Responses                   │
    │     ↓                                        │       │
    │   Items ←────────────────────────────────────┘       │
    │     ↓                                                │
    │   Item Pipeline (数据处理)                           │
    │     ↓                                                │
    │   Export (数据导出)                                  │
    │                                                      │
    └─────────────────────────────────────────────────────┘

    📦 核心组件:

    1. Engine (引擎)
       - 控制整个框架的数据流
       - 协调各组件工作

    2. Scheduler (调度器)
       - 管理待爬取的请求队列
       - 去重处理

    3. Downloader (下载器)
       - 发送 HTTP 请求
       - 接收响应

    4. Spider (爬虫)
       - 解析网页
       - 提取数据
       - 生成新请求

    5. Item Pipeline (管道)
       - 处理提取的数据
       - 清洗、验证、存储

    6. Middleware (中间件)
       - 请求/响应预处理
       - 扩展框架功能
    """
    print(lesson)


# ============ Scrapy 中间件 ============

class CustomMiddleware:
    """自定义中间件示例"""

    def __init__(self):
        self.request_count = 0

    def process_request(self, request, spider):
        """处理请求"""
        self.request_count += 1
        spider.logger.info(f"中间件处理请求 #{self.request_count}: {request.url}")

        # 可以修改请求
        # request.headers['User-Agent'] = 'Custom UA'

        return None  # 继续处理

    def process_response(self, request, response, spider):
        """处理响应"""
        spider.logger.info(f"中间件处理响应: {response.status}")

        # 可以修改响应
        return response

    def process_exception(self, request, exception, spider):
        """处理异常"""
        spider.logger.error(f"请求异常: {exception}")
        return None  # 继续抛出异常


def middleware_lesson() -> None:
    """中间件教程"""
    print_section("2. Scrapy 中间件")

    lesson = """
    🔧 Scrapy 中间件:

    ┌─────────────────────────────────────────────────────┐
    │              请求/响应处理流程                        │
    ├─────────────────────────────────────────────────────┤
    │                                                      │
    │   Spider                                           │
    │     ↓                                               │
    │   Engine                                           │
    │     ↓                                               │
    │   ↓ Spider Middleware (1-N)                        │
    │     ↓                                               │
    │   ↓ Downloader Middleware (1-N)                    │
    │     ↓                                               │
    │   Downloader (发送请求)                              │
    │     ↓                                               │
    │   ↓ Downloader Middleware (N-1)                    │
    │     ↓                                               │
    │   ↓ Spider Middleware (N-1)                        │
    │     ↓                                               │
    │   Spider (处理响应)                                  │
    │                                                      │
    └─────────────────────────────────────────────────────┘

    📝 常用中间件:

    1. UserAgentMiddleware
       - 随机切换 User-Agent

    2. ProxyMiddleware
       - 使用代理 IP

    3. RetryMiddleware
       - 失败重试

    4. RedirectMiddleware
       - 处理重定向

    🛠️  自定义中间件用途:
       - 添加自定义请求头
       - 实现代理轮换
       - 记录请求日志
       - 修改响应内容
    """
    print(lesson)


# ============ Scrapy Item Pipeline ============

class ProductItem(scrapy.Item):
    """商品 Item"""

    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()


class PriceValidationPipeline:
    """价格验证管道"""

    def process_item(self, item, spider):
        """验证价格"""
        price = item.get('price', 0)

        try:
            price_value = float(str(price).replace('¥', '').replace(',', '').strip())

            if price_value <= 0:
                raise ValueError(f"无效价格: {price}")

            item['price'] = price_value
            spider.logger.info(f"✅ 价格验证通过: {price_value}")

        except (ValueError, AttributeError) as e:
            spider.logger.error(f"❌ 价格验证失败: {e}")
            # 可以选择抛出异常丢弃该 item
            # raise DropItem(f"无效价格: {item.get('url')}")
            item['price'] = 0

        return item


class DuplicateFilterPipeline:
    """去重管道"""

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        """检查是否重复"""
        url = item.get('url')

        if url in self.seen_urls:
            spider.logger.warning(f"⚠️  重复 URL: {url}")
            # raise DropItem(f"重复项目: {url}")
            return item

        self.seen_urls.add(url)
        return item


def pipeline_lesson() -> None:
    """管道教程"""
    print_section("3. Item Pipeline")

    lesson = """
    📊 Item Pipeline 作用:

    ┌─────────────────────────────────────────────────────┐
    │              数据处理流程                             │
    ├─────────────────────────────────────────────────────┤
    │                                                      │
    │   Spider                                            │
    │     ↓ (yield item)                                  │
    │   Item                                              │
    │     ↓                                               │
    │   Pipeline 1 (验证)                                  │
    │     ↓                                               │
    │   Pipeline 2 (清洗)                                  │
    │     ↓                                               │
    │   Pipeline 3 (去重)                                  │
    │     ↓                                               │
    │   Pipeline 4 (存储)                                  │
    │     ↓                                               │
    │   Export (CSV/JSON/Database)                        │
    │                                                      │
    └─────────────────────────────────────────────────────┘

    🛠️  常用 Pipeline 功能:

    1. 数据验证
       - 检查必填字段
       - 验证数据格式
       - 检查数据范围

    2. 数据清洗
       - 去除空白字符
       - 统一日期格式
       - 处理缺失值

    3. 去重
       - URL 去重
       - 内容去重
       - 指纹去重

    4. 数据存储
       - 存入数据库
       - 写入文件
       - 发送到 API

    📝 Pipeline 开发建议:
       - 每个 Pipeline 只做一件事
       - 保持简洁，出错时决定是丢弃还是继续
       - 使用统计信息监控效果
    """
    print(lesson)


# ============ 分布式爬虫原理 ============

def distributed_lesson() -> None:
    """分布式爬虫教程"""
    print_section("4. 分布式爬虫")

    lesson = """
    🏗️  分布式爬虫架构:

    ┌───────────────────────────────────────────────────────┐
    │               分布式爬虫系统                           │
    ├───────────────────────────────────────────────────────┤
    │                                                        │
    │    ┌─────────┐                                        │
    │    │  Redis  │ ← 任务队列 + 去重中心                   │
    │    └────┬────┘                                        │
    │         │                                             │
    │    ┌────┴────────────────────────────┐               │
    │    ↓                                ↓                │
    │ ┌────────┐      ┌────────┐      ┌────────┐          │
    │ │Worker 1│      │Worker 2│      │Worker 3│  ...      │
    │ │        │      │        │      │        │          │
    │ │- 爬取  │      │- 爬取  │      │- 爬取  │          │
    │ │- 解析  │      │- 解析  │      │- 解析  │          │
    │ │- 存储  │      │- 存储  │      │- 存储  │          │
    │ └────────┘      └────────┘      └────────┘          │
    │         ↓              ↓              ↓               │
    │    ┌─────┴──────────────┴──────────────┴─────┐       │
    │    │              Database                   │       │
    │    └────────────────────────────────────────┘       │
    │                                                        │
    └───────────────────────────────────────────────────────┘

    🔑 核心概念:

    1. 任务队列 (Redis List)
       - 存储待爬取的 URL
       - 支持优先级
       - 多 Worker 共享

    2. 去重中心 (Redis Set)
       - 全局 URL 去重
       - 使用指纹或 Hash
       - 避免重复爬取

    3. 数据共享 (Redis Hash/String)
       - 爬取状态
       - 统计信息
       - 配置更新

    🛠️  技术方案:

    方案1: Scrapy-Redis
       - 成熟的解决方案
       - 内置去重和调度
       - 配置简单

    方案2: 自建方案
       - Redis + Scrapy
       - 更灵活的控制
       - 需要更多开发

    ⚙️  分布式要点:

    1. 避免重复
       - 全局去重
       - URL 指纹

    2. 负载均衡
       - 任务分配
       - Worker 健康检查

    3. 故障恢复
       - 断点续爬
       - 失败重试

    4. 性能优化
       - 合理的并发数
       - 带宽限制
       - 存储优化
    """
    print(lesson)


# ============ Scrapy-Redis 示例配置 ============

def scrapy_redis_config() -> None:
    """Scrapy-Redis 配置示例"""
    print_section("5. Scrapy-Redis 配置")

    config = """
    # settings.py 配置

    # 使用 Scrapy-Redis 的调度器
    SCHEDULER = "scrapy_redis.scheduler.Scheduler"

    # 使用 Scrapy-Redis 的去重组件
    DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

    # 在 Redis 中保持 scrapy-redis 用到的各个队列，从而允许暂停和恢复
    SCHEDULER_PERSIST = True

    # Redis 连接配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

    # Redis 编码 (默认 utf-8)
    REDIS_ENCODING = 'utf-8'

    #Spider 代码示例

    from scrapy_redis.spiders import RedisSpider

    class MyRedisSpider(RedisSpider):
        name = 'my_redis_spider'
        redis_key = 'my spider:start_urls'

        def parse(self, response):
            # 解析逻辑
            pass

    # 启动方式:

    # 1. 向 Redis 添加起始 URL
    $ redis-cli
    > lpush "my spider:start_urls" "https://example.com"

    # 2. 启动 Spider (可以从多个机器启动)
    $ scrapy crawl my_redis_spider
    """
    print(config)


# ============ 完整示例 ============

def complete_example() -> None:
    """完整示例"""
    print_section("6. 完整示例")

    example = """
    # 完整的 Scrapy 项目结构

    my_spider/
    ├── scrapy.cfg           # 项目配置
    ├── my_spider/           # 项目目录
    │   ├── __init__.py
    │   ├── items.py         # Item 定义
    │   ├── middlewares.py   # 中间件
    │   ├── pipelines.py     # 管道
    │   ├── settings.py      # 配置
    │   └── spiders/         # Spider 目录
    │       ├── __init__.py
    │       └── example.py   # 爬虫代码
    └── run.py               # 运行脚本

    # items.py
    import scrapy

    class ArticleItem(scrapy.Item):
        title = scrapy.Field()
        url = scrapy.Field()
        content = scrapy.Field()
        author = scrapy.Field()
        publish_time = scrapy.Field()

    # spiders/example.py
    import scrapy
    from my_spider.items import ArticleItem

    class ArticleSpider(scrapy.Spider):
        name = 'articles'
        start_urls = ['https://example.com/articles']

        def parse(self, response):
            # 提取文章列表
            for article in response.css('.article'):
                item = ArticleItem()
                item['title'] = article.css('.title::text').get()
                item['url'] = article.css('a::attr(href)').get()

                # 跟踪详情页
                yield response.follow(item['url'], self.parse_article)

        def parse_article(self, response):
            item = response.meta['item']
            item['content'] = response.css('.content::text').getall()
            item['author'] = response.css('.author::text').get()
            yield item

    # 运行
    scrapy crawl articles -o articles.json
    """
    print(example)


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🏗️  爬虫框架与分布式                                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个教程
    scrapy_basics_lesson()
    middleware_lesson()
    pipeline_lesson()
    distributed_lesson()
    scrapy_redis_config()
    complete_example()

    print_section("完成")
    print("💡 Scrapy 使用建议:")
    print("   1. 🎯 从简单的项目开始")
    print("   2. 🧩 善用中间件和管道")
    print("   3. ⚙️  根据需求调整配置")
    print("   4. 📊 监控爬虫状态")
    print("   5. 🔄 分布式使用 Scrapy-Redis")
    print("\n📚 练习:")
    print("   1. 创建一个完整的 Scrapy 项目")
    print("   2. 编写自定义中间件")
    print("   3. 实现一个简单的分布式爬虫")
    print("\n🔗 相关资源:")
    print("   - 官方文档: https://docs.scrapy.org/")
    print("   - Scrapy-Redis: https://github.com/rmax/scrapy-redis")


if __name__ == "__main__":
    main()
