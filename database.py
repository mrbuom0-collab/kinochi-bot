import sqlite3

def init_db():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            caption TEXT,
            file_name TEXT DEFAULT 'Noma''lum',
            views INTEGER DEFAULT 0
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM movies")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO movies (id, file_id, caption) VALUES (99, 'dummy', '')")
        cursor.execute("DELETE FROM movies WHERE id = 99")
    conn.commit()
    conn.close()

def add_movie(file_id, caption="", file_name="Noma'lum"):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movies (file_id, caption, file_name, views) VALUES (?, ?, ?, 0)", (file_id, caption, file_name))
    movie_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return movie_id

def get_movie(movie_id):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, caption, file_name, views FROM movies WHERE id = ?", (movie_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def increment_views(movie_id):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET views = views + 1 WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

def delete_movie(movie_id):
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
