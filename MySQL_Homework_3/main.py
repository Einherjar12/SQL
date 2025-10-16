# Задание №1. Необходимо создать базу данных Академия (Academy),
# которая будет содержать информацию о сотрудниках и внутреннем
# устройстве академии. Описание базы данных находится в конце этого файла.

# Задание №2. Для базы данных Академия создайте такие запросы:
# 1. Вывести таблицу кафедр, но расположить ее поля в обратном порядке.
# 2. Вывести названия групп и их рейтинги с
# уточнением имен полей именем таблицы.
# 3. Вывести для преподавателей их фамилию, процент ставки по отношению
# к надбавке и процент ставки по отношению
# к зарплате (сумма ставки и надбавки).
# 4. Вывести таблицу факультетов в виде одного поля в
# следующем формате: "he dean of faculty [faculty] is [dean]."
# 5. Вывести фамилии преподавателей, которые являются
# профессорами и ставка которых превышает 1050.
# 6. Вывести названия кафедр, фонд финансирования
# которых меньше 11000 или больше 25000.
# 7. Вывести названия факультетов кроме факультета “Computer Science”.
# 8. Вывести фамилии и должности преподавателей,
# которые не являются профессорами.
# 9. Вывести фамилии, должности, ставки и надбавки ассистентов,
# у которых надбавка в диапазоне от 160 до 550.
# 10. Вывести фамилии и ставки ассистентов.
# 11. Вывести фамилии и должности преподавателей,
# которые были приняты на работу до 01.01.2000.
# 12. Вывести названия кафедр, которые в алфавитном
# порядке располагаются до кафедры
# "Software Development". Выводимое поле должно
# иметь название “Name of Department”.
# 13. Вывести фамилии ассистентов, имеющих зарплату
# (сумма ставки и надбавки) не более 1200.
# 14. Вывести названия групп 5-го курса, имеющих рейтинг в диапазоне от 2 до 4.
# 15. Вывести фамилии ассистентов со ставкой меньше 550 или надбавкой меньше 200.

import sqlite3

