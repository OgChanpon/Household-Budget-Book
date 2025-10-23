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
        
        self.current_date = datetime.now()
        
        # --- ヘッダーフレーム (年月表示とナビゲーションボタン) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=5, padx=5)

        prev_button = ctk.CTkButton(header_frame, text="<", command=self.prev_month, width=40)
        prev_button.pack(side="left")

        next_button = ctk.CTkButton(header_frame, text=">", command=self.next_month, width=40)
        next_button.pack(side="right")

        self.month_label = ctk.CTkLabel(header_frame, font=ctk.CTkFont(size=18, weight="bold"))
        self.month_label.pack(side="left", expand=True, fill="x")

        # --- カレンダー本体のフレーム ---
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
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

        self.month_label.configure(text=f"{year}年 {month}月")
        daily_data = self.fetch_month_data(year, month)

        days_of_week = ["日", "月", "火", "水", "木", "金", "土"]
        for i, day_name in enumerate(days_of_week):
            label = ctk.CTkLabel(self.calendar_frame, text=day_name, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            if day_name == "日": label.configure(text_color="red")
            elif day_name == "土": label.configure(text_color="blue")

        month_calendar = calendar.monthcalendar(year, month)
        for row_idx, week in enumerate(month_calendar, start=1):
            for col_idx, day in enumerate(week):
                if day == 0: continue
                
                day_frame = ctk.CTkFrame(self.calendar_frame, border_width=1)
                day_frame.grid(row=row_idx, column=col_idx, sticky='nsew', padx=1, pady=1)
                day_frame.grid_rowconfigure(1, weight=1) # 中央寄せのために設定
                day_frame.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(day_frame, text=str(day)).grid(row=0, column=0, sticky="n", padx=2)
                
                content_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
                content_frame.grid(row=1, column=0)

                income = daily_data[day]["収入"]
                expense = daily_data[day]["支出"]
                
                if income > 0: ctk.CTkLabel(content_frame, text=f"{income:,}", text_color="#3377FF").pack()
                if expense > 0: ctk.CTkLabel(content_frame, text=f"{expense:,}", text_color="#FF3333").pack()

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