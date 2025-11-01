# setup_database.py
import sqlite3

def setup():
    DB_NAME = 'kakeibo.db'
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # (transactions, subscriptions, budgets テーブルは変更なし)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, type TEXT NOT NULL,
            amount INTEGER NOT NULL, memo TEXT, payment_method TEXT )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, service_name TEXT NOT NULL UNIQUE,
            amount INTEGER NOT NULL, payment_day INTEGER NOT NULL )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, year_month TEXT NOT NULL, memo TEXT,
            amount INTEGER NOT NULL, actual_amount INTEGER )
    ''')

    # ▼▼▼ 変更点1: fixed_costs テーブルを作成する処理を追加 ▼▼▼
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fixed_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment_day INTEGER NOT NULL,
            payment_method TEXT
        )
    ''')
    # ▲▲▲ ここまでが変更箇所 ▲▲▲

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            closing_day INTEGER NOT NULL,
            payment_day INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("データベースのセットアップが完了しました。")