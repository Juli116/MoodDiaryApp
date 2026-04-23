import tkinter as tk
from tkinter import messagebox, ttk
from database import Database


class DiaryController:
   def __init__(self, db):
       self.db = db


   def get_stats(self):
       notes = self.db.fetch_notes()
       total = len(notes)
       done = sum(1 for n in notes if n[4] == 1) # status теперь в 4-м индексе
       return {"total": total, "done": done, "pending": total - done}

class AddNoteWindow(tk.Toplevel):
   def __init__(self, parent, callback):
       super().__init__(parent)
       self.title("Новая запись")
       self.geometry("350x250")
       self.callback = callback
       self.transient(parent)
       self.grab_set()


       # Поле ввода текста
       tk.Label(self, text="Что произошло?").pack(pady=5)
       self.entry = tk.Entry(self, width=40)
       self.entry.pack(pady=5)
       self.entry.focus_set()


       # Выбор настроения (смайлики)
       tk.Label(self, text="Ваше настроение:").pack(pady=5)
       self.emoji_var = tk.StringVar(value="😊")
      
       emoji_frame = tk.Frame(self)
       emoji_frame.pack()
      
       emojis = [("😊", "Радость"), ("😐", "Спокойствие"), ("☹️", "Грусть"), ("😡", "Злость")]
       for emo, label in emojis:
           tk.Radiobutton(emoji_frame, text=emo, variable=self.emoji_var, value=emo, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)


       btn_frame = tk.Frame(self)
       btn_frame.pack(pady=20)
       tk.Button(btn_frame, text="Сохранить", command=self.submit, bg="#d1e7dd").pack(side=tk.LEFT, padx=5)
       tk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)


   def submit(self):
       content = self.entry.get().strip()
       emoji = self.emoji_var.get()
       if not content:
           messagebox.showwarning("Валидация", "Поле не может быть пустым!")
           return
       self.callback(content, emoji)
       self.destroy()


class MoodDiaryApp(tk.Tk):
   def __init__(self):
       super().__init__()
       self.db = Database()
       self.ctrl = DiaryController(self.db)
       self.title("Дневник настроения Pro")
       self.geometry("700x500")
      
       self.setup_ui()
       self.refresh_list()


   def setup_ui(self):
       # Поиск
       search_frame = tk.Frame(self)
       search_frame.pack(fill=tk.X, padx=10, pady=5)
       tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
       self.search_var = tk.StringVar()
       self.search_var.trace_add("write", lambda *args: self.refresh_list())
       tk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)


       # Таблица с колонками для даты и смайлика
       cols = ("ID", "Date", "Emoji", "Content", "Status")
       self.tree = ttk.Treeview(self, columns=cols, show="headings")
      
       headings = {"ID": "ID", "Date": "Дата", "Emoji": "Мнение", "Content": "Запись", "Status": "Статус"}
       for col, text in headings.items():
           self.tree.heading(col, text=text)
      
       self.tree.column("ID", width=30)
       self.tree.column("Date", width=120)
       self.tree.column("Emoji", width=60, anchor="center")
       self.tree.column("Status", width=60, anchor="center")
       self.tree.pack(fill=tk.BOTH, expand=True, padx=10)


       btn_frame = tk.Frame(self)
       btn_frame.pack(fill=tk.X, padx=10, pady=5)
       tk.Button(btn_frame, text="Добавить", command=self.open_add_window).pack(side=tk.LEFT, padx=2)
       tk.Button(btn_frame, text="Выполнено", command=self.mark_done).pack(side=tk.LEFT, padx=2)
       tk.Button(btn_frame, text="Удалить", command=self.delete_item).pack(side=tk.LEFT, padx=2)


       self.status_var = tk.StringVar()
       tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)
       self.protocol("WM_DELETE_WINDOW", self.on_exit)


   def refresh_list(self):
       for item in self.tree.get_children():
           self.tree.delete(item)
       for row in self.db.fetch_notes(self.search_var.get()):
           # row: 0=id, 1=content, 2=emoji, 3=date, 4=status
           status_icon = "✅" if row[4] == 1 else "⏳"
           self.tree.insert("", tk.END, values=(row[0], row[3], row[2], row[1], status_icon))
       self.update_stats()


   def update_stats(self):
       stats = self.ctrl.get_stats()
       self.status_var.set(f"Всего: {stats['total']} | Выполнено: {stats['done']} | Ожидает: {stats['pending']}")


   def open_add_window(self):
       AddNoteWindow(self, self.add_note_callback)


   def add_note_callback(self, content, emoji):
       self.db.add_note(content, emoji)
       self.refresh_list()


   def mark_done(self):
       selected = self.tree.selection()
       if not selected: return
       item_id = self.tree.item(selected[0])['values'][0]
       self.db.update_status(item_id, 1)
       self.refresh_list()


   def delete_item(self):
       selected = self.tree.selection()
       if not selected: return
       if messagebox.askyesno("Подтверждение", "Удалить эту запись?"):
           item_id = self.tree.item(selected[0])['values'][0]
           self.db.delete_note(item_id)
           self.refresh_list()


   def on_exit(self):
       if messagebox.askokcancel("Выход", "Вы уверены, что хотите закрыть приложение?"):
           self.destroy()
