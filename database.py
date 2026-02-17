import sqlite3
from datetime import date

DB_NAME = "bot_database.db"
FREE_DAILY_LIMIT = 3

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id   INTEGER PRIMARY KEY,
            email         TEXT UNIQUE,
            language      TEXT DEFAULT 'ar',
            is_subscribed INTEGER DEFAULT 0,
            joined_at     TEXT DEFAULT (date('now'))
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_usage (
            telegram_id INTEGER,
            usage_date  TEXT,
            count       INTEGER DEFAULT 0,
            PRIMARY KEY (telegram_id, usage_date)
        )
    ''')

    conn.commit()
    conn.close()

def user_exists(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def register_user(telegram_id, email, language='ar'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (telegram_id, email, language) VALUES (?, ?, ?)",
            (telegram_id, email, language)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_language(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE telegram_id = ?", (telegram_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'ar'

def update_language(telegram_id, language):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (language, telegram_id))
    conn.commit()
    conn.close()

def set_subscribed(telegram_id, status=1):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_subscribed = ? WHERE telegram_id = ?", (status, telegram_id))
    conn.commit()
    conn.close()

def is_subscribed(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_subscribed FROM users WHERE telegram_id = ?", (telegram_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def get_daily_usage(telegram_id):
    today = str(date.today())
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT count FROM daily_usage WHERE telegram_id = ? AND usage_date = ?",
        (telegram_id, today)
    )
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def increment_usage(telegram_id):
    today = str(date.today())
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO daily_usage (telegram_id, usage_date, count) VALUES (?, ?, 1)
        ON CONFLICT(telegram_id, usage_date) DO UPDATE SET count = count + 1
    ''', (telegram_id, today))
    conn.commit()
    conn.close()

def can_use_today(telegram_id):
    if is_subscribed(telegram_id):
        return True
    return get_daily_usage(telegram_id) < FREE_DAILY_LIMIT

def get_all_emails():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE email IS NOT NULL")
    results = c.fetchall()
    conn.close()
    return [r[0] for r in results]
