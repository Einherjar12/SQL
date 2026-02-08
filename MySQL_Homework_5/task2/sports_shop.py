import sqlite3
import os
from datetime import datetime


class SportsShopDB:
    def __init__(self, db_name="sport_shop.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        db_exists = os.path.exists(self.db_name)
        conn = self.connect()
        cursor = conn.cursor()

        if not db_exists:
            cursor.executescript("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            );

            CREATE TABLE employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date TEXT NOT NULL
            );

            CREATE TABLE employees_archive (
                id INTEGER,
                full_name TEXT,
                position TEXT,
                salary REAL,
                hire_date TEXT,
                fire_date TEXT
            );

            CREATE TRIGGER product_insert_check
            BEFORE INSERT ON products
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM products
                WHERE name = NEW.name
                  AND category = NEW.category
                  AND price = NEW.price
            )
            BEGIN
                UPDATE products
                SET quantity = quantity + NEW.quantity
                WHERE name = NEW.name
                  AND category = NEW.category
                  AND price = NEW.price;

                SELECT RAISE(IGNORE);
            END;

            CREATE TRIGGER seller_limit
            BEFORE INSERT ON employees
            FOR EACH ROW
            WHEN LOWER(NEW.position) = 'продавец'
             AND (
                SELECT COUNT(*) FROM employees
                WHERE LOWER(position) = 'продавец'
             ) >= 6
            BEGIN
                SELECT RAISE(ABORT, 'Невозможно добавить более 6 продавцов');
            END;

            CREATE TRIGGER employee_fire_archive
            BEFORE DELETE ON employees
            FOR EACH ROW
            BEGIN
                INSERT INTO employees_archive
                VALUES (
                    OLD.id,
                    OLD.full_name,
                    OLD.position,
                    OLD.salary,
                    OLD.hire_date,
                    DATETIME('now')
                );
            END;
            """)
            conn.commit()

        conn.close()

    # ---------------- Демонстрация ----------------

    def demo_products(self):
        print("\n1. Демонстрация триггера для товаров:")
        conn = self.connect()
        cursor = conn.cursor()

        products = [
            ("Беговая дорожка", "Кардиотренажёры", 79900.0, 3),
            ("Гантели 10 кг", "Силовой инвентарь", 4200.0, 12),
            ("Беговая дорожка", "Кардиотренажёры", 79900.0, 2),
        ]

        for name, category, price, qty in products:
            cursor.execute("""
            INSERT INTO products (name, category, price, quantity)
            VALUES (?, ?, ?, ?)
            """, (name, category, price, qty))
            print(f"Товар '{name}' добавлен/обновлён")

        conn.commit()

        print("Текущие товары на складе:")
        cursor.execute("SELECT * FROM products")
        for row in cursor.fetchall():
            print(
                f"  ID: {row[0]}, Название: {row[1]}, "
                f"Категория: {row[2]}, Цена: {row[3]}, Количество: {row[4]}"
            )

        conn.close()

    def demo_sellers(self):
        print("\n" + "=" * 50)
        print("\n2. Демонстрация триггера ограничения продавцов:")

        conn = self.connect()
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        employees = [
            ("Климов Артём", "продавец", 36000),
            ("Романова Полина", "продавец", 37500),
            ("Фёдоров Максим", "продавец", 35500),
            ("Никитина Алина", "продавец", 38000),
            ("Гусев Денис", "продавец", 36500),
            ("Власова Ирина", "продавец", 37000),
        ]

        for name, position, salary in employees:
            try:
                cursor.execute("""
                INSERT INTO employees (full_name, position, salary, hire_date)
                VALUES (?, ?, ?, ?)
                """, (name, position, salary, today))
                conn.commit()
                print(f"Сотрудник '{name}' успешно добавлен")
            except sqlite3.IntegrityError as e:
                print(f"Ошибка: {e}")

        print("Пытаемся добавить седьмого продавца...")
        try:
            cursor.execute("""
            INSERT INTO employees (full_name, position, salary, hire_date)
            VALUES ('Лазарев Кирилл', 'продавец', 35000, ?)
            """, (today,))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Ошибка: {e}")

        print("Добавляем администратора...")
        cursor.execute("""
        INSERT INTO employees (full_name, position, salary, hire_date)
        VALUES ('Соколова Марина', 'администратор', 52000, ?)
        """, (today,))
        conn.commit()
        print("Сотрудник 'Соколова Марина' успешно добавлен")

        print("Текущие сотрудники:")
        cursor.execute("SELECT * FROM employees")
        for row in cursor.fetchall():
            print(
                f"  ID: {row[0]}, Имя: {row[1]}, "
                f"Должность: {row[2]}, Зарплата: {row[3]}"
            )

        conn.close()

    def demo_archive(self):
        print("\n" + "=" * 50)
        print("\n3. Демонстрация триггера архивации сотрудников:")

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM employees WHERE id = 3")
        conn.commit()
        print("Сотрудник с ID 3 уволен и перемещён в архив")

        print("Архивные сотрудники:")
        cursor.execute("SELECT * FROM employees_archive")
        for row in cursor.fetchall():
            print(
                f"  ID: {row[0]}, Имя: {row[1]}, Должность: {row[2]}, "
                f"Дата приёма: {row[4]}, Дата увольнения: {row[5]}"
            )

        conn.close()


# ------------------ main ------------------

if __name__ == "__main__":
    print("=== База данных 'Спортивный магазин' ===")
    shop_db = SportsShopDB()
    shop_db.initialize_database()
    shop_db.demo_products()
    shop_db.demo_sellers()
    shop_db.demo_archive()
