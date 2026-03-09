# 🖥️ 多线程下载器 - Windows 版

> 一个简洁实用的 Windows 桌面下载工具

## 📥 下载地址

**GitHub**: https://github.com/ailisiwang/python-spider-course/tree/main/code/projects/final/windows-downloader

**或直接下载**:
- [windows-downloader.exe](https://github.com/ailisiwang/python-spider-course/releases) (打包好的可执行文件)

---

## 🛠️ 环境准备

### 方式一：直接运行（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/ailisiwang/python-spider-course.git

# 2. 进入目录
cd python-spider-course/code/projects/final/windows-downloader

# 3. 运行
python downloader.py
```

### 方式二：打包成 EXE

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --noconsole --icon=icon.ico downloader.py

# 生成的 EXE 在 dist 目录
```

---

## 📋 功能特性

| 功能 | 说明 |
|------|------|
| 🔽 多线程下载 | 支持 1-32 线程并发下载 |
| ⏸️ 断点续传 | 支持暂停/继续下载 |
| 📊 实时进度 | 显示下载速度、剩余时间 |
| 📁 文件管理 | 选择下载目录、查看下载历史 |
| 🌍 代理支持 | 支持 HTTP/SOCKS 代理 |
| 🔗 URL 批量下载 | 支持导入多个下载链接 |

---

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + V` | 粘贴 URL |
| `Enter` | 开始下载 |
| `Space` | 暂停/继续 |
| `Delete` | 删除任务 |

---

## 📝 使用说明

### 1. 基本下载
```
1. 在输入框粘贴下载链接
2. 选择下载目录（默认桌面）
3. 设置线程数（默认 8）
4. 点击"开始下载"
```

### 2. 批量下载
```
1. 点击"批量导入"
2. 选择 TXT 文件（每行一个 URL）
3. 确认导入
4. 自动开始队列下载
```

### 3. 断点续传
```
下载中断后，重新打开相同 URL
会自动检测并继续下载
```

---

## ⚙️ 配置说明

首次运行会在用户目录生成 `downloader_config.json`:

```json
{
    "default_path": "C:\\Users\\用户名\\Desktop",
    "default_threads": 8,
    "proxy": "",
    "max_concurrent": 3,
    "timeout": 30
}
```

---

## 🐛 常见问题

**Q: 下载速度慢？**
A: 尝试增加线程数，或检查网络/代理设置

**Q: 下载失败？**
A: 检查 URL 是否有效，尝试更换下载目录

**Q: EXE 报毒？**
A: 添加信任即可，这是 PyInstaller 打包的正常现象

---

## 📄 LICENSE

MIT License - 欢迎改进和贡献！
