#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单机版发票管理软件
功能：发票录入、查询、统计、导出、OCR识别
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import json
import os
import re

# OCR相关导入（可选，如果未安装则禁用OCR功能）
OCR_AVAILABLE = False
USE_PADDLEOCR = False

try:
    from paddleocr import PaddleOCR
    OCR_AVAILABLE = True
    USE_PADDLEOCR = True
except ImportError:
    try:
        import pytesseract
        from PIL import Image
        OCR_AVAILABLE = True
        USE_PADDLEOCR = False
    except ImportError:
        OCR_AVAILABLE = False
        USE_PADDLEOCR = False


class InvoiceDatabase:
    """发票数据库管理类"""
    
    def __init__(self, db_path='invoices.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL UNIQUE,
                invoice_date TEXT NOT NULL,
                buyer_name TEXT,
                buyer_tax_id TEXT,
                seller_name TEXT,
                seller_tax_id TEXT,
                amount REAL NOT NULL,
                tax_amount REAL,
                total_amount REAL NOT NULL,
                invoice_type TEXT,
                status TEXT DEFAULT '正常',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_invoice(self, invoice_data):
        """添加发票"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO invoices (
                    invoice_number, invoice_date, buyer_name, buyer_tax_id,
                    seller_name, seller_tax_id, amount, tax_amount,
                    total_amount, invoice_type, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_number'],
                invoice_data['invoice_date'],
                invoice_data.get('buyer_name', ''),
                invoice_data.get('buyer_tax_id', ''),
                invoice_data.get('seller_name', ''),
                invoice_data.get('seller_tax_id', ''),
                invoice_data['amount'],
                invoice_data.get('tax_amount', 0),
                invoice_data['total_amount'],
                invoice_data.get('invoice_type', '增值税发票'),
                invoice_data.get('status', '正常'),
                invoice_data.get('notes', '')
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_invoices(self):
        """获取所有发票"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invoices ORDER BY invoice_date DESC')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_invoices(self, keyword):
        """搜索发票"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM invoices 
            WHERE invoice_number LIKE ? OR buyer_name LIKE ? 
            OR seller_name LIKE ? OR notes LIKE ?
            ORDER BY invoice_date DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_invoice(self, invoice_id):
        """删除发票"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM invoices WHERE id = ?', (invoice_id,))
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), SUM(total_amount), SUM(tax_amount) FROM invoices')
        stats = cursor.fetchone()
        
        conn.close()
        return {
            'total_count': stats[0] or 0,
            'total_amount': stats[1] or 0,
            'total_tax': stats[2] or 0
        }


