# GitHub Actions 自动打包说明

本项目的 GitHub Actions 会自动在 Windows 服务器上打包生成 exe 文件，无需本地 Windows 环境。

## 📋 前置要求

1. **GitHub 账号**：需要一个 GitHub 账号
2. **Git 仓库**：将代码推送到 GitHub 仓库

## 🚀 使用步骤

### 第一步：创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库名称（例如：`invoice-manager`）
4. 选择 Public 或 Private
5. 点击 "Create repository"

### 第二步：推送代码到 GitHub

在本地项目目录执行以下命令：

```bash
# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "初始提交：发票管理系统"

# 添加远程仓库（替换 YOUR_USERNAME 和 YOUR_REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送代码
git branch -M main
git push -u origin main
```

### 第三步：触发 GitHub Actions

GitHub Actions 会在以下情况自动触发：

1. **推送到 main/master 分支**：每次推送代码都会自动构建
2. **创建标签**：创建以 `v` 开头的标签（如 `v1.0.0`）会触发构建
3. **手动触发**：在 GitHub 网页上手动运行工作流

#### 手动触发方法：

1. 打开 GitHub 仓库页面
2. 点击顶部 "Actions" 标签
3. 在左侧选择 "构建发票管理系统" 工作流
4. 点击右侧 "Run workflow" 按钮
5. 选择分支（通常是 main）
6. 点击 "Run workflow"

### 第四步：下载构建产物

1. 等待构建完成（通常需要 5-10 分钟）
2. 在 Actions 页面找到完成的构建
3. 点击构建任务
4. 滚动到页面底部的 "Artifacts" 部分
5. 下载以下文件：
   - **发票管理系统-Windows-基础版**：不含 OCR 的轻量版（约 20-30MB）
   - **发票管理系统-Windows-完整版**：包含 OCR 的完整版（约 200-300MB）

## 📦 构建产物说明

### 基础版（不含 OCR）

- **文件名**：`发票管理系统-基础版.exe`
- **大小**：约 20-30MB
- **功能**：发票录入、查询、统计、导出（手动录入）
- **适用场景**：不需要 OCR 功能的用户

### 完整版（含 OCR）

- **文件名**：`发票管理系统-完整版.exe`
- **大小**：约 200-300MB
- **功能**：包含基础版所有功能 + OCR 图片识别
- **适用场景**：需要 OCR 识别发票的用户

## ⚙️ 工作流配置说明

工作流文件位于：`.github/workflows/build.yml`

### 构建环境

- **操作系统**：Windows Latest
- **Python 版本**：3.11
- **架构**：x64

### 构建步骤

1. 检出代码
2. 设置 Python 环境
3. 安装依赖（PyInstaller + OCR 库）
4. 使用 PyInstaller 打包
5. 创建发布文件
6. 上传构建产物

## 🔧 自定义配置

如果需要修改构建配置，可以编辑 `.github/workflows/build.yml` 文件：

### 修改 Python 版本

```yaml
python-version: '3.11'  # 改为你需要的版本
```

### 修改输出文件名

```yaml
--name="发票管理系统"  # 改为你想要的名称
```

### 添加图标

1. 准备一个 `.ico` 图标文件
2. 放在项目根目录
3. 修改构建命令：
   ```yaml
   --icon=icon.ico
   ```

## 📝 注意事项

1. **首次构建较慢**：完整版首次构建可能需要 15-20 分钟（需要下载 OCR 模型）
2. **文件大小**：完整版 exe 文件较大，下载需要一些时间
3. **构建产物保留**：GitHub 会保留构建产物 30 天
4. **网络要求**：构建过程需要访问网络下载依赖

## 🐛 常见问题

### Q: 构建失败怎么办？

**可能原因**：
- 依赖安装失败
- PyInstaller 版本不兼容
- 代码有语法错误

**解决方法**：
1. 查看 Actions 日志，找到错误信息
2. 检查 `requirements-build.txt` 和 `requirements-ocr-paddle.txt` 中的依赖版本
3. 确保代码可以正常运行

### Q: 构建产物在哪里下载？

在 GitHub Actions 页面：
1. 点击完成的构建任务
2. 滚动到底部
3. 在 "Artifacts" 部分下载

### Q: 可以只构建基础版吗？

可以！修改 `.github/workflows/build.yml`，注释掉 `build-windows-with-ocr` 任务即可。

### Q: 构建产物可以自动发布到 Releases 吗？

可以！添加以下步骤到工作流：

```yaml
- name: 创建 Release
  uses: softprops/action-gh-release@v1
  with:
    files: |
      release/发票管理系统-基础版.exe
      release-ocr/发票管理系统-完整版.exe
    draft: false
    prerelease: false
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🎉 完成！

现在你可以：
1. 推送代码到 GitHub
2. 等待自动构建完成
3. 下载 exe 文件
4. 在 Windows 上直接运行，无需安装 Python！

---

**提示**：如果遇到问题，可以查看 GitHub Actions 的日志来诊断问题。
