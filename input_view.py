import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3
import customtkinter as ctk

class InputView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        # フレームを親ウィジェット(タブ)いっぱいに広げる
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # 支出／収入の切り替えボタン
        self.type_var = tk.StringVar(value="支出")
        seg_button = ctk.CTkSegmentedButton(self, values=["支出", "収入"], variable=self.type_var)
        seg_button.pack(pady=10, fill="x")

        # 金額
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="金額 (円)")
        self.amount_entry.pack(pady=10, fill="x")

        # メモ
        self.memo_entry = ctk.CTkEntry(self, placeholder_text="メモ (例: スーパーでの買い物)")
        self.memo_entry.pack(pady=10, fill="x")

        # 支払い方法
        self.payment_method_entry = ctk.CTkEntry(self, placeholder_text="支払い方法 (例: 現金, クレカ)")
        self.payment_method_entry.pack(pady=10, fill="x")
        
        # 日付
        self.date_entry = ctk.CTkEntry(self, placeholder_text="日付 (YYYY-MM-DD)")
        self.date_entry.pack(pady=10, fill="x")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # 保存ボタン
        save_button = ctk.CTkButton(self, text="保存", command=self.save_data, height=40)
        save_button.pack(pady=20, fill="x")

    def save_data(self):
        date_str = self.date_entry.get()
        trans_type = self.type_var.get()
        amount = self.amount_entry.get()
        memo = self.memo_entry.get()
        payment_method = self.payment_method_entry.get()
        
        if not date_str or not amount:
            messagebox.showwarning("入力エラー", "日付と金額は必須です。")
            return
        
        self.add_transaction(date_str, trans_type, amount, memo, payment_method)

    def add_transaction(self, date_str, trans_type, amount, memo, payment_method):
        if not amount.isdigit() or int(amount) <= 0:
            messagebox.showerror("エラー", "金額は正の整数で入力してください。")
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
            messagebox.showinfo("成功", "データを保存しました。")
            self.clear_entries()
        except sqlite3.Error as e:
            messagebox.showerror("データベースエラー", f"データの保存に失敗しました。\n{e}")

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("支出")
        self.amount_entry.delete(0, tk.END)
        self.memo_entry.delete(0, tk.END)
        self.payment_method_entry.delete(0, tk.END)