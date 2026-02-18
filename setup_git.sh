#!/bin/bash
# Git 仓库初始化脚本

echo "=========================================="
echo "发票管理系统 - Git 仓库初始化"
echo "=========================================="
echo ""

# 切换到项目目录
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查是否已有 git 仓库
if [ -d ".git" ]; then
    echo "⚠️  项目目录已存在 git 仓库"
    read -p "是否重新初始化？(y/n): " answer
    if [ "$answer" != "y" ]; then
        echo "取消操作"
        exit 0
    fi
    rm -rf .git
    echo "已删除旧的 git 仓库"
fi

# 初始化 git 仓库
echo "正在初始化 git 仓库..."
git init

# 设置默认分支为 main
git branch -M main

# 添加所有文件
echo "正在添加文件..."
git add .

# 创建初始提交
echo "正在创建初始提交..."
git commit -m "初始提交：发票管理系统"

echo ""
echo "✅ Git 仓库初始化完成！"
echo ""
echo "下一步："
echo "1. 在 GitHub 创建新仓库"
echo "2. 运行以下命令添加远程仓库并推送："
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "（请将 YOUR_USERNAME 和 YOUR_REPO 替换为你的实际仓库信息）"
echo ""
