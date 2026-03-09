#!/usr/bin/env python3
"""
第1章：爬虫入门与 HTTP 基础

本章目标：
1. 理解 HTTP 请求和响应的基本概念
2. 学习使用 requests 库发送请求
3. 掌握查看响应状态、头部和内容的方法

运行方式：python 01-http-basics.py
"""

import requests
import logging
from typing import Optional, Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str) -> None:
    """打印分隔线和标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def basic_request() -> None:
    """基础 HTTP 请求示例"""
    print_section("1. 基础 GET 请求")

    url = "https://example.com"

    try:
        response = requests.get(url, timeout=10)

        # 打印响应信息
        print(f"📡 请求 URL: {url}")
        print(f"✅ 状态码: {response.status_code}")
        print(f"📏 内容长度: {len(response.text)} 字符")
        print(f"🏷️  Content-Type: {response.headers.get('Content-Type')}")

        # 打印前200个字符
        print(f"\n📄 网页内容（前200字符）:")
        print(response.text[:200])

    except requests.RequestException as e:
        logger.error(f"请求失败: {e}")


def request_methods() -> None:
    """不同的 HTTP 方法演示"""
    print_section("2. HTTP 方法演示")

    url = "https://httpbin.org"

    # GET 请求
    print("\n📥 GET 请求:")
    response = requests.get(f"{url}/get", params={"key": "value"})
    print(f"   状态码: {response.status_code}")
    print(f"   请求参数: {response.json().get('args')}")

    # POST 请求
    print("\n📤 POST 请求:")
    response = requests.post(
        f"{url}/post",
        data={"username": "test", "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"   状态码: {response.status_code}")
    print(f"   提交数据: {response.json().get('form')}")


def response_details() -> None:
    """响应详细信息"""
    print_section("3. 响应详细信息")

    url = "https://httpbin.org/headers"

    response = requests.get(url)

    print("\n📋 响应头:")
    for key, value in response.headers.items():
        print(f"   {key}: {value}")

    print("\n📤 请求头（服务器收到的）:")
    request_headers = response.json().get("headers", {})
    for key, value in request_headers.items():
        print(f"   {key}: {value}")


def status_codes() -> None:
    """常见状态码"""
    print_section("4. 常见 HTTP 状态码")

    status_info = {
        200: "✅ OK - 请求成功",
        201: "✅ Created - 资源创建成功",
        301: "➡️  Moved Permanently - 永久重定向",
        302: "➡️  Found - 临时重定向",
        400: "❌ Bad Request - 请求有误",
        401: "❌ Unauthorized - 未授权",
        403: "❌ Forbidden - 禁止访问",
        404: "❌ Not Found - 资源不存在",
        429: "⏳ Too Many Requests - 请求过多",
        500: "❌ Internal Server Error - 服务器错误",
        502: "❌ Bad Gateway - 网关错误",
        503: "❌ Service Unavailable - 服务不可用",
    }

    for code, desc in status_info.items():
        print(f"   {code}: {desc}")


def error_handling() -> None:
    """错误处理示例"""
    print_section("5. 错误处理")

    # 测试各种错误情况
    test_cases = [
        ("不存在的域名", "https://this-domain-does-not-exist-12345.com"),
        ("404 错误", "https://httpbin.org/status/404"),
        ("超时设置", "https://httpbin.org/delay/5"),
    ]

    for name, url in test_cases:
        print(f"\n🔍 测试: {name}")
        print(f"   URL: {url}")

        try:
            if "超时" in name:
                response = requests.get(url, timeout=2)
            else:
                response = requests.get(url, timeout=10)

            if response.status_code >= 400:
                print(f"   ⚠️  HTTP 错误: {response.status_code}")
            else:
                print(f"   ✅ 成功: {response.status_code}")

        except requests.Timeout:
            print(f"   ⏰ 请求超时")
        except requests.ConnectionError:
            print(f"   🔌 连接错误")
        except requests.RequestException as e:
            print(f"   ❌ 请求异常: {type(e).__name__}")


def custom_headers() -> None:
    """自定义请求头"""
    print_section("6. 自定义请求头")

    url = "https://httpbin.org/headers"

    # 自定义请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers)

    print("\n📤 自定义的请求头:")
    for key, value in headers.items():
        print(f"   {key}: {value}")

    print("\n📋 服务器收到的 User-Agent:")
    received_ua = response.json().get("headers", {}).get("User-Agent")
    print(f"   {received_ua}")


def query_parameters() -> None:
    """URL 参数传递"""
    print_section("7. URL 参数")

    url = "https://httpbin.org/get"

    # 方式1：直接在 URL 中拼接
    print("\n📍 方式1: URL 拼接")
    response = requests.get(f"{url}?name=张三&age=25")
    print(f"   参数: {response.json().get('args')}")

    # 方式2：使用 params 参数
    print("\n📍 方式2: params 参数")
    params = {
        "name": "李四",
        "age": 30,
        "city": "北京"
    }
    response = requests.get(url, params=params)
    print(f"   参数: {response.json().get('args')}")
    print(f"   完整 URL: {response.url}")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🕷️ Python 爬虫入门 - HTTP 基础                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    basic_request()
    request_methods()
    response_details()
    status_codes()
    error_handling()
    custom_headers()
    query_parameters()

    print_section("完成")
    print("💡 提示: 尝试修改代码，访问不同的 URL，观察结果变化")
    print("📚 练习:")
    print("   1. 访问 https://httpbin.org/uuid 查看返回的 UUID")
    print("   2. 访问 https://httpbin.org/ip 查看你的 IP 地址")
    print("   3. 使用 requests.head() 只获取响应头")


if __name__ == "__main__":
    main()
