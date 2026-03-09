#!/usr/bin/env python3
"""
工具模块：User-Agent 请求头池

功能：
1. 提供大量真实的 User-Agent
2. 随机选择 User-Agent
3. 支持按浏览器/操作系统筛选
"""

import random
from typing import List, Optional


# User-Agent 池
USER_AGENTS = {
    'chrome': [
        # Windows Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        # Mac Chrome
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Linux Chrome
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ],
    'firefox': [
        # Windows Firefox
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
        # Mac Firefox
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
        # Linux Firefox
        'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    ],
    'safari': [
        # Mac Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        # iOS Safari
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    ],
    'edge': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    ],
    'mobile': [
        # Android Chrome
        'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        # iOS Safari
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    ]
}


class UserAgentPool:
    """User-Agent 池"""

    def __init__(self):
        self._all_agents = []
        for agents in USER_AGENTS.values():
            self._all_agents.extend(agents)

    def get_random(self, browser: Optional[str] = None) -> str:
        """
        获取随机 User-Agent

        Args:
            browser: 指定浏览器类型（chrome/firefox/safari/edge/mobile）
                    None 表示从所有浏览器中随机选择

        Returns:
            User-Agent 字符串
        """
        if browser and browser.lower() in USER_AGENTS:
            return random.choice(USER_AGENTS[browser.lower()])
        return random.choice(self._all_agents)

    def get_chrome(self) -> str:
        """获取 Chrome User-Agent"""
        return self.get_random('chrome')

    def get_firefox(self) -> str:
        """获取 Firefox User-Agent"""
        return self.get_random('firefox')

    def get_safari(self) -> str:
        """获取 Safari User-Agent"""
        return self.get_random('safari')

    def get_mobile(self) -> str:
        """获取移动端 User-Agent"""
        return self.get_random('mobile')


# 默认实例
_default_pool = UserAgentPool()


def get_random_ua(browser: Optional[str] = None) -> str:
    """获取随机 User-Agent（便捷函数）"""
    return _default_pool.get_random(browser)


def get_headers(browser: Optional[str] = None) -> dict:
    """
    获取完整的请求头

    Args:
        browser: 指定浏览器类型

    Returns:
        请求头字典
    """
    return {
        'User-Agent': get_random_ua(browser),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }


# 使用示例
if __name__ == "__main__":
    pool = UserAgentPool()

    print("随机 User-Agent:")
    print(pool.get_random())

    print("\nChrome User-Agent:")
    print(pool.get_chrome())

    print("\nFirefox User-Agent:")
    print(pool.get_firefox())

    print("\n移动端 User-Agent:")
    print(pool.get_mobile())

    print("\n完整请求头:")
    import json
    print(json.dumps(get_headers(), indent=2, ensure_ascii=False))
