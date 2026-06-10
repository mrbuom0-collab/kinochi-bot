import os
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    import psycopg2

def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect('movies.db')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id SERIAL PRIMARY KEY,
                file_id TEXT NOT NULL,
                caption TEXT,
                file_name TEXT DEFAULT 'Noma''lum',
                views INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM movies")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO movies (id, file_id, caption) VALUES (99, 'dummy', '') ON CONFLICT DO NOTHING")
            cursor.execute("DELETE FROM movies WHERE id = 99")
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                caption TEXT,
                file_name TEXT DEFAULT 'Noma''lum',
                views INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM movies")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO movies (id, file_id, caption) VALUES (99, 'dummy', '')")
            cursor.execute("DELETE FROM movies WHERE id = 99")
    conn.commit()
    conn.close()

def add_movie(file_id, caption="", file_name="Noma'lum"):
    conn = get_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("INSERT INTO movies (file_id, caption, file_name, views) VALUES (%s, %s, %s, 0) RETURNING id", (file_id, caption, file_name))
        movie_id = cursor.fetchone()[0]
    else:
        cursor.execute("INSERT INTO movies (file_id, caption, file_name, views) VALUES (?, ?, ?, 0)", (file_id, caption, file_name))
        movie_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return movie_id

def get_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("SELECT file_id, caption, file_name, views FROM movies WHERE id = %s", (movie_id,))
    else:
        cursor.execute("SELECT file_id, caption, file_name, views FROM movies WHERE id = ?", (movie_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def increment_views(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("UPDATE movies SET views = views + 1 WHERE id = %s", (movie_id,))
    else:
        cursor.execute("UPDATE movies SET views = views + 1 WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

def delete_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    else:
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def add_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
    else:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM movies WHERE id != 99")
    movies_count = cursor.fetchone()[0]
    conn.close()
    return users_count, movies_count

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users
