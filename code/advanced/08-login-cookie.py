#!/usr/bin/env python3
"""
第8章：登录与 Cookie 处理

本章目标：
1. 理解常见的登录方式
2. 掌握 Session 和 Cookie 的使用
3. 学会处理 CSRF Token
4. 了解 OAuth 认证

运行方式：python 08-login-cookie.py
"""

import requests
import time
import json
import logging
from typing import Dict, Optional, List
from urllib.parse import urljoin

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


# ============ Session 管理基础 ============

class SessionManager:
    """会话管理器 - 自动管理 Cookie"""

    def __init__(self):
        self.session = requests.Session()
        self.is_logged_in = False

    def get(self, url: str, **kwargs) -> requests.Response:
        """发送 GET 请求"""
        response = self.session.get(url, **kwargs)
        logger.info(f"GET {url} - {response.status_code}")
        return response

    def post(self, url: str, **kwargs) -> requests.Response:
        """发送 POST 请求"""
        response = self.session.post(url, **kwargs)
        logger.info(f"POST {url} - {response.status_code}")
        return response

    def print_cookies(self) -> None:
        """打印当前 Cookies"""
        print("\n🍪 当前 Cookies:")
        for cookie in self.session.cookies:
            print(f"   {cookie.name}: {cookie.value}")

    def save_cookies(self, filename: str) -> None:
        """保存 Cookies 到文件"""
        import http.cookiejar

        cookie_jar = http.cookiejar.LWPCookieJar(filename)
        cookie_jar.set_cookie(self.session.cookies.copy())
        cookie_jar.save()

        print(f"\n💾 Cookies 已保存到: {filename}")

    def load_cookies(self, filename: str) -> bool:
        """从文件加载 Cookies"""
        import http.cookiejar

        try:
            cookie_jar = http.cookiejar.LWPCookieJar()
            cookie_jar.load(filename)
            self.session.cookies.update(cookie_jar)

            print(f"\n📂 Cookies 已从 {filename} 加载")
            return True

        except Exception as e:
            logger.error(f"加载 Cookies 失败: {e}")
            return False


def session_demo() -> None:
    """Session 管理演示"""
    print_section("1. Session 管理")

    mgr = SessionManager()

    # 访问设置 Cookie 的页面
    print("\n📍 访问设置 Cookie 的页面")
    mgr.get("https://httpbin.org/cookies/set/session_id/abc123")

    # 检查 Cookie
    mgr.print_cookies()

    # 访问获取 Cookie 的页面
    print("\n📍 访问获取 Cookie 的页面")
    response = mgr.get("https://httpbin.org/cookies")
    print(f"   返回的 Cookies: {response.json()}")


# ============ 表单登录模拟 ============

