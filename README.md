# 发票管理系统 - 单机版

一个功能完整的单机版发票管理软件，使用 Python + Tkinter 开发。

> 📖 **详细使用指南**：请查看 [使用指南.md](使用指南.md) 获取完整的使用说明和OCR安装教程

## 功能特性

- ✅ **发票录入**：支持完整的发票信息录入
- ✅ **OCR识别**：支持上传发票图片，自动识别并填入信息（需安装OCR库）
- ✅ **发票查询**：支持按关键词搜索发票
- ✅ **发票列表**：清晰展示所有发票信息
- ✅ **发票统计**：实时显示发票总数、总金额、总税额
- ✅ **数据导出**：支持导出为JSON格式
- ✅ **发票详情**：双击查看发票详细信息
- ✅ **数据删除**：支持删除不需要的发票记录

## 系统要求

- Python 3.6 或更高版本
- 基础功能无需额外依赖（使用Python标准库）
- OCR功能需要安装OCR库（可选）

### 安装OCR功能（可选）

> 💡 **详细安装步骤**：请查看 [使用指南.md](使用指南.md) 中的"OCR功能安装"章节

**快速安装（方案1：PaddleOCR - 推荐）**
```bash
pip install paddleocr paddlepaddle
```
或在 Windows 上运行 `install_ocr.bat`，在 Mac/Linux 上运行 `./install_ocr.sh`

**备选方案（方案2：Tesseract OCR）**
```bash
# 安装Python库
pip install pytesseract pillow

# 还需要安装 Tesseract-OCR 软件
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract tesseract-lang
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

## 安装和使用

### 方法一：直接运行

1. 确保已安装 Python 3.6+
2. 运行程序：
```bash
python invoice_manager.py
```

### 方法二：打包成exe（Windows）

**方式A：使用 GitHub Actions 自动打包（推荐）⭐**

无需本地 Windows 环境，GitHub Actions 会自动在云端构建：

1. 将代码推送到 GitHub 仓库
2. GitHub Actions 会自动构建
3. 在 Actions 页面下载构建好的 exe 文件

详细说明请查看：[GitHub Actions 使用说明.md](GitHub Actions 使用说明.md)

**方式B：本地打包**

1. 安装 PyInstaller：
```bash
pip install pyinstaller
```

2. 打包程序：
```bash
pyinstaller --onefile --windowed --name="发票管理系统" invoice_manager.py
```

3. 打包后的exe文件在 `dist` 目录中

## 使用说明

### 新增发票

**方式一：手动录入**
1. 点击"新增发票"按钮
2. 填写发票信息（带*号的为必填项）
3. 点击"保存"按钮

**方式二：OCR识别（需安装OCR库）**
1. 点击"新增发票"按钮
2. 点击"📷 OCR识别发票"按钮
3. 选择发票图片文件
4. 等待识别完成
5. 查看识别结果，点击"应用识别结果"自动填入表单
6. 检查并完善信息后点击"保存"

### 查询发票

在搜索框中输入关键词，支持搜索：
- 发票号码
- 购买方名称
- 销售方名称
- 备注信息

### 查看详情

双击列表中的发票记录，即可查看详细信息

### 删除发票

1. 选中要删除的发票
2. 点击"删除发票"按钮
3. 确认删除

### 导出数据

1. 点击菜单栏"文件" -> "导出数据"
2. 选择保存位置
3. 数据将导出为JSON格式

## 数据存储

所有数据存储在本地 SQLite 数据库文件 `invoices.db` 中，无需网络连接。

## 注意事项

- 发票号码必须唯一
- 金额和合计必须大于0
- 数据文件 `invoices.db` 请妥善保管，建议定期备份

## 技术栈

- Python 3.6+
- Tkinter (GUI界面)
- SQLite (数据存储)
- PaddleOCR / Tesseract OCR (OCR识别，可选)

## 版本信息

- 版本：1.0
- 更新日期：2024
