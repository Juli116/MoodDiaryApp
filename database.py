import sqlite3
from datetime import datetime
from tkinter import messagebox

class Database:
    def __init__(self, db_name="mood_diary_pro.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    emoji TEXT,
                    date TEXT,
                    status INTEGER DEFAULT 0
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Не удалось подключить базу: {e}")

    def add_note(self, content, emoji):
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.cursor.execute(
            "INSERT INTO notes (content, emoji, date) VALUES (?, ?, ?)", 
            (content, emoji, current_date)
        )
        self.conn.commit()

    def fetch_notes(self, search_query=None):
        if search_query:
            self.cursor.execute("SELECT * FROM notes WHERE content LIKE ?", (f'%{search_query}%',))
        else:
            self.cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        return self.cursor.fetchall()

    def update_status(self, note_id, status):
        self.cursor.execute("UPDATE notes SET status = ? WHERE id = ?", (status, note_id))
        self.conn.commit()

    def delete_note(self, note_id):
        self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()
