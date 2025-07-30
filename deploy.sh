#!/bin/bash

echo "🚀 汇报评分投票系统 - 快速部署脚本"
echo "=================================="

# 检查Git是否已初始化
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit - 汇报评分投票系统"
    echo "✅ Git仓库初始化完成"
else
    echo "📦 更新Git仓库..."
    git add .
    git commit -m "Update - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "✅ Git仓库更新完成"
fi

echo ""
echo "🌐 部署选项："
echo "1. Railway.app (推荐)"
echo "2. Render.com"
echo "3. Docker本地测试"
echo "4. 生成部署包"

read -p "请选择部署方式 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚂 Railway.app 部署指南："
        echo "1. 访问 https://railway.app/"
        echo "2. 使用GitHub登录"
        echo "3. 点击 'New Project' → 'Deploy from GitHub repo'"
        echo "4. 选择此仓库"
        echo "5. 添加MySQL数据库服务"
        echo "6. 配置环境变量（参考 env.example 文件）"
        echo ""
        echo "📋 需要配置的环境变量："
        echo "SECRET_KEY=your-super-secret-key"
        echo "FLASK_DEBUG=False"
        echo "DB_HOST=<Railway提供>"
        echo "DB_NAME=railway"
        echo "DB_USER=root"
        echo "DB_PASSWORD=<Railway提供>"
        echo "DB_PORT=3306"
        ;;
    2)
        echo ""
        echo "🎨 Render.com 部署指南："
        echo "1. 访问 https://render.com/"
        echo "2. 连接GitHub仓库"
        echo "3. 创建Web Service"
        echo "4. 添加PostgreSQL数据库"
        echo "5. 配置环境变量"
        ;;
    3)
        echo ""
        echo "🐳 启动Docker本地测试..."
        if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
            docker-compose up --build -d
            echo "✅ Docker容器启动成功！"
            echo "🌐 访问地址: http://localhost:5000"
            echo "📊 MySQL管理: http://localhost:3306"
        else
            echo "❌ 请先安装Docker和Docker Compose"
            echo "安装指南: https://docs.docker.com/get-docker/"
        fi
        ;;
    4)
        echo ""
        echo "📦 生成部署包..."
        
        # 创建部署包目录
        DEPLOY_DIR="voting-system-deploy-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$DEPLOY_DIR"
        
        # 复制必要文件
        cp -r templates static app.py requirements.txt Dockerfile docker-compose.yml Procfile railway.json database_schema.sql env.example 部署说明文档.md "$DEPLOY_DIR/"
        
        # 创建压缩包
        tar -czf "${DEPLOY_DIR}.tar.gz" "$DEPLOY_DIR"
        
        echo "✅ 部署包已生成: ${DEPLOY_DIR}.tar.gz"
        echo "📋 包含文件:"
        echo "  - 应用代码和模板"
        echo "  - Docker配置"
        echo "  - 部署配置文件"
        echo "  - 数据库初始化脚本"
        echo "  - 详细部署说明文档"
        
        # 清理临时目录
        rm -rf "$DEPLOY_DIR"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "📖 详细部署说明请查看: 部署说明文档.md"
echo "🎉 部署准备完成！"