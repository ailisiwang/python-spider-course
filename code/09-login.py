#!/usr/bin/env python3
"""
第9关：突破防线 - 登录与验证码
突破登录防线
"""

import requests

print("=" * 40)
print("🔐 登录与验证")
print("=" * 40)

# 创建一个 Session（保持登录状态）
session = requests.Session()

# 1️⃣ 模拟登录
print("\n1️⃣ 模拟登录流程:")

# 第一步：获取登录页面（拿 csrf token 等）
# login_page = session.get('https://example.com/login')
# soup = BeautifulSoup(login_page.text, 'html.parser')
# csrf_token = soup.find('input', {'name': 'csrf'})['value']

# 第二步：提交登录表单
login_data = {
    'username': 'your_username',
    'password': 'your_password',
    # 'csrf_token': csrf_token  # 如果有
}

# response = session.post('https://example.com/login', data=login_data)

print("   📝 登录请求已发送（示例）")
print("   💡 实际使用时需要分析目标网站的表单字段")

# 2️⃣ Cookie 维持登录状态
print("\n2️⃣ Cookie 使用:")

# 模拟设置 Cookie
session.cookies.set('session_id', 'abc123xyz')
session.cookies.set('user_id', '1001')

# 后续请求自动带 Cookie
# response = session.get('https://example.com/profile')

print("   🍪 已设置 Cookie:")
for cookie in session.cookies:
    print(f"   - {cookie.name}: {cookie.value}")

# 3️⃣ 处理验证码（思路）
print("\n3️⃣ 验证码处理方法:")
print("   🔹 图形验证码 → OCR (pytesseract) 或 打码平台")
print("   🔹 滑动验证码 → 模拟滑动轨迹")
print("   🔹 点选验证码 → 图像识别 + 坐标计算")
print("   🔹 短信验证码 → 接码平台或社工")

# 4️⃣ 实战：GitHub 登录示例
print("\n4️⃣ GitHub API 认证示例:")

# 方法 1: Token 认证
headers = {
    'Authorization': 'token YOUR_GITHUB_TOKEN'
}
# response = requests.get('https://api.github.com/user', headers=headers)

print("   💡 推荐使用 Personal Access Token")
print("   📝 申请地址: https://github.com/settings/tokens")

# 方法 2: Session + Cookie
print("   🍪 或登录后导出 Cookie 使用")