class InvoiceOCR:
    """发票OCR识别类"""
    
    def __init__(self):
        self.ocr = None
        self.use_paddle = False
        if OCR_AVAILABLE:
            try:
                if USE_PADDLEOCR:
                    # 使用PaddleOCR（中文识别效果更好）
                    self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
                    self.use_paddle = True
                else:
                    # 使用pytesseract
                    self.use_paddle = False
            except Exception as e:
                print(f"OCR初始化失败: {e}")
                self.ocr = None
                self.use_paddle = False
    
    def recognize_image(self, image_path):
        """识别图片中的文字"""
        if not OCR_AVAILABLE or not self.ocr:
            return None
        
        try:
            if self.use_paddle:
                # 使用PaddleOCR
                result = self.ocr.ocr(image_path, cls=True)
                # 提取所有文本
                texts = []
                if result and result[0]:
                    for line in result[0]:
                        if line and len(line) > 1:
                            texts.append(line[1][0])
                return '\n'.join(texts)
            else:
                # 使用pytesseract
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                return text
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None
    
    def parse_invoice_info(self, ocr_text):
        """解析OCR识别的文本，提取发票信息"""
        if not ocr_text:
            return {}
        
        info = {}
        lines = ocr_text.split('\n')
        full_text = ocr_text
        
        # 提取发票号码（通常包含8位或12位数字）
        invoice_number_patterns = [
            r'发票号码[：:]\s*([0-9]{8,12})',
            r'号码[：:]\s*([0-9]{8,12})',
            r'No[.:]\s*([0-9]{8,12})',
            r'([0-9]{8,12})'
        ]
        for pattern in invoice_number_patterns:
            match = re.search(pattern, full_text)
            if match:
                info['invoice_number'] = match.group(1)
                break
        
        # 提取开票日期（格式：YYYY-MM-DD 或 YYYY年MM月DD日）
        date_patterns = [
            r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'开票日期[：:]\s*(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, full_text)
            if match:
                year, month, day = match.groups()
                info['invoice_date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                break
        
        # 提取购买方名称
        buyer_patterns = [
            r'购买方[：:]\s*([^\n]+)',
            r'买方[：:]\s*([^\n]+)',
            r'名称[：:]\s*([^\n]+)'
        ]
        for pattern in buyer_patterns:
            match = re.search(pattern, full_text)
            if match:
                buyer_name = match.group(1).strip()
                # 清理常见后缀
                buyer_name = re.sub(r'[税号|纳税人识别号|统一社会信用代码].*', '', buyer_name)
                if len(buyer_name) > 2:
                    info['buyer_name'] = buyer_name
                    break
        
        # 提取购买方税号（18位数字或字母数字组合）
        buyer_tax_patterns = [
            r'购买方.*?[税号|纳税人识别号|统一社会信用代码][：:]\s*([A-Z0-9]{15,20})',
            r'税号[：:]\s*([A-Z0-9]{15,20})',
            r'纳税人识别号[：:]\s*([A-Z0-9]{15,20})'
        ]
        for pattern in buyer_tax_patterns:
            match = re.search(pattern, full_text)
            if match:
                info['buyer_tax_id'] = match.group(1)
                break
        
        # 提取销售方名称
        seller_patterns = [
            r'销售方[：:]\s*([^\n]+)',
            r'卖方[：:]\s*([^\n]+)'
        ]
        for pattern in seller_patterns:
            match = re.search(pattern, full_text)
            if match:
                seller_name = match.group(1).strip()
                seller_name = re.sub(r'[税号|纳税人识别号|统一社会信用代码].*', '', seller_name)
                if len(seller_name) > 2:
                    info['seller_name'] = seller_name
                    break
        
        # 提取销售方税号
        seller_tax_patterns = [
            r'销售方.*?[税号|纳税人识别号|统一社会信用代码][：:]\s*([A-Z0-9]{15,20})'
        ]
        for pattern in seller_tax_patterns:
            match = re.search(pattern, full_text)
            if match:
                info['seller_tax_id'] = match.group(1)
                break
        
        # 提取金额（不含税金额）
        amount_patterns = [
            r'金额[：:]\s*[¥￥]?\s*([0-9,]+\.?\d*)',
            r'不含税金额[：:]\s*[¥￥]?\s*([0-9,]+\.?\d*)',
            r'[¥￥]\s*([0-9,]+\.?\d*)\s*元'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, full_text)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    info['amount'] = float(amount_str)
                except:
                    pass
                break
        
        # 提取税额
        tax_patterns = [
            r'税额[：:]\s*[¥￥]?\s*([0-9,]+\.?\d*)',
            r'[¥￥]\s*([0-9,]+\.?\d*)\s*元.*?税'
        ]
        for pattern in tax_patterns:
            match = re.search(pattern, full_text)
            if match:
                tax_str = match.group(1).replace(',', '')
                try:
                    info['tax_amount'] = float(tax_str)
                except:
                    pass
                break
        
        # 提取合计金额
        total_patterns = [
            r'合计[：:]\s*[¥￥]?\s*([0-9,]+\.?\d*)',
            r'价税合计[：:]\s*[¥￥]?\s*([0-9,]+\.?\d*)',
            r'总计[：:]\s*[¥￥]?\s*([0-9,]+\.?\d*)'
        ]
        for pattern in total_patterns:
            match = re.search(pattern, full_text)
            if match:
                total_str = match.group(1).replace(',', '')
                try:
                    info['total_amount'] = float(total_str)
                except:
                    pass
                break
        
        # 如果没有识别到合计，尝试用金额+税额计算
        if 'total_amount' not in info and 'amount' in info and 'tax_amount' in info:
            info['total_amount'] = info['amount'] + info['tax_amount']
        elif 'total_amount' not in info and 'amount' in info:
            # 假设税率为13%
            info['tax_amount'] = round(info['amount'] * 0.13, 2)
            info['total_amount'] = info['amount'] + info['tax_amount']
        
        return info


class InvoiceManagerApp:
    """发票管理主应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title('发票管理系统 - 单机版')
        self.root.geometry('1200x700')
        
        self.db = InvoiceDatabase()
        
        self.create_menu()
        self.create_widgets()
        self.refresh_invoice_list()
        self.update_statistics()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='导出数据', command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=help_menu)
        help_menu.add_command(label='关于', command=self.show_about)
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text='新增发票', command=self.add_invoice).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='删除发票', command=self.delete_invoice).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='刷新', command=self.refresh_invoice_list).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text='搜索:').pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_invoices())
        ttk.Entry(toolbar, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=2)
        
        # 统计信息面板
        stats_frame = ttk.LabelFrame(self.root, text='统计信息')
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_label = ttk.Label(
            stats_frame, 
            text='发票总数: 0 | 总金额: ¥0.00 | 总税额: ¥0.00',
            font=('Arial', 10, 'bold')
        )
        self.stats_label.pack(pady=5)
        
        # 发票列表
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ('ID', '发票号码', '开票日期', '购买方', '销售方', '金额', '税额', '合计', '状态')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列宽
        self.tree.heading('ID', text='ID')
        self.tree.heading('发票号码', text='发票号码')
        self.tree.heading('开票日期', text='开票日期')
        self.tree.heading('购买方', text='购买方')
        self.tree.heading('销售方', text='销售方')
        self.tree.heading('金额', text='金额')
        self.tree.heading('税额', text='税额')
        self.tree.heading('合计', text='合计')
        self.tree.heading('状态', text='状态')
        
        self.tree.column('ID', width=50)
        self.tree.column('发票号码', width=120)
        self.tree.column('开票日期', width=100)
        self.tree.column('购买方', width=150)
        self.tree.column('销售方', width=150)
        self.tree.column('金额', width=100)
        self.tree.column('税额', width=100)
        self.tree.column('合计', width=100)
        self.tree.column('状态', width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击查看详情
        self.tree.bind('<Double-1>', self.view_invoice_detail)
    
    def add_invoice(self):
        """添加发票对话框"""
        dialog = InvoiceDialog(self.root, self.db)
        self.root.wait_window(dialog.dialog)
        self.refresh_invoice_list()
        self.update_statistics()
    
    def delete_invoice(self):
        """删除选中的发票"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('警告', '请先选择要删除的发票')
            return
        
        if messagebox.askyesno('确认', '确定要删除选中的发票吗？'):
            item = self.tree.item(selected[0])
            invoice_id = item['values'][0]
            self.db.delete_invoice(invoice_id)
            self.refresh_invoice_list()
            self.update_statistics()
            messagebox.showinfo('成功', '发票已删除')
    
    def view_invoice_detail(self, event):
        """查看发票详情"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            invoice_id = item['values'][0]
            invoices = self.db.get_all_invoices()
            for inv in invoices:
                if inv[0] == invoice_id:
                    self.show_invoice_detail(inv)
                    break
    
    def show_invoice_detail(self, invoice):
        """显示发票详情窗口"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title('发票详情')
        detail_window.geometry('500x400')
        
        fields = [
            ('发票号码', invoice[1]),
            ('开票日期', invoice[2]),
            ('购买方名称', invoice[3]),
            ('购买方税号', invoice[4]),
            ('销售方名称', invoice[5]),
            ('销售方税号', invoice[6]),
            ('金额', f'¥{invoice[7]:.2f}'),
            ('税额', f'¥{invoice[8]:.2f}'),
            ('合计', f'¥{invoice[9]:.2f}'),
            ('发票类型', invoice[10]),
            ('状态', invoice[11]),
            ('备注', invoice[12] or '')
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(detail_window, text=f'{label}:', font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=5
            )
            ttk.Label(detail_window, text=str(value)).grid(
                row=i, column=1, sticky=tk.W, padx=10, pady=5
            )
    
    def search_invoices(self):
        """搜索发票"""
        keyword = self.search_var.get()
        if keyword:
            invoices = self.db.search_invoices(keyword)
        else:
            invoices = self.db.get_all_invoices()
        
        self.update_tree(invoices)
    
    def refresh_invoice_list(self):
        """刷新发票列表"""
        invoices = self.db.get_all_invoices()
        self.update_tree(invoices)
    
    def update_tree(self, invoices):
        """更新表格数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新数据
        for inv in invoices:
            self.tree.insert('', tk.END, values=(
                inv[0],  # ID
                inv[1],  # 发票号码
                inv[2],  # 开票日期
                inv[3],  # 购买方
                inv[5],  # 销售方
                f'¥{inv[7]:.2f}',  # 金额
                f'¥{inv[8]:.2f}',  # 税额
                f'¥{inv[9]:.2f}',  # 合计
                inv[11]  # 状态
            ))
    
    def update_statistics(self):
        """更新统计信息"""
        stats = self.db.get_statistics()
        self.stats_label.config(
            text=f'发票总数: {stats["total_count"]} | '
                 f'总金额: ¥{stats["total_amount"]:.2f} | '
                 f'总税额: ¥{stats["total_tax"]:.2f}'
        )
    
    def export_data(self):
        """导出数据"""
        filename = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON文件', '*.json'), ('所有文件', '*.*')]
        )
        
        if filename:
            invoices = self.db.get_all_invoices()
            data = []
            for inv in invoices:
                data.append({
                    'id': inv[0],
                    'invoice_number': inv[1],
                    'invoice_date': inv[2],
                    'buyer_name': inv[3],
                    'buyer_tax_id': inv[4],
                    'seller_name': inv[5],
                    'seller_tax_id': inv[6],
                    'amount': inv[7],
                    'tax_amount': inv[8],
                    'total_amount': inv[9],
                    'invoice_type': inv[10],
                    'status': inv[11],
                    'notes': inv[12]
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo('成功', f'数据已导出到: {filename}')
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            '关于',
            '发票管理系统 - 单机版\n\n'
            '版本: 1.0\n'
            '功能: 发票录入、查询、统计、导出\n'
            '数据库: SQLite'
        )


class InvoiceDialog:
    """发票录入对话框"""
    
    def __init__(self, parent, db):
        self.db = db
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('新增发票')
        self.dialog.geometry('500x600')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """创建对话框组件"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 发票号码
        ttk.Label(frame, text='发票号码 *:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.invoice_number = ttk.Entry(frame, width=30)
        self.invoice_number.grid(row=0, column=1, pady=5)
        
        # 开票日期
        ttk.Label(frame, text='开票日期 *:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.invoice_date = ttk.Entry(frame, width=30)
        self.invoice_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.invoice_date.grid(row=1, column=1, pady=5)
        
        # 购买方名称
        ttk.Label(frame, text='购买方名称:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.buyer_name = ttk.Entry(frame, width=30)
        self.buyer_name.grid(row=2, column=1, pady=5)
        
        # 购买方税号
        ttk.Label(frame, text='购买方税号:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.buyer_tax_id = ttk.Entry(frame, width=30)
        self.buyer_tax_id.grid(row=3, column=1, pady=5)
        
        # 销售方名称
        ttk.Label(frame, text='销售方名称:').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.seller_name = ttk.Entry(frame, width=30)
        self.seller_name.grid(row=4, column=1, pady=5)
        
        # 销售方税号
        ttk.Label(frame, text='销售方税号:').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.seller_tax_id = ttk.Entry(frame, width=30)
        self.seller_tax_id.grid(row=5, column=1, pady=5)
        
        # 金额
        ttk.Label(frame, text='金额 *:').grid(row=6, column=0, sticky=tk.W, pady=5)
        self.amount = ttk.Entry(frame, width=30)
        self.amount.grid(row=6, column=1, pady=5)
        
        # 税额
        ttk.Label(frame, text='税额:').grid(row=7, column=0, sticky=tk.W, pady=5)
        self.tax_amount = ttk.Entry(frame, width=30)
        self.tax_amount.insert(0, '0')
        self.tax_amount.grid(row=7, column=1, pady=5)
        
        # 合计
        ttk.Label(frame, text='合计 *:').grid(row=8, column=0, sticky=tk.W, pady=5)
        self.total_amount = ttk.Entry(frame, width=30)
        self.total_amount.grid(row=8, column=1, pady=5)
        
        # 发票类型
        ttk.Label(frame, text='发票类型:').grid(row=9, column=0, sticky=tk.W, pady=5)
        self.invoice_type = ttk.Combobox(frame, width=27, values=['增值税发票', '普通发票', '电子发票'])
        self.invoice_type.set('增值税发票')
        self.invoice_type.grid(row=9, column=1, pady=5)
        
        # 状态
        ttk.Label(frame, text='状态:').grid(row=10, column=0, sticky=tk.W, pady=5)
        self.status = ttk.Combobox(frame, width=27, values=['正常', '作废', '红冲'])
        self.status.set('正常')
        self.status.grid(row=10, column=1, pady=5)
        
        # 备注
        ttk.Label(frame, text='备注:').grid(row=11, column=0, sticky=tk.W, pady=5)
        self.notes = tk.Text(frame, width=30, height=4)
        self.notes.grid(row=11, column=1, pady=5)
        
        # OCR识别按钮
        ocr_frame = ttk.Frame(frame)
        ocr_frame.grid(row=12, column=0, columnspan=2, pady=10)
        
        if OCR_AVAILABLE:
            ttk.Button(ocr_frame, text='📷 OCR识别发票', command=self.ocr_recognize).pack(side=tk.LEFT, padx=5)
        else:
            ocr_info = ttk.Label(
                ocr_frame, 
                text='提示: 安装OCR库以启用识别功能 (pip install paddleocr 或 pip install pytesseract pillow)',
                foreground='gray',
                font=('Arial', 8)
            )
            ocr_info.pack()
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=13, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text='保存', command=self.save_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 初始化OCR
        self.ocr_engine = InvoiceOCR() if OCR_AVAILABLE else None
    
    def save_invoice(self):
        """保存发票"""
        try:
            invoice_data = {
                'invoice_number': self.invoice_number.get().strip(),
                'invoice_date': self.invoice_date.get().strip(),
                'buyer_name': self.buyer_name.get().strip(),
                'buyer_tax_id': self.buyer_tax_id.get().strip(),
                'seller_name': self.seller_name.get().strip(),
                'seller_tax_id': self.seller_tax_id.get().strip(),
                'amount': float(self.amount.get() or 0),
                'tax_amount': float(self.tax_amount.get() or 0),
                'total_amount': float(self.total_amount.get() or 0),
                'invoice_type': self.invoice_type.get(),
                'status': self.status.get(),
                'notes': self.notes.get('1.0', tk.END).strip()
            }
            
            # 验证必填字段
            if not invoice_data['invoice_number']:
                messagebox.showerror('错误', '请输入发票号码')
                return
            
            if not invoice_data['invoice_date']:
                messagebox.showerror('错误', '请输入开票日期')
                return
            
            if invoice_data['amount'] <= 0:
                messagebox.showerror('错误', '金额必须大于0')
                return
            
            # 保存到数据库
            if self.db.add_invoice(invoice_data):
                messagebox.showinfo('成功', '发票已保存')
                self.dialog.destroy()
            else:
                messagebox.showerror('错误', '发票号码已存在，请检查')
        
        except ValueError:
            messagebox.showerror('错误', '请输入有效的数字')
        except Exception as e:
            messagebox.showerror('错误', f'保存失败: {str(e)}')
    
    def ocr_recognize(self):
        """OCR识别发票图片"""
        if not self.ocr_engine:
            messagebox.showwarning('提示', 'OCR功能未启用，请先安装OCR库')
            return
        
        # 选择图片文件
        image_path = filedialog.askopenfilename(
            title='选择发票图片',
            filetypes=[
                ('图片文件', '*.jpg *.jpeg *.png *.bmp *.gif'),
                ('所有文件', '*.*')
            ]
        )
        
        if not image_path:
            return
        
        # 显示识别进度
        progress_window = tk.Toplevel(self.dialog)
        progress_window.title('OCR识别中')
        progress_window.geometry('300x100')
        progress_window.transient(self.dialog)
        
        progress_label = ttk.Label(progress_window, text='正在识别发票图片，请稍候...')
        progress_label.pack(pady=20)
        progress_window.update()
        
        try:
            # 执行OCR识别
            ocr_text = self.ocr_engine.recognize_image(image_path)
            
            if not ocr_text:
                progress_window.destroy()
                messagebox.showerror('错误', 'OCR识别失败，请检查图片质量或重试')
                return
            
            # 解析发票信息
            invoice_info = self.ocr_engine.parse_invoice_info(ocr_text)
            
            progress_window.destroy()
            
            # 显示识别结果预览
            preview_text = "识别到的信息：\n\n"
            for key, value in invoice_info.items():
                preview_text += f"{key}: {value}\n"
            
            preview_text += f"\n完整OCR文本（前500字符）：\n{ocr_text[:500]}..."
            
            # 询问是否使用识别结果
            result_window = tk.Toplevel(self.dialog)
            result_window.title('OCR识别结果')
            result_window.geometry('600x500')
            result_window.transient(self.dialog)
            
            text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', preview_text)
            text_widget.config(state=tk.DISABLED)
            
            button_frame = ttk.Frame(result_window)
            button_frame.pack(pady=10)
            
            def apply_ocr_result():
                # 填充表单
                if 'invoice_number' in invoice_info:
                    self.invoice_number.delete(0, tk.END)
                    self.invoice_number.insert(0, invoice_info['invoice_number'])
                
                if 'invoice_date' in invoice_info:
                    self.invoice_date.delete(0, tk.END)
                    self.invoice_date.insert(0, invoice_info['invoice_date'])
                
                if 'buyer_name' in invoice_info:
                    self.buyer_name.delete(0, tk.END)
                    self.buyer_name.insert(0, invoice_info['buyer_name'])
                
                if 'buyer_tax_id' in invoice_info:
                    self.buyer_tax_id.delete(0, tk.END)
                    self.buyer_tax_id.insert(0, invoice_info['buyer_tax_id'])
                
                if 'seller_name' in invoice_info:
                    self.seller_name.delete(0, tk.END)
                    self.seller_name.insert(0, invoice_info['seller_name'])
                
                if 'seller_tax_id' in invoice_info:
                    self.seller_tax_id.delete(0, tk.END)
                    self.seller_tax_id.insert(0, invoice_info['seller_tax_id'])
                
                if 'amount' in invoice_info:
                    self.amount.delete(0, tk.END)
                    self.amount.insert(0, str(invoice_info['amount']))
                
                if 'tax_amount' in invoice_info:
                    self.tax_amount.delete(0, tk.END)
                    self.tax_amount.insert(0, str(invoice_info['tax_amount']))
                
                if 'total_amount' in invoice_info:
                    self.total_amount.delete(0, tk.END)
                    self.total_amount.insert(0, str(invoice_info['total_amount']))
                
                result_window.destroy()
                messagebox.showinfo('成功', 'OCR识别结果已填入表单，请检查并完善信息')
            
            ttk.Button(button_frame, text='应用识别结果', command=apply_ocr_result).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text='关闭', command=result_window.destroy).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror('错误', f'OCR识别失败: {str(e)}')


def main():
    """主函数"""
    root = tk.Tk()
    app = InvoiceManagerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
