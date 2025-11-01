# app.py
import customtkinter as ctk
import setup_database
from datetime import datetime
import sqlite3 # 自動生成ロジックで必要

from input_view import InputView
from calendar_view import CalendarView
from details_view import DetailsView
from recurring_view import RecurringView # 新しくインポート

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def auto_generate_fixed_costs():
    """アプリ起動時に、その月の固定費を自動で生成する"""
    conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
    cursor.execute("SELECT name, amount, payment_day, payment_method FROM fixed_costs")
    today = datetime.now(); year, month = today.year, today.month
    for name, amount, day, pm in cursor.fetchall():
        try:
            target_date = datetime(year, month, day).strftime('%Y-%m-%d')
        except ValueError: continue
        memo_identifier = f"【固定費】{name}"
        cursor.execute("SELECT id FROM transactions WHERE memo = ? AND strftime('%Y-%m', date) = ?",
                       (memo_identifier, f"{year:04d}-{month:02d}"))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO transactions (date, type, amount, memo, payment_method) VALUES (?, '支出', ?, ?, ?)",
                           (target_date, amount, memo_identifier, pm))
            print(f"{target_date}に固定費「{name}」を追加しました。")
    conn.commit(); conn.close()

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("家計簿アプリ"); self.geometry("400x650")
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(master=self, command=self.on_tab_change)
        self.tab_view.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # ▼▼▼ 変更点: タブの構成を変更 ▼▼▼
        self.tab_view.add("入力")
        self.tab_view.add("カレンダー")
        self.tab_view.add("詳細")
        self.tab_view.add("固定・カード") # 新しい親タブ
        
        self.input_frame = InputView(parent=self.tab_view.tab("入力"), app=self)
        self.calendar_frame = CalendarView(parent=self.tab_view.tab("カレンダー"), app=self)
        self.details_frame = DetailsView(parent=self.tab_view.tab("詳細"), app=self)
        self.recurring_frame = RecurringView(parent=self.tab_view.tab("固定・カード"), app=self) # 新しいビューを初期化
        # ▲▲▲ ここまでが変更箇所 ▲▲▲
        
        self.tab_view.set("カレンダー")
        self.on_tab_change()

    def on_tab_change(self):
        current_tab = self.tab_view.get()
        if current_tab == "カレンダー": self.calendar_frame.draw_calendar()
        elif current_tab == "詳細": self.details_frame.update_display()
        elif current_tab == "固定・カード": self.recurring_frame.update_display() # 新しいタブの更新処理

    def switch_to_input_tab(self, date_obj):
        self.tab_view.set("入力")
        self.input_frame.set_date(date_obj)


if __name__ == '__main__':
    setup_database.setup()
    auto_generate_fixed_costs()
    app = MainApp()
    app.mainloop()