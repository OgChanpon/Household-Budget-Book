# recurring_view.py
import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from datetime import datetime, timedelta

class RecurringView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- このタブ内に、さらにサブタブを作成 ---
        self.sub_tab_view = ctk.CTkTabview(self, command=self.update_display)
        self.sub_tab_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.sub_tab_view.add("サブスク")
        self.sub_tab_view.add("クレジットカード")
        
        # --- 各サブタブの中身を作成 ---
        self._create_subscription_tab(self.sub_tab_view.tab("サブスク"))
        self._create_credit_card_tab(self.sub_tab_view.tab("クレジットカード"))

    def _create_subscription_tab(self, tab):
        tab.grid_rowconfigure(1, weight=1); tab.grid_columnconfigure(0, weight=1)
        
        input_frame = ctk.CTkFrame(tab)
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        name_entry = ctk.CTkEntry(input_frame, placeholder_text="項目名 (例: Netflix)")
        name_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        amount_entry = ctk.CTkEntry(input_frame, placeholder_text="金額", width=100)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        day_entry = ctk.CTkEntry(input_frame, placeholder_text="支払日(日)", width=80)
        day_entry.grid(row=0, column=2, padx=5, pady=5)
        pm_entry = ctk.CTkEntry(input_frame, placeholder_text="支払方法", width=100)
        pm_entry.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkButton(input_frame, text="追加", width=60, command=self._add_subscription).grid(row=0, column=4, padx=5, pady=5)

        list_frame = ctk.CTkScrollableFrame(tab, label_text="登録済み固定費リスト")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        tab.name_entry = name_entry; tab.amount_entry = amount_entry
        tab.day_entry = day_entry; tab.pm_entry = pm_entry; tab.list_frame = list_frame

    def _create_credit_card_tab(self, tab):
        tab.grid_rowconfigure(1, weight=1); tab.grid_columnconfigure(0, weight=1)
        
        input_frame = ctk.CTkFrame(tab)
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        name_entry = ctk.CTkEntry(input_frame, placeholder_text="カード名 (例: 楽天カード)")
        name_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        closing_day_entry = ctk.CTkEntry(input_frame, placeholder_text="締め日(日)", width=100)
        closing_day_entry.grid(row=0, column=1, padx=5, pady=5)
        payment_day_entry = ctk.CTkEntry(input_frame, placeholder_text="支払日(日)", width=100)
        payment_day_entry.grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(input_frame, text="追加", width=60, command=self._add_credit_card).grid(row=0, column=3, padx=5, pady=5)
        
        list_frame = ctk.CTkScrollableFrame(tab, label_text="クレジットカード請求予定額")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        tab.name_entry = name_entry; tab.closing_day_entry = closing_day_entry
        tab.payment_day_entry = payment_day_entry; tab.list_frame = list_frame

    def update_display(self):
        current_sub_tab = self.sub_tab_view.get()
        if current_sub_tab == "サブスク":
            self._update_subscription_list()
        elif current_sub_tab == "クレジットカード":
            self._update_credit_card_list()

    def _update_subscription_list(self):
        tab = self.sub_tab_view.tab("サブスク")
        for widget in tab.list_frame.winfo_children(): widget.destroy()
        conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
        cursor.execute("SELECT * FROM fixed_costs ORDER BY payment_day")
        for item in cursor.fetchall():
            item_id, name, amount, day, pm = item
            item_frame = ctk.CTkFrame(tab.list_frame); item_frame.pack(fill="x", pady=2)
            item_frame.grid_columnconfigure(0, weight=1)
            info_text = f"{day}日: {name} ({pm or '未設定'})"
            ctk.CTkLabel(item_frame, text=info_text).grid(row=0, column=0, sticky="w", padx=10)
            ctk.CTkLabel(item_frame, text=f"{amount:,}円").grid(row=0, column=1, padx=10)
        conn.close()

    def _update_credit_card_list(self):
        tab = self.sub_tab_view.tab("クレジットカード")
        for widget in tab.list_frame.winfo_children(): widget.destroy()
        conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
        cursor.execute("SELECT name, closing_day, payment_day FROM credit_cards ORDER BY name")
        today = datetime.now()
        for name, closing_day, payment_day in cursor.fetchall():
            if today.day <= closing_day:
                end_date = today.replace(day=closing_day)
                start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=closing_day + 1)
                payment_date = today.replace(day=payment_day)
            else:
                start_date = today.replace(day=closing_day + 1)
                end_date = (start_date + timedelta(days=32)).replace(day=closing_day)
                payment_date = (today + timedelta(days=32)).replace(day=payment_day)
            start_str, end_str = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE payment_method = ? AND date BETWEEN ? AND ?",
                           (name, start_str, end_str))
            total_amount = (result[0] if (result := cursor.fetchone()) and result[0] is not None else 0)
            item_frame = ctk.CTkFrame(tab.list_frame, fg_color=("gray90", "gray25"))
            item_frame.pack(fill="x", pady=2); item_frame.grid_columnconfigure(0, weight=1)
            font_big_bold = ctk.CTkFont(size=16, weight="bold")
            card_info = f"{name} ({start_str} ~ {end_str} 利用分)"
            ctk.CTkLabel(item_frame, text=card_info, font=font_big_bold).grid(row=0, column=0, sticky="w", padx=10, pady=2)
            payment_info = f"{payment_date.strftime('%Y-%m-%d')} 支払い予定"
            ctk.CTkLabel(item_frame, text=payment_info, text_color="gray").grid(row=1, column=0, sticky="w", padx=10, pady=2)
            ctk.CTkLabel(item_frame, text=f"{total_amount:,} 円", font=font_big_bold).grid(row=0, column=1, rowspan=2, sticky="e", padx=10)
        conn.close()

    def _add_subscription(self):
        tab = self.sub_tab_view.tab("サブスク")
        name, amount, day, pm = tab.name_entry.get(), tab.amount_entry.get(), tab.day_entry.get(), tab.pm_entry.get()
        if not all([name, amount, day]) or not amount.isdigit() or not day.isdigit():
            messagebox.showerror("エラー", "項目名、金額(数字)、支払日(数字)を正しく入力してください。"); return
        conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
        cursor.execute("INSERT INTO fixed_costs (name, amount, payment_day, payment_method) VALUES (?, ?, ?, ?)",
                       (name, int(amount), int(day), pm))
        conn.commit(); conn.close()
        for entry in [tab.name_entry, tab.amount_entry, tab.day_entry, tab.pm_entry]: entry.delete(0, 'end')
        self.update_display()
    
    def _add_credit_card(self):
        tab = self.sub_tab_view.tab("クレジットカード")
        name, closing_day, payment_day = tab.name_entry.get(), tab.closing_day_entry.get(), tab.payment_day_entry.get()
        if not all([name, closing_day, payment_day]) or not closing_day.isdigit() or not payment_day.isdigit():
            messagebox.showerror("エラー", "カード名、締め日(数字)、支払日(数字)を正しく入力してください。"); return
        try:
            conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
            cursor.execute("INSERT INTO credit_cards (name, closing_day, payment_day) VALUES (?, ?, ?)",
                           (name, int(closing_day), int(payment_day)))
            conn.commit(); conn.close()
            for entry in [tab.name_entry, tab.closing_day_entry, tab.payment_day_entry]: entry.delete(0, 'end')
            self.update_display()
        except sqlite3.IntegrityError:
            messagebox.showerror("エラー", "同じ名前のカードが既に登録されています。")