connection = sqlite3.connect("academy.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    financing REAL NOT NULL CHECK(financing >= 0) DEFAULT 0,
    name TEXT NOT NULL UNIQUE CHECK(name <> '')
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS faculties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dean TEXT NOT NULL CHECK(dean <> ''),
    name TEXT NOT NULL UNIQUE CHECK(name <> '')
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE CHECK(name <> ''),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 0 AND 5),
    year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 5)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employment_date TEXT NOT NULL CHECK(employment_date >= '1990-01-01'),
    is_assistant INTEGER NOT NULL DEFAULT 0 CHECK(is_assistant IN (0,1)),
    is_professor INTEGER NOT NULL DEFAULT 0 CHECK(is_professor IN (0,1)),
    name TEXT NOT NULL CHECK(name <> ''),
    position TEXT NOT NULL CHECK(position <> ''),
    premium REAL NOT NULL DEFAULT 0 CHECK(premium >= 0),
    salary REAL NOT NULL CHECK(salary > 0),
    surname TEXT NOT NULL CHECK(surname <> '')
)
""")

connection.commit()

# cursor.execute("DELETE FROM teachers")
# cursor.execute("DELETE FROM groups")
# cursor.execute("DELETE FROM faculties")
# cursor.execute("DELETE FROM departments")
# connection.commit()

departments = [
    ("Информатика", 25000),
    ("Software Development", 20000),
    ("Математика", 8000),
    ("Экономика", 12000),
]

faculties = [
    ("Иванов И.И.", "Computer Science"),
    ("Петров П.П.", "Mathematics"),
    ("Сидорова С.С.", "Economics"),
]

groups = [
    ("CS-101", 4, 5),
    ("CS-102", 3, 5),
    ("MATH-201", 5, 4),
    ("ECO-301", 2, 3),
]

teachers = [
    ("1998-05-10", 1, 0, "Иван", "Профессор", 300, 1200, "Иванов"),
    ("2005-04-21", 0, 0, "Анна", "Ассистент", 400, 500, "Смирнова"),
    ("1999-07-19", 0, 1, "Петр", "Профессор", 200, 1300, "Петров"),
    ("2010-09-01", 1, 0, "Елена", "Ассистент", 150, 480, "Кузнецова"),
    ("2015-02-14", 0, 0, "Максим", "Доцент", 350, 900, "Федоров"),
]

cursor.executemany("INSERT INTO departments (name, financing) "
                   "VALUES (?, ?)", [(d[0], d[1]) for d in departments])
cursor.executemany("INSERT INTO faculties (dean, name) "
                   "VALUES (?, ?)", faculties)
cursor.executemany("INSERT INTO groups (name, rating, year) "
                   "VALUES (?, ?, ?)", groups)
cursor.executemany("INSERT INTO teachers (employment_date, is_assistant, "
                   "is_professor, name, position, premium, salary, surname) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", teachers)

connection.commit()

# Задание №1.-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

print("\n1. Таблица кафедр (поля в обратном порядке):")
cursor.execute("SELECT name, financing, id "
               "FROM departments")

for row in cursor.fetchall():
    print(*row, sep=", ")

print("\n2. Названия групп и рейтинги (с уточнением таблицы):")
cursor.execute("SELECT groups.name AS 'groups.name', "
               "groups.rating AS 'groups.rating' "
               "FROM groups")
for row in cursor.fetchall():
    print(*row, sep=", ")

print("\n3. Фамилия, % ставки к надбавке и к зарплате:")
cursor.execute("SELECT surname, "
               "ROUND((salary / premium) * 100, 2) AS 'ставка к надбавке, %', "
               "ROUND((salary / (salary + premium)) * 100, 2) AS 'ставка к зарплате, %' "
               "FROM teachers "
               "WHERE premium > 0")
for row in cursor.fetchall():
    print(*row, sep=", ")

print("\n4. Таблица факультетов одним полем [dean]:")
cursor.execute("SELECT dean AS 'dean' "
               "FROM faculties")
for row in cursor.fetchall():
    print(*row)

print("\n5. Профессора с зарплатой > 1050:")
cursor.execute("SELECT surname "
               "FROM teachers "
               "WHERE is_professor = 1 AND salary > 1050")
for row in cursor.fetchall():
    print(*row)

print("\n6. Кафедры с финансированием < 11000 или > 25000:")
cursor.execute("SELECT name "
               "FROM departments "
               "WHERE financing < 11000 OR financing > 25000")
for row in cursor.fetchall():
    print(*row)

print("\n7. Факультеты кроме 'Computer Science':")
cursor.execute("SELECT name "
               "FROM faculties "
               "WHERE name <> 'Computer Science'")
for row in cursor.fetchall():
    print(*row)

print("\n8. Преподаватели, которые не профессора:")
cursor.execute("SELECT surname, position "
               "FROM teachers "
               "WHERE is_professor = 0")
for row in cursor.fetchall():
    print(*row, sep=", ")

print("\n9. Ассистенты с надбавкой 160–550:")
cursor.execute("""
SELECT surname, position, salary, premium
FROM teachers
WHERE is_assistant = 1 AND premium BETWEEN 160 AND 550
""")
for row in cursor.fetchall():
    print(*row, sep=", ")

print("\n10. Фамилии и ставки ассистентов:")
cursor.execute("SELECT surname, salary "
               "FROM teachers "
               "WHERE is_assistant = 1")
for row in cursor.fetchall():
    print(*row, sep=", ")

print("\n11. Преподаватели, принятые до 01.01.2000:")
cursor.execute("SELECT surname, position "
               "FROM teachers "
               "WHERE employment_date < '2000-01-01'")
for row in cursor.fetchall():
    print(*row, sep=" - ")

print("\n12. Кафедры до 'Software Development' (Name of Department):")
cursor.execute("""
SELECT name AS 'Name of Department'
FROM departments
WHERE name < 'Software Development'
ORDER BY name
""")
for row in cursor.fetchall():
    print(row)

print("\n13. Ассистенты с зарплатой <= 1200:")
cursor.execute("""
SELECT surname
FROM teachers
WHERE is_assistant = 1 AND (salary + premium) <= 1200
""")
for row in cursor.fetchall():
    print(*row)

print("\n14. Группы 5-го курса с рейтингом от 2 до 4:")
cursor.execute("""
SELECT name
FROM groups
WHERE year = 5 AND rating BETWEEN 2 AND 4
""")
for row in cursor.fetchall():
    print(*row)

print("\n15. Ассистенты со ставкой < 550 или надбавкой < 200:")
cursor.execute("""
SELECT surname, salary, premium
FROM teachers
WHERE is_assistant = 1 AND (salary < 550 OR premium < 200)
""")
for row in cursor.fetchall():
    print(*row, sep=", ")

connection.close()
