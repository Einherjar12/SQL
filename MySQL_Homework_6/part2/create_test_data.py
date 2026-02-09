import sqlite3


def create_test_data():
    """Создание тестовых данных для демонстрации работы приложения"""
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    try:
        # Очистка существующих данных
        tables = ['examinations', 'donations', 'doctors', 'wards', 'sponsors', 'departments']
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")

        # Сброс автоинкремента
        for table in tables:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")

        # Добавление отделений
        departments = [
            ('Педиатрическое отделение', 'Лечение и наблюдение детей'),
            ('Травматологическое отделение', 'Лечение травм и переломов'),
            ('Эндокринологическое отделение', 'Заболевания эндокринной системы'),
            ('Офтальмологическое отделение', 'Диагностика и лечение зрения')
        ]
        cursor.executemany(
            "INSERT INTO departments (name, description) VALUES (?, ?)",
            departments
        )

        # Добавление спонсоров
        sponsors = [
            ('HealthPlus', 'Андреева Наталья', '+7-901-234-56-78'),
            ('MedInvest', 'Ковалёв Роман', '+7-902-345-67-89'),
            ('LifeCare', 'Орлова Анна', '+7-903-456-78-90')
        ]
        cursor.executemany(
            "INSERT INTO sponsors (company_name, contact_person, phone) VALUES (?, ?, ?)",
            sponsors
        )

        # Добавление палат
        wards = [
            ('Палата 101', 1, 4),
            ('Палата 102', 1, 3),
            ('Палата 201', 2, 2),
            ('Палата 202', 2, 2),
            ('Палата 301', 3, 3),
            ('Палата 401', 4, 4)
        ]
        cursor.executemany("INSERT INTO wards (name, department_id, capacity) VALUES (?, ?, ?)", wards)

        # Добавление врачей
        doctors = [
            ('Антон', 'Мельников', 'Педиатр', 52000, 9000, 1, 0),
            ('Ирина', 'Белова', 'Травматолог', 68000, 14000, 2, 0),
            ('Максим', 'Егоров', 'Эндокринолог', 61000, 11000, 3, 1),
            ('Светлана', 'Романова', 'Офтальмолог', 57000, 8500, 4, 0),
            ('Павел', 'Дорохов', 'Педиатр', 50000, 6000, 1, 0),
            ('Юлия', 'Никитина', 'Травматолог', 73000, 16000, 2, 1)
        ]
        cursor.executemany(
            '''INSERT INTO doctors 
               (first_name, last_name, specialization, salary_base, salary_bonus, department_id, on_vacation) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            doctors
        )

        # Добавление пожертвований
        donations = [
            (1, 1, 42000, '2024-03-05'),
            (2, 2, 90000, '2024-03-10'),
            (3, 3, 67000, '2024-03-15'),
            (1, 4, 38000, '2024-03-20'),
            (2, 1, 51000, '2024-03-25'),
            (3, 2, 86000, '2024-03-28')
        ]
        cursor.executemany(
            '''INSERT INTO donations 
               (sponsor_id, department_id, amount, donation_date) 
               VALUES (?, ?, ?, ?)''',
            donations
        )

        # Добавление обследований
        examinations = [
            (1, 1, 'Громов И.С.', '2024-03-02', 'ОРЗ'),
            (2, 2, 'Лебедева Н.А.', '2024-03-04', 'Вывих плеча'),
            (3, 3, 'Фёдоров К.М.', '2024-03-06', 'Сахарный диабет'),
            (4, 4, 'Соколова Е.П.', '2024-03-08', 'Близорукость'),
            (5, 1, 'Тарасов Д.В.', '2024-03-11', 'Ангина'),
            (6, 2, 'Морозова О.Н.', '2024-03-13', 'Перелом руки')
        ]

        cursor.executemany('''INSERT INTO examinations 
                          (doctor_id, department_id, patient_name, examination_date, diagnosis) 
                          VALUES (?, ?, ?, ?, ?)''', examinations)

        conn.commit()
        print("Тестовые данные успешно добавлены в базу данных!")

    except sqlite3.Error as e:
        print(f"Ошибка при добавлении тестовых данных: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_test_data()
