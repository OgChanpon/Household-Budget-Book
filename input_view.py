# input_view.py
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3
import customtkinter as ctk
from tkcalendar import Calendar

class InputView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.selected_date = datetime.now().date()
        self.popup_frame = None

        # --- UIウィジェット ---
        self.type_var = tk.StringVar(value="支出")
        self.seg_button = ctk.CTkSegmentedButton(self, values=["支出", "収入"], variable=self.type_var)
        self.seg_button.pack(pady=10, fill="x")

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="金額 (円)")
        self.amount_entry.pack(pady=10, fill="x")

        self.memo_entry = ctk.CTkEntry(self, placeholder_text="メモ (例: スーパーでの買い物)")
        self.memo_entry.pack(pady=10, fill="x")

        self.payment_method_entry = ctk.CTkEntry(self, placeholder_text="支払い方法 (任意)")
        self.payment_method_entry.pack(pady=10, fill="x")
        
        self.date_button = ctk.CTkButton(self, text=self.selected_date.strftime("%Y-%m-%d"), command=self.pick_date)
        self.date_button.pack(pady=10, fill="x")

        self.save_button = ctk.CTkButton(self, text="保存", command=self.save_data, height=40)
        self.save_button.pack(pady=20, fill="x")

    def pick_date(self):
        if self.popup_frame:
            return

        self.popup_frame = ctk.CTkFrame(self, border_width=2, width=400, height=350)
        
        self.popup_frame.place(relx=0.5, rely=0.55, anchor="center")

        cal = Calendar(self.popup_frame, selectmode='day', date_pattern='y-mm-dd',
                       year=self.selected_date.year, month=self.selected_date.month, day=self.selected_date.day,
                       font="Arial 16",
                       showweeknumbers=False,
                       weekendbackground="white", weekendforeground="black",
                       othermonthbackground="gray90", othermonthforeground="gray50",
                       othermonthwebackground="gray90", othermonthweforeground="gray50")
        cal.pack(pady=10, padx=10, fill="both", expand=True)

        def on_date_select():
            self.selected_date = datetime.strptime(cal.get_date(), "%Y-%m-%d").date()
            self.date_button.configure(text=self.selected_date.strftime("%Y-%m-%d"))
            self.popup_frame.destroy()
            self.popup_frame = None

        select_button = ctk.CTkButton(self.popup_frame, text="決定", command=on_date_select, height=35)
        select_button.pack(pady=(0, 10), padx=10, fill="x")

    def save_data(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        trans_type = self.type_var.get()
        amount = self.amount_entry.get()
        memo = self.memo_entry.get()
        payment_method = self.payment_method_entry.get()
        if not amount:
            messagebox.showwarning("入力エラー", "金額は必須です。")
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
        self.type_var.set("支出")
        self.amount_entry.delete(0, tk.END)
        self.memo_entry.delete(0, tk.END)
        self.payment_method_entry.delete(0, tk.END)