import customtkinter as ctk
import sqlite3
from datetime import datetime

class DetailsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # --- データ表示用の変数を準備 ---
        self.monthly_income = ctk.StringVar(value="0 円")
        self.monthly_expense = ctk.StringVar(value="0 円")
        self.monthly_balance = ctk.StringVar(value="0 円")
        self.annual_income = ctk.StringVar(value="0 円")
        self.annual_expense = ctk.StringVar(value="0 円")
        self.annual_balance = ctk.StringVar(value="0 円")
        self.total_savings = ctk.StringVar(value="0 円")

        # --- ウィジェットの作成 ---
        selector_frame = ctk.CTkFrame(self)
        selector_frame.pack(fill="x", pady=(0, 15))
        
        current_year = datetime.now().year
        current_month = datetime.now().month

        ctk.CTkLabel(selector_frame, text="年:").pack(side="left", padx=(10, 0))
        self.year_spinbox = ctk.CTkEntry(selector_frame, width=60)
        self.year_spinbox.insert(0, str(current_year))
        self.year_spinbox.pack(side="left", padx=5)

        ctk.CTkLabel(selector_frame, text="月:").pack(side="left")
        self.month_spinbox = ctk.CTkEntry(selector_frame, width=40)
        self.month_spinbox.insert(0, str(current_month))
        self.month_spinbox.pack(side="left", padx=5)

        ctk.CTkButton(selector_frame, text="表示更新", command=self.update_display, width=80).pack(side="right", padx=10)

        # --- 月間収支 ---
        monthly_frame = ctk.CTkFrame(self)
        monthly_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(monthly_frame, text="--- 月間収支 ---", font=ctk.CTkFont(weight="bold")).pack(pady=(5,10))
        ctk.CTkLabel(monthly_frame, text="収入:").pack(padx=10, pady=2, anchor="w")
        ctk.CTkLabel(monthly_frame, textvariable=self.monthly_income, font=ctk.CTkFont(size=16)).pack(padx=10, pady=2, anchor="e")
        ctk.CTkLabel(monthly_frame, text="支出:").pack(padx=10, pady=2, anchor="w")
        ctk.CTkLabel(monthly_frame, textvariable=self.monthly_expense, font=ctk.CTkFont(size=16)).pack(padx=10, pady=2, anchor="e")
        ctk.CTkLabel(monthly_frame, text="収支:").pack(padx=10, pady=2, anchor="w")
        self.m_balance_label = ctk.CTkLabel(monthly_frame, textvariable=self.monthly_balance, font=ctk.CTkFont(size=16, weight="bold"))
        self.m_balance_label.pack(padx=10, pady=2, anchor="e")

        # --- 年間収支 ---
        annual_frame = ctk.CTkFrame(self)
        annual_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(annual_frame, text="--- 年間収支 ---", font=ctk.CTkFont(weight="bold")).pack(pady=(5,10))
        ctk.CTkLabel(annual_frame, text="収入:").pack(padx=10, pady=2, anchor="w")
        ctk.CTkLabel(annual_frame, textvariable=self.annual_income, font=ctk.CTkFont(size=16)).pack(padx=10, pady=2, anchor="e")
        ctk.CTkLabel(annual_frame, text="支出:").pack(padx=10, pady=2, anchor="w")
        ctk.CTkLabel(annual_frame, textvariable=self.annual_expense, font=ctk.CTkFont(size=16)).pack(padx=10, pady=2, anchor="e")
        ctk.CTkLabel(annual_frame, text="収支:").pack(padx=10, pady=2, anchor="w")
        self.a_balance_label = ctk.CTkLabel(annual_frame, textvariable=self.annual_balance, font=ctk.CTkFont(size=16, weight="bold"))
        self.a_balance_label.pack(padx=10, pady=2, anchor="e")

        # --- 総資産 ---
        savings_frame = ctk.CTkFrame(self)
        savings_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(savings_frame, text="総貯金額", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        ctk.CTkLabel(savings_frame, textvariable=self.total_savings, font=ctk.CTkFont(size=22, weight="bold")).pack(pady=5)

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
        try:
            year = int(self.year_spinbox.get())
            month = int(self.month_spinbox.get())
        except ValueError:
            messagebox.showerror("入力エラー", "年と月は数字で入力してください。")
            return

        month_str = f"{year}-{month:02d}"
        m_income = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='収入' AND date LIKE ?", (month_str + '%',))
        m_expense = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='支出' AND date LIKE ?", (month_str + '%',))
        m_balance = m_income - m_expense
        self.monthly_income.set(f"{m_income:,} 円")
        self.monthly_expense.set(f"{m_expense:,} 円")
        self.monthly_balance.set(f"{m_balance:+,} 円")
        self.m_balance_label.configure(text_color="blue" if m_balance >= 0 else "red")
        
        year_str = f"{year}"
        a_income = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='収入' AND date LIKE ?", (year_str + '%',))
        a_expense = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='支出' AND date LIKE ?", (year_str + '%',))
        a_balance = a_income - a_expense
        self.annual_income.set(f"{a_income:,} 円")
        self.annual_expense.set(f"{a_expense:,} 円")
        self.annual_balance.set(f"{a_balance:+,} 円")
        self.a_balance_label.configure(text_color="blue" if a_balance >= 0 else "red")

        total_income = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='収入'")
        total_expense = self.fetch_data("SELECT SUM(amount) FROM transactions WHERE type='支出'")
        savings = total_income - total_expense
        self.total_savings.set(f"{savings:,} 円")