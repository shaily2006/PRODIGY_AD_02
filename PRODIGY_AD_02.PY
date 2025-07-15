import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3 as sql 


class TodoListApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("To‑Do List Manager")
        self.root.geometry("640x480")
        self.root.minsize(560, 420)

        # ---------- ttk styling ----------
        style = ttk.Style(self.root)
        style.theme_use("clam")  # modern built‑in theme
        style.configure(
            "TButton",
            font=("Helvetica", 10),
            padding=(8, 4),
        )
        style.configure(
            "Accent.TButton",
            foreground="white",
            background="#4a7a8c",
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#3d6977")],
        )

        # ---------- database ----------
        self.connection = sql.connect("listOfTasks.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks (title TEXT)")

        self.tasks: list[str] = []
        self.retrieve_database()

        # ---------- layout helpers ----------
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # ---------- header ----------
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(
            header_frame,
            text="🗒  To‑Do List",
            font=("Helvetica", 22, "bold"),
        ).pack()

        # ---------- left‑hand controls ----------
        controls = ttk.Frame(self.root, padding=(12, 10))
        controls.grid(row=1, column=0, sticky="ns")
        controls.columnconfigure(0, weight=1)

        ttk.Label(
            controls,
            text="New task:",
            font=("Helvetica", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.task_field = ttk.Entry(controls, width=24, font=("Helvetica", 11))
        self.task_field.grid(row=1, column=0, pady=(0, 12), sticky="ew")
        self.task_field.bind("<Return>", lambda _: self.add_task())

        ttk.Button(controls, text="Add", style="Accent.TButton",
                   command=self.add_task).grid(row=2, column=0, sticky="ew")
        ttk.Button(controls, text="Delete selected",
                   command=self.delete_task).grid(row=3, column=0, sticky="ew", pady=4)
        ttk.Button(controls, text="Clear all",
                   command=self.delete_all_tasks).grid(row=4, column=0, sticky="ew")
        ttk.Separator(controls, orient="horizontal").grid(
            row=5, column=0, sticky="ew", pady=8)
        ttk.Button(controls, text="Exit",
                   command=self.close).grid(row=6, column=0, sticky="ew")

        # ---------- right‑hand list ----------
        list_frame = ttk.Frame(self.root, padding=(0, 10, 10, 10))
        list_frame.grid(row=1, column=1, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.task_listbox = tk.Listbox(
            list_frame,
            font=("Helvetica", 12),
            selectmode="browse",
            activestyle="none",
            highlightthickness=0,
            bd=0,
            yscrollcommand=scrollbar.set,
            selectbackground="#4a7a8c",
            selectforeground="white",
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.task_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.list_update()

    # ---------- functional logic (unchanged) ----------
    def add_task(self) -> None:
        task_string = self.task_field.get().strip()
        if not task_string:
            messagebox.showinfo("Error", "Field is empty.")
            return
        self.tasks.append(task_string)
        self.cursor.execute("INSERT INTO tasks VALUES (?)", (task_string,))
        self.list_update()
        self.task_field.delete(0, tk.END)

    def list_update(self) -> None:
        self.clear_list()
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

    def delete_task(self) -> None:
        try:
            index = self.task_listbox.curselection()[0]
        except IndexError:
            messagebox.showinfo("Error", "No task selected.")
            return
        value = self.task_listbox.get(index)
        if value in self.tasks:
            self.tasks.remove(value)
            self.cursor.execute("DELETE FROM tasks WHERE title = ?", (value,))
            self.list_update()

    def delete_all_tasks(self) -> None:
        if messagebox.askyesno("Delete All", "Delete every task?"):
            self.tasks.clear()
            self.cursor.execute("DELETE FROM tasks")
            self.list_update()

    def clear_list(self) -> None:
        self.task_listbox.delete(0, tk.END)

    def retrieve_database(self) -> None:
        self.tasks.clear()
        self.tasks += [row[0] for row in self.cursor.execute("SELECT title FROM tasks")]

    def close(self) -> None:
        self.connection.commit()
        self.cursor.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    TodoListApp(root)
    root.mainloop()
