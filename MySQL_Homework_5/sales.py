import sqlite3
import os


class SalesDB:
    def __init__(self, db_name="sales.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        db_exists = os.path.exists(self.db_name)
        conn = self.connect()
        cursor = conn.cursor()

        if not db_exists:
            cursor.executescript("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            );

            CREATE TABLE sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            );

            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                product_id INTEGER,
                seller_id INTEGER,
                sale_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (seller_id) REFERENCES sellers(id)
            );

            CREATE TABLE duplicate_customers_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT,
                info TEXT
            );

            CREATE TABLE purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                product_name TEXT,
                sale_date TEXT
            );

            -- 1. Лог одинаковых фамилий покупателей
            CREATE TRIGGER check_duplicate_customer_lastname
            AFTER INSERT ON customers
            BEGIN
                INSERT INTO duplicate_customers_log (last_name, info)
                SELECT NEW.last_name,
                       'Найден покупатель с такой же фамилией'
                WHERE (
                    SELECT COUNT(*) FROM customers
                    WHERE last_name = NEW.last_name
                ) > 1;
            END;

            -- 2. Архивация истории покупок при удалении покупателя
            CREATE TRIGGER archive_customer_sales
            BEFORE DELETE ON customers
            BEGIN
                INSERT INTO purchase_history (customer_name, product_name, sale_date)
                SELECT
                    OLD.first_name || ' ' || OLD.last_name,
                    products.name,
                    sales.sale_date
                FROM sales
                JOIN products ON products.id = sales.product_id
                WHERE sales.customer_id = OLD.id;
            END;

            -- 3. Запрет добавления продавца, если он есть среди покупателей
            CREATE TRIGGER prevent_seller_if_customer_exists
            BEFORE INSERT ON sellers
            WHEN EXISTS (
                SELECT 1 FROM customers
                WHERE first_name = NEW.first_name
                  AND last_name = NEW.last_name
            )
            BEGIN
                SELECT RAISE(ABORT, 'Этот человек уже существует как покупатель');
            END;

            -- 4. Запрет добавления покупателя, если он есть среди продавцов
            CREATE TRIGGER prevent_customer_if_seller_exists
            BEFORE INSERT ON customers
            WHEN EXISTS (
                SELECT 1 FROM sellers
                WHERE first_name = NEW.first_name
                  AND last_name = NEW.last_name
            )
            BEGIN
                SELECT RAISE(ABORT, 'Этот человек уже существует как продавец');
            END;

            -- 5. Запрет продажи определённых товаров
            CREATE TRIGGER forbid_specific_products
            BEFORE INSERT ON sales
            WHEN (
                SELECT name FROM products WHERE id = NEW.product_id
            ) IN ('яблоки', 'груши', 'сливы', 'кинза')
            BEGIN
                SELECT RAISE(ABORT, 'Продажа данного товара запрещена');
            END;
            """)
            conn.commit()

        conn.close()

    # ---------------- Демонстрация ----------------
    def demo_triggers(self):
        conn = self.connect()
        cursor = conn.cursor()

        print("\n=== Демонстрация триггеров Задания 3 ===")

        # --- Добавление покупателей ---
        print("\nДобавляем покупателей:")
        customers = [
            ("Анна", "Иванова"),
            ("Мария", "Иванова"),  # совпадение фамилии
            ("Олег", "Смирнов"),
        ]
        for f, l in customers:
            try:
                cursor.execute("INSERT INTO customers (first_name, last_name) VALUES (?, ?)", (f, l))
                conn.commit()
                print(f"Покупатель {f} {l} добавлен")
            except sqlite3.IntegrityError as e:
                print(f"Ошибка: {e}")

        # Проверка лога дубликатов
        print("\nЛог совпадений фамилий покупателей:")
        cursor.execute("SELECT * FROM duplicate_customers_log")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Фамилия: {row[1]}, Info: {row[2]}")

        # --- Добавление продавцов ---
        print("\nДобавляем продавцов:")
        sellers = [
            ("Игорь", "Петров"),
            ("Анна", "Иванова"),  # запрещено, есть покупатель
        ]
        for f, l in sellers:
            try:
                cursor.execute("INSERT INTO sellers (first_name, last_name) VALUES (?, ?)", (f, l))
                conn.commit()
                print(f"Продавец {f} {l} добавлен")
            except sqlite3.IntegrityError as e:
                print(f"Ошибка: {e}")

        # --- Добавление продуктов ---
        print("\nДобавляем продукты:")
        products = ["хлеб", "молоко", "яблоки", "сыр"]
        for p in products:
            cursor.execute("INSERT OR IGNORE INTO products (name) VALUES (?)", (p,))
        conn.commit()
        print("Продукты добавлены:", products)

        # --- Добавление продаж ---
        print("\nДобавляем продажи:")
        # покупатель 1 покупает хлеб (разрешено)
        cursor.execute("INSERT INTO sales (customer_id, product_id, seller_id, sale_date) VALUES (1, 1, 1, '2026-02-08')")
        conn.commit()
        print("Продажа: Анна Иванова купила хлеб")

        # покупатель 1 покупает яблоки (запрещено)
        try:
            cursor.execute("INSERT INTO sales (customer_id, product_id, seller_id, sale_date) VALUES (1, 3, 1, '2026-02-08')")
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Ошибка при продаже яблок: {e}")

        # --- Удаление покупателя ---
        print("\nУдаляем покупателя Олег Смирнов (архивация истории):")
        cursor.execute("DELETE FROM customers WHERE first_name='Олег' AND last_name='Смирнов'")
        conn.commit()

        print("История покупок после удаления:")
        cursor.execute("SELECT * FROM purchase_history")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Клиент: {row[1]}, Продукт: {row[2]}, Дата: {row[3]}")

        # --- Проверка таблиц ---
        print("\nТекущие покупатели:")
        cursor.execute("SELECT * FROM customers")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, {row[1]} {row[2]}")

        print("\nТекущие продавцы:")
        cursor.execute("SELECT * FROM sellers")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, {row[1]} {row[2]}")

        print("\nТекущие продажи:")
        cursor.execute("SELECT * FROM sales")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Customer_ID: {row[1]}, Product_ID: {row[2]}, Seller_ID: {row[3]}, Date: {row[4]}")

        conn.close()


# ------------------ main ------------------

if __name__ == "__main__":
    # Удаляем старую БД для чистого запуска
    if os.path.exists("sales.db"):
        os.remove("sales.db")

    db = SalesDB()
    db.initialize_database()
    db.demo_triggers()

