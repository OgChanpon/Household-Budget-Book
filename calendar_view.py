# calendar_view_refactored.py
import tkinter as tk
from tkinter import ttk
import sqlite3
import calendar
from datetime import datetime
from collections import defaultdict

calendar.setfirstweekday(calendar.SUNDAY)

class CalendarApp:
    # (以前の calendar_view.py のコードとほぼ同じ。変更点は__init__のみ)
    def __init__(self, root):
        self.root = root
        self.root.title("家計簿 - カレンダー表示")
        self.root.geometry("650x450")
        
        self.current_date = datetime.now()
        
        header_frame = ttk.Frame(self.root, padding=5)
        header_frame.pack(fill=tk.X)

        self.prev_button = ttk.Button(header_frame, text="< 前の月", command=self.prev_month)
        self.prev_button.pack(side=tk.LEFT)
        self.next_button = ttk.Button(header_frame, text="次の月 >", command=self.next_month)
        self.next_button.pack(side=tk.RIGHT)
        self.month_label = ttk.Label(header_frame, font=("", 16, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)

        self.calendar_frame = ttk.Frame(self.root, padding=5)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)

        self.draw_calendar()
    
    # ... (fetch_month_data, draw_calendar, prev_month, next_month メソッドは変更なし) ...
    def fetch_month_data(self, year, month):
        daily_totals = defaultdict(lambda: {"収入": 0, "支出": 0})
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        try:
            conn = sqlite3.connect('kakeibo.db')
            cursor = conn.cursor()
            cursor.execute('SELECT date, type, amount FROM transactions WHERE date BETWEEN ? AND ?', (start_date, end_date))
            for row in cursor.fetchall():
                day = int(row[0].split('-')[2])
                trans_type = row[1]
                amount = row[2]
                daily_totals[day][trans_type] += amount
            conn.close()
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
        return daily_totals

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        year = self.current_date.year
        month = self.current_date.month
        self.month_label.config(text=f"{year}年 {month}月")
        daily_data = self.fetch_month_data(year, month)
        days_of_week = ["日", "月", "火", "水", "木", "金", "土"]
        for i, day_name in enumerate(days_of_week):
            label = ttk.Label(self.calendar_frame, text=day_name, width=12, anchor=tk.CENTER)
            label.grid(row=0, column=i, sticky='nsew')
            if day_name == "日": label.config(foreground="red")
            elif day_name == "土": label.config(foreground="blue")
        month_calendar = calendar.monthcalendar(year, month)
        for row_idx, week in enumerate(month_calendar, start=1):
            for col_idx, day in enumerate(week):
                if day == 0: continue
                day_frame = ttk.Frame(self.calendar_frame, borderwidth=1, relief="solid")
                day_frame.grid(row=row_idx, column=col_idx, sticky='nsew', ipady=5)
                ttk.Label(day_frame, text=str(day)).pack(anchor=tk.NW)
                income = daily_data[day]["収入"]
                expense = daily_data[day]["支出"]
                if income > 0: ttk.Label(day_frame, text=f"+{income:,}", foreground="blue").pack(anchor=tk.CENTER)
                if expense > 0: ttk.Label(day_frame, text=f"-{expense:,}", foreground="red").pack(anchor=tk.CENTER)
                if income == 0 and expense == 0: ttk.Label(day_frame, text="0円", foreground="gray").pack(anchor=tk.CENTER)
        for i in range(7): self.calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(month_calendar) + 1): self.calendar_frame.grid_rowconfigure(i, weight=1)

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