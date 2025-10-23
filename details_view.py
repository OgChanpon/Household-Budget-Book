# details_view.py
import customtkinter as ctk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import calendar

# Matplotlibのインポート
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Matplotlibの日本語設定 (環境に合わせて調整が必要な場合があります)
try:
    plt.rcParams['font.sans-serif'] = ['Yu Gothic', 'Hiragino Maru Gothic Pro', 'Meiryo', 'MS Gothic']
except:
    pass

class DetailsView(ctk.CTkFrame):
    # ▼▼▼ 変更点: __init__メソッドに app 引数を追加 ▼▼▼
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app # メインアプリのインスタンスを保持
        self.pack(fill="both", expand=True, padx=10, pady=10)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 詳細タブの中にさらにタブを作成 ---
        self.details_tab_view = ctk.CTkTabview(self)
        self.details_tab_view.grid(row=0, column=0, sticky="nsew")
        
        self.details_tab_view.add("年間収支グラフ")
        # 他のタブも同様に追加可能...

        # --- 「年間収支グラフ」タブの中身を作成 ---
        savings_tab = self.details_tab_view.tab("年間収支グラフ")
        savings_tab.grid_rowconfigure(1, weight=1)
        savings_tab.grid_columnconfigure(0, weight=1)

        # グラフ描画エリア
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=savings_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 年セレクター
        selector_frame = ctk.CTkFrame(savings_tab)
        selector_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(selector_frame, text="表示年:").pack(side="left", padx=5)
        self.year_entry = ctk.CTkEntry(selector_frame, width=80)
        self.year_entry.insert(0, str(datetime.now().year))
        self.year_entry.pack(side="left")
        ctk.CTkButton(selector_frame, text="グラフ更新", command=self.update_display).pack(side="left", padx=5)

    def fetch_data(self, query, params=()):
        try:
            conn = sqlite3.connect('kakeibo.db')
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return []
    
    def update_display(self):
        try:
            year = int(self.year_entry.get())
        except ValueError:
            messagebox.showerror("入力エラー", "年は数字で入力してください。")
            return
            
        self.draw_bar_chart(year)

    def draw_bar_chart(self, year):
        monthly_balances = {month: 0 for month in range(1, 13)}

        income_data = self.fetch_data("SELECT strftime('%m', date), SUM(amount) FROM transactions WHERE type='収入' AND strftime('%Y', date)=? GROUP BY strftime('%m', date)", (str(year),))
        for month_str, total in income_data:
            monthly_balances[int(month_str)] += total

        expense_data = self.fetch_data("SELECT strftime('%m', date), SUM(amount) FROM transactions WHERE type='支出' AND strftime('%Y', date)=? GROUP BY strftime('%m', date)", (str(year),))
        for month_str, total in expense_data:
            monthly_balances[int(month_str)] -= total
        
        self.ax.clear()

        months = [f"{m}月" for m in range(1, 13)]
        balances = [monthly_balances[m] for m in range(1, 13)]
        colors = ['#3377FF' if b >= 0 else '#FF3333' for b in balances]
        
        self.ax.bar(months, balances, color=colors)
        self.ax.set_title(f"{year}年 月別収支")
        self.ax.set_ylabel("収支 (円)")
        self.ax.axhline(0, color='gray', linewidth=0.8)
        self.fig.tight_layout()

        self.canvas.draw()