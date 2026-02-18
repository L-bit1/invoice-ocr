# 🚀 GitHub Actions 快速开始指南

## 5分钟快速打包 exe

### 步骤 1：准备 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库名称（例如：`invoice-manager`）
4. 选择 Public 或 Private
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

### 步骤 2：推送代码

在项目目录打开终端，执行：

```bash
# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "初始提交：发票管理系统"

# 添加远程仓库（替换成你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 3：触发构建

**方法1：自动触发（推荐）**
- 代码推送后会自动开始构建
- 无需任何操作

**方法2：手动触发**
1. 打开 GitHub 仓库页面
2. 点击顶部 "Actions" 标签
3. 选择 "构建发票管理系统" 工作流
4. 点击 "Run workflow" → "Run workflow"

### 步骤 4：下载 exe

1. 等待构建完成（约 5-10 分钟）
2. 点击完成的构建任务
3. 滚动到底部 "Artifacts" 部分
4. 下载：
   - **发票管理系统-Windows-基础版**（约 20-30MB，不含 OCR）
   - **发票管理系统-Windows-完整版**（约 200-300MB，含 OCR）

### 步骤 5：运行程序

1. 下载 exe 文件到 Windows 电脑
2. 双击运行
3. 开始使用！

---

## 📋 构建产物说明

| 版本 | 大小 | OCR功能 | 适用场景 |
|------|------|---------|----------|
| 基础版 | ~30MB | ❌ | 不需要OCR，只需手动录入 |
| 完整版 | ~300MB | ✅ | 需要OCR识别发票图片 |

---

## ⚠️ 注意事项

1. **首次构建较慢**：完整版首次构建可能需要 15-20 分钟
2. **文件较大**：完整版 exe 约 200-300MB，下载需要时间
3. **保留期限**：构建产物保留 30 天，请及时下载
4. **无需 Windows**：整个过程在云端完成，Mac/Linux 也可以使用

---

## 🆘 遇到问题？

查看详细说明：[GitHub Actions 使用说明.md](GitHub Actions 使用说明.md)

---

**就这么简单！** 🎉
