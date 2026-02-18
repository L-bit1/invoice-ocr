# 📤 推送代码到 GitHub 指南

## ⚠️ 重要提示

**不要在用户主目录（~）执行 git 命令！**

你刚才在 `~` 目录执行了 `git init`，这会在用户主目录创建 git 仓库，这是不对的。

## ✅ 正确步骤

### 方法一：使用脚本（推荐）

在项目目录执行：

```bash
cd "/Users/mac/Desktop/工作/软件/发票软件"
./setup_git.sh
```

脚本会自动：
1. 切换到项目目录
2. 初始化 git 仓库
3. 设置分支为 main
4. 添加所有文件
5. 创建初始提交

### 方法二：手动执行

```bash
# 1. 切换到项目目录（重要！）
cd "/Users/mac/Desktop/工作/软件/发票软件"

# 2. 初始化 git 仓库
git init

# 3. 设置默认分支为 main
git branch -M main

# 4. 添加所有文件
git add .

# 5. 创建初始提交
git commit -m "初始提交：发票管理系统"
```

## 🔗 连接到 GitHub

### 第一步：创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库名称（例如：`invoice-manager`）
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 第二步：添加远程仓库并推送

```bash
# 添加远程仓库（替换 YOUR_USERNAME 和 YOUR_REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送代码
git push -u origin main
```

**示例**：
```bash
git remote add origin https://github.com/zhangsan/invoice-manager.git
git push -u origin main
```

## 🧹 清理错误位置的 git 仓库

如果你在用户主目录（~）错误地创建了 git 仓库，可以手动删除：

```bash
# 删除用户主目录的 .git 文件夹
rm -rf ~/.git
```

**注意**：如果提示权限不足，可能需要使用 `sudo`，但请谨慎操作。

## ✅ 验证

推送成功后：

1. 打开 GitHub 仓库页面
2. 应该能看到所有项目文件
3. 点击 "Actions" 标签
4. 应该能看到 "构建发票管理系统" 工作流
5. 工作流会自动开始运行

## 🎉 完成！

等待 GitHub Actions 构建完成（约 5-10 分钟），然后在 Actions 页面下载 exe 文件。

---

**提示**：如果遇到问题，请检查：
- ✅ 是否在正确的项目目录
- ✅ GitHub 仓库地址是否正确
- ✅ 是否有推送权限
