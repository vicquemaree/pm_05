import tkinter as tk
from tkinter import messagebox, ttk
import random
import psycopg2


class PolesyeApp:
    def __init__(self, root):
        self.root = root
        self.root.title('ООО "Молочный комбинат Полесье" — Администрирование')
        self.root.geometry("800x700")
        self.root.minsize(600, 600)

        self.captcha_attempts = 0
        self.max_captcha_attempts = 3
        self.temp_user_data = None

        self.correct_order = ["1.png", "2.png", "3.png", "4.png"]
        self.current_order = self.correct_order.copy()

        self.show_login_ui()

    def get_db_connection(self):
        return psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="Ona4f4OxDZ6UO3M!",
            host="localhost",
            client_encoding="utf8"
        )

    # --- ЭКРАНЫ АВТОРИЗАЦИИ (БЕЗ ИЗМЕНЕНИЙ) ---
    def show_login_ui(self):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        tk.Label(frame, text="МК ПОЛЕСЬЕ", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(frame, text="Логин:").pack(anchor="w")
        self.ent_login = tk.Entry(frame, width=35)
        self.ent_login.pack(pady=5)
        tk.Label(frame, text="Пароль:").pack(anchor="w")
        self.ent_pass = tk.Entry(frame, width=35, show="*")
        self.ent_pass.pack(pady=5)
        tk.Button(frame, text="Войти", bg="#2c3e50", fg="white", width=20, height=2,
                  command=self.check_user_exists).pack(pady=(20, 10))
        tk.Button(frame, text="Регистрация", bg="#95a5a6", fg="white", width=20,
                  command=self.show_register_ui).pack()

    def check_user_exists(self):
        login = self.ent_login.get().strip()
        pwd = self.ent_pass.get().strip()
        if not login or not pwd:
            messagebox.showwarning("Внимание", "Введите данные")
            return
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT role, is_blocked, id FROM users WHERE login = %s AND password = %s", (login, pwd))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if user:
                if user[1]:  # is_blocked
                    messagebox.showerror("Доступ", "Аккаунт заблокирован")
                    return
                self.temp_user_data = user
                self.show_captcha_ui()
            else:
                messagebox.showinfo("Инфо", "Пользователь не найден")
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Нет связи: {e}")

    def show_captcha_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Соберите пазл:", font=("Arial", 11)).pack(pady=20)
        self.p_frame = tk.Frame(self.root)
        self.p_frame.pack()
        random.shuffle(self.current_order)
        self.draw_puzzle()
        tk.Button(self.root, text="Проверить", bg="#27ae60", fg="white",
                  command=self.validate_captcha, width=20, height=2).pack(pady=20)

    def draw_puzzle(self):
        for w in self.p_frame.winfo_children(): w.destroy()
        self.reps = []
        for i, f in enumerate(self.current_order):
            try:
                img = tk.PhotoImage(file=f).subsample(3, 3)
                self.reps.append(img)
                r, c = divmod(i, 2)
                btn = tk.Button(self.p_frame, image=img, command=lambda idx=i: self.swap(idx))
                btn.grid(row=r, column=c, padx=5, pady=5)
            except:
                tk.Label(self.p_frame, text="ERR").grid(row=i // 2, column=i % 2)

    def swap(self, i):
        ni = (i + 1) % 4
        self.current_order[i], self.current_order[ni] = self.current_order[ni], self.current_order[i]
        self.draw_puzzle()

    def validate_captcha(self):
        if self.current_order == self.correct_order:
            role = self.temp_user_data[0]
            messagebox.showinfo("Успех", f"Добро пожаловать, {role}!")
            if role == 'Администратор':
                self.show_admin_panel()
            else:
                self.show_user_panel()
        else:
            self.captcha_attempts += 1
            if self.captcha_attempts >= 3:
                messagebox.showerror("Блокировка", "Приложение закрыто.")
                self.root.destroy()
            else:
                messagebox.showwarning("Ошибка", f"Неверно! Попыток: {3 - self.captcha_attempts}")
                random.shuffle(self.current_order)
                self.draw_puzzle()

    # --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (НОВОЕ) ---

    def show_admin_panel(self):
        """Главное меню администратора"""
        self.clear_window()
        tk.Label(self.root, text="ПАНЕЛЬ АДМИНИСТРАТОРА", font=("Arial", 14, "bold")).pack(pady=20)

        # Кнопка перехода к списку
        tk.Button(self.root, text="Управление пользователями", width=35, height=2,
                  bg="#34495e", fg="white", command=self.show_users_list).pack(pady=10)

        tk.Button(self.root, text="Выход", command=self.show_login_ui, fg="red").pack(pady=20)

    def show_users_list(self):
        """Окно со списком пользователей и блокировкой"""
        self.clear_window()
        tk.Label(self.root, text="СПИСОК ПОЛЬЗОВАТЕЛЕЙ", font=("Arial", 12, "bold")).pack(pady=10)

        # Таблица
        cols = ('ID', 'Логин', 'Роль', 'Заблокирован')
        self.tree = ttk.Treeview(self.root, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10)

        # Кнопки управления
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Добавить нового", bg="#27ae60", fg="white",
                  command=self.show_add_user_window).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Переключить Блок (Да/Нет)", bg="#e67e22", fg="white",
                  command=self.toggle_block).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Назад в меню", command=self.show_admin_panel).grid(row=0, column=2, padx=5)

        self.refresh_users_table()

    def refresh_users_table(self):
        """Загрузка данных из БД в таблицу"""
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, login, role, is_blocked FROM users ORDER BY id")
            for row in cur.fetchall():
                status = "ДА" if row[3] else "Нет"
                self.tree.insert('', 'end', values=(row[0], row[1], row[2], status))
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def toggle_block(self):
        """Инверсия галочки (статуса блокировки)"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите пользователя в таблице")
            return

        item = self.tree.item(selected)
        user_id = item['values'][0]
        current_status = item['values'][3]
        new_status = False if current_status == "ДА" else True

        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET is_blocked = %s WHERE id = %s", (new_status, user_id))
            conn.commit()
            cur.close()
            conn.close()
            self.refresh_users_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_add_user_window(self):
        """Всплывающее окно для создания нового пользователя"""
        self.win = tk.Toplevel(self.root)
        self.win.title("Новый сотрудник")
        self.win.geometry("300x350")

        tk.Label(self.win, text="Логин:").pack(pady=5)
        self.new_l = tk.Entry(self.win)
        self.new_l.pack()

        tk.Label(self.win, text="Пароль:").pack(pady=5)
        self.new_p = tk.Entry(self.win)
        self.new_p.pack()

        tk.Label(self.win, text="Роль:").pack(pady=5)
        self.role_cb = ttk.Combobox(self.win, values=["Пользователь", "Администратор", "Менеджер"])
        self.role_cb.current(0)
        self.role_cb.pack()

        tk.Button(self.win, text="Сохранить", bg="#27ae60", fg="white",
                  command=self.save_new_user).pack(pady=20)

    def save_new_user(self):
        l, p, r = self.new_l.get().strip(), self.new_p.get().strip(), self.role_cb.get()
        if not l or not p: return

        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (login, password, role) VALUES (%s, %s, %s)", (l, p, r))
            conn.commit()
            cur.close()
            conn.close()
            self.win.destroy()
            self.refresh_users_table()
        except Exception:
            messagebox.showerror("Ошибка", "Логин уже занят!")

    # --- ВСПОМОГАТЕЛЬНОЕ ---
    def show_user_panel(self):
        self.clear_window()
        tk.Label(self.root, text="МЕНЮ ПОЛЬЗОВАТЕЛЯ", font=("Arial", 14)).pack(pady=50)
        tk.Button(self.root, text="Выйти", command=self.show_login_ui).pack()

    def show_register_ui(self):
        # Оставим логику регистрации из прошлого сообщения
        self.clear_window()
        tk.Label(self.root, text="РЕГИСТРАЦИЯ", font=("Arial", 14)).pack(pady=20)
        tk.Label(self.root, text="Логин:").pack()
        self.reg_l = tk.Entry(self.root)
        self.reg_l.pack()
        tk.Label(self.root, text="Пароль:").pack()
        self.reg_p = tk.Entry(self.root)
        self.reg_p.pack()
        tk.Button(self.root, text="Создать", command=self.do_reg).pack(pady=10)
        tk.Button(self.root, text="Назад", command=self.show_login_ui).pack()

    def do_reg(self):
        l, p = self.reg_l.get(), self.reg_p.get()
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (login, password, role) VALUES (%s, %s, 'Пользователь')", (l, p))
        conn.commit()
        cur.close();
        conn.close()
        self.show_login_ui()

    def clear_window(self):
        for w in self.root.winfo_children(): w.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PolesyeApp(root)
    root.mainloop()