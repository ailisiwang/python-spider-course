#!/usr/bin/env python3
"""
第4章：数据存储

本章目标：
1. 掌握常见的数据存储格式（CSV、JSON）
2. 学会使用 SQLite 数据库
3. 了解数据存储的最佳实践

运行方式：python 04-data-storage.py
"""

import csv
import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict
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


# 示例数据
SAMPLE_PRODUCTS = [
    {
        'id': 1,
        'name': 'iPhone 15 Pro',
        'brand': 'Apple',
        'price': 7999,
        'category': '手机',
        'description': 'A17 Pro 芯片，钛金属边框',
        'in_stock': True,
        'tags': ['5G', '旗舰', '新品']
    },
    {
        'id': 2,
        'name': 'MacBook Pro 14寸',
        'brand': 'Apple',
        'price': 14999,
        'category': '电脑',
        'description': 'M3 Max 芯片，专业性能',
        'in_stock': True,
        'tags': ['笔记本', '专业', '高性能']
    },
    {
        'id': 3,
        'name': '华为 Mate 60 Pro',
        'brand': '华为',
        'price': 6999,
        'category': '手机',
        'description': '卫星通信，超光变摄像头',
        'in_stock': False,
        'tags': ['5G', '旗舰', '卫星通信']
    },
    {
        'id': 4,
        'name': 'iPad Air 5',
        'brand': 'Apple',
        'price': 4799,
        'category': '平板',
        'description': 'M1 芯片，全面屏设计',
        'in_stock': True,
        'tags': ['平板', '轻薄', '高性价比']
    },
]


# ============ CSV 存储和读取 ============

def save_to_csv(data: List[Dict], filename: str) -> None:
    """保存数据到 CSV 文件"""
    print(f"\n💾 保存到 CSV: {filename}")

    # 确保目录存在
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        # 处理 tags 列表，转换为字符串
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'name', 'brand', 'price', 'category',
            'description', 'in_stock', 'tags'
        ])

        writer.writeheader()

        for item in data:
            row = item.copy()
            row['tags'] = json.dumps(row['tags'], ensure_ascii=False)
            writer.writerow(row)

    print(f"   ✅ 已保存 {len(data)} 条记录")


def load_from_csv(filename: str) -> List[Dict]:
    """从 CSV 文件读取数据"""
    print(f"\n📂 从 CSV 读取: {filename}")

    data = []
    filepath = Path(filename)

    if not filepath.exists():
        print(f"   ⚠️  文件不存在")
        return data

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 恢复 tags 列表
            row['tags'] = json.loads(row['tags'])
            row['price'] = int(row['price'])
            row['in_stock'] = row['in_stock'] == 'True'
            data.append(row)

    print(f"   ✅ 已读取 {len(data)} 条记录")
    return data


def csv_advanced_usage() -> None:
    """CSV 高级用法"""
    print_section("1. CSV 高级用法")

    filename = 'data/products.csv'

    # 写入数据
    save_to_csv(SAMPLE_PRODUCTS, filename)

    # 读取数据
    data = load_from_csv(filename)

    print(f"\n📊 读取的数据:")
    for item in data[:2]:
        print(f"   📦 {item['name']} - ¥{item['price']}")


# ============ JSON 存储和读取 ============

def save_to_json(data, filename: str, indent: int = 2) -> None:
    """保存数据到 JSON 文件"""
    print(f"\n💾 保存到 JSON: {filename}")

    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

    print(f"   ✅ 已保存 {len(data) if isinstance(data, list) else 1} 项")


def load_from_json(filename: str):
    """从 JSON 文件读取数据"""
    print(f"\n📂 从 JSON 读取: {filename}")

    filepath = Path(filename)

    if not filepath.exists():
        print(f"   ⚠️  文件不存在")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"   ✅ 已读取数据")
    return data


def json_advanced_usage() -> None:
    """JSON 高级用法"""
    print_section("2. JSON 高级用法")

    filename = 'data/products.json'

    # 保存列表数据
    save_to_json(SAMPLE_PRODUCTS, filename)

    # 保存嵌套数据结构
    nested_data = {
        'metadata': {
            'total': len(SAMPLE_PRODUCTS),
            'category': '电子产品',
            'updated_at': datetime.now().isoformat()
        },
        'products': SAMPLE_PRODUCTS
    }

    save_to_json(nested_data, 'data/products_nested.json')

    # 读取并解析
    loaded = load_from_json(filename)
    print(f"\n📊 解析后的数据:")
    print(f"   商品数量: {len(loaded)}")
    print(f"   第一个商品: {loaded[0]['name']}")


