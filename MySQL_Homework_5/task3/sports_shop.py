import sqlite3

class SportsShopDB:
    def __init__(self, db_name='sports_shop.db'):
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблица производителей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT
            )
        ''')

        # Таблица категорий товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        # Таблица товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                manufacturer_id INTEGER,
                price DECIMAL(10,2),
                quantity INTEGER,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
            )
        ''')

        # Таблица клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                registration_date DATE,
                phone TEXT
            )
        ''')

        # Таблица продавцов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hire_date DATE,
                salary DECIMAL(10,2)
            )
        ''')

        # Таблица продаж
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                customer_id INTEGER,
                seller_id INTEGER,
                sale_date DATE,
                quantity INTEGER,
                total_amount DECIMAL(10,2),
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (seller_id) REFERENCES sellers(id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    # ---------------- Методы для демонстрации ----------------

    def get_all_products(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, c.name as category, m.name as manufacturer, 
                   p.price, p.quantity, p.description
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
            ORDER BY p.id
        ''')
        products = cursor.fetchall()
        conn.close()
        print("\nВсе товары:")
        for p in products:
            print(f"ID: {p[0]}, {p[1]}, Категория: {p[2]}, Производитель: {p[3]}, Цена: {p[4]}, Кол-во: {p[5]}, Описание: {p[6]}")
        return products

    def get_products_by_category(self, category_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, c.name as category, m.name as manufacturer, 
                   p.price, p.quantity, p.description
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE c.name = ? AND p.quantity > 0
            ORDER BY p.id
        ''', (category_name,))
        products = cursor.fetchall()
        conn.close()
        print(f"\nТовары категории '{category_name}':")
        for p in products:
            print(f"ID: {p[0]}, {p[1]}, Производитель: {p[3]}, Цена: {p[4]}, Кол-во: {p[5]}")
        if not products:
            print("Товары не найдены или отсутствуют в наличии")
        return products

    def get_top3_oldest_customers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, registration_date, phone
            FROM customers
            ORDER BY registration_date ASC
            LIMIT 3
        ''')
        customers = cursor.fetchall()
        conn.close()
        print("\nТоп-3 старейших клиентов:")
        for i, c in enumerate(customers, 1):
            print(f"{i}. {c[1]}, Email: {c[2]}, Дата регистрации: {c[3]}, Телефон: {c[4]}")
        return customers

    def get_most_successful_seller(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.name, s.hire_date, s.salary, SUM(sa.total_amount) as total_sales
            FROM sellers s
            JOIN sales sa ON s.id = sa.seller_id
            GROUP BY s.id
            ORDER BY total_sales DESC
            LIMIT 1
        ''')
        seller = cursor.fetchone()
        conn.close()
        print("\nСамый успешный продавец:")
        if seller:
            print(f"{seller[1]}, Зарплата: {seller[3]}, Общая сумма продаж: {seller[4]}")
        else:
            print("Нет данных")
        return seller

    def check_manufacturer_products(self, manufacturer_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) 
            FROM products p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            WHERE m.name = ? AND p.quantity > 0
        ''', (manufacturer_name,))
        count = cursor.fetchone()[0]
        conn.close()
        print(f"\nНаличие товаров производителя '{manufacturer_name}': {'Да' if count>0 else 'Нет'}, Кол-во: {count}")
        return count

    def get_most_popular_manufacturer(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.id, m.name, m.country, SUM(s.total_amount) as total_sales
            FROM manufacturers m
            JOIN products p ON m.id = p.manufacturer_id
            JOIN sales s ON p.id = s.product_id
            GROUP BY m.id
            ORDER BY total_sales DESC
            LIMIT 1
        ''')
        manufacturer = cursor.fetchone()
        conn.close()
        print("\nСамый популярный производитель:")
        if manufacturer:
            print(f"{manufacturer[1]}, Страна: {manufacturer[2]}, Общая сумма продаж: {manufacturer[3]}")
        else:
            print("Нет данных")
        return manufacturer

    def delete_customers_after_date(self, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers WHERE registration_date > ?", (date,))
        count_before = cursor.fetchone()[0]
        cursor.execute("DELETE FROM customers WHERE registration_date > ?", (date,))
        conn.commit()
        conn.close()
        print(f"\nУдаление клиентов после {date}: Найдено {count_before}, Фактически удалено {count_before}")
        return count_before

    # ---------------- Тестовые данные ----------------
    def populate_test_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Очистка
        cursor.execute("DELETE FROM sales")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM customers")
        cursor.execute("DELETE FROM sellers")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM manufacturers")

        # Производители
        manufacturers = [
            ('Asics', 'Japan'),
            ('New Balance', 'USA'),
            ('Fila', 'Italy'),
            ('Mizuno', 'Japan'),
            ('Converse', 'USA')
        ]
        cursor.executemany("INSERT INTO manufacturers (name, country) VALUES (?, ?)", manufacturers)

        # Категории
        categories = ['Обувь', 'Одежда', 'Аксессуары', 'Экипировка']
        cursor.executemany("INSERT INTO categories (name) VALUES (?)", [(c,) for c in categories])

        # Товары
        products = [
            ('Кроссовки Asics Gel', 1, 1, 130.00, 12, 'Лёгкие беговые кроссовки'),
            ('Толстовка New Balance', 2, 2, 55.00, 20, 'Тёплая спортивная толстовка'),
            ('Шапка Fila', 3, 3, 18.00, 30, 'Зимняя спортивная шапка'),
            ('Кроссовки Mizuno Wave', 1, 4, 140.00, 5, 'Профессиональные кроссовки'),
            ('Мяч баскетбольный', 4, 2, 75.00, 8, 'Официальный баскетбольный мяч'),
            ('Рюкзак Converse', 3, 5, 40.00, 15, 'Стильный городской рюкзак')
        ]
        cursor.executemany(
            "INSERT INTO products (name, category_id, manufacturer_id, price, quantity, description) VALUES (?, ?, ?, ?, ?, ?)",
            products)

        # Клиенты
        customers = [
            ('Светлана Кузнецова', 'svetlana@mail.com', '2019-02-10', '+79161234580'),
            ('Виктор Смирнов', 'viktor@mail.com', '2020-07-21', '+79161234581'),
            ('Екатерина Белова', 'ekaterina@mail.com', '2018-05-05', '+79161234582'),
            ('Даниил Морозов', 'danil@mail.com', '2021-03-12', '+79161234583'),
            ('Наталья Романова', 'natasha@mail.com', '2017-09-18', '+79161234584')
        ]
        cursor.executemany(
            "INSERT INTO customers (name, email, registration_date, phone) VALUES (?, ?, ?, ?)",
            customers
        )

        # Продавцы
        sellers = [
            ('Алексей Смирнов', '2019-01-05', 52000),
            ('Мария Климова', '2020-06-18', 50000),
            ('Игорь Васильев', '2018-11-12', 54000)
        ]
        cursor.executemany(
            "INSERT INTO sellers (name, hire_date, salary) VALUES (?, ?, ?)",
            sellers
        )

        # Продажи
        sales = [
            (1, 1, 1, '2023-02-15', 1, 130.00),
            (2, 2, 2, '2023-02-18', 2, 110.00),
            (3, 3, 3, '2023-03-01', 1, 18.00),
            (5, 4, 1, '2023-03-05', 1, 75.00),
            (6, 5, 2, '2023-03-10', 1, 40.00),
            (4, 1, 3, '2023-03-12', 1, 140.00)
        ]
        cursor.executemany(
            "INSERT INTO sales (product_id, customer_id, seller_id, sale_date, quantity, total_amount) VALUES (?, ?, ?, ?, ?, ?)",
            sales
        )

        conn.commit()
        conn.close()
        print("Новые тестовые данные успешно добавлены!")


# ---------------- Демонстрация ----------------
def main():
    db = SportsShopDB()
    db.populate_test_data()

    db.get_all_products()
    db.get_products_by_category('Обувь')
    db.get_products_by_category('Одежда')
    db.get_top3_oldest_customers()
    db.get_most_successful_seller()
    db.check_manufacturer_products('Asics')
    db.check_manufacturer_products('Fila')
    db.get_most_popular_manufacturer()
    db.delete_customers_after_date('2020-01-01')


if __name__ == "__main__":
    main()
