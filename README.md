# 🕷️ Python 爬虫教程：从入门到实战

> **课程宗旨**：授人以渔，掌握数据获取的核心技能

---

## 📚 课程简介

想象一下，互联网是一座巨大的海洋，网页就是海洋里的宝藏。爬虫，就是你的寻宝地图和潜水装备。

本课程将带你：
- 理解 Web 的工作原理
- 掌握数据提取的核心技术
- 学会应对各种反爬机制
- 构健壮、高效的爬虫系统

---

## 🎯 学习目标

完成本课程后，你将能够：
- 独立编写爬虫获取网页数据
- 处理复杂的页面结构（动态加载、登录验证）
- 使用异步技术提升爬取效率
- 应对常见的反爬虫机制
- 遵守爬虫伦理和法律法规

## 📋 前置知识

- Python 基础语法（变量、函数、类、模块）
- 基本的 HTML/CSS 了解
- 了解 HTTP 协议（会在课程中讲解）

---

# 📖 基础篇

> 阶段目标：掌握爬虫的基本原理和核心技术

## 第1章 爬虫入门与 HTTP 基础

### 📖 理论知识

**什么是爬虫？**
Web 爬虫（Web Spider）是一种自动浏览万维网的程序，按照一定的规则抓取网络信息。

**HTTP 协议基础**
- **请求方法**：GET（获取）、POST（提交）、PUT（更新）、DELETE（删除）
- **请求头**：User-Agent、Accept、Cookie、Referer 等
- **响应状态码**：200（成功）、403（禁止）、404（未找到）、500（服务器错误）

**网页结构**
- **HTML**：网页的骨架和内容
- **CSS**：网页的样式和布局
- **JavaScript**：网页的交互行为

### 💻 代码示例

```python
# 代码位置: code/01-http-basics.py
import requests

# 发送 GET 请求
response = requests.get('https://example.com')

# 查看响应信息
print(f"状态码: {response.status_code}")
print(f"响应头: {response.headers['Content-Type']}")
print(f"网页内容: {response.text[:200]}")
```

### ✏️ 课后练习

1. 访问 `https://httpbin.org/get`，查看返回的请求头信息
2. 尝试访问一个不存在的页面，观察 404 状态码
3. 使用 `requests.head()` 方法只获取响应头

---

## 第2章 HTML 解析基础 - BeautifulSoup

### 📖 理论知识

**BeautifulSoup 简介**
BeautifulSoup 是一个 Python 库，用于从 HTML 或 XML 文件中提取数据。它创建了一个解析树，可以方便地查找和操作页面元素。

**常用方法**
- `find()`：查找第一个匹配的元素
- `find_all()`：查找所有匹配的元素
- `select()`：使用 CSS 选择器查找元素

**选择器语法**
- 标签选择器：`soup.find('div')`
- 类选择器：`soup.find(class_='content')`
- ID 选择器：`soup.find(id='main')`
- 属性选择器：`soup.find('a', href=True)`

### 💻 代码示例

```python
# 代码位置: code/02-beautifulsoup.py
from bs4 import BeautifulSoup

html = """
<html>
    <body>
        <div class="container">
            <h1 class="title">文章标题</h1>
            <p class="content">这是文章内容</p>
            <a href="/page/1">第一页</a>
            <a href="/page/2">第二页</a>
        </div>
    </body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')

# 查找元素
title = soup.find('h1', class_='title')
print(title.text)

# 查找所有链接
links = soup.find_all('a')
for link in links:
    print(link['href'])
```

### ✏️ 课后练习

1. 爬取一个简单的网页，提取所有的标题（h1-h6）
2. 提取页面中的所有图片链接
3. 使用 CSS 选择器提取特定的元素

---

## 第3章 精准定位 - XPath

### 📖 理论知识

**XPath 简介**
XPath 是一门在 XML 文档中查找信息的语言，同样适用于 HTML 文档。它比 BeautifulSoup 更强大，支持复杂的查询条件。

**XPath 语法**
- `/`：从根节点选择
- `//`：从任意位置选择
- `@`：选择属性
- `[]`：条件筛选
- `text()`：获取文本内容

