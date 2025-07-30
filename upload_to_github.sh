#!/bin/bash

echo "🚀 自动上传到GitHub并准备Railway部署"
echo "======================================="

# 检查是否已有GitHub远程仓库
if git remote get-url origin &> /dev/null; then
    echo "📦 发现已有GitHub仓库，更新代码..."
    git add .
    git commit -m "更新投票系统 - $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
    echo "✅ 代码更新完成！"
else
    echo "⚠️  请先设置GitHub仓库地址："
    echo "1. 在GitHub创建新仓库：voting-system"
    echo "2. 复制仓库URL（如：https://github.com/username/voting-system.git）"
    echo ""
    read -p "请输入GitHub仓库URL: " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ 未输入仓库URL，退出"
        exit 1
    fi
    
    echo "📦 设置GitHub仓库并上传代码..."
    git remote add origin "$repo_url"
    git branch -M main
    git add .
    git commit -m "首次提交 - 汇报评分投票系统"
    git push -u origin main
    echo "✅ 代码上传完成！"
fi

echo ""
echo "🎯 下一步：Railway部署"
echo "======================="
echo "1. 访问 https://railway.app"
echo "2. 使用GitHub登录"
echo "3. 点击 'New Project' → 'Deploy from GitHub repo'"
echo "4. 选择您的 voting-system 仓库"
echo "5. 添加 MySQL 数据库服务"
echo "6. 等待部署完成，获取访问URL"
echo ""
echo "📖 详细说明请查看：一键部署到Railway.md"
echo ""
echo "🎉 准备就绪！您的投票系统即将上线！"