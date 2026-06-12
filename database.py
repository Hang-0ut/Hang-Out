import sqlite3
import os



def get_db_conn():
    conn = sqlite3.connect("data/database.db")
    cur = conn.cursor()
    return conn, cur


def construct_db():
    if not os.path.exists("data/database.db"):
        with open("data/database.db", "w"):
            pass
    conn, cur = get_db_conn()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                friends TEXT,
                icon TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS groups (
                
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                users TEXT UNIQUE NOT NULL,
                colour TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS sessions (
                
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                for_users TEXT,
                for_groups TEXT,
                attending TEXT,
                not_attending TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS comments (
                
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NTO NULL,
                session_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                images TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()


def drop_db():
    if os.path.exists("data/database.db"):
        os.remove("data/database.db")