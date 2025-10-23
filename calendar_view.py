# calendar_view.py
import customtkinter as ctk
import sqlite3
import calendar
from datetime import datetime
from collections import defaultdict

calendar.setfirstweekday(calendar.SUNDAY)

class CalendarView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(2, weight=1) # スクロールリストのために設定
        self.grid_columnconfigure(0, weight=1)
        
        self.current_date = datetime.now()

        # --- 1. ヘッダーフレーム (年月とナビゲーション) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(header_frame, text="<", command=self.prev_month, width=40).grid(row=0, column=0)
        self.month_label = ctk.CTkLabel(header_frame, font=ctk.CTkFont(size=18, weight="bold"))
        self.month_label.grid(row=0, column=1)
        ctk.CTkButton(header_frame, text=">", command=self.next_month, width=40).grid(row=0, column=2)

        # --- 2. 月間合計フレーム ---
        total_frame = ctk.CTkFrame(self)
        total_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        total_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.income_label = ctk.CTkLabel(total_frame, text="収入\n0円", justify="center")
        self.income_label.grid(row=0, column=0)
        self.expense_label = ctk.CTkLabel(total_frame, text="支出\n0円", justify="center")
        self.expense_label.grid(row=0, column=1)
        self.balance_label = ctk.CTkLabel(total_frame, text="合計\n0円", justify="center")
        self.balance_label.grid(row=0, column=2)

        # --- 3. 取引履歴リスト (スクロール可能) ---
        self.history_list = ctk.CTkScrollableFrame(self, label_text="今月の履歴")
        self.history_list.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

    def fetch_month_data(self, year, month):
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        try:
            conn = sqlite3.connect('kakeibo.db')
            cursor = conn.cursor()
            # ORDER BY date DESC で新しい順にソート
            cursor.execute('SELECT date, type, amount, memo FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC', (start_date, end_date))
            transactions = cursor.fetchall()
            conn.close()
            return transactions
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return []

    def draw_calendar(self):
        # 1. ヘッダーの年月を更新
        year = self.current_date.year
        month = self.current_date.month
        self.month_label.configure(text=f"{year}年 {month}月")
        
        # 2. データベースから今月の全データを取得
        transactions = self.fetch_month_data(year, month)
        
        # 3. 月間合計を計算して表示
        total_income = sum(row[2] for row in transactions if row[1] == '収入')
        total_expense = sum(row[2] for row in transactions if row[1] == '支出')
        balance = total_income - total_expense
        self.income_label.configure(text=f"収入\n{total_income:,}円")
        self.expense_label.configure(text=f"支出\n{total_expense:,}円")
        self.balance_label.configure(text=f"合計\n{balance:+,}円")
        
        # 4. 取引履歴リストを更新
        # まずリストを空にする
        for widget in self.history_list.winfo_children():
            widget.destroy()
        
        # 取得したデータをリストに表示
        last_date = None
        for date_str, trans_type, amount, memo in transactions:
            # 日付が変わったら、日付ヘッダーを表示
            if date_str != last_date:
                date_header = ctk.CTkLabel(self.history_list, text=date_str, font=ctk.CTkFont(weight="bold"))
                date_header.pack(fill="x", pady=(10, 2))
                last_date = date_str
            
            # 1件ごとの取引フレーム
            item_frame = ctk.CTkFrame(self.history_list, fg_color="gray85")
            item_frame.pack(fill="x", padx=5, pady=2)
            item_frame.grid_columnconfigure(0, weight=1)
            
            color = "blue" if trans_type == "収入" else "red"
            sign = "+" if trans_type == "収入" else "-"
            
            ctk.CTkLabel(item_frame, text=memo or "(メモなし)", anchor="w").grid(row=0, column=0, sticky="ew", padx=5)
            ctk.CTkLabel(item_frame, text=f"{sign}{amount:,}円", anchor="e", text_color=color).grid(row=0, column=1, padx=5)

    def prev_month(self):
        year, month = self.current_date.year, self.current_date.month
        new_month, new_year = (12, year - 1) if month == 1 else (month - 1, year)
        self.current_date = self.current_date.replace(year=new_year, month=new_month)
        self.draw_calendar()

    def next_month(self):
        year, month = self.current_date.year, self.current_date.month
        new_month, new_year = (1, year + 1) if month == 12 else (month + 1, year)
        self.current_date = self.current_date.replace(year=new_year, month=new_month)
        self.draw_calendar()