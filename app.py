# app.py
import customtkinter as ctk
import setup_database

from input_view import InputView
from calendar_view import CalendarView
from details_view import DetailsView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("家計簿アプリ")
        self.geometry("400x650")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(master=self, command=self.on_tab_change)
        self.tab_view.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.tab_view.add("入力")
        self.tab_view.add("カレンダー")
        self.tab_view.add("詳細")
        
        # ▼▼▼ 変更点1: selfを渡して、各タブがメインアプリを操作できるようにする ▼▼▼
        self.input_frame = InputView(parent=self.tab_view.tab("入力"), app=self)
        self.calendar_frame = CalendarView(parent=self.tab_view.tab("カレンダー"), app=self)
        self.details_frame = DetailsView(parent=self.tab_view.tab("詳細"), app=self)
        
        self.tab_view.set("カレンダー")
        self.calendar_frame.draw_calendar()

    def on_tab_change(self):
        current_tab = self.tab_view.get()
        if current_tab == "カレンダー":
            self.calendar_frame.draw_calendar()
        elif current_tab == "詳細":
            self.details_frame.update_display()

    # ▼▼▼ 変更点2: 他のタブから入力タブを開くための関数を追加 ▼▼▼
    def switch_to_input_tab(self, date_obj):
        """指定された日付で入力タブに切り替える"""
        self.tab_view.set("入力")
        self.input_frame.set_date(date_obj)


if __name__ == '__main__':
    setup_database.setup()
    app = MainApp()
    app.mainloop()