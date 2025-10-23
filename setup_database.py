# setup_database.py
import sqlite3

def setup():
    DB_NAME = 'kakeibo.db'
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # カテゴリ列がないテーブル定義
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            memo TEXT,
            payment_method TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL UNIQUE,
            amount INTEGER NOT NULL,
            payment_day INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_month TEXT NOT NULL UNIQUE,
            memo TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("データベースのセットアップが完了しました。")