**常用表达式**
- `//div[@class='content']`：选择 class 为 content 的 div
- `//a/@href`：选择所有 a 标签的 href 属性
- `//li[position()<=3]`：选择前三个 li 元素

### 💻 代码示例

```python
# 代码位置: code/03-xpath.py
from lxml import etree

html = """
<html>
    <body>
        <div class="product-list">
            <div class="product">
                <h3 class="name">iPhone 15</h3>
                <span class="price">6999</span>
            </div>
            <div class="product">
                <h3 class="name">MacBook Pro</h3>
                <span class="price">19999</span>
            </div>
        </div>
    </body>
</html>
"""

tree = etree.HTML(html)

# 提取所有商品名称
names = tree.xpath('//h3[@class="name"]/text()')
prices = tree.xpath('//span[@class="price"]/text()')

for name, price in zip(names, prices):
    print(f"{name}: ¥{price}")
```

### ✏️ 课后练习

1. 使用 XPath 提取一个网页的所有链接
2. 练习使用 XPath 的各种轴（ancestor、following-sibling 等）
3. 对比 BeautifulSoup 和 XPath 的性能差异

---

## 第4章 数据存储

### 📖 理论知识

**常见存储方式**
- **文本文件**：CSV、JSON
- **数据库**：SQLite、MySQL、MongoDB
- **云存储**：AWS S3、阿里云 OSS

**数据格式**
- **CSV**：适合表格数据，Excel 可直接打开
- **JSON**：适合结构化数据，支持嵌套
- **XML**：适合需要严格格式的数据

### 💻 代码示例

```python
# 代码位置: code/04-data-storage.py
import csv
import json

# CSV 存储
data = [
    ['名称', '价格'],
    ['iPhone 15', '6999'],
    ['MacBook Pro', '19999']
]

with open('products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)

# JSON 存储
products = [
    {'name': 'iPhone 15', 'price': 6999},
    {'name': 'MacBook Pro', 'price': 19999}
]

with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)
```

### ✏️ 课后练习

1. 将爬取的数据保存为 CSV 文件
2. 将爬取的数据保存为 JSON 文件
3. 尝试使用 SQLite 数据库存储数据

---

## 🎯 基础篇实战项目：豆瓣电影 Top250

### 项目目标

爬取豆瓣电影 Top250 的电影信息，包括：
- 电影名称
- 评分
- 导演/演员
- 评价人数

### 涉及技术

- requests 发送 HTTP 请求
- BeautifulSoup 解析 HTML
- 数据存储（CSV/JSON）
- 简单的反爬处理

### 代码位置

`code/projects/basics/douban_top250.py`

### 📝 作业要求

1. 完成电影信息的爬取
2. 将数据保存为 CSV 和 JSON 两种格式
3. 添加进度显示
4. 添加错误处理和日志记录

---

# 🚀 进阶篇

> 阶段目标：掌握异步爬虫、Session 管理、反爬应对等进阶技术

## 第5章 请求伪装与反爬基础

### 📖 理论知识

**常见的反爬机制**
- User-Agent 检测
- IP 限制和封禁
- 请求频率限制
- Cookie/Session 验证

**应对策略**
- **请求头伪装**：模拟真实浏览器
- **代理 IP**：使用代理池轮换 IP
- **请求延迟**：控制请求频率
- **Session 管理**：保持登录状态

### 💻 代码示例

```python
# 代码位置: code/05-request-disguise.py
import requests
import time
import random

# 请求头池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
]

def get_headers():
    """随机获取请求头"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

# 使用 Session 保持会话
session = requests.Session()
session.headers.update(get_headers())

# 添加随机延迟
time.sleep(random.uniform(1, 3))
```

### ✏️ 课后练习

1. 编写一个请求头池，随机切换 User-Agent
2. 实现一个简单的请求延迟装饰器
3. 使用 requests.Session 保持登录状态

---

## 第6章 异步爬虫

### 📖 理论知识

**同步 vs 异步**
- **同步（阻塞）**：一个请求完成后才开始下一个
- **异步（非阻塞）**：多个请求同时进行

**异步爬虫的优势**
- 大幅提升爬取速度（3-10倍）
- 更高效地利用网络资源
- 适合 I/O 密集型任务

