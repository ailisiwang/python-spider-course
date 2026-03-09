#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖥️ 多线程下载器 - Windows 版
author: AI Assistant
version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
import time
import hashlib
import socket
import urllib.request
import urllib.error
import ssl
from urllib.parse import urlparse
from queue import Queue
import configparser

# 配置
CONFIG_FILE = "downloader_config.json"
DEFAULT_THREADS = 8
DEFAULT_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
MAX_THREADS = 32
MAX_CONCURRENT = 5


class DownloadTask:
    """下载任务类"""
    
    def __init__(self, url, save_path, threads=8):
        self.url = url
        self.save_path = save_path
        self.threads = threads
        self.filename = self.get_filename()
        self.filepath = os.path.join(save_path, self.filename)
        self.total_size = 0
        self.downloaded = 0
        self.status = "waiting"  # waiting, downloading, paused, completed, failed
        self.speed = 0
        self.start_time = 0
        self.chunks = []  # 存储每个线程的下载区间
        self.error = None
        
    def get_filename(self):
        """从URL获取文件名"""
        parsed = urlparse(self.url)
        path = parsed.path
        filename = os.path.basename(path)
        
        if not filename or '.' not in filename:
            # 尝试从Content-Disposition获取
            return "downloaded_file"
        
        # 处理中文编码
        try:
            filename = urllib.parse.unquote(filename)
        except:
            filename = "downloaded_file"
            
        return filename if filename else "downloaded_file"


