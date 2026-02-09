import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class HospitalDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления базой данных 'Больница'")
        self.root.geometry("1000x700")

        # Подключение к базе данных
        self.conn = sqlite3.connect('hospital.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Создание структуры базы данных, если она не существует
        self.create_database_structure()

        # Создание интерфейса
        self.create_interface()

    def create_database_structure(self):
        """Создание структуры базы данных"""
        try:
            # Таблица отделений
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            ''')

            # Таблица спонсоров
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sponsors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT
                )
            ''')

            # Таблица палат
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS wards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    department_id INTEGER,
                    capacity INTEGER,
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')

            # Таблица врачей
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    specialization TEXT,
                    salary_base REAL,
                    salary_bonus REAL,
                    department_id INTEGER,
                    on_vacation BOOLEAN DEFAULT 0,
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')

            # Таблица пожертвований
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sponsor_id INTEGER,
                    department_id INTEGER,
                    amount REAL,
                    donation_date DATE,
                    FOREIGN KEY (sponsor_id) REFERENCES sponsors (id),
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')

            # Таблица обследований
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS examinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id INTEGER,
                    department_id INTEGER,
                    patient_name TEXT,
                    examination_date DATE,
                    diagnosis TEXT,
                    FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')

            self.conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Ошибка при создании структуры БД: {e}")

    def create_interface(self):
        """Создание графического интерфейса"""
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка для работы с данными
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="Работа с данными")

        # Вкладка для работы со структурой БД
        structure_frame = ttk.Frame(notebook)
        notebook.add(structure_frame, text="Структура БД")

        # Вкладка для отчетов
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Отчеты")

        # Настройка вкладки работы с данными
        self.setup_data_tab(data_frame)

        # Настройка вкладки структуры БД
        self.setup_structure_tab(structure_frame)

        # Настройка вкладки отчетов
        self.setup_reports_tab(reports_frame)

    def setup_data_tab(self, parent):
        """Настройка вкладки для работы с данными"""
        # Выбор таблицы
        table_frame = ttk.LabelFrame(parent, text="Выбор таблицы")
        table_frame.pack(fill='x', padx=5, pady=5)

        self.table_var = tk.StringVar()
        tables = ['departments', 'doctors', 'wards', 'sponsors', 'donations', 'examinations']
        table_combo = ttk.Combobox(table_frame, textvariable=self.table_var, values=tables, state='readonly')
        table_combo.pack(side='left', padx=5, pady=5)
        table_combo.bind('<<ComboboxSelected>>', self.on_table_selected)

        # Кнопки операций
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Добавить запись", command=self.insert_record).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить запись", command=self.update_record).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить запись", command=self.delete_record).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить все записи", command=self.update_all_records).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить все записи", command=self.delete_all_records).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить данные", command=self.refresh_data).pack(side='left', padx=5)

        # Таблица для отображения данных
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, show='headings')
        self.tree.pack(side='left', fill='both', expand=True)

        # Полосы прокрутки для таблицы
        scrollbar_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        scrollbar_y.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(parent, orient='horizontal', command=self.tree.xview)
        scrollbar_x.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=scrollbar_x.set)

    def setup_structure_tab(self, parent):
        """Настройка вкладки для работы со структурой БД"""
        # Кнопки для операций со структурой
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Показать все таблицы", command=self.show_tables).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Показать столбцы таблицы", command=self.show_columns).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Показать связи", command=self.show_relationships).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Создать таблицу", command=self.create_table).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить таблицу", command=self.drop_table).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Добавить столбец", command=self.add_column).pack(side='left', padx=5)

        # Область для вывода информации
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.structure_text = tk.Text(text_frame, height=20, width=80)
        self.structure_text.pack(side='left', fill='both', expand=True)

        # Полоса прокрутки для текстовой области
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.structure_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.structure_text.configure(yscrollcommand=scrollbar.set)

    def setup_reports_tab(self, parent):
        """Настройка вкладки для отчетов"""
        # Кнопки отчетов
        reports_frame = ttk.Frame(parent)
        reports_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(reports_frame, text="Врачи и специализации",
                   command=self.report_doctors_specializations).pack(side='left', padx=5)
        ttk.Button(reports_frame, text="Врачи не в отпуске",
                   command=self.report_doctors_not_on_vacation).pack(side='left', padx=5)
        ttk.Button(reports_frame, text="Палаты по отделениям",
                   command=self.report_wards_by_department).pack(side='left', padx=5)
        ttk.Button(reports_frame, text="Отделения по спонсорам",
                   command=self.report_departments_by_sponsor).pack(side='left', padx=5)
        ttk.Button(reports_frame, text="Пожертвования за месяц",
                   command=self.report_donations_by_month).pack(side='left', padx=5)
        ttk.Button(reports_frame, text="Врачи и отделения",
                   command=self.report_doctors_departments).pack(side='left', padx=5)

        # Область для вывода отчетов
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.reports_text = tk.Text(text_frame, height=20, width=80)
        self.reports_text.pack(side='left', fill='both', expand=True)

        # Полоса прокрутки для текстовой области
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.reports_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.reports_text.configure(yscrollcommand=scrollbar.set)

    def on_table_selected(self, event=None):
        """Обработчик выбора таблицы"""
        table_name = self.table_var.get()
        if table_name:
            self.display_table_data(table_name)

    def refresh_data(self):
        """Обновление данных таблицы"""
        table_name = self.table_var.get()
        if table_name:
            self.display_table_data(table_name)
        else:
            messagebox.showwarning("Предупреждение", "Выберите таблицу для обновления")

    def display_table_data(self, table_name):
        """Отображение данных таблицы"""
        try:
            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Получение структуры таблицы
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()
            columns = [column[1] for column in columns_info]

            # Настройка столбцов
            self.tree['columns'] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, minwidth=50)

            # Получение данных
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()

            # Заполнение данными
            for row in rows:
                self.tree.insert('', 'end', values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {e}")

    def insert_record(self):
        """Вставка новой записи"""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return

        try:
            # Получение структуры таблицы
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()

            # Создание диалога для ввода данных
            input_dialog = RecordInputDialog(self.root, columns_info, "Добавить запись")
            self.root.wait_window(input_dialog)

            if input_dialog.result:
                # Формирование SQL запроса
                columns = [col[1] for col in columns_info if col[1].lower() != 'id']
                placeholders = ['?' for _ in columns]

                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                self.cursor.execute(query, input_dialog.result)
                self.conn.commit()

                messagebox.showinfo("Успех", "Запись успешно добавлена")
                self.display_table_data(table_name)

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении записи: {e}")

    def update_record(self):
        """Обновление записи"""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для обновления")
            return

        try:
            # Получение структуры таблицы
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = self.cursor.fetchall()

            # Получение текущих значений
            current_values = self.tree.item(selected_item[0])['values']

            # Создание диалога для обновления данных
            input_dialog = RecordInputDialog(self.root, columns_info, "Обновить запись", current_values)
            self.root.wait_window(input_dialog)

            if input_dialog.result:
                # Формирование SQL запроса
                set_clause = []
                values = []
                primary_key_col = None
                primary_key_value = None

                for i, col in enumerate(columns_info):
                    col_name = col[1]
                    if col[5]:  # PRIMARY KEY
                        primary_key_col = col_name
                        primary_key_value = current_values[i]
                    else:
                        if input_dialog.result[i] is not None:
                            set_clause.append(f"{col_name} = ?")
                            values.append(input_dialog.result[i])

                if primary_key_col and primary_key_value:
                    values.append(primary_key_value)
                    query = f"UPDATE {table_name} SET {', '.join(set_clause)} WHERE {primary_key_col} = ?"
                    self.cursor.execute(query, values)
                    self.conn.commit()

                    messagebox.showinfo("Успех", "Запись успешно обновлена")
                    self.display_table_data(table_name)
                else:
                    messagebox.showerror("Ошибка", "Не удалось определить первичный ключ")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении записи: {e}")

    def delete_record(self):
        """Удаление записи"""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную запись?"):
            try:
                # Получение структуры таблицы
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()

                # Поиск первичного ключа
                primary_key_col = None
                for col in columns_info:
                    if col[5]:  # PRIMARY KEY
                        primary_key_col = col[1]
                        break

                if primary_key_col:
                    # Получение значения первичного ключа
                    current_values = self.tree.item(selected_item[0])['values']
                    primary_key_index = [col[1] for col in columns_info].index(primary_key_col)
                    primary_key_value = current_values[primary_key_index]

                    # Удаление записи
                    query = f"DELETE FROM {table_name} WHERE {primary_key_col} = ?"
                    self.cursor.execute(query, (primary_key_value,))
                    self.conn.commit()

                    messagebox.showinfo("Успех", "Запись успешно удалена")
                    self.display_table_data(table_name)
                else:
                    messagebox.showerror("Ошибка", "Не удалось определить первичный ключ")

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении записи: {e}")

    def update_all_records(self):
        """Обновление всех записей в таблице"""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return

        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите обновить ВСЕ записи в таблице? Это действие нельзя отменить."):
            try:
                # Получение структуры таблицы
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()

                # Создание диалога для ввода новых значений
                input_dialog = RecordInputDialog(self.root, columns_info, "Обновить все записи")
                self.root.wait_window(input_dialog)

                if input_dialog.result:
                    # Формирование SQL запроса
                    set_clause = []
                    values = []

                    for i, col in enumerate(columns_info):
                        if not col[5] and input_dialog.result[i] is not None:  # Исключаем PRIMARY KEY
                            set_clause.append(f"{col[1]} = ?")
                            values.append(input_dialog.result[i])

                    if set_clause:
                        query = f"UPDATE {table_name} SET {', '.join(set_clause)}"
                        self.cursor.execute(query, values)
                        self.conn.commit()

                        messagebox.showinfo("Успех", "Все записи успешно обновлены")
                        self.display_table_data(table_name)
                    else:
                        messagebox.showwarning("Предупреждение", "Не указаны данные для обновления")

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении записей: {e}")

    def delete_all_records(self):
        """Удаление всех записей в таблице"""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("Предупреждение", "Выберите таблицу")
            return

        if messagebox.askyesno("Подтверждение",
                               "Вы уверены, что хотите удалить ВСЕ записи в таблице? Это действие нельзя отменить."):
            try:
                self.cursor.execute(f"DELETE FROM {table_name}")
                self.conn.commit()

                messagebox.showinfo("Успех", "Все записи успешно удалены")
                self.display_table_data(table_name)

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении записей: {e}")

    # Методы для работы со структурой БД
    def show_tables(self):
        """Показать все таблицы"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
            tables = self.cursor.fetchall()

            self.structure_text.delete(1.0, tk.END)
            self.structure_text.insert(tk.END, "Таблицы в базе данных:\n\n")
            for table in tables:
                self.structure_text.insert(tk.END, f"- {table[0]}\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении списка таблиц: {e}")

    def show_columns(self):
        """Показать столбцы таблицы"""
        table_name = simpledialog.askstring("Ввод", "Введите название таблицы:")
        if table_name:
            try:
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()

                self.structure_text.delete(1.0, tk.END)
                self.structure_text.insert(tk.END, f"Структура таблицы '{table_name}':\n\n")

                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_info = " PRIMARY KEY" if pk else ""
                    not_null_info = " NOT NULL" if not_null else ""
                    default_info = f" DEFAULT {default_val}" if default_val else ""

                    self.structure_text.insert(tk.END,
                                               f"- {col_name} ({col_type}{pk_info}{not_null_info}{default_info})\n")

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при получении структуры таблицы: {e}")

    def show_relationships(self):
        """Показать связи между таблицами"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
            tables = self.cursor.fetchall()

            self.structure_text.delete(1.0, tk.END)
            self.structure_text.insert(tk.END, "Связи между таблицами:\n\n")

            has_relationships = False
            for table in tables:
                table_name = table[0]

                self.cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = self.cursor.fetchall()

                if foreign_keys:
                    has_relationships = True
                    self.structure_text.insert(tk.END, f"Таблица '{table_name}':\n")
                    for fk in foreign_keys:
                        id, seq, fk_table, from_col, to_col, on_update, on_delete, match = fk
                        self.structure_text.insert(tk.END,
                                                   f"  Связь: {from_col} -> {fk_table}({to_col})\n")
                    self.structure_text.insert(tk.END, "\n")

            if not has_relationships:
                self.structure_text.insert(tk.END, "Связи между таблицами не найдены.\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении информации о связях: {e}")

    def create_table(self):
        """Создание новой таблицы"""
        table_name = simpledialog.askstring("Создание таблицы", "Введите название таблицы:")
        if table_name:
            columns_def = simpledialog.askstring("Создание таблицы",
                                                 "Введите определение столбцов (например: id INTEGER PRIMARY KEY, name TEXT, age INTEGER):")
            if columns_def:
                try:
                    query = f"CREATE TABLE {table_name} ({columns_def})"
                    self.cursor.execute(query)
                    self.conn.commit()

                    messagebox.showinfo("Успех", f"Таблица '{table_name}' успешно создана")
                    self.show_tables()

                except sqlite3.Error as e:
                    messagebox.showerror("Ошибка", f"Ошибка при создании таблицы: {e}")

    def drop_table(self):
        """Удаление таблицы"""
        table_name = simpledialog.askstring("Удаление таблицы", "Введите название таблицы для удаления:")
        if table_name and messagebox.askyesno("Подтверждение",
                                              f"Вы уверены, что хотите удалить таблицу '{table_name}'?"):
            try:
                self.cursor.execute(f"DROP TABLE {table_name}")
                self.conn.commit()

                messagebox.showinfo("Успех", f"Таблица '{table_name}' успешно удалена")
                self.show_tables()

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении таблицы: {e}")

    def add_column(self):
        """Добавление столбца в таблицу"""
        table_name = simpledialog.askstring("Добавление столбца", "Введите название таблицы:")
        if table_name:
            column_def = simpledialog.askstring("Добавление столбца",
                                                "Введите определение столбца (например: new_column TEXT):")
            if column_def:
                try:
                    query = f"ALTER TABLE {table_name} ADD COLUMN {column_def}"
                    self.cursor.execute(query)
                    self.conn.commit()

                    messagebox.showinfo("Успех", f"Столбец успешно добавлен в таблицу '{table_name}'")
                    self.show_columns()

                except sqlite3.Error as e:
                    messagebox.showerror("Ошибка", f"Ошибка при добавлении столбца: {e}")

    # Методы для генерации отчетов
    def report_doctors_specializations(self):
        """Отчет: врачи и их специализации"""
        try:
            self.cursor.execute('''
                SELECT first_name || ' ' || last_name AS full_name, specialization 
                FROM doctors
                ORDER BY full_name
            ''')
            results = self.cursor.fetchall()

            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(tk.END, "Врачи и их специализации:\n\n")
            for row in results:
                self.reports_text.insert(tk.END, f"• {row[0]} - {row[1]}\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при формировании отчета: {e}")

    def report_doctors_not_on_vacation(self):
        """Отчет: врачи не в отпуске с зарплатами"""
        try:
            self.cursor.execute('''
                SELECT last_name, (salary_base + COALESCE(salary_bonus, 0)) AS total_salary
                FROM doctors
                WHERE on_vacation = 0
                ORDER BY total_salary DESC
            ''')
            results = self.cursor.fetchall()

            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(tk.END, "Врачи не в отпуске и их зарплаты:\n\n")
            total_sum = 0
            for row in results:
                salary = row[1]
                self.reports_text.insert(tk.END, f"• {row[0]} - {salary:,.2f} руб.\n")
                total_sum += salary

            self.reports_text.insert(tk.END, f"\nОбщая сумма зарплат: {total_sum:,.2f} руб.\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при формировании отчета: {e}")

    def report_wards_by_department(self):
        """Отчет: палаты по отделениям"""
        # Сначала покажем доступные отделения
        try:
            self.cursor.execute("SELECT name FROM departments")
            departments = [row[0] for row in self.cursor.fetchall()]

            if not departments:
                messagebox.showwarning("Предупреждение", "В базе данных нет отделений")
                return

            department = simpledialog.askstring("Отчет",
                                                f"Введите название отделения из списка: {', '.join(departments)}")
            if department:
                self.cursor.execute('''
                    SELECT w.name, w.capacity
                    FROM wards w
                    JOIN departments d ON w.department_id = d.id
                    WHERE d.name = ?
                    ORDER BY w.name
                ''', (department,))
                results = self.cursor.fetchall()

                self.reports_text.delete(1.0, tk.END)
                self.reports_text.insert(tk.END, f"Палаты в отделении '{department}':\n\n")
                total_capacity = 0
                for row in results:
                    self.reports_text.insert(tk.END, f"• {row[0]} (вместимость: {row[1]} чел.)\n")
                    total_capacity += row[1]

                self.reports_text.insert(tk.END, f"\nОбщая вместимость: {total_capacity} чел.\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при формировании отчета: {e}")

    def report_departments_by_sponsor(self):
        """Отчет: отделения по спонсорам"""
        try:
            self.cursor.execute("SELECT company_name FROM sponsors")
            sponsors = [row[0] for row in self.cursor.fetchall()]

            if not sponsors:
                messagebox.showwarning("Предупреждение", "В базе данных нет спонсоров")
                return

            sponsor = simpledialog.askstring("Отчет",
                                             f"Введите название компании-спонсора из списка: {', '.join(sponsors)}")
            if sponsor:
                self.cursor.execute('''
                    SELECT DISTINCT d.name, d.description
                    FROM departments d
                    JOIN donations dn ON d.id = dn.department_id
                    JOIN sponsors s ON dn.sponsor_id = s.id
                    WHERE s.company_name = ?
                ''', (sponsor,))
                results = self.cursor.fetchall()

                self.reports_text.delete(1.0, tk.END)
                self.reports_text.insert(tk.END, f"Отделения, спонсируемые компанией '{sponsor}':\n\n")
                for row in results:
                    self.reports_text.insert(tk.END, f"• {row[0]}")
                    if row[1]:
                        self.reports_text.insert(tk.END, f" - {row[1]}")
                    self.reports_text.insert(tk.END, "\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при формировании отчета: {e}")

    def report_donations_by_month(self):
        """Отчет: пожертвования за месяц"""
        month_year = simpledialog.askstring("Отчет", "Введите месяц и год в формате ММ-ГГГГ (например: 01-2024):")
        if month_year:
            try:
                # Преобразование ввода в формат даты
                month, year = month_year.split('-')
                start_date = f"{year}-{month}-01"

                # Определение последнего дня месяца
                if month in ['01', '03', '05', '07', '08', '10', '12']:
                    end_date = f"{year}-{month}-31"
                elif month in ['04', '06', '09', '11']:
                    end_date = f"{year}-{month}-30"
                else:
                    # Февраль (учитываем високосный год)
                    if int(year) % 4 == 0 and (int(year) % 100 != 0 or int(year) % 400 == 0):
                        end_date = f"{year}-{month}-29"
                    else:
                        end_date = f"{year}-{month}-28"

                self.cursor.execute('''
                    SELECT d.name, s.company_name, dn.amount, dn.donation_date
                    FROM donations dn
                    JOIN departments d ON dn.department_id = d.id
                    JOIN sponsors s ON dn.sponsor_id = s.id
                    WHERE dn.donation_date BETWEEN ? AND ?
                    ORDER BY dn.donation_date
                ''', (start_date, end_date))
                results = self.cursor.fetchall()

                self.reports_text.delete(1.0, tk.END)
                self.reports_text.insert(tk.END, f"Пожертвования за {month_year}:\n\n")
                total = 0
                for row in results:
                    self.reports_text.insert(tk.END,
                                             f"• Отделение: {row[0]}\n")
                    self.reports_text.insert(tk.END,
                                             f"  Спонсор: {row[1]}, Сумма: {row[2]:,.2f} руб., Дата: {row[3]}\n\n")
                    total += row[2]

                self.reports_text.insert(tk.END, f"Общая сумма пожертвований: {total:,.2f} руб.\n")

            except (ValueError, sqlite3.Error) as e:
                messagebox.showerror("Ошибка", f"Ошибка при формировании отчета: {e}")

    def report_doctors_departments(self):
        """Отчет: врачи с указанием отделений"""
        try:
            self.cursor.execute('''
                SELECT d.last_name, d.first_name, dep.name, d.specialization
                FROM doctors d
                JOIN departments dep ON d.department_id = dep.id
                ORDER BY dep.name, d.last_name
            ''')
            results = self.cursor.fetchall()

            self.reports_text.delete(1.0, tk.END)
            self.reports_text.insert(tk.END, "Врачи и их отделения:\n\n")

            current_department = ""
            for row in results:
                if row[2] != current_department:
                    current_department = row[2]
                    self.reports_text.insert(tk.END, f"\n{current_department}:\n")
                self.reports_text.insert(tk.END, f"  • {row[0]} {row[1]} ({row[3]})\n")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при формировании отчета: {e}")

    def __del__(self):
        """Закрытие соединения с БД при уничтожении объекта"""
        if hasattr(self, 'conn'):
            self.conn.close()


class RecordInputDialog(tk.Toplevel):
    """Диалог для ввода данных записи"""

    def __init__(self, parent, columns_info, title, current_values=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x500")
        self.parent = parent
        self.columns_info = columns_info
        self.current_values = current_values
        self.result = None

        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Центрирование окна"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Создание виджетов"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Создание полей ввода
        self.entries = []

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, col in enumerate(self.columns_info):
            ttk.Label(scrollable_frame, text=f"{col[1]} ({col[2]}):").grid(row=i, column=0, sticky='w', padx=5, pady=2)

            entry = ttk.Entry(scrollable_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=2)

            # Заполнение текущими значениями, если они есть
            if self.current_values and i < len(self.current_values):
                entry.insert(0, str(self.current_values[i]))

            self.entries.append(entry)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=10)

        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.on_cancel).pack(side='left', padx=5)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def on_ok(self):
        """Обработка нажатия OK"""
        self.result = []
        for entry in self.entries:
            value = entry.get().strip()
            # Пустые строки преобразуем в None
            self.result.append(value if value else None)
        self.destroy()

    def on_cancel(self):
        """Обработка нажатия Отмена"""
        self.result = None
        self.destroy()


def main():
    """Главная функция приложения"""
    root = tk.Tk()
    app = HospitalDBApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()