**核心概念**
- `async/await`：定义和调用异步函数
- `asyncio`：Python 异步编程标准库
- `aiohttp`：异步 HTTP 客户端

### 💻 代码示例

```python
# 代码位置: code/06-async-spider.py
import asyncio
import aiohttp
import time

async def fetch(session, url):
    """异步获取单个页面"""
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [f'https://example.com/page/{i}' for i in range(1, 11)]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# 运行
results = asyncio.run(main())
```

### ✏️ 课后练习

1. 将同步爬虫改写为异步爬虫
2. 实现并发控制（限制同时请求数）
3. 添加超时和重试机制

---

## 第7章 动态网页渲染

### 📖 理论知识

**什么是动态网页？**
页面内容通过 JavaScript 动态加载，初始 HTML 不包含完整数据。

**渲染方式对比**
- **服务端渲染（SSR）**：服务器返回完整 HTML
- **客户端渲染（CSR）**：JavaScript 动态生成内容

**应对方案**
- **Selenium**：模拟真实浏览器
- **Playwright**：新一代浏览器自动化工具
- **API 接口**：直接请求后端 API

### 💻 代码示例

```python
# 代码位置: code/07-dynamic-page.py
from playwright.async_api import async_playwright

async def scrape_dynamic_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 访问页面并等待内容加载
        await page.goto('https://example.com')
        await page.wait_for_selector('.content')

        # 提取数据
        content = await page.text_content('.content')

        await browser.close()
        return content
```

### ✏️ 课后练习

1. 使用 Selenium 爬取一个动态网页
2. 对比 Selenium 和 Playwright 的差异
3. 尝试找到并直接请求后端 API

---

## 🎯 进阶篇实战项目：GitHub Trending + 异步并发

### 项目目标

爬取 GitHub Trending 页面的热门项目信息：
- 项目名称
- 编程语言
- Stars 数量
- 今日增长

### 涉及技术

- 异步爬虫（aiohttp）
- 并发控制
- 数据解析和存储
- 错误处理和重试

### 代码位置

`code/projects/advanced/github_trending.py`

### 📝 作业要求

1. 使用异步方式爬取多页数据
2. 实现并发限制（不超过 5 个并发）
3. 添加完整的错误处理
4. 将数据保存到 SQLite 数据库

---

# ⚔️ 实战篇

> 阶段目标：综合运用所学知识，完成复杂的实战项目

## 第8章 登录与 Cookie 处理

### 📖 理论知识

**登录方式**
- 表单登录：POST 提交账号密码
- Cookie 登录：直接使用已登录的 Cookie
- Token 认证：使用 API Token
- OAuth：第三方授权登录

**Session 管理**
- 自动处理 Cookie
- 保持连接复用
- 提升请求效率

### 💻 代码示例

```python
# 代码位置: code/08-login-cookie.py
import requests

# 使用 Session 自动管理 Cookie
session = requests.Session()

# 登录
login_data = {
    'username': 'your_username',
    'password': 'your_password'
}
session.post('https://example.com/login', data=login_data)

# 后续请求自动带 Cookie
response = session.get('https://example.com/profile')
```

### ✏️ 课后练习

1. 分析一个网站的登录流程
2. 实现自动登录并保持会话
3. 处理 CSRF Token

---

## 第9章 反爬虫对抗进阶

### 📖 理论知识

**高级反爬机制**
- **验证码**：图形验证、滑块验证、点选验证
- **加密参数**：请求参数加密、签名
- **指纹识别**：Canvas 指纹、WebGL 指纹
- **行为检测**：鼠标轨迹、滚动行为

**应对策略**
- **验证码识别**：OCR、打码平台
- **参数破解**：逆向分析 JS 代码
- **浏览器指纹伪装**：使用无头浏览器
- **行为模拟**：模拟人类操作

### 💻 代码示例

```python
# 代码位置: code/09-anti-adv.py
import requests
from fake_useragent import UserAgent

class RobustSpider:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()

    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def fetch_with_retry(self, url, max_retries=3):
        for i in range(max_retries):
            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=10)
                if response.status_code == 200:
                    return response
            except Exception as e:
                print(f"重试 {i+1}/{max_retries}: {e}")
        return None
```

### ✏️ 课后练习

