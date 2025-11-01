# details_view.py
import customtkinter as ctk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import calendar

class DetailsView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(1, weight=1); self.grid_columnconfigure(0, weight=1)
        
        selector_frame = ctk.CTkFrame(self); selector_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(selector_frame, text="表示年:").pack(side="left", padx=(10, 5))
        self.year_entry = ctk.CTkEntry(selector_frame, width=70); self.year_entry.insert(0, str(datetime.now().year)); self.year_entry.pack(side="left")
        ctk.CTkButton(selector_frame, text="更新", command=self.update_display, width=60).pack(side="left", padx=10)
        
        self.details_tab_view = ctk.CTkTabview(self, command=self.update_display); self.details_tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.details_tab_view.add("支出"); self.details_tab_view.add("収入"); self.details_tab_view.add("貯金額")
        self.details_tab_view.add("年間支出"); self.details_tab_view.add("年間収入"); self.details_tab_view.add("予算")
        
        self._create_history_tab(self.details_tab_view.tab("支出"), "支出")
        self._create_history_tab(self.details_tab_view.tab("収入"), "収入")
        self._create_savings_tab(self.details_tab_view.tab("貯金額"))
        self._create_annual_summary_tab(self.details_tab_view.tab("年間支出"), "年間支出")
        self._create_annual_summary_tab(self.details_tab_view.tab("年間収入"), "年間収入")
        self._create_budget_tab(self.details_tab_view.tab("予算"))
        
    def _create_history_tab(self, tab, history_type):
        tab.grid_rowconfigure(2, weight=1); tab.grid_columnconfigure(0, weight=1)
        month_selector_frame = ctk.CTkFrame(tab); month_selector_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        month_selector_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(month_selector_frame, text="<", width=40, command=lambda t=tab: self._navigate_month(t, -1)).grid(row=0, column=0, padx=5)
        month_entry = ctk.CTkEntry(month_selector_frame, justify="center"); month_entry.insert(0, str(datetime.now().month)); month_entry.grid(row=0, column=1, sticky="ew")
        month_entry.bind("<Return>", lambda event: self.update_display())
        ctk.CTkButton(month_selector_frame, text=">", width=40, command=lambda t=tab: self._navigate_month(t, 1)).grid(row=0, column=2, padx=5)
        total_label = ctk.CTkLabel(tab, text="合計: 0円", font=ctk.CTkFont(size=16, weight="bold")); total_label.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        history_list = ctk.CTkScrollableFrame(tab); history_list.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        tab.month_entry = month_entry; tab.total_label = total_label; tab.history_list = history_list; tab.history_type = history_type

    def _create_savings_tab(self, tab):
        tab.grid_rowconfigure(1, weight=1); tab.grid_columnconfigure(0, weight=1)
        total_savings_frame = ctk.CTkFrame(tab); total_savings_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(total_savings_frame, text="総貯金額:", font=ctk.CTkFont(size=16)).pack(side="left", padx=10)
        total_savings_label = ctk.CTkLabel(total_savings_frame, text="0円", font=ctk.CTkFont(size=20, weight="bold")); total_savings_label.pack(side="right", padx=10, pady=5)
        savings_list = ctk.CTkScrollableFrame(tab, label_text="月別収支リスト"); savings_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tab.total_savings_label = total_savings_label; tab.savings_list = savings_list

    def _create_annual_summary_tab(self, tab, summary_type):
        tab.grid_rowconfigure(0, weight=1); tab.grid_columnconfigure(0, weight=1)
        label = ctk.CTkLabel(tab, text="0 円", font=ctk.CTkFont(size=40, weight="bold")); label.grid(row=0, column=0, sticky="nsew")
        tab.label = label; tab.summary_type = summary_type
    
    # ▼▼▼ 変更点: 予算タブのUIと機能を大幅に更新 ▼▼▼
    def _create_budget_tab(self, tab):
        tab.grid_rowconfigure(2, weight=1); tab.grid_columnconfigure(0, weight=1)
        
        month_selector_frame = ctk.CTkFrame(tab); month_selector_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        month_selector_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(month_selector_frame, text="<", width=40, command=lambda t=tab: self._navigate_month(t, -1)).grid(row=0, column=0, padx=5)
        month_entry = ctk.CTkEntry(month_selector_frame, justify="center"); month_entry.insert(0, str(datetime.now().month)); month_entry.grid(row=0, column=1, sticky="ew")
        month_entry.bind("<Return>", lambda event: self.update_display())
        ctk.CTkButton(month_selector_frame, text=">", width=40, command=lambda t=tab: self._navigate_month(t, 1)).grid(row=0, column=2, padx=5)

        input_frame = ctk.CTkFrame(tab); input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        budget_memo_entry = ctk.CTkEntry(input_frame, placeholder_text="メモ (例: 旅行)"); budget_memo_entry.grid(row=0, column=0, sticky="ew", padx=(0,5))
        budget_amount_entry = ctk.CTkEntry(input_frame, placeholder_text="予算額", width=100); budget_amount_entry.grid(row=0, column=1, padx=(0,5))
        ctk.CTkButton(input_frame, text="追加", width=60, command=self._save_budget).grid(row=0, column=2)

        budget_list = ctk.CTkScrollableFrame(tab, label_text="月間予算リスト"); budget_list.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        tab.month_entry = month_entry; tab.budget_memo_entry = budget_memo_entry
        tab.budget_amount_entry = budget_amount_entry; tab.budget_list = budget_list
    
    def _navigate_month(self, tab, direction):
        try:
            current_month = int(tab.month_entry.get()); new_month = current_month + direction
            if 1 <= new_month <= 12:
                tab.month_entry.delete(0, "end"); tab.month_entry.insert(0, str(new_month))
                self.update_display()
        except ValueError: pass

    def fetch_data(self, query, params=()):
        try:
            conn = sqlite3.connect('kakeibo.db'); conn.row_factory = sqlite3.Row
            cursor = conn.cursor(); cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]; conn.close()
            return results
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}"); return []
    def update_display(self):
        current_tab_name = self.details_tab_view.get(); current_tab_widget = self.details_tab_view.tab(current_tab_name)
        try: year = int(self.year_entry.get())
        except ValueError: messagebox.showerror("入力エラー", "年は数字で入力してください。"); return
        if current_tab_name in ["支出", "収入"]: self._update_history_tab(current_tab_widget, year)
        elif current_tab_name == "貯金額": self._update_savings_tab(current_tab_widget, year)
        elif current_tab_name in ["年間支出", "年間収入"]: self._update_annual_summary_tab(current_tab_widget, year)
        elif current_tab_name == "予算": self._update_budget_tab(current_tab_widget, year)
    def _update_history_tab(self, tab, year):
        list_frame = tab.history_list; trans_type = tab.history_type
        try: month = int(tab.month_entry.get())
        except ValueError: messagebox.showerror("入力エラー", "月は数字で入力してください。"); return
        for widget in list_frame.winfo_children(): widget.destroy()
        start_date = f"{year}-{month:02d}-01"; end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        query = f"SELECT * FROM transactions WHERE type='{trans_type}' AND date BETWEEN ? AND ? ORDER BY date DESC, id DESC"
        transactions = self.fetch_data(query, (start_date, end_date))
        total_amount = sum(t['amount'] for t in transactions)
        color = "#3377FF" if trans_type == "収入" else "#FF3333"; tab.total_label.configure(text=f"合計: {total_amount:,}円", text_color=color)
        last_date = None
        for t in transactions:
            if t['date'] != last_date:
                ctk.CTkLabel(list_frame, text=t['date'], font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(10, 2))
                last_date = t['date']
            item_button = ctk.CTkButton(list_frame, text="", fg_color=("gray90", "gray25"), command=lambda trans=t: self.open_edit_window(trans))
            item_button.pack(fill="x", padx=5, pady=2); item_button.grid_columnconfigure(0, weight=1)
            sign = "+" if trans_type == "収入" else "-"; font_big_bold = ctk.CTkFont(size=16, weight="bold")
            memo_label = ctk.CTkLabel(item_button, text=t['memo'] or "(メモなし)", anchor="w", fg_color="transparent", font=font_big_bold)
            memo_label.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            amount_label = ctk.CTkLabel(item_button, text=f"{sign}{t['amount']:,}円", anchor="e", fg_color="transparent", font=font_big_bold, text_color=color)
            amount_label.grid(row=0, column=1, padx=10, pady=8)
            memo_label.bind("<Button-1>", lambda event, trans=t: self.open_edit_window(trans))
            amount_label.bind("<Button-1>", lambda event, trans=t: self.open_edit_window(trans))
    def _update_savings_tab(self, tab, year):
        total_income_all = self.fetch_data("SELECT SUM(amount) as total FROM transactions WHERE type='収入'")
        total_expense_all = self.fetch_data("SELECT SUM(amount) as total FROM transactions WHERE type='支出'")
        total_savings = (total_income_all[0]['total'] or 0) - (total_expense_all[0]['total'] or 0)
        tab.total_savings_label.configure(text=f"{total_savings:+,}円", text_color=("#3377FF" if total_savings >= 0 else "#FF3333"))
        list_frame = tab.savings_list; 
        for widget in list_frame.winfo_children(): widget.destroy()
        monthly_balances = {m: 0 for m in range(1, 13)}
        income_data = self.fetch_data("SELECT strftime('%m', date) as month, SUM(amount) as total FROM transactions WHERE type='収入' AND strftime('%Y', date)=? GROUP BY month", (str(year),))
        for row in income_data: monthly_balances[int(row['month'])] += row['total']
        expense_data = self.fetch_data("SELECT strftime('%m', date) as month, SUM(amount) as total FROM transactions WHERE type='支出' AND strftime('%Y', date)=? GROUP BY month", (str(year),))
        for row in expense_data: monthly_balances[int(row['month'])] -= row['total']
        for month in range(12, 0, -1):
            balance = monthly_balances[month]
            if balance != 0 or any(d['month'] == str(month).zfill(2) for d in income_data + expense_data):
                item_frame = ctk.CTkFrame(list_frame); item_frame.pack(fill="x", pady=2)
                item_frame.grid_columnconfigure(1, weight=1)
                font_big_bold = ctk.CTkFont(size=16, weight="bold")
                ctk.CTkLabel(item_frame, text=f"{month}月", font=font_big_bold).grid(row=0, column=0, padx=10, pady=8)
                color = "#3377FF" if balance >= 0 else "#FF3333"
                ctk.CTkLabel(item_frame, text=f"{balance:+,} 円", font=font_big_bold, text_color=color).grid(row=0, column=1, sticky="e", padx=10, pady=8)
    def _update_annual_summary_tab(self, tab, year):
        summary_type = "支出" if "支出" in tab.summary_type else "収入"
        data = self.fetch_data(f"SELECT SUM(amount) as total FROM transactions WHERE type='{summary_type}' AND strftime('%Y', date)=?", (str(year),))
        total = data[0]['total'] if data and data[0]['total'] else 0
        color = "#FF3333" if summary_type == "支出" else "#3377FF"
        tab.label.configure(text=f"{total:,} 円", text_color=color)

    def _update_budget_tab(self, tab, year):
        try: month = int(tab.month_entry.get())
        except ValueError: return
        list_frame = tab.budget_list; 
        for widget in list_frame.winfo_children(): widget.destroy()
        year_month = f"{year}-{month:02d}"
        budgets = self.fetch_data("SELECT * FROM budgets WHERE year_month = ? ORDER BY id DESC", (year_month,))
        for budget in budgets:
            self._create_budget_item(list_frame, budget)

    def _create_budget_item(self, parent, budget_data):
        item_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray25")); 
        item_frame.pack(fill="x", pady=2, padx=2)
        item_frame.grid_columnconfigure(0, weight=1)
        
        # 1行目: メモと予算額
        top_frame = ctk.CTkFrame(item_frame, fg_color="transparent"); 
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,0))
        top_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top_frame, text=budget_data['memo'], font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(top_frame, text=f"予算: {budget_data['amount']:,}円").grid(row=0, column=1, sticky="e")
        
        # 2行目: 実績入力とギャップ表示
        bottom_frame = ctk.CTkFrame(item_frame, fg_color="transparent"); 
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,5))
        bottom_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(bottom_frame, text="実績:").grid(row=0, column=0, sticky="w")
        actual_entry = ctk.CTkEntry(bottom_frame, width=100)
        if budget_data['actual_amount'] is not None:
            actual_entry.insert(0, str(budget_data['actual_amount']))
        actual_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        gap = (budget_data['actual_amount'] or 0) - budget_data['amount']
        gap_color = "gray" if gap == 0 else ("#FF3333" if gap > 0 else "#3377FF")
        gap_label = ctk.CTkLabel(bottom_frame, text=f"差額: {gap:+,}円", text_color=gap_color, font=ctk.CTkFont(weight="bold"))
        gap_label.grid(row=0, column=2, sticky="e")
        
        # Enterキーで実績を保存するイベント
        actual_entry.bind("<Return>", lambda event, b_id=budget_data['id'], entry=actual_entry: self._save_actual_amount(b_id, entry))

    def _save_budget(self):
        tab = self.details_tab_view.tab("予算"); year = int(self.year_entry.get())
        try: month = int(tab.month_entry.get()); memo = tab.budget_memo_entry.get(); amount = tab.budget_amount_entry.get()
        except ValueError: messagebox.showerror("エラー", "月と予算額を正しく入力してください。"); return
        if not memo or not amount or not amount.isdigit():
            messagebox.showerror("エラー", "メモと予算額(数字)の両方を入力してください。"); return
        year_month = f"{year}-{month:02d}"
        conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
        cursor.execute("INSERT INTO budgets (year_month, memo, amount) VALUES (?, ?, ?)", (year_month, memo, int(amount)))
        conn.commit(); conn.close()
        tab.budget_memo_entry.delete(0, 'end'); tab.budget_amount_entry.delete(0, 'end')
        messagebox.showinfo("成功", f"{year}年{month}月の予算を保存しました。"); self.update_display()
    
    def _save_actual_amount(self, budget_id, entry_widget):
        actual_amount = entry_widget.get()
        if not actual_amount.isdigit():
            messagebox.showerror("エラー", "実績は数字で入力してください。"); return
        conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
        cursor.execute("UPDATE budgets SET actual_amount = ? WHERE id = ?", (int(actual_amount), budget_id))
        conn.commit(); conn.close()
        self.update_display() # 再描画してギャップを更新

    def open_edit_window(self, transaction):
        edit_win = ctk.CTkToplevel(self); edit_win.title("取引の編集"); edit_win.geometry("350x350"); edit_win.grab_set()
        main_frame = ctk.CTkFrame(edit_win, fg_color="transparent"); main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(main_frame, text=f"ID: {transaction['id']}").pack(pady=5)
        type_var = ctk.StringVar(value=transaction['type']); ctk.CTkSegmentedButton(main_frame, values=["支出", "収入"], variable=type_var).pack(pady=10, fill="x")
        amount_entry = ctk.CTkEntry(main_frame); amount_entry.insert(0, str(transaction['amount'])); amount_entry.pack(pady=5, fill="x")
        memo_entry = ctk.CTkEntry(main_frame); memo_entry.insert(0, transaction['memo'] or ""); memo_entry.pack(pady=5, fill="x")
        pm_entry = ctk.CTkEntry(main_frame); pm_entry.insert(0, transaction['payment_method'] or ""); pm_entry.pack(pady=5, fill="x")
        def update_transaction():
            new_amount = amount_entry.get()
            if not new_amount.isdigit() or int(new_amount) <= 0: messagebox.showerror("エラー", "金額は正の整数で入力してください。", parent=edit_win); return
            conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
            cursor.execute('UPDATE transactions SET type=?, amount=?, memo=?, payment_method=? WHERE id=?', (type_var.get(), int(new_amount), memo_entry.get(), pm_entry.get(), transaction['id'])); conn.commit(); conn.close(); edit_win.destroy(); self.update_display()
        def delete_transaction():
            if messagebox.askyesno("確認", "この取引を削除しますか？", parent=edit_win):
                conn = sqlite3.connect('kakeibo.db'); cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id=?", (transaction['id'],)); conn.commit(); conn.close()
                edit_win.destroy(); self.update_display()
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent"); btn_frame.pack(pady=20, fill="x")
        ctk.CTkButton(btn_frame, text="更新", command=update_transaction).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="削除", command=delete_transaction, fg_color="red").pack(side="right", expand=True, padx=5)