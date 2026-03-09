#!/usr/bin/env python3
"""
基础篇实战项目：豆瓣电影 Top250

项目目标：
1. 爬取豆瓣电影 Top250 的电影信息
2. 提取电影名称、评分、导演、演员等信息
3. 将数据保存为 CSV 和 JSON 格式
4. 添加进度显示和错误处理

豆瓣电影 Top250: https://movie.douban.com/top250

运行方式：python douban_top250.py
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/douban.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DoubanTop250Spider:
    """豆瓣电影 Top250 爬虫"""

    def __init__(self):
        self.base_url = "https://movie.douban.com/top250"
        self.session = requests.Session()
        self.movies: List[Dict] = []

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # 确保目录存在
        Path('data').mkdir(exist_ok=True)
        Path('logs').mkdir(exist_ok=True)

    def fetch_page(self, page_num: int) -> Optional[str]:
        """获取指定页的 HTML"""
        params = {
            'start': page_num * 25,
            'filter': ''
        }

        try:
            logger.info(f"正在获取第 {page_num + 1} 页...")
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                # 随机延迟，避免请求过快
                time.sleep(1)
                return response.text
            else:
                logger.warning(f"状态码: {response.status_code}")
                return None

        except requests.Timeout:
            logger.error("请求超时")
            return None
        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None

    def parse_movie(self, movie_div) -> Optional[Dict]:
        """解析单个电影信息"""
        try:
            movie = {}

            # 电影排名
            movie['rank'] = movie_div.find('em', class_='').text

            # 电影详情页链接
            info_div = movie_div.find('div', class_='info')
            link = info_div.find('a')
            movie['url'] = link['href']

            # 电影标题（可能有中英文）
            titles = link.find_all('span', class_='title')
            movie['title'] = titles[0].text
            movie['title_en'] = titles[1].text if len(titles) > 1 else ''

            # 电影评分
            rating_num = info_div.find('span', class_='rating_num')
            movie['rating'] = float(rating_num.text) if rating_num else 0

            # 评价人数
            people_num = info_div.find('div', class_='star').find_all('span')[-1]
            movie['rating_people'] = people_num.text.replace('人评价', '')

            # 一句话评价
            quote = info_div.find('span', class_='inq')
            movie['quote'] = quote.text if quote else ''

            # 电影详情（导演、主演等）
            movie_info = info_div.find('div', class_='bd').p.text.strip()
            lines = movie_info.split('\n')
            if len(lines) > 0:
                # 导演主演信息
                info_text = lines[0].strip()
                # 移除导演/主演标签，只保留名字
                movie['info'] = info_text

            return movie

        except Exception as e:
            logger.error(f"解析电影失败: {e}")
            return None

    def parse_page(self, html: str) -> List[Dict]:
        """解析一页的电影信息"""
        soup = BeautifulSoup(html, 'html.parser')
        movie_divs = soup.find_all('div', class_='item')

        movies = []
        for movie_div in movie_divs:
            movie = self.parse_movie(movie_div)
            if movie:
                movies.append(movie)
                print(f"   ✅ [{movie['rank']}] {movie['title']} - {movie['rating']}")

        return movies

    def run(self) -> List[Dict]:
        """运行爬虫"""
        print("\n" + "=" * 60)
        print("  🎬 豆瓣电影 Top250 爬虫")
        print("=" * 60)

        logger.info("开始爬取豆瓣电影 Top250...")

        for page in range(10):  # 共 10 页，每页 25 部
            print(f"\n📄 第 {page + 1}/10 页:")

            html = self.fetch_page(page)
            if not html:
                logger.warning(f"第 {page + 1} 页获取失败，跳过")
                continue

            movies = self.parse_page(html)
            self.movies.extend(movies)
            logger.info(f"第 {page + 1} 页解析完成，获取 {len(movies)} 部电影")

        logger.info(f"爬取完成！共获取 {len(self.movies)} 部电影")
        return self.movies

    def save_csv(self, filename: str = 'data/douban_top250.csv'):
        """保存为 CSV 文件"""
        if not self.movies:
            logger.warning("没有数据可保存")
            return

        filepath = Path(filename)

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['rank', 'title', 'title_en', 'rating', 'rating_people', 'quote', 'info', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self.movies)

        logger.info(f"CSV 文件已保存: {filepath}")

    def save_json(self, filename: str = 'data/douban_top250.json'):
        """保存为 JSON 文件"""
        if not self.movies:
            logger.warning("没有数据可保存")
            return

        filepath = Path(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.movies, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON 文件已保存: {filepath}")

    def print_summary(self):
        """打印统计信息"""
        if not self.movies:
            return

        print("\n" + "=" * 60)
        print("  📊 爬取结果统计")
        print("=" * 60)

        print(f"\n   总计: {len(self.movies)} 部电影")

        # 评分统计
        ratings = [m['rating'] for m in self.movies]
        print(f"\n   📈 评分统计:")
        print(f"      最高分: {max(ratings):.1f}")
        print(f"      最低分: {min(ratings):.1f}")
        print(f"      平均分: {sum(ratings) / len(ratings):.2f}")

        # Top 10
        print(f"\n   🏆 Top 10:")
        for i, movie in enumerate(self.movies[:10], 1):
            print(f"      {i}. {movie['title']} - {movie['rating']} - {movie['quote'][:30]}...")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🎬 豆瓣电影 Top250 爬虫                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 创建爬虫实例
    spider = DoubanTop250Spider()

    # 运行爬虫
    spider.run()

    # 保存数据
    print("\n💾 保存数据...")
    spider.save_csv()
    spider.save_json()

    # 打印统计
    spider.print_summary()

    print("\n" + "=" * 60)
    print("  ✅ 完成！")
    print("=" * 60)
    print("\n📁 数据文件:")
    print("   - CSV: data/douban_top250.csv")
    print("   - JSON: data/douban_top250.json")
    print("   - 日志: logs/douban.log")


if __name__ == "__main__":
    main()
