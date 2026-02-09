import sqlite3


# Создание трёхтабличной базы данных Sales (продажи) (Задание 1)
class SalesDB:
    def __init__(self, db_name='sales.db'):
        self.db_name = db_name
        self.export_path = 'results.txt'  # путь по умолчанию для сохранения

    def connect(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = self.connect()
        cursor = conn.cursor()

        # Создание таблицы Salesmen (продавцы)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Salesmen (
                salesman_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        ''')

        # Создание таблицы Customers (покупатели)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        ''')

        # Создание таблицы Sales (продажи)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                salesman_id INTEGER,
                customer_id INTEGER,
                amount REAL NOT NULL,
                sale_date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (salesman_id) REFERENCES Salesmen(salesman_id),
                FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
            )
        ''')

        conn.commit()
        conn.close()

        # Добавление тестовых данных, если таблицы пустые
        self.add_sample_data()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Salesmen")
        if cursor.fetchone()[0] == 0:
            # Продавцы
            salesmen = [
                ('Антон Морозов', 'morozov@mail.com', '+79031234567'),
                ('Екатерина Волкова', 'volkova@mail.com', '+79039876543'),
                ('Дмитрий Орлов', 'orlov@mail.com', '+79035558899')
            ]
            cursor.executemany(
                "INSERT INTO Salesmen (name, email, phone) VALUES (?, ?, ?)",
                salesmen
            )

            # Покупатели
            customers = [
                ('ООО "Альфа"', 'alpha@company.ru', '+74951112233'),
                ('ИП Кузнецов', 'kuznetsov@ip.ru', '+79164445566'),
                ('ООО "Гамма"', 'gamma@company.ru', '+74957778899')
            ]
            cursor.executemany(
                "INSERT INTO Customers (name, email, phone) VALUES (?, ?, ?)",
                customers
            )

            # Продажи
            sales = [
                (1, 1, 13200.00),
                (1, 2, 9100.50),
                (2, 1, 27800.75),
                (2, 3, 15400.00),
                (3, 2, 18750.25),
                (3, 3, 6400.00)
            ]
            cursor.executemany(
                "INSERT INTO Sales (salesman_id, customer_id, amount) VALUES (?, ?, ?)",
                sales
            )

            conn.commit()

        conn.close()

    def display_all_sales(self):
        """Отображение всех сделок"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            ORDER BY s.sale_date DESC
        ''')

        results = cursor.fetchall()
        print("\n=== ВСЕ СДЕЛКИ ===")
        for row in results:
            print(f"ID: {row[0]}, Продавец: {row[1]}, Покупатель: {row[2]}, Сумма: {row[3]:.2f}, Дата: {row[4]}")

        conn.close()
        return results

    def display_salesman_sales(self, salesman_id):
        """Отображение сделок конкретного продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.salesman_id = ?
            ORDER BY s.amount DESC
        ''', (salesman_id,))

        results = cursor.fetchall()
        if results:
            print(f"\n=== СДЕЛКИ ПРОДАВЦА {results[0][1]} ===")
            for row in results:
                print(f"ID: {row[0]}, Покупатель: {row[2]}, Сумма: {row[3]:.2f}, Дата: {row[4]}")
        else:
            print("Продавец не найден или у него нет сделок")

        conn.close()
        return results

    def display_max_sale(self):
        """Отображение максимальной по сумме сделки"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            ORDER BY s.amount DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        if result:
            print("\n=== МАКСИМАЛЬНАЯ СДЕЛКА ===")
            print(
                f"ID: {result[0]}, Продавец: {result[1]}, Покупатель: {result[2]}, Сумма: {result[3]:.2f}, Дата: {result[4]}")

        conn.close()
        return [result] if result else []

    def display_min_sale(self):
        """Отображение минимальной по сумме сделки"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            ORDER BY s.amount ASC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        if result:
            print("\n=== МИНИМАЛЬНАЯ СДЕЛКА ===")
            print(
                f"ID: {result[0]}, Продавец: {result[1]}, Покупатель: {result[2]}, Сумма: {result[3]:.2f}, Дата: {result[4]}")

        conn.close()
        return [result] if result else []

    def display_salesman_max_sale(self, salesman_id):
        """Отображение максимальной по сумме сделки для конкретного продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.salesman_id = ?
            ORDER BY s.amount DESC
            LIMIT 1
        ''', (salesman_id,))

        result = cursor.fetchone()
        if result:
            print(f"\n=== МАКСИМАЛЬНАЯ СДЕЛКА ПРОДАВЦА {result[1]} ===")
            print(f"ID: {result[0]}, Покупатель: {result[2]}, Сумма: {result[3]:.2f}, Дата: {result[4]}")
        else:
            print("Продавец не найден или у него нет сделок")

        conn.close()
        return [result] if result else []

    def display_salesman_min_sale(self, salesman_id):
        """Отображение минимальной по сумме сделки для конкретного продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.salesman_id = ?
            ORDER BY s.amount ASC
            LIMIT 1
        ''', (salesman_id,))

        result = cursor.fetchone()
        if result:
            print(f"\n=== МИНИМАЛЬНАЯ СДЕЛКА ПРОДАВЦА {result[1]} ===")
            print(f"ID: {result[0]}, Покупатель: {result[2]}, Сумма: {result[3]:.2f}, Дата: {result[4]}")
        else:
            print("Продавец не найден или у него нет сделок")

        conn.close()
        return [result] if result else []

    def display_customer_max_sale(self, customer_id):
        """Отображение максимальной по сумме сделки для конкретного покупателя"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.customer_id = ?
            ORDER BY s.amount DESC
            LIMIT 1
        ''', (customer_id,))

        result = cursor.fetchone()
        if result:
            print(f"\n=== МАКСИМАЛЬНАЯ СДЕЛКА ПОКУПАТЕЛЯ {result[2]} ===")
            print(f"ID: {result[0]}, Продавец: {result[1]}, Сумма: {result[3]:.2f}, Дата: {result[4]}")
        else:
            print("Покупатель не найден или у него нет сделок")

        conn.close()
        return [result] if result else []

    def display_customer_min_sale(self, customer_id):
        """Отображение минимальной по сумме сделки для конкретного покупателя"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT s.sale_id, sm.name as salesman, c.name as customer, s.amount, s.sale_date
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.customer_id = ?
            ORDER BY s.amount ASC
            LIMIT 1
        ''', (customer_id,))

        result = cursor.fetchone()
        if result:
            print(f"\n=== МИНИМАЛЬНАЯ СДЕЛКА ПОКУПАТЕЛЯ {result[2]} ===")
            print(f"ID: {result[0]}, Продавец: {result[1]}, Сумма: {result[3]:.2f}, Дата: {result[4]}")
        else:
            print("Покупатель не найден или у него нет сделок")

        conn.close()
        return [result] if result else []

    def display_top_salesman(self):
        """Отображение продавца с максимальной суммой продаж"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT sm.name, SUM(s.amount) as total_sales
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            GROUP BY sm.salesman_id
            ORDER BY total_sales DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        if result:
            print("\n=== ПРОДАВЕЦ С МАКСИМАЛЬНОЙ СУММОЙ ПРОДАЖ ===")
            print(f"Продавец: {result[0]}, Общая сумма: {result[1]:.2f}")

        conn.close()
        return [result] if result else []

    def display_bottom_salesman(self):
        """Отображение продавца с минимальной суммой продаж"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT sm.name, SUM(s.amount) as total_sales
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            GROUP BY sm.salesman_id
            ORDER BY total_sales ASC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        if result:
            print("\n=== ПРОДАВЕЦ С МИНИМАЛЬНОЙ СУММОЙ ПРОДАЖ ===")
            print(f"Продавец: {result[0]}, Общая сумма: {result[1]:.2f}")

        conn.close()
        return [result] if result else []

    def display_top_customer(self):
        """Отображение покупателя с максимальной суммой покупок"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.name, SUM(s.amount) as total_purchases
            FROM Sales s
            JOIN Customers c ON s.customer_id = c.customer_id
            GROUP BY c.customer_id
            ORDER BY total_purchases DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        if result:
            print("\n=== ПОКУПАТЕЛЬ С МАКСИМАЛЬНОЙ СУММОЙ ПОКУПОК ===")
            print(f"Покупатель: {result[0]}, Общая сумма: {result[1]:.2f}")

        conn.close()
        return [result] if result else []

    def display_avg_customer_purchase(self, customer_id):
        """Отображение средней суммы покупки для конкретного покупателя"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.name, AVG(s.amount) as avg_purchase
            FROM Sales s
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.customer_id = ?
            GROUP BY c.customer_id
        ''', (customer_id,))

        result = cursor.fetchone()
        if result:
            print(f"\n=== СРЕДНЯЯ СУММА ПОКУПКИ ПОКУПАТЕЛЯ {result[0]} ===")
            print(f"Средняя сумма: {result[1]:.2f}")
        else:
            print("Покупатель не найден или у него нет сделок")

        conn.close()
        return [result] if result else []

    def display_avg_salesman_sale(self, salesman_id):
        """Отображение средней суммы покупки для конкретного продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT sm.name, AVG(s.amount) as avg_sale
            FROM Sales s
            JOIN Salesmen sm ON s.salesman_id = sm.salesman_id
            WHERE s.salesman_id = ?
            GROUP BY sm.salesman_id
        ''', (salesman_id,))

        result = cursor.fetchone()
        if result:
            print(f"\n=== СРЕДНЯЯ СУММА ПРОДАЖИ ПРОДАВЦА {result[0]} ===")
            print(f"Средняя сумма: {result[1]:.2f}")
        else:
            print("Продавец не найден или у него нет сделок")

        conn.close()
        return [result] if result else []

    # Методы для работы с данными (Задание 2)
    def insert_sale(self, salesman_id, customer_id, amount):
        """Добавление новой продажи"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO Sales (salesman_id, customer_id, amount)
                VALUES (?, ?, ?)
            ''', (salesman_id, customer_id, amount))
            conn.commit()
            print("Продажа успешно добавлена!")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении продажи: {e}")
        finally:
            conn.close()

    def update_sale(self, sale_id, amount):
        """Обновление суммы продажи"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE Sales SET amount = ? WHERE sale_id = ?
            ''', (amount, sale_id))

            if cursor.rowcount > 0:
                print("Продажа успешно обновлена!")
            else:
                print("Продажа с указанным ID не найдена")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении продажи: {e}")
        finally:
            conn.close()

    def delete_sale(self, sale_id):
        """Удаление продажи"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM Sales WHERE sale_id = ?', (sale_id,))

            if cursor.rowcount > 0:
                print("Продажа успешно удалена!")
            else:
                print("Продажа с указанным ID не найдена")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при удалении продажи: {e}")
        finally:
            conn.close()

    def insert_salesman(self, name, email, phone):
        """Добавление нового продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO Salesmen (name, email, phone)
                VALUES (?, ?, ?)
            ''', (name, email, phone))
            conn.commit()
            print("Продавец успешно добавлен!")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении продавца: {e}")
        finally:
            conn.close()

    def update_salesman(self, salesman_id, name, email, phone):
        """Обновление данных продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE Salesmen SET name = ?, email = ?, phone = ? 
                WHERE salesman_id = ?
            ''', (name, email, phone, salesman_id))

            if cursor.rowcount > 0:
                print("Данные продавца успешно обновлены!")
            else:
                print("Продавец с указанным ID не найден")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении продавца: {e}")
        finally:
            conn.close()

    def delete_salesman(self, salesman_id):
        """Удаление продавца"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            # Проверяем, есть ли связанные продажи
            cursor.execute('SELECT COUNT(*) FROM Sales WHERE salesman_id = ?', (salesman_id,))
            if cursor.fetchone()[0] > 0:
                print("Невозможно удалить продавца, у которого есть связанные продажи")
                return

            cursor.execute('DELETE FROM Salesmen WHERE salesman_id = ?', (salesman_id,))

            if cursor.rowcount > 0:
                print("Продавец успешно удален!")
            else:
                print("Продавец с указанным ID не найден")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при удалении продавца: {e}")
        finally:
            conn.close()

    def insert_customer(self, name, email, phone):
        """Добавление нового покупателя"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO Customers (name, email, phone)
                VALUES (?, ?, ?)
            ''', (name, email, phone))
            conn.commit()
            print("Покупатель успешно добавлен!")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении покупателя: {e}")
        finally:
            conn.close()

    def update_customer(self, customer_id, name, email, phone):
        """Обновление данных покупателя"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE Customers SET name = ?, email = ?, phone = ? 
                WHERE customer_id = ?
            ''', (name, email, phone, customer_id))

            if cursor.rowcount > 0:
                print("Данные покупателя успешно обновлены!")
            else:
                print("Покупатель с указанным ID не найден")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении покупателя: {e}")
        finally:
            conn.close()

    def delete_customer(self, customer_id):
        """Удаление покупателя"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            # Проверяем, есть ли связанные продажи
            cursor.execute('SELECT COUNT(*) FROM Sales WHERE customer_id = ?', (customer_id,))
            if cursor.fetchone()[0] > 0:
                print("Невозможно удалить покупателя, у которого есть связанные продажи")
                return

            cursor.execute('DELETE FROM Customers WHERE customer_id = ?', (customer_id,))

            if cursor.rowcount > 0:
                print("Покупатель успешно удален!")
            else:
                print("Покупатель с указанным ID не найден")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при удалении покупателя: {e}")
        finally:
            conn.close()

    # Метод для сохранения результатов (Задание 3)
    def save_results_to_file(self, results, filename=None):
        """Сохранение результатов в файл"""
        if filename is None:
            filename = self.export_path

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for row in results:
                    f.write(str(row) + '\n')
            print(f"Результаты успешно сохранены в файл: {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")

    def set_export_path(self, path):
        """Установка пути для сохранения файлов"""
        self.export_path = path
        print(f"Путь для сохранения установлен: {path}")

    def display_salesmen(self):
        """Отображение списка продавцов"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT salesman_id, name, email, phone FROM Salesmen")
        results = cursor.fetchall()
        print("\n=== СПИСОК ПРОДАВЦОВ ===")
        for row in results:
            print(f"ID: {row[0]}, Имя: {row[1]}, Email: {row[2]}, Телефон: {row[3]}")
        conn.close()
        return results

    def display_customers(self):
        """Отображение списка покупателей"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, name, email, phone FROM Customers")
        results = cursor.fetchall()
        print("\n=== СПИСОК ПОКУПАТЕЛЕЙ ===")
        for row in results:
            print(f"ID: {row[0]}, Имя: {row[1]}, Email: {row[2]}, Телефон: {row[3]}")
        conn.close()
        return results


def main():
    db = SalesDB()
    db.initialize_database()

    while True:
        print("\n" + "=" * 50)
        print("БАЗА ДАННЫХ 'ПРОДАЖИ'")
        print("=" * 50)
        print("1. Отчеты")
        print("2. Управление данными")
        print("3. Настройки")
        print("0. Выход")

        choice = input("Выберите пункт меню: ")

        if choice == '1':
            reports_menu(db)
        elif choice == '2':
            data_management_menu(db)
        elif choice == '3':
            settings_menu(db)
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор!")


def reports_menu(db):
    """Меню отчетов"""
    while True:
        print("\n" + "-" * 30)
        print("ОТЧЕТЫ")
        print("-" * 30)
        print("1. Все сделки")
        print("2. Сделки конкретного продавца")
        print("3. Максимальная сделка")
        print("4. Минимальная сделка")
        print("5. Максимальная сделка продавца")
        print("6. Минимальная сделка продавца")
        print("7. Максимальная сделка покупателя")
        print("8. Минимальная сделка покупателя")
        print("9. Продавец с максимальной суммой продаж")
        print("10. Продавец с минимальной суммой продаж")
        print("11. Покупатель с максимальной суммой покупок")
        print("12. Средняя сумма покупки покупателя")
        print("13. Средняя сумма продажи продавца")
        print("14. Сохранить результаты в файл")
        print("0. Назад")

        choice = input("Выберите отчет: ")
        results = []

        if choice == '1':
            results = db.display_all_sales()
        elif choice == '2':
            salesman_id = int(input("Введите ID продавца: "))
            results = db.display_salesman_sales(salesman_id)
        elif choice == '3':
            results = db.display_max_sale()
        elif choice == '4':
            results = db.display_min_sale()
        elif choice == '5':
            salesman_id = int(input("Введите ID продавца: "))
            results = db.display_salesman_max_sale(salesman_id)
        elif choice == '6':
            salesman_id = int(input("Введите ID продавца: "))
            results = db.display_salesman_min_sale(salesman_id)
        elif choice == '7':
            customer_id = int(input("Введите ID покупателя: "))
            results = db.display_customer_max_sale(customer_id)
        elif choice == '8':
            customer_id = int(input("Введите ID покупателя: "))
            results = db.display_customer_min_sale(customer_id)
        elif choice == '9':
            results = db.display_top_salesman()
        elif choice == '10':
            results = db.display_bottom_salesman()
        elif choice == '11':
            results = db.display_top_customer()
        elif choice == '12':
            customer_id = int(input("Введите ID покупателя: "))
            results = db.display_avg_customer_purchase(customer_id)
        elif choice == '13':
            salesman_id = int(input("Введите ID продавца: "))
            results = db.display_avg_salesman_sale(salesman_id)
        elif choice == '14':
            if results:
                filename = input("Введите имя файла (или нажмите Enter для использования настроек): ")
                if filename:
                    db.save_results_to_file(results, filename)
                else:
                    db.save_results_to_file(results)
            else:
                print("Сначала выполните какой-либо отчет!")
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


def data_management_menu(db):
    """Меню управления данными"""
    while True:
        print("\n" + "-" * 30)
        print("УПРАВЛЕНИЕ ДАННЫМИ")
        print("-" * 30)
        print("1. Продажи")
        print("2. Продавцы")
        print("3. Покупатели")
        print("0. Назад")

        choice = input("Выберите таблицу: ")

        if choice == '1':
            sales_management(db)
        elif choice == '2':
            salesmen_management(db)
        elif choice == '3':
            customers_management(db)
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


def sales_management(db):
    """Управление продажами"""
    while True:
        print("\n--- УПРАВЛЕНИЕ ПРОДАЖАМИ ---")
        print("1. Показать все продажи")
        print("2. Добавить продажу")
        print("3. Обновить продажу")
        print("4. Удалить продажу")
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == '1':
            db.display_all_sales()
        elif choice == '2':
            db.display_salesmen()
            salesman_id = int(input("Введите ID продавца: "))
            db.display_customers()
            customer_id = int(input("Введите ID покупателя: "))
            amount = float(input("Введите сумму продажи: "))
            db.insert_sale(salesman_id, customer_id, amount)
        elif choice == '3':
            db.display_all_sales()
            sale_id = int(input("Введите ID продажи для обновления: "))
            amount = float(input("Введите новую сумму: "))
            db.update_sale(sale_id, amount)
        elif choice == '4':
            db.display_all_sales()
            sale_id = int(input("Введите ID продажи для удаления: "))
            db.delete_sale(sale_id)
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


def salesmen_management(db):
    """Управление продавцами"""
    while True:
        print("\n--- УПРАВЛЕНИЕ ПРОДАВЦАМИ ---")
        print("1. Показать всех продавцов")
        print("2. Добавить продавца")
        print("3. Обновить продавца")
        print("4. Удалить продавца")
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == '1':
            db.display_salesmen()
        elif choice == '2':
            name = input("Введите имя: ")
            email = input("Введите email: ")
            phone = input("Введите телефон: ")
            db.insert_salesman(name, email, phone)
        elif choice == '3':
            db.display_salesmen()
            salesman_id = int(input("Введите ID продавца для обновления: "))
            name = input("Введите новое имя: ")
            email = input("Введите новый email: ")
            phone = input("Введите новый телефон: ")
            db.update_salesman(salesman_id, name, email, phone)
        elif choice == '4':
            db.display_salesmen()
            salesman_id = int(input("Введите ID продавца для удаления: "))
            db.delete_salesman(salesman_id)
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


def customers_management(db):
    """Управление покупателями"""
    while True:
        print("\n--- УПРАВЛЕНИЕ ПОКУПАТЕЛЯМИ ---")
        print("1. Показать всех покупателей")
        print("2. Добавить покупателя")
        print("3. Обновить покупателя")
        print("4. Удалить покупателя")
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == '1':
            db.display_customers()
        elif choice == '2':
            name = input("Введите имя: ")
            email = input("Введите email: ")
            phone = input("Введите телефон: ")
            db.insert_customer(name, email, phone)
        elif choice == '3':
            db.display_customers()
            customer_id = int(input("Введите ID покупателя для обновления: "))
            name = input("Введите новое имя: ")
            email = input("Введите новый email: ")
            phone = input("Введите новый телефон: ")
            db.update_customer(customer_id, name, email, phone)
        elif choice == '4':
            db.display_customers()
            customer_id = int(input("Введите ID покупателя для удаления: "))
            db.delete_customer(customer_id)
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


def settings_menu(db):
    """Меню настроек"""
    while True:
        print("\n--- НАСТРОЙКИ ---")
        print("1. Установить путь для сохранения файлов")
        print("0. Назад")

        choice = input("Выберите действие: ")

        if choice == '1':
            path = input("Введите путь для сохранения файлов: ")
            db.set_export_path(path)
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()