class DownloaderApp:
    """下载器主程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ 多线程下载器 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 加载配置
        self.config = self.load_config()
        
        # 下载任务列表
        self.tasks = []
        self.active_downloads = []
        self.download_queue = Queue()
        
        # 创建界面
        self.create_widgets()
        
        # 启动下载调度器
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler, daemon=True)
        self.scheduler_thread.start()
        
    def load_config(self):
        """加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
                
        return {
            "default_path": DEFAULT_PATH,
            "default_threads": DEFAULT_THREADS,
            "proxy": "",
            "max_concurrent": MAX_CONCURRENT,
            "timeout": 30
        }
    
    def save_config(self):
        """保存配置"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            
    def create_widgets(self):
        """创建界面组件"""
        
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg="#f0f0f0", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
        
        # URL输入框
        tk.Label(toolbar, text="URL:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.url_entry = tk.Entry(toolbar, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 线程数选择
        tk.Label(toolbar, text="线程:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.thread_var = tk.IntVar(value=self.config["default_threads"])
        self.thread_spin = tk.Spinbox(toolbar, from_=1, to=MAX_THREADS, 
                                       textvariable=self.thread_var, width=5)
        self.thread_spin.pack(side=tk.LEFT, padx=5)
        
        # 下载目录选择
        tk.Button(toolbar, text="📁 选择目录", command=self.select_folder,
                 bg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # 开始按钮
        self.start_btn = tk.Button(toolbar, text="▶ 开始下载", command=self.start_download,
                                   bg="#4CAF50", fg="white", relief=tk.FLAT)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 批量导入按钮
        tk.Button(toolbar, text="📥 批量导入", command=self.batch_import,
                  bg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # 设置按钮
        tk.Button(toolbar, text="⚙️ 设置", command=self.show_settings,
                  bg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        
        # 分割线
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # 任务列表区域
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 表头
        header_frame = tk.Frame(list_frame, bg="#e0e0e0")
        header_frame.pack(fill=tk.X)
        
        headers = ["文件名", "大小", "进度", "速度", "状态", "操作"]
        widths = [250, 80, 150, 80, 80, 100]
        
        for i, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(header_frame, text=h, bg="#e0e0e0", font=("微软雅光", 9, "bold"),
                    width=w, anchor="w").pack(side=tk.LEFT, padx=1)
        
        # 任务列表（可滚动）
        self.task_list_frame = tk.Frame(list_frame, bg="white")
        self.task_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(self.task_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_canvas = tk.Canvas(self.task_list_frame, bg="white", 
                                      yscrollcommand=scrollbar.set)
        self.task_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_canvas.yview)
        
        # 底部状态栏
        self.status_bar = tk.Label(self.root, text="就绪", bg="#f0f0f0", 
                                   anchor="w", padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定快捷键
        self.root.bind('<Control-v>', lambda e: self.paste_url())
        self.root.bind('<Return>', lambda e: self.start_download())
        
    def paste_url(self):
        """粘贴URL"""
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard)
        except:
            pass
            
    def select_folder(self):
        """选择下载目录"""
        folder = filedialog.askdirectory(initialdir=self.config["default_path"])
        if folder:
            self.config["default_path"] = folder
            self.save_config()
            
    def start_download(self):
        """开始下载"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("提示", "请输入下载链接")
            return
            
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            
        # 获取线程数
        try:
            threads = int(self.thread_var.get())
        except:
            threads = DEFAULT_THREADS
            
        # 创建任务
        task = DownloadTask(url, self.config["default_path"], threads)
        
        # 检查文件是否已存在
        if os.path.exists(task.filepath):
            result = messagebox.askyesno("文件存在", 
                f"文件已存在，是否覆盖？\n{task.filename}")
            if not result:
                return
                
        # 添加任务
        self.tasks.append(task)
        self.download_queue.put(task)
        
        # 更新界面
        self.add_task_widget(task)
        self.url_entry.delete(0, tk.END)
        
        self.status_bar.config(text=f"已添加任务: {task.filename}")
        
    def add_task_widget(self, task):
        """添加任务显示组件"""
        # 任务行框架
        row = tk.Frame(self.task_canvas, bg="white", height=30)
        row.pack(fill=tk.X, pady=1)
        
        # 文件名
        name_label = tk.Label(row, text=task.filename[:35] + "..." if len(task.filename) > 35 else task.filename,
                             bg="white", width=250, anchor="w")
        name_label.pack(side=tk.LEFT, padx=1)
        
        # 大小
        size_label = tk.Label(row, text="0 KB", bg="white", width=8)
        size_label.pack(side=tk.LEFT, padx=1)
        
        # 进度条
        progress = ttk.Progressbar(row, length=120, mode='determinate')
        progress.pack(side=tk.LEFT, padx=1)
        
        # 速度
        speed_label = tk.Label(row, text="0 KB/s", bg="white", width=10)
        speed_label.pack(side=tk.LEFT, padx=1)
        
        # 状态
        status_label = tk.Label(row, text="等待中", bg="white", width=10)
        status_label.pack(side=tk.LEFT, padx=1)
        
        # 操作按钮
        btn_frame = tk.Frame(row, bg="white")
        btn_frame.pack(side=tk.LEFT, padx=1)
        
        pause_btn = tk.Button(btn_frame, text="⏸", width=3, font=("Arial", 8),
                             command=lambda: self.toggle_pause(task))
        pause_btn.pack(side=tk.LEFT, padx=1)
        
        stop_btn = tk.Button(btn_frame, text="⏹", width=3, font=("Arial", 8),
                            command=lambda: self.stop_task(task))
        stop_btn.pack(side=tk.LEFT, padx=1)
        
        del_btn = tk.Button(btn_frame, text="✕", width=3, font=("Arial", 8),
                           command=lambda: self.delete_task(task))
        del_btn.pack(side=tk.LEFT, padx=1)
        
        # 保存引用以便更新
        task.widget = {
            "row": row,
            "name": name_label,
            "size": size_label,
            "progress": progress,
            "speed": speed_label,
            "status": status_label,
            "pause_btn": pause_btn
        }
        
        # 添加到Canvas
        self.task_canvas.create_window(0, len(self.tasks) * 32, anchor=tk.NW, window=row, width=750)
        
    def scheduler(self):
        """下载调度器"""
        while self.scheduler_running:
            # 检查是否可以启动新下载
            while len(self.active_downloads) < self.config["max_concurrent"]:
                if self.download_queue.empty():
                    break
                    
                task = self.download_queue.get()
                if task.status == "stopped":
                    continue
                    
                # 启动下载线程
                task.status = "downloading"
                self.active_downloads.append(task)
                
                download_thread = threading.Thread(target=self.download_file, 
                                                  args=(task,), daemon=True)
                download_thread.start()
                    
            time.sleep(0.5)
            
    def download_file(self, task):
        """下载文件"""
        try:
            # 获取文件大小
            task.status = "downloading"
            self.update_task_status(task, "下载中")
            
            # 创建请求
            req = urllib.request.Request(task.url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # 添加代理
            if self.config.get("proxy"):
                proxy_handler = urllib.request.ProxyHandler({
                    'http': self.config['proxy'],
                    'https': self.config['proxy']
                })
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
                
            # 获取文件信息
            response = opener.open(req, timeout=self.config.get("timeout", 30))
            task.total_size = int(response.headers.get('Content-Length', 0))
            
            if task.total_size > 0:
                # 多线程下载
                self.multi_thread_download(task, opener, req)
            else:
                # 单线程下载
                self.single_thread_download(task, opener)
                
            # 标记完成
            task.status = "completed"
            self.update_task_status(task, "已完成")
            self.status_bar.config(text=f"下载完成: {task.filename}")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.update_task_status(task, f"失败: {e}")
            
        finally:
            if task in self.active_downloads:
                self.active_downloads.remove(task)
                
    def multi_thread_download(self, task, opener, req):
        """多线程下载"""
        chunk_size = task.total_size // task.threads
        threads = []
        
        # 创建临时文件
        temp_file = task.filepath + ".tmp"
        
        # 打开文件
        with open(temp_file, 'wb') as f:
            pass
            
        # 下载区间
        ranges = []
        for i in range(task.threads):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < task.threads - 1 else task.total_size - 1
            ranges.append((start, end))
            
        # 下载函数
        def download_chunk(start, end, thread_id):
            try:
                req = urllib.request.Request(task.url)
                req.add_header('Range', f'bytes={start}-{end}')
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                response = opener.open(req, timeout=30)
                data = response.read()
                
                with open(temp_file, 'rb+') as f:
                    f.seek(start)
                    f.write(data)
                    
                task.downloaded += len(data)
                
            except Exception as e:
                print(f"线程 {thread_id} 错误: {e}")
                
        # 启动线程
        for i, (start, end) in enumerate(ranges):
            t = threading.Thread(target=download_chunk, args=(start, end, i))
            t.start()
            threads.append(t)
            
        # 等待完成
        last_downloaded = 0
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
            
            # 计算速度
            if task.downloaded > last_downloaded:
                task.speed = (task.downloaded - last_downloaded) * 10
                last_downloaded = task.downloaded
                
            self.update_task_progress(task)
            
        # 完成后重命名
        if os.path.exists(task.filepath):
            os.remove(task.filepath)
        os.rename(temp_file, task.filepath)
        
    def single_thread_download(self, task, opener):
        """单线程下载"""
        response = opener.open(task.url, timeout=30)
        
        chunk_size = 8192
        with open(task.filepath, 'wb') as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                    
                f.write(chunk)
                task.downloaded += len(chunk)
                
                if task.total_size > 0:
                    progress = (task.downloaded / task.total_size) * 100
                    task.widget["progress"]["value"] = progress
                    
    def update_task_progress(self, task):
        """更新任务进度"""
        if task.status != "downloading":
            return
            
        if task.total_size > 0:
            progress = (task.downloaded / task.total_size) * 100
            task.widget["progress"]["value"] = progress
            
            size_mb = task.total_size / (1024 * 1024)
            downloaded_mb = task.downloaded / (1024 * 1024)
            task.widget["size"].config(text=f"{downloaded_mb:.1f}/{size_mb:.1f} MB")
            
        speed_kb = task.speed / 1024
        task.widget["speed"].config(text=f"{speed_kb:.0f} KB/s")
        
    def update_task_status(self, task, status):
        """更新任务状态"""
        if task.widget:
            task.widget["status"].config(text=status)
            
    def toggle_pause(self, task):
        """暂停/继续"""
        if task.status == "downcasting":
            task.status = "paused"
            self.update_task_status(task, "已暂停")
            task.widget["pause_btn"].config(text="▶")
        elif task.status == "paused":
            task.status = "downloading"
            self.update_task_status(task, "下载中")
            task.widget["pause_btn"].config(text="⏸")
            
    def stop_task(self, task):
        """停止任务"""
        task.status = "stopped"
        if task in self.active_downloads:
            self.active_downloads.remove(task)
        self.update_task_status(task, "已停止")
        
    def delete_task(self, task):
        """删除任务"""
        if task in self.active_downloads:
            self.stop_task(task)
            
        if task in self.tasks:
            self.tasks.remove(task)
            
        if task.widget:
            task.widget["row"].destroy()
            
    def batch_import(self):
        """批量导入"""
        filename = filedialog.askopenfilename(
            title="选择导入文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            for url in urls:
                if url.startswith(('http://', 'https://')):
                    task = DownloadTask(url, self.config["default_path"], 
                                       self.config["default_threads"])
                    self.tasks.append(task)
                    self.download_queue.put(task)
                    self.add_task_widget(task)
                    
            messagebox.showinfo("导入成功", f"已导入 {len(urls)} 个下载链接")
            
        except Exception as e:
            messagebox.showerror("导入失败", str(e))
            
    def show_settings(self):
        """显示设置窗口"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("⚙️ 设置")
        settings_win.geometry("400x300")
        
        # 线程数
        tk.Label(settings_win, text="默认线程数:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        threads_var = tk.IntVar(value=self.config["default_threads"])
        tk.Spinbox(settings_win, from_=1, to=MAX_THREADS, 
                  textvariable=threads_var, width=10).grid(row=0, column=1, padx=10, pady=10)
        
        # 并发数
        tk.Label(settings_win, text="最大并发:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        concurrent_var = tk.IntVar(value=self.config["max_concurrent"])
        tk.Spinbox(settings_win, from_=1, to=10, 
                  textvariable=concurrent_var, width=10).grid(row=1, column=1, padx=10, pady=10)
        
        # 超时
        tk.Label(settings_win, text="超时时间(秒):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        timeout_var = tk.IntVar(value=self.config.get("timeout", 30))
        tk.Spinbox(settings_win, from_=5, to=300, 
                  textvariable=timeout_var, width=10).grid(row=2, column=1, padx=10, pady=10)
        
        # 代理
        tk.Label(settings_win, text="代理地址:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        proxy_var = tk.StringVar(value=self.config.get("proxy", ""))
        tk.Entry(settings_win, textvariable=proxy_var, width=25).grid(row=3, column=1, padx=10, pady=10)
        
        # 保存按钮
        def save_settings():
            self.config["default_threads"] = threads_var.get()
            self.config["max_concurrent"] = concurrent_var.get()
            self.config["timeout"] = timeout_var.get()
            self.config["proxy"] = proxy_var.get()
            self.save_config()
            settings_win.destroy()
            messagebox.showinfo("提示", "设置已保存")
            
        tk.Button(settings_win, text="保存", command=save_settings,
                 bg="#4CAF50", fg="white").grid(row=4, column=1, padx=10, pady=20)


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    
    # 运行程序
    app = DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
