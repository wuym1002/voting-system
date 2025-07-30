#!/bin/bash

# 启动汇报评分投票系统
echo "正在启动汇报评分投票系统..."

# 激活虚拟环境
source voting_env/bin/activate

# 启动Flask应用
echo "启动Flask应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo "=========================="

python3 app.py