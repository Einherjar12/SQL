import sqlite3


class MusicCollectionDB:
    def __init__(self, db_name='music_collection.db'):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        """Инициализация базы данных Музыкальная коллекция"""
        conn = self.connect()
        cursor = conn.cursor()

        # Создание таблиц
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Artists (
                artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Genres (
                genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Publishers (
                publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Discs (
                disc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER,
                publisher_id INTEGER,
                release_year INTEGER,
                total_duration INTEGER,
                FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
                FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Songs (
                song_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                disc_id INTEGER,
                duration INTEGER,
                genre_id INTEGER,
                FOREIGN KEY (disc_id) REFERENCES Discs(disc_id),
                FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
            )
        ''')

        conn.commit()
        conn.close()

        # Добавление тестовых данных
        self.add_sample_data()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Artists")
        if cursor.fetchone()[0] == 0:
            # Добавляем исполнителей
            artists = [
                ('Imagine Dragons',), ('Coldplay',), ('Nirvana',),
                ('Red Hot Chili Peppers',), ('Green Day',), ('Linkin Park',)
            ]
            cursor.executemany("INSERT INTO Artists (name) VALUES (?)", artists)

            # Добавляем жанры
            genres = [
                ('Alternative',), ('Pop Rock',), ('Grunge',),
                ('Funk Rock',), ('Punk Rock',), ('Nu Metal',)
            ]
            cursor.executemany("INSERT INTO Genres (name) VALUES (?)", genres)

            # Добавляем издателей
            publishers = [
                ('Universal Music',), ('Sony Music',), ('Warner Bros',),
                ('Island Records',), ('Epic Records',)
            ]
            cursor.executemany("INSERT INTO Publishers (name) VALUES (?)", publishers)

            # Добавляем диски
            discs = [
                ('Evolve', 1, 1, 2017, 1800),
                ('A Head Full of Dreams', 2, 2, 2015, 2100),
                ('Nevermind', 3, 3, 1991, 2300),
                ('Californication', 4, 4, 1999, 2400),
                ('American Idiot', 5, 5, 2004, 2500),
                ('Hybrid Theory', 6, 2, 2000, 2200)
            ]
            cursor.executemany('''
                INSERT INTO Discs (title, artist_id, publisher_id, release_year, total_duration) 
                VALUES (?, ?, ?, ?, ?)
            ''', discs)

            # Добавляем песни
            songs = [
                ('Believer', 1, 204, 1),
                ('Thunder', 1, 187, 1),
                ('Adventure of a Lifetime', 2, 245, 2),
                ('Hymn for the Weekend', 2, 250, 2),
                ('Smells Like Teen Spirit', 3, 301, 3),
                ('Come As You Are', 3, 219, 3),
                ('Scar Tissue', 4, 215, 4),
                ('Otherside', 4, 260, 4),
                ('Holiday', 5, 210, 5),
                ('Boulevard of Broken Dreams', 5, 250, 5),
                ('In the End', 6, 216, 6),
                ('Crawling', 6, 209, 6)
            ]
            cursor.executemany('''
                INSERT INTO Songs (title, disc_id, duration, genre_id) 
                VALUES (?, ?, ?, ?)
            ''', songs)

            conn.commit()

        conn.close()

    # ЗАДАНИЕ 1: Представления для Музыкальной коллекции
    def create_views_task1(self):
        """Создание представлений для Задания 1"""
        conn = self.connect()
        cursor = conn.cursor()

        # 1. Представление всех исполнителей
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS AllArtists AS
            SELECT name FROM Artists
            ORDER BY name
        ''')

        # 2. Полная информация о всех песнях
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS FullSongInfo AS
            SELECT 
                s.title as song_title,
                d.title as disc_title,
                s.duration,
                g.name as genre,
                a.name as artist
            FROM Songs s
            JOIN Discs d ON s.disc_id = d.disc_id
            JOIN Artists a ON d.artist_id = a.artist_id
            JOIN Genres g ON s.genre_id = g.genre_id
            ORDER BY a.name, d.title, s.title
        ''')

        # 3. Диски конкретной группы (The Beatles)
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS BeatlesDiscs AS
            SELECT 
                d.title as disc_title,
                d.release_year,
                d.total_duration,
                p.name as publisher
            FROM Discs d
            JOIN Artists a ON d.artist_id = a.artist_id
            JOIN Publishers p ON d.publisher_id = p.publisher_id
            WHERE a.name = 'The Beatles'
            ORDER BY d.release_year
        ''')

        # 4. Самый популярный исполнитель (по количеству дисков)
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS MostPopularArtist AS
            SELECT a.name as artist_name, COUNT(d.disc_id) as disc_count
            FROM Artists a
            JOIN Discs d ON a.artist_id = d.artist_id
            GROUP BY a.artist_id
            ORDER BY disc_count DESC
            LIMIT 1
        ''')

        # 5. Топ-3 самых популярных исполнителей
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS Top3Artists AS
            SELECT a.name as artist_name, COUNT(d.disc_id) as disc_count
            FROM Artists a
            JOIN Discs d ON a.artist_id = d.artist_id
            GROUP BY a.artist_id
            ORDER BY disc_count DESC
            LIMIT 3
        ''')

        # 6. Самый долгий музыкальный альбом
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS LongestAlbum AS
            SELECT 
                d.title as album_title,
                a.name as artist,
                d.total_duration,
                d.release_year
            FROM Discs d
            JOIN Artists a ON d.artist_id = a.artist_id
            ORDER BY d.total_duration DESC
            LIMIT 1
        ''')

        conn.commit()
        conn.close()
        print("Представления для Задания 1 созданы успешно!")

    # ЗАДАНИЕ 2: Обновляемые представления для Музыкальной коллекции
    def create_updatable_views_task2(self):
        """Создание обновляемых представлений для Задания 2"""
        conn = self.connect()
        cursor = conn.cursor()

        # 1. Представление для вставки новых стилей
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS InsertGenres AS
            SELECT genre_id, name FROM Genres
        ''')

        # 2. Представление для вставки новых песен
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS InsertSongs AS
            SELECT song_id, title, disc_id, duration, genre_id FROM Songs
        ''')

        # 3. Представление для обновления информации об издателе
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS UpdatePublishers AS
            SELECT publisher_id, name FROM Publishers
        ''')

        # 4. Представление для удаления исполнителей
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS DeleteArtists AS
            SELECT artist_id, name FROM Artists
        ''')

        # 5. Представление для обновления информации о конкретном исполнителе (Muse)
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS UpdateMuse AS
            SELECT artist_id, name FROM Artists WHERE name = 'Muse'
        ''')

        conn.commit()
        conn.close()
        print("Обновляемые представления для Задания 2 созданы успешно!")

    # Методы для демонстрации представлений
    def display_all_artists(self):
        """Отображение всех исполнителей"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AllArtists")
        results = cursor.fetchall()
        print("\n=== ВСЕ ИСПОЛНИТЕЛИ ===")
        for row in results:
            print(f"Исполнитель: {row[0]}")
        conn.close()
        return results

    def display_full_song_info(self):
        """Отображение полной информации о песнях"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM FullSongInfo")
        results = cursor.fetchall()
        print("\n=== ПОЛНАЯ ИНФОРМАЦИЯ О ПЕСНЯХ ===")
        for row in results:
            print(f"Песня: {row[0]}, Альбом: {row[1]}, Длительность: {row[2]}с, Жанр: {row[3]}, Исполнитель: {row[4]}")
        conn.close()
        return results

    def display_beatles_discs(self):
        """Отображение дисков The Beatles"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM BeatlesDiscs")
        results = cursor.fetchall()
        print("\n=== ДИСКИ THE BEATLES ===")
        for row in results:
            print(f"Альбом: {row[0]}, Год: {row[1]}, Длительность: {row[2]}с, Издатель: {row[3]}")
        conn.close()
        return results

    def display_most_popular_artist(self):
        """Отображение самого популярного исполнителя"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM MostPopularArtist")
        result = cursor.fetchone()
        print("\n=== САМЫЙ ПОПУЛЯРНЫЙ ИСПОЛНИТЕЛЬ ===")
        if result:
            print(f"Исполнитель: {result[0]}, Количество дисков: {result[1]}")
        conn.close()
        return [result] if result else []

    def display_top3_artists(self):
        """Отображение топ-3 исполнителей"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Top3Artists")
        results = cursor.fetchall()
        print("\n=== ТОП-3 ИСПОЛНИТЕЛЕЙ ===")
        for i, row in enumerate(results, 1):
            print(f"{i}. {row[0]} - {row[1]} дисков")
        conn.close()
        return results

    def display_longest_album(self):
        """Отображение самого долгого альбома"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LongestAlbum")
        result = cursor.fetchone()
        print("\n=== САМЫЙ ДОЛГИЙ АЛЬБОМ ===")
        if result:
            print(f"Альбом: {result[0]}, Исполнитель: {result[1]}, Длительность: {result[2]}с, Год: {result[3]}")
        conn.close()
        return [result] if result else []


