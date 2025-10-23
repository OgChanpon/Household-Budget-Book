# details_view_refactored.py
import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

class DetailsApp:
    # (以前の details_view.py のコードとほぼ同じ。変更点は__init__のみ)
    def __init__(self, root):
        self.root = root
        self.root.title("家計簿 - 詳細表示")
        self.root.geometry("400x350")

        self.monthly_income = tk.StringVar(value="0 円")
        self.monthly_expense = tk.StringVar(value="0 円")
        # ... (他のStringVarも同様) ...
        self.monthly_balance = tk.StringVar(value="0 円")
        self.annual_income = tk.StringVar(value="0 円")
        self.annual_expense = tk.StringVar(value="0 円")
        self.annual_balance = tk.StringVar(value="0 円")
        self.total_savings = tk.StringVar(value="0 円")
        
        main_frame = ttk.Frame(root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        selector_frame = ttk.Frame(main_frame)
        selector_frame.pack(fill=tk.X, pady=(0, 15))
        
        current_year = datetime.now().year
        current_month = datetime.now().month

        ttk.Label(selector_frame, text="年:").pack(side=tk.LEFT)
        self.year_spinbox = ttk.Spinbox(selector_frame, from_=2020, to=2050, width=6)
        self.year_spinbox.set(current_year)
        self.year_spinbox.pack(side=tk.LEFT, padx=(5, 15))
        ttk.Label(selector_frame, text="月:").pack(side=tk.LEFT)
        self.month_spinbox = ttk.Spinbox(selector_frame, from_=1, to=12, width=4)
        self.month_spinbox.set(current_month)
        self.month_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Button(selector_frame, text="表示更新", command=self.update_display).pack(side=tk.RIGHT)

        monthly_frame = ttk.LabelFrame(main_frame, text="月間収支", padding=10)
        monthly_frame.pack(fill=tk.X, pady=5)
        # ... (月間・年間・貯金額のラベル配置は変更なし) ...
        ttk.Label(monthly_frame, text="月間収入:").grid(row=0, column=0, sticky=tk.W)
        self.m_income_label = ttk.Label(monthly_frame, textvariable=self.monthly_income, font=("", 10, "bold"))
        self.m_income_label.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(monthly_frame, text="月間支出:").grid(row=1, column=0, sticky=tk.W)
        self.m_expense_label = ttk.Label(monthly_frame, textvariable=self.monthly_expense, font=("", 10, "bold"))
        self.m_expense_label.grid(row=1, column=1, sticky=tk.E)
        ttk.Label(monthly_frame, text="月間黒字/赤字:").grid(row=2, column=0, sticky=tk.W)
        self.m_balance_label = ttk.Label(monthly_frame, textvariable=self.monthly_balance, font=("", 10, "bold"))
        self.m_balance_label.grid(row=2, column=1, sticky=tk.E)
        monthly_frame.columnconfigure(1, weight=1)

        annual_frame = ttk.LabelFrame(main_frame, text="年間収支", padding=10)
        annual_frame.pack(fill=tk.X, pady=5)
        ttk.Label(annual_frame, text="年間収入:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(annual_frame, textvariable=self.annual_income, font=("", 10, "bold")).grid(row=0, column=1, sticky=tk.E)
        ttk.Label(annual_frame, text="年間支出:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(annual_frame, textvariable=self.annual_expense, font=("", 10, "bold")).grid(row=1, column=1, sticky=tk.E)
        ttk.Label(annual_frame, text="年間黒字/赤字:").grid(row=2, column=0, sticky=tk.W)
        self.a_balance_label = ttk.Label(annual_frame, textvariable=self.annual_balance, font=("", 10, "bold"))
        self.a_balance_label.grid(row=2, column=1, sticky=tk.E)
        annual_frame.columnconfigure(1, weight=1)

        savings_frame = ttk.LabelFrame(main_frame, text="貯金額", padding=10)
        savings_frame.pack(fill=tk.X, pady=5)
        ttk.Label(savings_frame, text="総貯金額:", font=("", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(savings_frame, textvariable=self.total_savings, font=("", 12, "bold")).pack(side=tk.RIGHT)

        self.update_display()
    
    # ... (fetch_data, update_display メソッドは変更なし) ...
    def fetch_data(self, query, params=()):
        try:
            conn = sqlite3.connect('kakeibo.db')
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()[0]
            conn.close()
            return result if result is not None else 0
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return 0

    def update_display(self):
        year, month = int(self.year_spinbox.get()), int(self.month_spinbox.get())
        
        m_income = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='収入' AND date LIKE ?", (f"{year}-{month:02d}%",))
        m_expense = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='支出' AND date LIKE ?", (f"{year}-{month:02d}%",))
        m_balance = m_income - m_expense
        self.monthly_income.set(f"{m_income:,} 円")
        self.monthly_expense.set(f"{m_expense:,} 円")
        self.monthly_balance.set(f"{m_balance:+,} 円")
        self.m_balance_label.config(foreground="blue" if m_balance >= 0 else "red")
        
        a_income = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='収入' AND date LIKE ?", (f"{year}%",))
        a_expense = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='支出' AND date LIKE ?", (f"{year}%",))
        a_balance = a_income - a_expense
        self.annual_income.set(f"{a_income:,} 円")
        self.annual_expense.set(f"{a_expense:,} 円")
        self.annual_balance.set(f"{a_balance:+,} 円")
        self.a_balance_label.config(foreground="blue" if a_balance >= 0 else "red")

        total_income = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='収入'")
        total_expense = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='支出'")
        savings = total_income - total_expense
        self.total_savings.set(f"{savings:,} 円")