1. 实现一个带重试机制的爬虫
2. 添加代理池支持
3. 处理常见的验证码

---

## 第10章 爬虫框架与分布式

### 📖 理论知识

**Scrapy 框架**
- 强大的爬虫框架
- 内置调度、去重、管道
- 支持中间件扩展

**分布式爬虫**
- 多台机器协同工作
- Redis 作为任务队列
- 去重中心化

### 💻 代码示例

```python
# 代码位置: code/10-scrapy-intro.py
# Scrapy Spider 示例
import scrapy

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://example.com']

    def parse(self, response):
        # 提取数据
        for item in response.css('.item'):
            yield {
                'title': item.css('.title::text').get(),
                'url': item.css('a::attr(href)').get(),
            }

        # 跟踪链接
        next_page = response.css('.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### ✏️ 课后练习

1. 使用 Scrapy 重写之前的爬虫项目
2. 学习 Scrapy 中间件的使用
3. 了解 Scrapy-Redis 分布式爬虫

---

## 🎯 实战篇项目：图片爬虫 + 反爬应对

### 项目目标

构建一个完整的图片爬虫系统：
- 支持批量下载图片
- 自动去重
- 多线程下载
- 应对各种反爬机制

### 涉及技术

- 多线程/多进程
- 图片去重（MD5）
- 断点续传
- 完整的错误处理

### 代码位置

`code/projects/advanced/image_spider/`

### 📝 作业要求

1. 实现多线程图片下载
2. 添加图片去重功能
3. 支持断点续传
4. 完善的日志和错误处理

---

# 📜 爬虫伦理与法律

## 🤔 爬虫伦理

**robots.txt 协议**
- 爬虫的"君子协定"
- 规定哪些可以爬，哪些不可以
- 必须遵守！

**合理使用**
- 不要过度频繁请求
- 不要爬取个人隐私数据
- 不要对服务器造成压力

## ⚖️ 法律法规

**相关法律**
- 《网络安全法》
- 《数据安全法》
- 《个人信息保护法》

**红线不能踩**
- 不要爬取涉及国家安全的数据
- 不要爬取个人隐私信息
- 不要用于非法用途

## ✅ 最佳实践

1. **检查 robots.txt**：遵守网站规定
2. **添加标识**：在 User-Agent 中标明身份
3. **控制频率**：避免对服务器造成压力
4. **数据使用**：尊重数据版权和隐私

---

# 📦 配套资源

## 📁 项目结构

```
python-spider-course/
├── README.md              # 课程文档
├── requirements.txt       # 依赖包
├── .gitignore            # Git 忽略文件
├── code/                 # 代码示例
│   ├── basics/           # 基础篇代码
│   ├── advanced/         # 进阶篇代码
│   ├── projects/         # 实战项目
│   │   ├── basics/       # 基础篇实战
│   │   ├── advanced/     # 进阶篇实战
│   │   └── final/        # 综合实战
│   └── utils/            # 工具函数
└── data/                 # 数据存储目录
```

## 🛠️ 环境配置

```bash
# 克隆项目
git clone https://github.com/your-repo/python-spider-course.git
cd python-spider-course

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 📚 推荐资源

**官方文档**
- [requests](https://docs.python-requests.org/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [lxml](https://lxml.de/)
- [aiohttp](https://docs.aiohttp.org/)
- [Scrapy](https://docs.scrapy.org/)

**推荐书籍**
- 《Python网络数据采集》
- 《Python爬虫开发与项目实战》
- 《Scrapy网络爬虫实战》

**在线资源**
- [Scrapy入门教程](https://scrapy-chs.readthedocs.io/)
- [崔庆才的博客](https://cuiqingcai.com/)

---

# 📝 学习建议

1. **循序渐进**：不要跳过基础篇
2. **动手实践**：每个示例都要亲自运行
3. **举一反三**：尝试用不同方法实现相同功能
4. **关注实战**：理论要结合实际项目
5. **遵守规则**：始终记住爬虫伦理

---

> 🎉 祝你学习愉快，掌握爬虫技能！
>
> 如有问题，欢迎提 Issue 或 PR

---

**课程作者**: Claude Code
**最后更新**: 2026-03
**许可协议**: MIT License
