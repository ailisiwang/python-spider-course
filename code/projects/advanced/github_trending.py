#!/usr/bin/env python3
"""
进阶篇实战项目：GitHub Trending + 异步爬虫

项目目标：
1. 使用异步方式爬取 GitHub Trending 页面
2. 实现并发控制
3. 添加错误处理和重试机制
4. 将数据保存到 SQLite 数据库
5. 实现定时爬取和数据对比

GitHub Trending: https://github.com/trending

运行方式：python github_trending.py
"""

import asyncio
import aiohttp
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/github_trending.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ 数据模型 ============

@dataclass
class Repo:
    """GitHub 仓库数据模型"""
    name: str
    url: str
    description: str
    language: str
    stars: str
    forks: str
    stars_today: str
    avatar: str
    author: str
    crawled_at: str


# ============ 数据库管理 ============

class Database:
    """数据库管理类"""

    def __init__(self, db_path: str = 'data/github_trending.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    description TEXT,
                    language TEXT,
                    stars INTEGER,
                    forks INTEGER,
                    stars_today INTEGER,
                    avatar TEXT,
                    author TEXT,
                    crawled_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_url ON repos(url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_crawled_at ON repos(crawled_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stars_today ON repos(stars_today)")

            conn.commit()

    def save_repos(self, repos: List[Repo]) -> int:
        """保存仓库数据"""
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            for repo in repos:
                try:
                    # 清理 stars 数据
                    stars_str = repo.stars.replace('k', '000').replace(',', '')
                    stars_today_str = repo.stars_today.replace('k', '000').replace(',', '').replace('stars today', '').replace('+', '').strip()
                    forks_str = repo.forks.replace('k', '000').replace(',', '')

                    conn.execute("""
                        INSERT OR REPLACE INTO repos
                        (name, url, description, language, stars, forks, stars_today, avatar, author, crawled_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        repo.name,
                        repo.url,
                        repo.description,
                        repo.language,
                        int(float(stars_str) if stars_str else 0),
                        int(float(forks_str) if forks_str else 0),
                        int(float(stars_today_str) if stars_today_str else 0),
                        repo.avatar,
                        repo.author,
                        repo.crawled_at
                    ))
                    count += 1
                except Exception as e:
                    logger.error(f"保存失败 {repo.name}: {e}")

            conn.commit()

        logger.info(f"保存了 {count} 个仓库到数据库")
        return count

    def get_top_repos(self, limit: int = 10) -> List[Dict]:
        """获取今日增长最多的仓库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT name, url, description, language, stars_today
                FROM repos
                WHERE crawled_at >= date('now')
                ORDER BY stars_today DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_language_stats(self) -> List[Dict]:
        """获取语言统计"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT language,
                       COUNT(*) as count,
                       AVG(stars_today) as avg_stars_today
                FROM repos
                WHERE language IS NOT NULL AND language != ''
                GROUP BY language
                ORDER BY count DESC
                LIMIT 10
            """)

            return [dict(row) for row in cursor.fetchall()]


# ============ 异步爬虫 ============

class GitHubTrendingSpider:
    """GitHub Trending 异步爬虫"""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.base_url = "https://github.com/trending"
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # 语言列表
        self.languages = ['', 'python', 'javascript', 'java', 'go', 'rust', 'cpp', 'typescript']

    async def fetch_page(self, session: aiohttp.ClientSession, language: str = '') -> str:
        """获取单页内容"""
        async with self.semaphore:
            url = self.base_url
            if language:
                url = f"{self.base_url}/{language}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            try:
                logger.info(f"获取: {url}")

                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"状态码: {response.status}")
                        return ''

            except asyncio.TimeoutError:
                logger.error(f"超时: {url}")
                return ''
            except Exception as e:
                logger.error(f"请求失败 {url}: {e}")
                return ''

    def parse_repos(self, html: str, language: str = '') -> List[Repo]:
        """解析仓库列表"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_='Box-row')

        repos = []
        for article in articles:
            try:
                # 仓库名称和链接
                link = article.find('a', class_='Link')
                if not link:
                    continue

                full_name = link.text.strip()
                url = f"https://github.com{link['href']}"

                # 描述
                desc_elem = article.find('p', class_='col-9')
                description = desc_elem.text.strip() if desc_elem else ''

                # 语言
                language_elem = article.find('span', itemprop='programmingLanguage')
                repo_language = language_elem.text.strip() if language_elem else language or 'Unknown'

                # Stars 和 Forks
                stars_elem = article.find('a', href=lambda x: x and '/stargazers' in x)
                forks_elem = article.find('a', href=lambda x: x and '/forks' in x)
                stars_today_elem = article.find('span', class_='d-inline-block float-sm-right')

                stars = stars_elem.text.strip() if stars_elem else '0'
                forks = forks_elem.text.strip() if forks_elem else '0'
                stars_today = stars_today_elem.text.strip() if stars_today_elem else '0'

                # 头像和作者
                avatar_elem = article.find('img', class_='avatar')
                avatar = avatar_elem['src'] if avatar_elem else ''
                author = full_name.split('/')[0] if '/' in full_name else ''

                repo = Repo(
                    name=full_name,
                    url=url,
                    description=description,
                    language=repo_language,
                    stars=stars,
                    forks=forks,
                    stars_today=stars_today,
                    avatar=avatar,
                    author=author,
                    crawled_at=datetime.now().isoformat()
                )

                repos.append(repo)

            except Exception as e:
                logger.error(f"解析仓库失败: {e}")

        return repos

    async def crawl_all(self) -> List[Repo]:
        """爬取所有语言的趋势"""
        all_repos = []

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_page(session, lang) for lang in self.languages]

            print("\n" + "=" * 60)
            print("  🚀 开始爬取 GitHub Trending")
            print("=" * 60)

            for i, future in enumerate(asyncio.as_completed(tasks)):
                lang = self.languages[tasks.index(future)]
                html = await future

                if html:
                    repos = self.parse_repos(html, lang)
                    all_repos.extend(repos)
                    print(f"   ✅ {lang or 'All':15} - {len(repos)} 个仓库")

        return all_repos


# ============ 报告生成 ============

class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def print_summary(repos: List[Repo], db: Database):
        """打印汇总信息"""
        print("\n" + "=" * 60)
        print("  📊 GitHub Trending 报告")
        print("=" * 60)

        print(f"\n   爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   仓库总数: {len(repos)}")

        # 按语言统计
        lang_count = {}
        for repo in repos:
            lang = repo.language
            lang_count[lang] = lang_count.get(lang, 0) + 1

        print(f"\n   📚 语言分布:")
        for lang, count in sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {lang:15} {count:3} 个")

        # Top 10 今日增长
        top_repos = sorted(repos, key=lambda x: float(x.stars_today.replace('k', '000').replace(',', '').replace('stars today', '').replace('+', '').strip() or 0), reverse=True)[:10]

        print(f"\n   🔥 今日增长 Top 10:")
        for i, repo in enumerate(top_repos, 1):
            print(f"      {i:2}. {repo.name:40} ⭐ +{repo.stars_today}")

        # 保存详细报告
        ReportGenerator.save_json_report(repos)

    @staticmethod
    def save_json_report(repos: List[Repo]):
        """保存 JSON 报告"""
        report = {
            'crawled_at': datetime.now().isoformat(),
            'total_count': len(repos),
            'repos': [asdict(repo) for repo in repos]
        }

        filepath = Path('data/github_trending_report.json')

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"报告已保存: {filepath}")


# ============ 主程序 ============

async def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🚀 GitHub Trending 异步爬虫                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 创建目录
    Path('data').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)

    # 创建爬虫
    spider = GitHubTrendingSpider(max_concurrent=3)

    # 爬取数据
    repos = await spider.crawl_all()

    # 去重（同一仓库可能在多个语言列表中出现）
    seen_urls = set()
    unique_repos = []
    for repo in repos:
        if repo.url not in seen_urls:
            seen_urls.add(repo.url)
            unique_repos.append(repo)

    print(f"\n   📊 去重后: {len(unique_repos)} 个唯一仓库")

    # 保存到数据库
    db = Database()
    saved_count = db.save_repos(unique_repos)

    # 生成报告
    ReportGenerator.print_summary(unique_repos, db)

    print("\n" + "=" * 60)
    print("  ✅ 完成！")
    print("=" * 60)
    print("\n📁 数据文件:")
    print("   - 数据库: data/github_trending.db")
    print("   - 报告: data/github_trending_report.json")
    print("   - 日志: logs/github_trending.log")


if __name__ == "__main__":
    asyncio.run(main())
