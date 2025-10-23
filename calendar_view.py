# calendar_view.py
import customtkinter as ctk
import sqlite3
import calendar
from datetime import datetime, date
from collections import defaultdict
from tkinter import messagebox

calendar.setfirstweekday(calendar.SUNDAY)

class CalendarView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)
        
        self.current_date = datetime.now()
        
        # UI作成部分は変更ありません
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        header_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(header_frame, text="<", command=self.prev_month, width=40).grid(row=0, column=0)
        self.month_label = ctk.CTkLabel(header_frame, font=ctk.CTkFont(size=18, weight="bold"))
        self.month_label.grid(row=0, column=1)
        ctk.CTkButton(header_frame, text=">", command=self.next_month, width=40).grid(row=0, column=2)
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        total_frame = ctk.CTkFrame(self)
        total_frame.grid(row=2, column=0, sticky="ew", padx=5)
        total_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.income_label = ctk.CTkLabel(total_frame, text="収入\n0円", justify="center", font=ctk.CTkFont(size=14))
        self.income_label.grid(row=0, column=0, pady=5)
        self.expense_label = ctk.CTkLabel(total_frame, text="支出\n0円", justify="center", font=ctk.CTkFont(size=14))
        self.expense_label.grid(row=0, column=1, pady=5)
        self.balance_label = ctk.CTkLabel(total_frame, text="合計\n0円", justify="center", font=ctk.CTkFont(size=14))
        self.balance_label.grid(row=0, column=2, pady=5)
        self.history_list = ctk.CTkScrollableFrame(self)
        self.history_list.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0); self.grid_rowconfigure(3, weight=1)

    def fetch_transactions(self, query, params=()):
        try:
            conn = sqlite3.connect('kakeibo.db'); conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return []
    
    def draw_calendar(self):
        year, month = self.current_date.year, self.current_date.month
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        transactions = self.fetch_transactions('SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC', (start_date, end_date))
        
        daily_totals = defaultdict(lambda: {"収入": 0, "支出": 0})
        for t in transactions:
            day = int(t['date'].split('-')[2])
            daily_totals[day][t['type']] += t['amount']
        
        for widget in self.calendar_frame.winfo_children(): widget.destroy()
        self.month_label.configure(text=f"{year}年 {month}月")
        
        days_of_week = ["日", "月", "火", "水", "木", "金", "土"]
        for i, day_name in enumerate(days_of_week):
            label = ctk.CTkLabel(self.calendar_frame, text=day_name, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, sticky='nsew'); 
            if day_name == "日": label.configure(text_color="red")
            elif day_name == "土": label.configure(text_color="blue")

        month_calendar = calendar.monthcalendar(year, month)
        for row_idx, week in enumerate(month_calendar, start=1):
            # ▼▼▼ 変更点2: カレンダーの各行の高さを均等にする ▼▼▼
            self.calendar_frame.grid_rowconfigure(row_idx, weight=1)
            for col_idx, day in enumerate(week):
                if day == 0: continue
                
                day_button = ctk.CTkButton(self.calendar_frame, text="", fg_color="transparent", border_width=1,
                                           command=lambda d=day: self.show_day_menu(d))
                day_button.grid(row=row_idx, column=col_idx, sticky='nsew', padx=1, pady=1)
                day_button.grid_columnconfigure(0, weight=1)
                
                ctk.CTkLabel(day_button, text=str(day), fg_color="transparent").grid(row=0, column=0, sticky="nw", padx=2)
                
                income = daily_totals[day]["収入"]
                expense = daily_totals[day]["支出"]
                
                if income > 0: ctk.CTkLabel(day_button, text=f"+{income:,}", text_color="#3377FF", fg_color="transparent").grid(row=1, column=0)
                if expense > 0: ctk.CTkLabel(day_button, text=f"-{expense:,}", text_color="#FF3333", fg_color="transparent").grid(row=2, column=0)
                
                current_day = date(year, month, day)
                if income == 0 and expense == 0 and current_day < date.today():
                    ctk.CTkLabel(day_button, text="0", text_color="gray", fg_color="transparent").grid(row=1, column=0, rowspan=2)

        for i in range(7): self.calendar_frame.grid_columnconfigure(i, weight=1)

        # 月間合計の更新
        total_income = sum(t['amount'] for t in transactions if t['type'] == '収入')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == '支出')
        balance = total_income - total_expense

        # ▼▼▼ 変更点4: 合計金額の文字色を動的に変更 ▼▼▼
        self.income_label.configure(text=f"収入\n{total_income:,}円", text_color="#3377FF")
        self.expense_label.configure(text=f"支出\n{total_expense:,}円", text_color="#FF3333")
        self.balance_label.configure(text=f"合計\n{balance:+,}円", text_color=("#3377FF" if balance >= 0 else "#FF3333"))
        
        for widget in self.history_list.winfo_children(): widget.destroy()
        last_date = None
        for t in transactions:
            if t['date'] != last_date:
                ctk.CTkLabel(self.history_list, text=t['date'], font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(10, 2))
                last_date = t['date']
            
            # ▼▼▼ 変更点1 & 3: 履歴リストの見た目を改善 ▼▼▼
            item_button = ctk.CTkButton(self.history_list, 
                                        text="", # ボタンのデフォルトテキストを消去
                                        fg_color=("gray90", "gray25"), # 背景色を調整
                                        command=lambda trans=t: self.open_edit_window(trans))
            item_button.pack(fill="x", padx=5, pady=2)
            item_button.grid_columnconfigure(0, weight=1)
            
            # 収入か支出かで文字色を決定
            color = "#3377FF" if t['type'] == "収入" else ("#FF3333" if t['type'] == "支出" else "white")
            sign = "+" if t['type'] == "収入" else "-"
            
            font_big_bold = ctk.CTkFont(size=16, weight="bold")

            memo_label = ctk.CTkLabel(item_button, text=t['memo'] or "(メモなし)", anchor="w", fg_color="transparent")
            memo_label.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            
            amount_label = ctk.CTkLabel(item_button, text=f"{sign}{t['amount']:,}円", anchor="e", fg_color="transparent",
                                        font=ctk.CTkFont(weight="bold"))
            amount_label.configure(text_color=color) # 金額の文字色を設定
            amount_label.grid(row=0, column=1, padx=10, pady=8)

            memo_label.bind("<Button-1>", lambda event, trans=t: self.open_edit_window(trans))
            amount_label.bind("<Button-1>", lambda event, trans=t: self.open_edit_window(trans))

    # (show_day_menu, open_edit_window, prev_month, next_month は変更ありません)
    def show_day_menu(self, day):
        selected_date = date(self.current_date.year, self.current_date.month, day)
        date_str = selected_date.strftime("%Y-%m-%d")
        transactions_on_day = self.fetch_transactions("SELECT * FROM transactions WHERE date = ?", (date_str,))
        popup = ctk.CTkToplevel(self); popup.title(f"{date_str} の操作")
        ctk.CTkButton(popup, text="この日付で新規作成", command=lambda: (self.app.switch_to_input_tab(selected_date), popup.destroy())).pack(pady=10, padx=10, fill="x")
        if transactions_on_day:
            ctk.CTkLabel(popup, text="--- 編集 ---").pack(pady=(5,0))
            for t in transactions_on_day:
                btn_text = f"{t['memo'] or '(メモなし)'}: {t['amount']:,}円"
                ctk.CTkButton(popup, text=btn_text, command=lambda trans=t: (self.open_edit_window(trans), popup.destroy())).pack(pady=2, padx=10, fill="x")
        popup.grab_set()
    def open_edit_window(self, transaction):
        edit_win = ctk.CTkToplevel(self); edit_win.title("取引の編集"); edit_win.geometry("350x350")
        ctk.CTkLabel(edit_win, text=f"ID: {transaction['id']}").pack(pady=5)
        type_var = ctk.StringVar(value=transaction['type'])
        ctk.CTkSegmentedButton(edit_win, values=["支出", "収入"], variable=type_var).pack(pady=5, padx=10, fill="x")
        amount_entry = ctk.CTkEntry(edit_win); amount_entry.insert(0, str(transaction['amount'])); amount_entry.pack(pady=5, padx=10, fill="x")
        memo_entry = ctk.CTkEntry(edit_win); memo_entry.insert(0, transaction['memo'] or ""); memo_entry.pack(pady=5, padx=10, fill="x")
        pm_entry = ctk.CTkEntry(edit_win); pm_entry.insert(0, transaction['payment_method'] or ""); pm_entry.pack(pady=5, padx=10, fill="x")
        def update_transaction():
            new_amount = amount_entry.get()
            if not new_amount.isdigit() or int(new_amount) <= 0: messagebox.showerror("エラー", "金額は正の整数で入力してください。", parent=edit_win); return
            conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
            cursor.execute('UPDATE transactions SET type=?, amount=?, memo=?, payment_method=? WHERE id=?',
                           (type_var.get(), int(new_amount), memo_entry.get(), pm_entry.get(), transaction['id']))
            conn.commit(); conn.close(); edit_win.destroy(); self.draw_calendar()
        def delete_transaction():
            if messagebox.askyesno("確認", "この取引を削除しますか？", parent=edit_win):
                conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id=?", (transaction['id'],)); conn.commit(); conn.close()
                edit_win.destroy(); self.draw_calendar()
        btn_frame = ctk.CTkFrame(edit_win, fg_color="transparent"); btn_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(btn_frame, text="更新", command=update_transaction).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="削除", command=delete_transaction, fg_color="red").pack(side="right", expand=True, padx=5)
        edit_win.grab_set()
    def prev_month(self):
        year, month = self.current_date.year, self.current_date.month
        new_month, new_year = (12, year - 1) if month == 1 else (month - 1, year)
        self.current_date = self.current_date.replace(year=new_year, month=new_month); self.draw_calendar()
    def next_month(self):
        year, month = self.current_date.year, self.current_date.month
        new_month, new_year = (1, year + 1) if month == 12 else (month + 1, year)
        self.current_date = self.current_date.replace(year=new_year, month=new_month); self.draw_calendar()