# ============ SQLite 数据库 ============

class ProductDatabase:
    """商品数据库管理类"""

    def __init__(self, db_path: str = 'data/products.db'):
        self.db_path = db_path
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    brand TEXT,
                    price REAL,
                    category TEXT,
                    description TEXT,
                    in_stock INTEGER,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category
                ON products(category)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_price
                ON products(price)
            """)

            conn.commit()

    def insert_product(self, product: Dict) -> int:
        """插入单个商品"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO products
                (name, brand, price, category, description, in_stock, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                product['name'],
                product['brand'],
                product['price'],
                product['category'],
                product['description'],
                1 if product['in_stock'] else 0,
                json.dumps(product['tags'], ensure_ascii=False)
            ))
            conn.commit()
            return cursor.lastrowid

    def insert_products(self, products: List[Dict]) -> int:
        """批量插入商品"""
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            for product in products:
                conn.execute("""
                    INSERT INTO products
                    (name, brand, price, category, description, in_stock, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['name'],
                    product['brand'],
                    product['price'],
                    product['category'],
                    product['description'],
                    1 if product['in_stock'] else 0,
                    json.dumps(product['tags'], ensure_ascii=False)
                ))
                count += 1
            conn.commit()
        return count

    def get_all_products(self) -> List[Dict]:
        """获取所有商品"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM products ORDER BY id")
            rows = cursor.fetchall()

            products = []
            for row in rows:
                product = dict(row)
                product['in_stock'] = bool(product['in_stock'])
                product['tags'] = json.loads(product['tags'])
                products.append(product)

            return products

    def get_by_category(self, category: str) -> List[Dict]:
        """按分类获取商品"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM products WHERE category = ?",
                (category,)
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """按价格区间获取商品"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM products WHERE price BETWEEN ? AND ?",
                (min_price, max_price)
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def update_product(self, product_id: int, updates: Dict) -> bool:
        """更新商品信息"""
        set_clauses = []
        values = []

        for key, value in updates.items():
            if key == 'tags':
                value = json.dumps(value, ensure_ascii=False)
            elif key == 'in_stock':
                value = 1 if value else 0

            set_clauses.append(f"{key} = ?")
            values.append(value)

        values.append(product_id)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"UPDATE products SET {', '.join(set_clauses)} WHERE id = ?",
                values
            )
            conn.commit()
            return conn.total_changes > 0

    def delete_product(self, product_id: int) -> bool:
        """删除商品"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return conn.total_changes > 0

    def search_products(self, keyword: str) -> List[Dict]:
        """搜索商品（按名称或描述）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?",
                (f'%{keyword}%', f'%{keyword}%')
            )
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(DISTINCT category) as categories,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price
                FROM products
            """)
            row = cursor.fetchone()

            return {
                'total': row[0],
                'categories': row[1],
                'avg_price': round(row[2], 2) if row[2] else 0,
                'min_price': row[3],
                'max_price': row[4]
            }


def sqlite_demo() -> None:
    """SQLite 数据库演示"""
    print_section("3. SQLite 数据库")

    # 创建数据库实例
    db = ProductDatabase()

    # 插入数据
    print(f"\n💾 插入商品数据...")
    count = db.insert_products(SAMPLE_PRODUCTS)
    print(f"   ✅ 插入 {count} 条记录")

    # 查询所有商品
    print(f"\n📂 查询所有商品:")
    products = db.get_all_products()
    for p in products:
        stock = "✅ 有货" if p['in_stock'] else "❌ 缺货"
        print(f"   📦 {p['name']} - ¥{p['price']} {stock}")

    # 按分类查询
    print(f"\n📱 查询手机分类:")
    phones = db.get_by_category('手机')
    for p in phones:
        print(f"   📱 {p['name']}")

    # 价格区间查询
    print(f"\n💰 查询 5000-10000 元的商品:")
    mid_range = db.get_by_price_range(5000, 10000)
    for p in mid_range:
        print(f"   📦 {p['name']} - ¥{p['price']}")

    # 搜索商品
    print(f"\n🔍 搜索 'Pro':")
    results = db.search_products('Pro')
    for p in results:
        print(f"   📦 {p['name']}")

    # 更新商品
    print(f"\n✏️  更新商品库存...")
    db.update_product(3, {'in_stock': True})
    print(f"   ✅ 已更新")

    # 统计信息
    print(f"\n📊 统计信息:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


# ============ 数据格式对比 ============

def compare_formats() -> None:
    """对比不同存储格式"""
    print_section("4. 数据格式对比")

    comparison = """
    ┌─────────┬──────────────┬──────────────┬──────────────┐
    │  特性   │     CSV      │     JSON     │   SQLite     │
    ├─────────┼──────────────┼──────────────┼──────────────┤
    │ 可读性  │     ✅ 高    │     ✅ 高    │     ⚠️ 中    │
    │ 结构支持│    ❌ 扁平   │    ✅ 嵌套   │    ✅ 关联   │
    │ 查询能力│    ❌ 无     │    ❌ 无     │    ✅ SQL    │
    │ 文件大小│    ✅ 小     │    ⚠️ 中     │    ⚠️ 大     │
    │ 写入速度│    ✅ 快     │    ✅ 快     │    ⚠️ 慢     │
    │ 并发支持│    ❌ 无     │    ❌ 无     │    ✅ 有     │
    │ 适用场景│ 表格数据导出 │ 配置/API数据 │ 持久化存储  │
    └─────────┴──────────────┴──────────────┴──────────────┘
    """
    print(comparison)

    print("💡 选择建议:")
    print("   📊 CSV - 适合简单的表格数据，需要用 Excel 打开")
    print("   📋 JSON - 适合配置文件、API 数据交换")
    print("   🗄️  SQLite - 适合需要查询、更新的持久化存储")


# ============ 实用工具函数 ============

def export_to_csv_with_encoding(data: List[Dict], filename: str) -> None:
    """导出 CSV 并处理编码问题"""
    print(f"\n💾 导出 CSV（多种编码）")

    # UTF-8 with BOM（Excel 可正确识别中文）
    filename_utf8 = filename.replace('.csv', '_utf8.csv')
    with open(filename_utf8, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"   ✅ UTF-8: {filename_utf8}")

    # GBK（兼容老版本 Excel）
    filename_gbk = filename.replace('.csv', '_gbk.csv')
    try:
        with open(filename_gbk, 'w', newline='', encoding='gbk') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"   ✅ GBK: {filename_gbk}")
    except UnicodeEncodeError as e:
        print(f"   ⚠️  GBK 编码失败: {e}")


def append_to_csv(data: List[Dict], filename: str) -> None:
    """追加数据到现有 CSV 文件"""
    print(f"\n📝 追加数据到 CSV")

    filepath = Path(filename)

    # 检查文件是否存在
    file_exists = filepath.exists()

    with open(filepath, 'a', newline='', encoding='utf-8-sig') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())

            if not file_exists:
                writer.writeheader()

            writer.writerows(data)

    print(f"   ✅ 追加了 {len(data)} 条记录")


def validate_csv(filename: str) -> bool:
    """验证 CSV 文件格式"""
    print(f"\n🔍 验证 CSV 文件")

    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            # 尝试解析
            reader = csv.DictReader(f)
            rows = list(reader)

            print(f"   ✅ 文件格式正确")
            print(f"   📊 行数: {len(rows)}")
            print(f"   🔢 列数: {len(rows[0].keys()) if rows else 0}")

            return True

    except Exception as e:
        print(f"   ❌ 文件格式错误: {e}")
        return False


def utilities_demo() -> None:
    """实用工具演示"""
    print_section("5. 实用工具函数")

    # 简化数据用于演示
    simple_data = [
        {'name': '商品1', 'price': 100, 'stock': 10},
        {'name': '商品2', 'price': 200, 'stock': 20},
    ]

    # 导出不同编码
    export_to_csv_with_encoding(simple_data, 'data/export_test.csv')

    # 追加数据
    append_to_csv(simple_data, 'data/products_append.csv')
    append_to_csv(simple_data, 'data/products_append.csv')

    # 验证 CSV
    validate_csv('data/products_append.csv')


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🕷️ 数据存储 - CSV、JSON、SQLite                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    csv_advanced_usage()
    json_advanced_usage()
    sqlite_demo()
    compare_formats()
    utilities_demo()

    print_section("完成")
    print("💡 数据存储选择指南:")
    print("   1. 临时数据、需要 Excel 打开 → CSV")
    print("   2. 配置文件、API 交互 → JSON")
    print("   3. 需要查询、更新、大量数据 → SQLite/MySQL")
    print("\n📚 练习:")
    print("   1. 爬取一个网站的数据，分别用 CSV 和 JSON 保存")
    print("   2. 使用 SQLite 存储数据并实现简单的查询功能")
    print("   3. 对比三种方式的存储大小和读写速度")


if __name__ == "__main__":
    main()
