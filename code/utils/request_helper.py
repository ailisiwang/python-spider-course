#!/usr/bin/env python3
"""
工具模块：请求助手

功能：
1. 自动重试机制
2. 随机延迟
3. 请求装饰器
4. Session 管理
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟倍数
        exceptions: 需要重试的异常类型

    Usage:
        @retry(max_retries=3, delay=1)
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries}): {e}. "
                            f"等待 {current_delay:.1f} 秒后重试..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} 失败，已达最大重试次数")

            raise last_exception

        return wrapper
    return decorator


def random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
    """
    随机延迟装饰器

    Args:
        min_delay: 最小延迟（秒）
        max_delay: 最大延迟（秒）

    Usage:
        @random_delay(1, 3)
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RetrySession:
    """带自动重试的 Session"""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[tuple] = None,
        session: Optional[requests.Session] = None
    ):
        """
        初始化 RetrySession

        Args:
            max_retries: 最大重试次数
            backoff_factor: 重试延迟因子
            status_forcelist: 需要重试的HTTP状态码
            session: 自定义 Session 对象
        """
        self.session = session or requests.Session()

        if status_forcelist is None:
            status_forcelist = (500, 502, 503, 504, 429)

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, *args, **kwargs):
        """发送 GET 请求"""
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """发送 POST 请求"""
        return self.session.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        """发送 PUT 请求"""
        return self.session.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """发送 DELETE 请求"""
        return self.session.delete(*args, **kwargs)

    def close(self):
        """关闭 Session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RequestLimiter:
    """请求频率限制器"""

    def __init__(self, requests_per_second: float = 1.0):
        """
        初始化请求频率限制器

        Args:
            requests_per_second: 每秒请求数
        """
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    def wait(self):
        """等待以确保不超过请求频率"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)

        self.last_request_time = time.time()


def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    delay: float = 1.0,
    **kwargs
) -> Optional[requests.Response]:
    """
    带重试的请求函数

    Args:
        url: 请求 URL
        max_retries: 最大重试次数
        delay: 重试延迟
        **kwargs: 传递给 requests.get 的参数

    Returns:
        Response 对象或 None
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30, **kwargs)
            if response.status_code == 200:
                return response
            else:
                logger.warning(f"状态码 {response.status_code}: {url}")

        except requests.Timeout:
            logger.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries}): {url}")
        except requests.RequestException as e:
            logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            time.sleep(delay * (2 ** attempt))  # 指数退避

    return None


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 示例 1：使用装饰器
    @retry(max_retries=3, delay=1)
    def unstable_function():
        import random
        if random.random() < 0.7:
            raise ValueError("随机失败")
        return "成功"

    print("\n=== 测试重试装饰器 ===")
    try:
        result = unstable_function()
        print(f"结果: {result}")
    except Exception as e:
        print(f"最终失败: {e}")

    # 示例 2：使用 RetrySession
    print("\n=== 测试 RetrySession ===")
    with RetrySession(max_retries=2) as session:
        try:
            response = session.get('https://httpbin.org/get')
            print(f"状态码: {response.status_code}")
        except Exception as e:
            print(f"请求失败: {e}")

    # 示例 3：使用请求频率限制
    print("\n=== 测试请求频率限制 ===")
    limiter = RequestLimiter(requests_per_second=2)

    for i in range(3):
        limiter.wait()
        print(f"请求 {i + 1} 发送时间: {time.time():.2f}")
