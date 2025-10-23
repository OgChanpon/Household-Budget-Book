import tkinter as tk
from tkinter import ttk
# 各ウィンドウのクラスをインポートするためにファイル名を指定
from input_view import InputWindow
from calendar_view import CalendarApp
from details_view import DetailsApp

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("統合家計簿アプリ")
        self.root.geometry("300x200")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # --- 各ウィンドウを開くためのボタン ---
        input_button = ttk.Button(frame, text="入力画面を開く", command=self.open_input)
        input_button.pack(pady=5, fill=tk.X)

        calendar_button = ttk.Button(frame, text="カレンダー表示を開く", command=self.open_calendar)
        calendar_button.pack(pady=5, fill=tk.X)

        details_button = ttk.Button(frame, text="詳細表示を開く", command=self.open_details)
        details_button.pack(pady=5, fill=tk.X)

    def open_window(self, window_class):
        """新しいウィンドウを開くための共通関数"""
        # Toplevelでメインウィンドウの子ウィンドウとして作成
        new_window = tk.Toplevel(self.root) 
        app = window_class(new_window)

    def open_input(self):
        self.open_window(InputWindow)

    def open_calendar(self):
        self.open_window(CalendarApp)

    def open_details(self):
        self.open_window(DetailsApp)


if __name__ == '__main__':
    # データベースのセットアップを最初に実行（初回のみ必要）
    import setup_database
    setup_database.setup()
    
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()