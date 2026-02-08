import sqlite3
import os


class MusicCollectionDB:
    def __init__(self, db_name="music_collection.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        db_exists = os.path.exists(self.db_name)
        conn = self.connect()
        cursor = conn.cursor()

        if not db_exists:
            cursor.executescript("""
            CREATE TABLE albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist TEXT NOT NULL,
                album TEXT NOT NULL,
                genre TEXT NOT NULL,
                release_year INTEGER NOT NULL
            );

            CREATE TABLE albums_archive (
                id INTEGER,
                artist TEXT,
                album TEXT,
                genre TEXT,
                release_year INTEGER,
                delete_date TEXT
            );

            -- 1. Запрет добавления существующего альбома
            CREATE TRIGGER prevent_duplicate_album
            BEFORE INSERT ON albums
            FOR EACH ROW
            WHEN EXISTS (
                SELECT 1 FROM albums
                WHERE artist = NEW.artist
                  AND album = NEW.album
                  AND release_year = NEW.release_year
            )
            BEGIN
                SELECT RAISE(ABORT, 'Альбом уже существует в коллекции');
            END;

            -- 2. Запрет удаления дисков The Beatles
            CREATE TRIGGER prevent_delete_beatles
            BEFORE DELETE ON albums
            FOR EACH ROW
            WHEN OLD.artist = 'The Beatles'
            BEGIN
                SELECT RAISE(ABORT, 'Запрещено удалять диски группы The Beatles');
            END;

            -- 3. Архивация удалённых дисков
            CREATE TRIGGER archive_deleted_album
            BEFORE DELETE ON albums
            FOR EACH ROW
            BEGIN
                INSERT INTO albums_archive
                VALUES (
                    OLD.id,
                    OLD.artist,
                    OLD.album,
                    OLD.genre,
                    OLD.release_year,
                    DATETIME('now')
                );
            END;

            -- 4. Запрет стиля Dark Power Pop
            CREATE TRIGGER prevent_dark_power_pop
            BEFORE INSERT ON albums
            FOR EACH ROW
            WHEN LOWER(NEW.genre) = 'dark power pop'
            BEGIN
                SELECT RAISE(ABORT, 'Стиль Dark Power Pop запрещён');
            END;
            """)
            conn.commit()

        conn.close()

    # ---------------- Демонстрация ----------------

    def demo_insert_albums(self):
        print("\n1. Демонстрация добавления альбомов:")
        conn = self.connect()
        cursor = conn.cursor()

        albums = [
            ("Pink Floyd", "The Dark Side of the Moon", "Progressive Rock", 1973),
            ("Nirvana", "Nevermind", "Grunge", 1991),
            ("The Beatles", "Abbey Road", "Rock", 1969),
        ]

        for artist, album, genre, year in albums:
            try:
                cursor.execute("""
                INSERT INTO albums (artist, album, genre, release_year)
                VALUES (?, ?, ?, ?)
                """, (artist, album, genre, year))
                conn.commit()
                print(f"Альбом '{album}' добавлен")
            except sqlite3.IntegrityError as e:
                print(f"Ошибка: {e}")

        print("Пробуем добавить дубликат альбома...")
        try:
            cursor.execute("""
            INSERT INTO albums (artist, album, genre, release_year)
            VALUES ('Pink Floyd', 'The Dark Side of the Moon', 'Progressive Rock', 1973)
            """)
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Ошибка: {e}")

        print("Пробуем добавить запрещённый стиль...")
        try:
            cursor.execute("""
            INSERT INTO albums (artist, album, genre, release_year)
            VALUES ('Test Band', 'Dark Album', 'Dark Power Pop', 2022)
            """)
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Ошибка: {e}")

        conn.close()

    def demo_delete_albums(self):
        print("\n" + "=" * 50)
        print("\n2. Демонстрация удаления альбомов:")
        conn = self.connect()
        cursor = conn.cursor()

        print("Пробуем удалить альбом The Beatles...")
        try:
            cursor.execute("""
            DELETE FROM albums
            WHERE artist = 'The Beatles'
            """)
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Ошибка: {e}")

        print("Удаляем альбом Nirvana...")
        cursor.execute("""
        DELETE FROM albums
        WHERE artist = 'Nirvana'
        """)
        conn.commit()
        print("Альбом Nirvana удалён и перенесён в архив")

        print("Архив альбомов:")
        cursor.execute("SELECT * FROM albums_archive")
        for row in cursor.fetchall():
            print(
                f"  ID: {row[0]}, Исполнитель: {row[1]}, Альбом: {row[2]}, "
                f"Год: {row[4]}, Дата удаления: {row[5]}"
            )

        conn.close()


# ------------------ main ------------------

if __name__ == "__main__":
    print("=== База данных 'Музыкальная коллекция' ===")
    music_db = MusicCollectionDB()
    music_db.initialize_database()
    music_db.demo_insert_albums()
    music_db.demo_delete_albums()
