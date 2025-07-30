#!/bin/bash

# 启动脚本 - 确保端口配置正确
echo "🚀 启动汇报评分投票系统..."

# 设置默认端口（如果没有设置PORT环境变量）
if [ -z "$PORT" ]; then
    export PORT=5000
    echo "📌 使用默认端口: $PORT"
else
    echo "📌 使用环境变量端口: $PORT"
fi

# 验证端口是否为有效数字
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "⚠️  警告: PORT不是有效数字，使用默认端口5000"
    export PORT=5000
fi

# 设置其他环境变量
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

echo "🌐 启动地址: 0.0.0.0:$PORT"
echo "🔧 环境: $FLASK_ENV"

# 启动应用
python app.py