# Gunicorn配置文件
import os

# 服务器绑定
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# 工作进程数
workers = int(os.getenv('WEB_CONCURRENCY', '4'))

# 工作进程类型
worker_class = "sync"

# 超时时间
timeout = 120
keepalive = 2

# 日志配置
loglevel = "info"
accesslog = "-"
errorlog = "-"

# 进程名称
proc_name = "voting-system"

# 预加载应用
preload_app = True

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 启动时的钩子函数
def on_starting(server):
    """启动时执行"""
    server.log.info("启动汇报评分投票系统...")

def when_ready(server):
    """准备就绪时执行"""
    server.log.info(f"投票系统已启动，监听端口: {server.address}")

def on_exit(server):
    """退出时执行"""
    server.log.info("投票系统已停止")