class SalesDB:
    def __init__(self, db_name='sales.db'):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        """Инициализация базы данных Продажи"""
        conn = self.connect()
        cursor = conn.cursor()

        # Создание таблиц
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sellers (
                seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                seller_id INTEGER,
                customer_id INTEGER,
                quantity INTEGER NOT NULL,
                sale_date DATE DEFAULT CURRENT_DATE,
                total_amount REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products(product_id),
                FOREIGN KEY (seller_id) REFERENCES Sellers(seller_id),
                FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
            )
        ''')

        conn.commit()
        conn.close()

        # Добавление тестовых данных
        self.add_sample_data()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Products")
        if cursor.fetchone()[0] == 0:
            # Добавляем товары
            products = [
                ('Яблоки', 55.0), ('Груши', 65.0), ('Виноград', 90.0),
                ('Молоко', 60.0), ('Хлеб', 45.0), ('Сыр', 210.0)
            ]
            cursor.executemany("INSERT INTO Products (name, price) VALUES (?, ?)", products)

            # Добавляем продавцов
            sellers = [
                ('Ольга Иванова', 'olga@example.com'),
                ('Павел Смирнов', 'pavel@example.com'),
                ('Екатерина Лебедева', 'ekaterina@example.com')
            ]
            cursor.executemany("INSERT INTO Sellers (name, email) VALUES (?, ?)", sellers)

            # Добавляем покупателей
            customers = [
                ('ООО "Лилия"', 'liliya@example.com'),
                ('ИП Кузнецов', 'kuznetsov@example.com'),
                ('ЗАО "Сфера"', 'sfera@example.com')
            ]
            cursor.executemany("INSERT INTO Customers (name, email) VALUES (?, ?)", customers)

            # Добавляем продажи
            sales = [
                (1, 1, 1, 12, 660.0), (2, 2, 2, 8, 520.0), (3, 3, 3, 15, 1350.0),
                (4, 1, 2, 5, 300.0), (5, 2, 3, 7, 315.0), (6, 3, 1, 3, 630.0)
            ]
            cursor.executemany('''
                INSERT INTO Sales (product_id, seller_id, customer_id, quantity, total_amount) 
                VALUES (?, ?, ?, ?, ?)
            ''', sales)

            conn.commit()

        conn.close()

    # ЗАДАНИЕ 3: Представления для базы данных Продажи
    def create_views_task3(self):
        """Создание представлений для Задания 3"""
        conn = self.connect()
        cursor = conn.cursor()

        # 1. Обновляемое представление всех продавцов
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS AllSellers AS
            SELECT seller_id, name, email FROM Sellers
        ''')

        # 2. Обновляемое представление всех покупателей
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS AllCustomers AS
            SELECT customer_id, name, email FROM Customers
        ''')

        # 3. Обновляемое представление продаж конкретного товара (Яблоки)
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS AppleSales AS
            SELECT 
                s.sale_id,
                p.name as product_name,
                sel.name as seller_name,
                c.name as customer_name,
                s.quantity,
                s.total_amount,
                s.sale_date
            FROM Sales s
            JOIN Products p ON s.product_id = p.product_id
            JOIN Sellers sel ON s.seller_id = sel.seller_id
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE p.name = 'Яблоки'
            ORDER BY s.sale_date DESC
        ''')

        # 4. Представление всех осуществленных сделок
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS AllSales AS
            SELECT 
                s.sale_id,
                p.name as product_name,
                sel.name as seller_name,
                c.name as customer_name,
                s.quantity,
                s.total_amount,
                s.sale_date
            FROM Sales s
            JOIN Products p ON s.product_id = p.product_id
            JOIN Sellers sel ON s.seller_id = sel.seller_id
            JOIN Customers c ON s.customer_id = c.customer_id
            ORDER BY s.sale_date DESC
        ''')

        # 5. Представление самого активного продавца
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS MostActiveSeller AS
            SELECT 
                sel.name as seller_name,
                SUM(s.total_amount) as total_sales,
                COUNT(s.sale_id) as sales_count
            FROM Sales s
            JOIN Sellers sel ON s.seller_id = sel.seller_id
            GROUP BY sel.seller_id
            ORDER BY total_sales DESC
            LIMIT 1
        ''')

        # 6. Представление самого активного покупателя
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS MostActiveCustomer AS
            SELECT 
                c.name as customer_name,
                SUM(s.total_amount) as total_purchases,
                COUNT(s.sale_id) as purchases_count
            FROM Sales s
            JOIN Customers c ON s.customer_id = c.customer_id
            GROUP BY c.customer_id
            ORDER BY total_purchases DESC
            LIMIT 1
        ''')

        conn.commit()
        conn.close()
        print("Представления для Задания 3 созданы успешно!")

    # Методы для демонстрации представлений
    def display_all_sellers(self):
        """Отображение всех продавцов"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AllSellers")
        results = cursor.fetchall()
        print("\n=== ВСЕ ПРОДАВЦЫ ===")
        for row in results:
            print(f"ID: {row[0]}, Имя: {row[1]}, Email: {row[2]}")
        conn.close()
        return results

    def display_all_customers(self):
        """Отображение всех покупателей"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AllCustomers")
        results = cursor.fetchall()
        print("\n=== ВСЕ ПОКУПАТЕЛИ ===")
        for row in results:
            print(f"ID: {row[0]}, Имя: {row[1]}, Email: {row[2]}")
        conn.close()
        return results

    def display_apple_sales(self):
        """Отображение продаж яблок"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AppleSales")
        results = cursor.fetchall()
        print("\n=== ПРОДАЖИ ЯБЛОК ===")
        for row in results:
            print(
                f"ID: {row[0]}, Товар: {row[1]}, Продавец: {row[2]}, Покупатель: {row[3]}, Количество: {row[4]}, Сумма: {row[5]:.2f}, Дата: {row[6]}")
        conn.close()
        return results

    def display_all_sales(self):
        """Отображение всех сделок"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AllSales")
        results = cursor.fetchall()
        print("\n=== ВСЕ СДЕЛКИ ===")
        for row in results:
            print(
                f"ID: {row[0]}, Товар: {row[1]}, Продавец: {row[2]}, Покупатель: {row[3]}, Количество: {row[4]}, Сумма: {row[5]:.2f}, Дата: {row[6]}")
        conn.close()
        return results

    def display_most_active_seller(self):
        """Отображение самого активного продавца"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM MostActiveSeller")
        result = cursor.fetchone()
        print("\n=== САМЫЙ АКТИВНЫЙ ПРОДАВЕЦ ===")
        if result:
            print(f"Продавец: {result[0]}, Общая сумма продаж: {result[1]:.2f}, Количество сделок: {result[2]}")
        conn.close()
        return [result] if result else []

    def display_most_active_customer(self):
        """Отображение самого активного покупателя"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM MostActiveCustomer")
        result = cursor.fetchone()
        print("\n=== САМЫЙ АКТИВНЫЙ ПОКУПАТЕЛЬ ===")
        if result:
            print(f"Покупатель: {result[0]}, Общая сумма покупок: {result[1]:.2f}, Количество покупок: {result[2]}")
        conn.close()
        return [result] if result else []


def main():
    music_db = MusicCollectionDB()
    sales_db = SalesDB()

    # Инициализация баз данных
    print("Инициализация базы данных 'Музыкальная коллекция'...")
    music_db.initialize_database()
    music_db.create_views_task1()
    music_db.create_updatable_views_task2()

    print("Инициализация базы данных 'Продажи'...")
    sales_db.initialize_database()
    sales_db.create_views_task3()

    while True:
        print("\n" + "=" * 50)
        print("ГЛАВНОЕ МЕНЮ")
        print("=" * 50)
        print("1. Музыкальная коллекция - Задание 1")
        print("2. Музыкальная коллекция - Задание 2")
        print("3. Продажи - Задание 3")
        print("0. Выход")

        choice = input("Выберите пункт меню: ")

        if choice == '1':
            music_task1_menu(music_db)
        elif choice == '2':
            music_task2_menu(music_db)
        elif choice == '3':
            sales_task3_menu(sales_db)
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор!")


def music_task1_menu(db):
    """Меню для Задания 1 (Музыкальная коллекция)"""
    while True:
        print("\n" + "-" * 40)
        print("МУЗЫКАЛЬНАЯ КОЛЛЕКЦИЯ - ЗАДАНИЕ 1")
        print("-" * 40)
        print("1. Все исполнители")
        print("2. Полная информация о песнях")
        print("3. Диски The Beatles")
        print("4. Самый популярный исполнитель")
        print("5. Топ-3 исполнителей")
        print("6. Самый долгий альбом")
        print("0. Назад")

        choice = input("Выберите представление: ")

        if choice == '1':
            db.display_all_artists()
        elif choice == '2':
            db.display_full_song_info()
        elif choice == '3':
            db.display_beatles_discs()
        elif choice == '4':
            db.display_most_popular_artist()
        elif choice == '5':
            db.display_top3_artists()
        elif choice == '6':
            db.display_longest_album()
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


def music_task2_menu(db):
    """Меню для Задания 2 (Музыкальная коллекция)"""
    print("\n" + "-" * 40)
    print("МУЗЫКАЛЬНАЯ КОЛЛЕКЦИЯ - ЗАДАНИЕ 2")
    print("-" * 40)
    print("Обновляемые представления созданы:")
    print("- InsertGenres (вставка стилей)")
    print("- InsertSongs (вставка песен)")
    print("- UpdatePublishers (обновление издателей)")
    print("- DeleteArtists (удаление исполнителей)")
    print("- UpdateMuse (обновление Muse)")
    print("\nЭти представления можно использовать в SQL-запросах")
    input("Нажмите Enter для продолжения...")


def sales_task3_menu(db):
    """Меню для Задания 3 (Продажи)"""
    while True:
        print("\n" + "-" * 40)
        print("ПРОДАЖИ - ЗАДАНИЕ 3")
        print("-" * 40)
        print("1. Все продавцы")
        print("2. Все покупатели")
        print("3. Продажи яблок")
        print("4. Все сделки")
        print("5. Самый активный продавец")
        print("6. Самый активный покупатель")
        print("0. Назад")

        choice = input("Выберите представление: ")

        if choice == '1':
            db.display_all_sellers()
        elif choice == '2':
            db.display_all_customers()
        elif choice == '3':
            db.display_apple_sales()
        elif choice == '4':
            db.display_all_sales()
        elif choice == '5':
            db.display_most_active_seller()
        elif choice == '6':
            db.display_most_active_customer()
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()
