import sqlite3


class MusicCollectionDB:
    def __init__(self, db_name='music_collection.db'):
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        """Создание таблиц базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблица стилей музыки
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS styles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        ''')

        # Таблица издателей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                country TEXT,
                founded_year INTEGER
            )
        ''')

        # Таблица исполнителей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                country TEXT,
                active_years TEXT
            )
        ''')

        # Таблица музыкальных дисков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist_id INTEGER,
                publisher_id INTEGER,
                style_id INTEGER,
                release_date DATE,
                total_tracks INTEGER,
                duration INTEGER, -- в минутах
                price DECIMAL(10,2),
                FOREIGN KEY (artist_id) REFERENCES artists(id),
                FOREIGN KEY (publisher_id) REFERENCES publishers(id),
                FOREIGN KEY (style_id) REFERENCES styles(id)
            )
        ''')

        # Таблица песен
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disc_id INTEGER,
                title TEXT NOT NULL,
                track_number INTEGER,
                duration INTEGER, -- в секундах
                FOREIGN KEY (disc_id) REFERENCES discs(id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        """Получение соединения с базой данных"""
        return sqlite3.connect(self.db_name)

    # ---------------- Хранимые процедуры ---------------- #

    # 1. Полная информация о всех музыкальных дисках
    def get_all_discs_info(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.title, a.name as artist, p.name as publisher, 
                   s.name as style, d.release_date, d.total_tracks, 
                   d.duration, d.price
            FROM discs d
            LEFT JOIN artists a ON d.artist_id = a.id
            LEFT JOIN publishers p ON d.publisher_id = p.id
            LEFT JOIN styles s ON d.style_id = s.id
            ORDER BY d.release_date DESC
        ''')
        discs = cursor.fetchall()
        conn.close()
        return discs

    # 2. Информация о дисках конкретного издателя
    def get_discs_by_publisher(self, publisher_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, d.title, a.name as artist, p.name as publisher, 
                   s.name as style, d.release_date, d.total_tracks, 
                   d.duration, d.price
            FROM discs d
            LEFT JOIN artists a ON d.artist_id = a.id
            LEFT JOIN publishers p ON d.publisher_id = p.id
            LEFT JOIN styles s ON d.style_id = s.id
            WHERE p.name = ?
            ORDER BY d.release_date DESC
        ''', (publisher_name,))
        discs = cursor.fetchall()
        conn.close()
        return discs

    # 3. Название самого популярного стиля
    def get_most_popular_style(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.name, COUNT(d.id) as disc_count
            FROM styles s
            LEFT JOIN discs d ON s.id = d.style_id
            GROUP BY s.id, s.name
            ORDER BY disc_count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        return result

    # 4. Диск с наибольшим количеством песен (по стилю)
    def get_disc_with_most_tracks(self, style_name='all'):
        conn = self.get_connection()
        cursor = conn.cursor()
        if style_name.lower() == 'all':
            cursor.execute('''
                SELECT d.id, d.title, a.name as artist, s.name as style, 
                       d.total_tracks, d.release_date
                FROM discs d
                LEFT JOIN artists a ON d.artist_id = a.id
                LEFT JOIN styles s ON d.style_id = s.id
                ORDER BY d.total_tracks DESC
                LIMIT 1
            ''')
        else:
            cursor.execute('''
                SELECT d.id, d.title, a.name as artist, s.name as style, 
                       d.total_tracks, d.release_date
                FROM discs d
                LEFT JOIN artists a ON d.artist_id = a.id
                LEFT JOIN styles s ON d.style_id = s.id
                WHERE s.name = ?
                ORDER BY d.total_tracks DESC
                LIMIT 1
            ''', (style_name,))
        disc = cursor.fetchone()
        conn.close()
        return disc

    # 5. Удаление всех дисков заданного стиля
    def delete_discs_by_style(self, style_name):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Сначала удаляем песни
        cursor.execute('''
            DELETE FROM songs
            WHERE disc_id IN (
                SELECT d.id
                FROM discs d
                JOIN styles s ON d.style_id = s.id
                WHERE s.name = ?
            )
        ''', (style_name,))

        # Удаляем диски
        cursor.execute('''
            DELETE FROM discs
            WHERE style_id IN (
                SELECT id FROM styles WHERE name = ?
            )
        ''', (style_name,))
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()
        return deleted_count

    # 6. Самый старый и самый молодой альбом
    def get_oldest_and_newest_albums(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT d.id, d.title, a.name as artist, d.release_date, s.name as style
            FROM discs d
            LEFT JOIN artists a ON d.artist_id = a.id
            LEFT JOIN styles s ON d.style_id = s.id
            WHERE d.release_date IS NOT NULL
            ORDER BY d.release_date ASC
            LIMIT 1
        ''')
        oldest = cursor.fetchone()

        cursor.execute('''
            SELECT d.id, d.title, a.name as artist, d.release_date, s.name as style
            FROM discs d
            LEFT JOIN artists a ON d.artist_id = a.id
            LEFT JOIN styles s ON d.style_id = s.id
            WHERE d.release_date IS NOT NULL
            ORDER BY d.release_date DESC
            LIMIT 1
        ''')
        newest = cursor.fetchone()
        conn.close()
        return {'oldest': oldest, 'newest': newest}

    # 7. Удаление всех дисков, в названии которых есть ключевое слово
    def delete_discs_by_keyword(self, keyword):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Удаляем песни
        cursor.execute('''
            DELETE FROM songs
            WHERE disc_id IN (
                SELECT id FROM discs WHERE title LIKE ?
            )
        ''', (f'%{keyword}%',))

        # Удаляем диски
        cursor.execute('''
            DELETE FROM discs
            WHERE title LIKE ?
        ''', (f'%{keyword}%',))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count

    # ---------------- Тестовые данные ---------------- #
    def populate_test_data(self):
        """Заполнение базы данных тестовыми данными"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Очистка таблиц
        cursor.execute("DELETE FROM songs")
        cursor.execute("DELETE FROM discs")
        cursor.execute("DELETE FROM artists")
        cursor.execute("DELETE FROM publishers")
        cursor.execute("DELETE FROM styles")

        # Стиль
        styles = [
            ('Рок', 'Рок-музыка'),
            ('Поп', 'Популярная музыка'),
            ('Джаз', 'Джазовая музыка'),
            ('Классика', 'Классическая музыка'),
            ('Электроника', 'Электронная музыка'),
            ('Хип-хоп', 'Хип-хоп музыка')
        ]
        cursor.executemany('INSERT INTO styles (name, description) VALUES (?, ?)', styles)

        # Издатели
        publishers = [
            ('Universal Music', 'USA', 1934),
            ('Sony Music', 'Japan', 1929),
            ('Warner Music', 'USA', 1958),
            ('EMI', 'UK', 1931),
            ('Independent', 'Various', 2000)
        ]
        cursor.executemany('INSERT INTO publishers (name, country, founded_year) VALUES (?, ?, ?)', publishers)

        # Исполнители
        artists = [
            ('The Beatles', 'UK', '1960-1970'),
            ('Queen', 'UK', '1970-1991'),
            ('Michael Jackson', 'USA', '1964-2009'),
            ('Miles Davis', 'USA', '1944-1991'),
            ('Daft Punk', 'France', '1993-2021'),
            ('Eminem', 'USA', '1992-н.в.'),
            ('Mozart', 'Austria', '1762-1791'),
            ('Madonna', 'USA', '1979-н.в.')
        ]
        cursor.executemany('INSERT INTO artists (name, country, active_years) VALUES (?, ?, ?)', artists)

        # Диски
        discs = [
            ('Pet Sounds', 1, 1, 1, '1966-05-16', 13, 45, 28.99),
            ('A Day at the Races', 2, 2, 1, '1976-12-10', 11, 41, 25.99),
            ('Bad', 3, 1, 2, '1987-08-31', 10, 48, 25.99),
            ('Blue Train', 4, 3, 3, '1957-09-15', 7, 42, 23.99),
            ('Random Access Memories', 5, 4, 5, '2013-05-17', 13, 75, 31.99),
            ('The Eminem Show', 6, 1, 6, '2002-05-26', 20, 71, 29.99),
            ('Requiem', 7, 2, 4, '1791-01-01', 14, 55, 26.99),
            ('Like a Virgin', 8, 1, 2, '1984-11-12', 9, 44, 22.99),
            ('News of the World', 2, 3, 1, '1977-10-28', 11, 39, 21.99),
            ('Dangerous', 3, 1, 2, '1991-11-26', 14, 58, 27.99)
        ]
        cursor.executemany('''
            INSERT INTO discs (title, artist_id, publisher_id, style_id, release_date, total_tracks, duration, price) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', discs)

        # Песни (пример для двух дисков)
        songs_data = []
        # Pet Sounds
        pet_sounds_songs = [
            'Wouldn\'t It Be Nice', 'You Still Believe in Me', 'That\'s Not Me',
            'Don\'t Talk', 'I Just Wasn\'t Made for These Times', 'Pet Sounds',
            'God Only Knows', 'I Know There\'s an Answer', 'Here Today',
            'I Just Wasn\'t Made for These Times', 'Caroline, No'
        ]
        for i, song in enumerate(pet_sounds_songs, 1):
            songs_data.append((1, song, i, 180 + i * 10))

        # Bad
        bad_songs = [
            'Bad', 'The Way You Make Me Feel', 'Speed Demon',
            'Liberian Girl', 'Just Good Friends', 'Another Part of Me',
            'Man in the Mirror', 'I Just Can\'t Stop Loving You', 'Dirty Diana', 'Smooth Criminal'
        ]
        for i, song in enumerate(bad_songs, 1):
            songs_data.append((3, song, i, 240 + i * 15))

        cursor.executemany('''
            INSERT INTO songs (disc_id, title, track_number, duration)
            VALUES (?, ?, ?, ?)
        ''', songs_data)

        conn.commit()
        conn.close()


# ---------------- Демонстрация работы ---------------- #
def main():
    db = MusicCollectionDB()
    db.populate_test_data()

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ХРАНИМЫХ ПРОЦЕДУР - МУЗЫКАЛЬНАЯ КОЛЛЕКЦИЯ")
    print("=" * 60)

    # 1. Все диски
    discs = db.get_all_discs_info()
    print("\n1. Полная информация о всех музыкальных дисках:")
    for disc in discs:
        print(f"ID: {disc[0]}, Альбом: {disc[1]}, Исполнитель: {disc[2]}, "
              f"Издатель: {disc[3]}, Стиль: {disc[4]}, Дата: {disc[5]}, "
              f"Треков: {disc[6]}, Длительность: {disc[7]} мин, Цена: {disc[8]}")

    # 2. Диски издателя
    universal_discs = db.get_discs_by_publisher('Universal Music')
    print("\n2. Диски издателя 'Universal Music':")
    for disc in universal_discs:
        print(f"ID: {disc[0]}, Альбом: {disc[1]}, Исполнитель: {disc[2]}, "
              f"Издатель: {disc[3]}, Стиль: {disc[4]}, Дата: {disc[5]}, "
              f"Треков: {disc[6]}, Длительность: {disc[7]} мин, Цена: {disc[8]}")

    # 3. Самый популярный стиль
    style = db.get_most_popular_style()
    print("\n3. Самый популярный стиль:")
    if style:
        print(f"Стиль: {style[0]}, Количество дисков: {style[1]}")

    # 4. Диск с наибольшим количеством песен
    disc_most_tracks = db.get_disc_with_most_tracks('all')
    print("\n4. Диск с наибольшим количеством песен (все стили):")
    if disc_most_tracks:
        print(f"Альбом: {disc_most_tracks[1]}, Исполнитель: {disc_most_tracks[2]}, "
              f"Стиль: {disc_most_tracks[3]}, Треков: {disc_most_tracks[4]}, Дата: {disc_most_tracks[5]}")

    # 5. Удаление дисков по стилю
    deleted_count = db.delete_discs_by_style('Хип-хоп')
    print(f"\n5. Удалено дисков стиля 'Хип-хоп': {deleted_count}")

    # 6. Старый и молодой альбом
    albums = db.get_oldest_and_newest_albums()
    print("\n6. Старый и молодой альбом:")
    if albums['oldest']:
        print(
            f"Самый старый: '{albums['oldest'][1]}' - {albums['oldest'][2]} ({albums['oldest'][3]}, {albums['oldest'][4]})")
    if albums['newest']:
        print(
            f"Самый молодой: '{albums['newest'][1]}' - {albums['newest'][2]} ({albums['newest'][3]}, {albums['newest'][4]})")

    # 7. Удаление дисков по ключевому слову
    deleted_keyword = db.delete_discs_by_keyword('The')
    print(f"\n7. Удалено дисков с ключевым словом 'The': {deleted_keyword}")


if __name__ == "__main__":
    main()