class FormLogin:
    """表单登录处理器"""

    def __init__(self, login_url: str):
        self.login_url = login_url
        self.session = requests.Session()
        self.csrf_token = None

    def get_login_page(self) -> bool:
        """获取登录页面并提取 CSRF Token"""
        print(f"\n📄 获取登录页面: {self.login_url}")

        try:
            response = self.session.get(self.login_url)
            if response.status_code != 200:
                print(f"   ❌ 获取登录页失败: {response.status_code}")
                return False

            # 尝试提取 CSRF Token
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # 常见的 CSRF Token 字段名
            csrf_names = ['csrf_token', 'csrfmiddlewaretoken', '_token', 'authenticity_token']

            for name in csrf_names:
                token_input = soup.find('input', {'name': name})
                if token_input and token_input.get('value'):
                    self.csrf_token = token_input['value']
                    print(f"   ✅ 找到 CSRF Token: {name}")
                    break

            return True

        except Exception as e:
            logger.error(f"获取登录页失败: {e}")
            return False

    def login(self, username: str, password: str, extra_data: Dict = None) -> bool:
        """执行登录"""
        print(f"\n🔐 执行登录")

        # 准备登录数据
        login_data = {
            'username': username,
            'password': password,
        }

        # 添加 CSRF Token
        if self.csrf_token:
            login_data['csrf_token'] = self.csrf_token

        # 添加额外数据
        if extra_data:
            login_data.update(extra_data)

        print(f"   📝 登录数据: {list(login_data.keys())}")

        try:
            response = self.session.post(
                self.login_url,
                data=login_data,
                headers={'Referer': self.login_url}
            )

            # 检查登录是否成功
            if response.status_code == 200:
                print(f"   ✅ 登录请求发送成功")

                # 检查是否有错误提示
                if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                    print(f"   ⚠️  可能登录失败")
                    return False

                return True
            else:
                print(f"   ❌ 登录失败: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False

    def check_login_status(self) -> bool:
        """检查登录状态"""
        # 这里需要根据实际情况实现
        return True


def form_login_demo() -> None:
    """表单登录演示"""
    print_section("2. 表单登录模拟")

    # 使用 httpbin 的 post 接口模拟
    login = FormLogin("https://httpbin.org/post")

    # 获取登录页（httpbin 不需要真实获取）
    print("\n💡 真实场景示例:")
    print("   1. 访问登录页获取 CSRF Token")
    print("   2. 提交登录表单（username + password + csrf_token）")
    print("   3. 服务器返回包含认证 Cookie 的响应")
    print("   4. 后续请求自动携带 Cookie")

    # 演示 POST 请求
    print("\n📤 演示 POST 请求:")
    response = login.session.post(
        "https://httpbin.org/post",
        data={
            'username': 'test_user',
            'password': 'test_password',
            'csrf_token': 'abc123'
        }
    )

    result = response.json()
    print(f"   发送的数据: {result.get('form', {})}")


# ============ Cookie 手动处理 ============

def manual_cookie_demo() -> None:
    """手动 Cookie 处理"""
    print_section("3. 手动 Cookie 处理")

    session = requests.Session()

    # 方式1: 直接设置 Cookie
    print("\n🍪 方式1: 直接设置 Cookie")
    session.cookies.set('session_id', 'xyz789')
    session.cookies.set('user_id', '1001')
    session.cookies.set('preferences', json.dumps({'theme': 'dark'}))

    response = session.get('https://httpbin.org/cookies')
    print(f"   Cookies: {response.json()}")

    # 方式2: 使用 Cookie 字典
    print("\n🍪 方式2: 使用 Cookie 字典")
    cookies = {
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
        'language': 'zh-CN',
    }

    response = requests.get('https://httpbin.org/cookies', cookies=cookies)
    print(f"   Cookies: {response.json()}")

    # 方式3: 从浏览器复制 Cookie
    print("\n🍪 方式3: 使用浏览器复制的 Cookie")
    print("   步骤:")
    print("   1. 浏览器登录后打开开发者工具")
    print("   2. Application/Storage → Cookies")
    print("   3. 复制需要的 Cookie")
    print("   4. 在代码中使用")
    print("\n   示例代码:")
    print("   session.cookies.set('name', 'value', domain='.example.com')")


# ============ Token 认证 ============

class TokenAuth:
    """Token 认证处理器"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None

    def set_token(self, token: str) -> None:
        """设置 Token"""
        self.token = token
        print(f"   ✅ Token 已设置")

    def get_headers(self) -> Dict[str, str]:
        """获取带认证的请求头"""
        headers = {
            'Content-Type': 'application/json',
        }

        if self.token:
            # 常见的 Token 认证方式
            headers['Authorization'] = f'Bearer {self.token}'
            # 或者其他方式:
            # headers['X-API-Key'] = self.token
            # headers['Authorization'] = f'Token {self.token}'

        return headers

    def request(self, method: str, endpoint: str, data: Dict = None) -> Optional[dict]:
        """发送认证请求"""
        url = urljoin(self.base_url, endpoint)

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.get_headers())
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=self.get_headers())
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print(f"   ❌ 认证失败: Token 可能已过期")
            else:
                print(f"   ⚠️  请求失败: {response.status_code}")

        except Exception as e:
            logger.error(f"请求失败: {e}")

        return None


def token_auth_demo() -> None:
    """Token 认证演示"""
    print_section("4. Token 认证")

    auth = TokenAuth("https://api.example.com")

    print("\n🔑 设置 API Token")
    print("   示例 Token:")
    example_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    print(f"   {example_token[:20]}...")

    auth.set_token(example_token)

    print("\n📤 认证请求头:")
    headers = auth.get_headers()
    print(f"   Authorization: {headers.get('Authorization', 'N/A')[:30]}...")

    print("\n💡 常见的 Token 认证方式:")
    print("   1. Bearer Token (OAuth 2.0)")
    print("      Authorization: Bearer <token>")
    print("   2. API Key")
    print("      X-API-Key: <key>")
    print("   3. Custom Token")
    print("      Authorization: Token <token>")


# ============ OAuth 认证 ============

def oauth_lesson() -> None:
    """OAuth 认证讲解"""
    print_section("5. OAuth 认证流程")

    lesson = """
    🔐 OAuth 2.0 认证流程:

    1. 📱 用户点击"使用 xxx 登录"
       └──> 重定向到认证服务器

    2. 🔑 用户授权
       └──> 认证服务器返回授权码

    3. 🔄 应用后端用授权码换取 Token
       └──> POST https://oauth.server/token
           grant_type=authorization_code
           code=AUTHORIZATION_CODE
           client_id=YOUR_CLIENT_ID
           client_secret=YOUR_CLIENT_SECRET

    4. ✅ 获得 Access Token
       └──> 使用 Token 访问受保护的资源

    💡 对于爬虫开发者:
       - 使用 Personal Access Token (最简单)
       - 使用 OAuth 应用 (需要注册)
       - 直接使用 Session Cookie (最直接)

    📚 常见平台的 OAuth:
       - GitHub: Settings → Developer settings → Personal access tokens
       - Google: Cloud Console → Credentials
       - 微信: 微信开放平台
    """
    print(lesson)


# ============ 完整的登录流程示例 ============

class SmartLogin:
    """智能登录处理器"""

    def __init__(self):
        self.session = requests.Session()
        self.config = {}

    def load_config(self, config: Dict) -> None:
        """加载配置"""
        self.config = config

    def login_with_password(self) -> bool:
        """密码登录"""
        login_url = self.config.get('login_url')
        username = self.config.get('username')
        password = self.config.get('password')

        if not all([login_url, username, password]):
            print("   ⚠️  配置不完整")
            return False

        print(f"\n🔐 使用密码登录: {username}")

        # 这里实现实际的登录逻辑
        # ...
        return True

    def login_with_cookie(self) -> bool:
        """Cookie 登录"""
        cookies = self.config.get('cookies')

        if not cookies:
            print("   ⚠️  未配置 Cookie")
            return False

        print(f"\n🍪 使用 Cookie 登录")

        for name, value in cookies.items():
            self.session.cookies.set(name, value)

        print(f"   ✅ 已设置 {len(cookies)} 个 Cookie")
        return True

    def login_with_token(self) -> bool:
        """Token 登录"""
        token = self.config.get('token')

        if not token:
            print("   ⚠️  未配置 Token")
            return False

        print(f"\n🔑 使用 Token 登录")

        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })

        return True

    def login(self) -> bool:
        """自动选择登录方式"""
        print("\n🔑 尝试登录...")

        # 优先级: Token > Cookie > 密码
        if self.config.get('token'):
            return self.login_with_token()
        elif self.config.get('cookies'):
            return self.login_with_cookie()
        elif self.config.get('password'):
            return self.login_with_password()

        print("   ❌ 没有可用的登录凭据")
        return False

    def test_login(self) -> bool:
        """测试登录状态"""
        test_url = self.config.get('test_url')

        if not test_url:
            print("   ⚠️  未配置测试 URL")
            return False

        print(f"\n🧪 测试登录状态: {test_url}")

        response = self.session.get(test_url)

        if response.status_code == 200:
            print(f"   ✅ 登录成功")
            return True
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
            return False


def smart_login_demo() -> None:
    """智能登录演示"""
    print_section("6. 完整登录流程")

    login = SmartLogin()

    print("\n💡 配置示例:")
    config_example = {
        'login_url': 'https://example.com/login',
        'username': 'your_username',
        'password': 'your_password',
        'token': 'your_token',  # 可选
        'cookies': {            # 可选
            'session_id': 'xxx',
            'token': 'yyy',
        },
        'test_url': 'https://example.com/profile',
    }

    print(json.dumps(config_example, indent=2, ensure_ascii=False))

    print("\n🔧 使用方法:")
    print("   login.load_config(config)")
    print("   if login.login():")
    print("       # 登录成功，继续操作")


def main() -> None:
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🔐 登录与 Cookie 处理                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 运行各个示例
    session_demo()
    form_login_demo()
    manual_cookie_demo()
    token_auth_demo()
    oauth_lesson()
    smart_login_demo()

    print_section("完成")
    print("💡 登录处理建议:")
    print("   1. 🍪 优先使用 Session 自动管理 Cookie")
    print("   2. 🔐 注意处理 CSRF Token")
    print("   3. 🔑 API 调用使用 Token 认证")
    print("   4. 💾 可以保存 Cookie 避免重复登录")
    print("   5. 🧪 登录后验证状态")
    print("\n📚 练习:")
    print("   1. 实现一个完整的登录流程")
    print("   2. 使用 Cookie 保持登录状态")
    print("   3. 获取并使用 GitHub Personal Access Token")


if __name__ == "__main__":
    main()
