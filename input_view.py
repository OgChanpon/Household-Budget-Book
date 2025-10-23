import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

class InputWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("家計簿 - 入力画面")
        self.root.geometry("350x270")

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.type_var = tk.StringVar(value="支出")
        ttk.Label(frame, text="収支タイプ:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(frame, text="支出", variable=self.type_var, value="支出").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="収入", variable=self.type_var, value="収入").grid(row=0, column=2, sticky=tk.W)

        ttk.Label(frame, text="日付:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.date_entry = ttk.Entry(frame)
        self.date_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(frame, text="金額 (円):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=2, column=1, columnspan=2, sticky=tk.EW)

        ttk.Label(frame, text="メモ:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.memo_entry = ttk.Entry(frame)
        self.memo_entry.grid(row=3, column=1, columnspan=2, sticky=tk.EW)

        ttk.Label(frame, text="支払い方法:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.payment_method_entry = ttk.Entry(frame)
        self.payment_method_entry.grid(row=4, column=1, columnspan=2, sticky=tk.EW)

        save_button = ttk.Button(frame, text="保存", command=self.save_data)
        save_button.grid(row=5, column=1, columnspan=2, pady=10, sticky=tk.EW)

    def save_data(self):
        date_str = self.date_entry.get()
        trans_type = self.type_var.get()
        amount = self.amount_entry.get()
        memo = self.memo_entry.get()
        payment_method = self.payment_method_entry.get()
        
        if not date_str or not amount:
            messagebox.showwarning("入力エラー", "日付と金額は必須です。", parent=self.root)
            return
        
        self.add_transaction(date_str, trans_type, amount, memo, payment_method)

    def add_transaction(self, date_str, trans_type, amount, memo, payment_method):
        if not amount.isdigit() or int(amount) <= 0:
            messagebox.showerror("エラー", "金額は正の整数で入力してください。", parent=self.root)
            return

        try:
            conn = sqlite3.connect('kakeibo.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (date, type, amount, memo, payment_method)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, trans_type, int(amount), memo, payment_method))
            conn.commit()
            conn.close()
            messagebox.showinfo("成功", "データを保存しました。", parent=self.root)
            self.clear_entries()
        except sqlite3.Error as e:
            messagebox.showerror("データベースエラー", f"データの保存に失敗しました。\n{e}", parent=self.root)

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("支出")
        self.amount_entry.delete(0, tk.END)
        self.memo_entry.delete(0, tk.END)
        self.payment_method_entry.delete(0, tk.END)