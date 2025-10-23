import customtkinter as ctk
import setup_database

# 各画面のクラスをインポート
from input_view import InputView
from calendar_view import CalendarView
from details_view import DetailsView

# --- アプリの基本設定 ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("家計簿アプリ")
        self.geometry("400x650")

        # --- ウィンドウのグリッド設定 ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- タブビューの作成 ---
        self.tab_view = ctk.CTkTabview(master=self, command=self.on_tab_change)
        self.tab_view.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # --- 各タブの作成 ---
        self.tab_view.add("入力")
        self.tab_view.add("カレンダー")
        self.tab_view.add("詳細")
        
        # --- 各タブの中に、それぞれの画面(フレーム)を埋め込む ---
        self.input_frame = InputView(parent=self.tab_view.tab("入力"))
        self.calendar_frame = CalendarView(parent=self.tab_view.tab("カレンダー"))
        self.details_frame = DetailsView(parent=self.tab_view.tab("詳細"))
        
        # 起動時に「カレンダー」タブを選択し、内容を更新する
        self.tab_view.set("カレンダー")
        self.calendar_frame.draw_calendar()


    def on_tab_change(self):
        """タブが切り替わったときに呼ばれる関数"""
        current_tab = self.tab_view.get()
        
        # カレンダーまたは詳細タブが表示されたら、表示を最新データに更新する
        if current_tab == "カレンダー":
            self.calendar_frame.draw_calendar()
        elif current_tab == "詳細":
            self.details_frame.update_display()


if __name__ == '__main__':
    setup_database.setup()
    app = MainApp()
    app.mainloop()