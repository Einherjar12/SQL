import sqlite3


def create_tables(cursor):
    """Создание таблиц только если их ещё нет"""
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Faculties (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Departments (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE,
        Building INTEGER NOT NULL,
        Financing REAL NOT NULL DEFAULT 0,
        FacultyId INTEGER NOT NULL,
        FOREIGN KEY(FacultyId) REFERENCES Faculties(Id)
    );

    CREATE TABLE IF NOT EXISTS Teachers (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Surname TEXT NOT NULL,
        Salary REAL NOT NULL,
        IsProfessor INTEGER NOT NULL DEFAULT 0,
        DepartmentId INTEGER NOT NULL,
        FOREIGN KEY(DepartmentId) REFERENCES Departments(Id)
    );

    CREATE TABLE IF NOT EXISTS Subjects (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Auditoriums (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Groups (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE,
        Year INTEGER NOT NULL,
        DepartmentId INTEGER NOT NULL,
        FOREIGN KEY(DepartmentId) REFERENCES Departments(Id)
    );

    CREATE TABLE IF NOT EXISTS Students (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Surname TEXT NOT NULL,
        Rating INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Curators (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Surname TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS GroupsCurators (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        GroupId INTEGER NOT NULL,
        CuratorId INTEGER NOT NULL,
        FOREIGN KEY(GroupId) REFERENCES Groups(Id),
        FOREIGN KEY(CuratorId) REFERENCES Curators(Id)
    );

    CREATE TABLE IF NOT EXISTS Lectures (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT NOT NULL,
        SubjectId INTEGER NOT NULL,
        TeacherId INTEGER NOT NULL,
        AuditoriumId INTEGER NOT NULL,
        FOREIGN KEY(SubjectId) REFERENCES Subjects(Id),
        FOREIGN KEY(TeacherId) REFERENCES Teachers(Id),
        FOREIGN KEY(AuditoriumId) REFERENCES Auditoriums(Id)
    );

    CREATE TABLE IF NOT EXISTS GroupsStudents (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        GroupId INTEGER NOT NULL,
        StudentId INTEGER NOT NULL,
        FOREIGN KEY(GroupId) REFERENCES Groups(Id),
        FOREIGN KEY(StudentId) REFERENCES Students(Id)
    );
    """)


def fill_test_data(cursor):
    """Добавление тестовых данных (только если их ещё нет)"""
    cursor.executescript("""
    INSERT OR IGNORE INTO Faculties (Id, Name) VALUES
    (1,'Computer Science'),(2,'Engineering');

    INSERT OR IGNORE INTO Departments (Id, Name, Building, Financing, FacultyId) VALUES
    (1,'Software Development', 1, 120000, 1),
    (2,'Data Science', 2, 90000, 1),
    (3,'Robotics', 3, 70000, 2);

    INSERT OR IGNORE INTO Teachers (Id, Name, Surname, Salary, IsProfessor, DepartmentId) VALUES
    (1,'Dave','McQueen',5000,1,1),
    (2,'Jack','Underhill',4200,0,1),
    (3,'Alice','Brown',3900,0,2);

    INSERT OR IGNORE INTO Subjects (Id, Name) VALUES
    (1,'Python'),(2,'Databases'),(3,'Algorithms');

    INSERT OR IGNORE INTO Auditoriums (Id, Name) VALUES
    (1,'D201'),(2,'D202'),(3,'R101');

    INSERT OR IGNORE INTO Groups (Id, Name, Year, DepartmentId) VALUES
    (1,'D221',5,1),
    (2,'SD101',5,1),
    (3,'DS201',4,2);

    INSERT OR IGNORE INTO Students (Id, Name, Surname, Rating) VALUES
    (1,'Anna','Ivanova',5),
    (2,'Petr','Petrov',4),
    (3,'Ivan','Sidorov',3),
    (4,'Maria','Smirnova',2);

    INSERT OR IGNORE INTO Curators (Id, Name, Surname) VALUES
    (1,'Curator1','One'),
    (2,'Curator2','Two');

    INSERT OR IGNORE INTO GroupsCurators (Id, GroupId, CuratorId) VALUES
    (1,1,1),
    (2,1,2),
    (3,2,1);

    INSERT OR IGNORE INTO GroupsStudents (Id, GroupId, StudentId) VALUES
    (1,1,1),
    (2,1,2),
    (3,2,3),
    (4,3,4);

    INSERT OR IGNORE INTO Lectures (Id, Date, SubjectId, TeacherId, AuditoriumId) VALUES
    (1,'2024-01-01',1,1,1),
    (2,'2024-01-02',1,1,1),
    (3,'2024-01-03',2,2,1),
    (4,'2024-01-04',3,3,2);
    """)


def print_query(cursor, title, query):
    """Выполнение запроса"""
    print(f"\n📌 {title}")
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(*row)
    else:
        print("Нет данных")


def run_all_queries(cursor):
    """Выполнение всех 23 заданий"""

    # ===== Задание 1 =====
    print_query(cursor, "Задание 1. Вывести количество преподавателей кафедры “Software Development”.",
                """
                SELECT COUNT(*) 
                FROM Teachers t 
                JOIN Departments d ON t.DepartmentId = d.Id 
                WHERE d.Name = 'Software Development';
                """)

    print_query(cursor, "Задание 2. Вывести количество лекций, которые читает преподаватель “Dave McQueen”.",
                """
                SELECT COUNT(*) 
                FROM Lectures l 
                JOIN Teachers t ON l.TeacherId = t.Id 
                WHERE t.Name = 'Dave' AND t.Surname = 'McQueen';
                """)

    print_query(cursor, "Задание 3. Вывести количество занятий, проводимых в аудитории “D201”.",
                """
                SELECT COUNT(*) 
                FROM Lectures l 
                JOIN Auditoriums a ON l.AuditoriumId = a.Id 
                WHERE a.Name = 'D201';
                """)

    print_query(cursor, "Задание 4. Вывести названия аудиторий и количество лекций, проводимых в них.",
                """
                SELECT a.Name, COUNT(l.Id) 
                FROM Auditoriums a 
                LEFT JOIN Lectures l ON a.Id = l.AuditoriumId 
                GROUP BY a.Id;
                """)

    print_query(cursor, "Задание 5. Вывести количество студентов, посещающих лекции преподавателя “Jack Underhill”.",
                """
                SELECT COUNT(DISTINCT gs.StudentId) 
                FROM Teachers t 
                JOIN Lectures l ON t.Id = l.TeacherId 
                JOIN GroupsStudents gs ON gs.GroupId IN (SELECT Id FROM Groups) 
                WHERE t.Name='Jack' AND t.Surname='Underhill';
                """)

    print_query(cursor, "Задание 6. Вывести среднюю ставку преподавателей факультета “Computer Science”.",
                """
                SELECT AVG(t.Salary) 
                FROM Teachers t 
                JOIN Departments d ON t.DepartmentId = d.Id 
                JOIN Faculties f ON d.FacultyId = f.Id 
                WHERE f.Name = 'Computer Science';
                """)

    print_query(cursor, "Задание 7. Вывести минимальное и максимальное количество студентов среди всех групп.",
                """
                SELECT MIN(cnt), MAX(cnt) 
                FROM (
                    SELECT g.Id, COUNT(gs.StudentId) AS cnt 
                    FROM Groups g 
                    LEFT JOIN GroupsStudents gs ON g.Id = gs.GroupId 
                    GROUP BY g.Id
                );
                """)

    print_query(cursor, "Задание 8. Вывести средний фонд финансирования кафедр.",
                """
                SELECT AVG(Financing) 
                FROM Departments;
                """)

    print_query(cursor, "Задание 9. Вывести полные имена преподавателей и количество читаемых ими дисциплин.",
                """
                SELECT t.Name, t.Surname, COUNT(DISTINCT l.SubjectId) 
                FROM Teachers t 
                LEFT JOIN Lectures l ON t.Id = l.TeacherId 
                GROUP BY t.Id;
                """)

    print_query(cursor, "Задание 10. Вывести количество лекций в каждый день недели.",
                """
                WITH Days(day_num, name) AS (
                    SELECT 0,'Воскресенье' UNION ALL 
                    SELECT 1,'Понедельник' UNION ALL 
                    SELECT 2,'Вторник' UNION ALL 
                    SELECT 3,'Среда' UNION ALL 
                    SELECT 4,'Четверг' UNION ALL 
                    SELECT 5,'Пятница' UNION ALL 
                    SELECT 6,'Суббота'
                )
                SELECT d.name, COUNT(l.Id)
                FROM Days d
                LEFT JOIN Lectures l ON strftime('%w', l.Date) = CAST(d.day_num AS TEXT)
                GROUP BY d.day_num, d.name
                ORDER BY d.day_num;
                """)

    print_query(cursor, "Задание 11. Вывести номера аудиторий и количество кафедр, чьи лекции в них читаются.",
                """
                SELECT a.Name, COUNT(DISTINCT t.DepartmentId) 
                FROM Auditoriums a 
                LEFT JOIN Lectures l ON a.Id = l.AuditoriumId 
                LEFT JOIN Teachers t ON l.TeacherId = t.Id 
                GROUP BY a.Id;
                """)

    print_query(cursor, "Задание 12. Вывести названия факультетов и количество дисциплин, которые на них читаются.",
                """
                SELECT f.Name, COUNT(DISTINCT l.SubjectId) 
                FROM Faculties f 
                LEFT JOIN Departments d ON d.FacultyId = f.Id 
                LEFT JOIN Teachers t ON t.DepartmentId = d.Id 
                LEFT JOIN Lectures l ON l.TeacherId = t.Id 
                GROUP BY f.Id;
                """)

    print_query(cursor, "Задание 13. Вывести количество лекций для каждой пары преподаватель-аудитория.",
                """
                SELECT t.Name || ' ' || t.Surname, a.Name, COUNT(l.Id) 
                FROM Teachers t 
                LEFT JOIN Lectures l ON l.TeacherId = t.Id 
                LEFT JOIN Auditoriums a ON a.Id = l.AuditoriumId 
                GROUP BY t.Id, a.Id;
                """)

    # ===== Задание 2 =====
    print_query(cursor, "Задание 14. Вывести номера корпусов, если суммарный фонд финансирования >100000.",
                """
                SELECT Building 
                FROM Departments 
                GROUP BY Building 
                HAVING SUM(Financing) > 100000;
                """)

    print_query(cursor,
                "Задание 15. Вывести названия групп 5-го курса кафедры “Software Development”, которые имеют более 10 пар в первую неделю.",
                """
                SELECT g.Name 
                FROM Groups g 
                JOIN Departments d ON g.DepartmentId = d.Id 
                WHERE g.Year = 5 AND d.Name = 'Software Development';
                """)

    print_query(cursor, "Задание 16. Вывести названия групп, имеющих рейтинг больше группы D221.",
                """
                SELECT g.Name 
                FROM Groups g 
                JOIN GroupsStudents gs ON g.Id = gs.GroupId 
                JOIN Students s ON s.Id = gs.StudentId 
                GROUP BY g.Id 
                HAVING AVG(s.Rating) > (
                    SELECT AVG(s.Rating) 
                    FROM Groups g 
                    JOIN GroupsStudents gs ON g.Id = gs.GroupId 
                    JOIN Students s ON s.Id = gs.StudentId 
                    WHERE g.Name = 'D221'
                );
                """)

    print_query(cursor,
                "Задание 17. Вывести фамилии и имена преподавателей, ставка которых выше средней ставки профессоров.",
                """
                SELECT Name, Surname 
                FROM Teachers 
                WHERE Salary > (
                    SELECT AVG(Salary) 
                    FROM Teachers 
                    WHERE IsProfessor = 1
                );
                """)

    print_query(cursor, "Задание 18. Вывести названия групп, у которых больше одного куратора.",
                """
                SELECT g.Name 
                FROM Groups g 
                JOIN GroupsCurators gc ON g.Id = gc.GroupId 
                GROUP BY g.Id 
                HAVING COUNT(gc.CuratorId) > 1;
                """)

    print_query(cursor, "Задание 19. Вывести названия групп, имеющих рейтинг ниже минимума 5-го курса.",
                """
                SELECT g.Name 
                FROM Groups g 
                JOIN GroupsStudents gs ON g.Id = gs.GroupId 
                JOIN Students s ON s.Id = gs.StudentId 
                GROUP BY g.Id 
                HAVING AVG(s.Rating) < (
                    SELECT MIN(avg_rating) 
                    FROM (
                        SELECT AVG(s.Rating) AS avg_rating 
                        FROM Groups g 
                        JOIN GroupsStudents gs ON g.Id = gs.GroupId 
                        JOIN Students s ON s.Id = gs.StudentId 
                        WHERE g.Year = 5 
                        GROUP BY g.Id
                    )
                );
                """)

    print_query(cursor, "Задание 20. Вывести названия факультетов с фондом > фонда Computer Science.",
                """
                SELECT f.Name 
                FROM Faculties f 
                JOIN Departments d ON d.FacultyId = f.Id 
                GROUP BY f.Id 
                HAVING SUM(d.Financing) > (
                    SELECT SUM(d.Financing) 
                    FROM Faculties f 
                    JOIN Departments d ON d.FacultyId = f.Id 
                    WHERE f.Name = 'Computer Science'
                );
                """)

    print_query(cursor,
                "Задание 21. Вывести названия дисциплин и полные имена преподавателей, читающих наибольшее количество лекций по ним.",
                """
                SELECT s.Name, t.Name || ' ' || t.Surname 
                FROM Subjects s 
                JOIN Lectures l ON s.Id = l.SubjectId 
                JOIN Teachers t ON t.Id = l.TeacherId 
                GROUP BY s.Id, t.Id 
                HAVING COUNT(l.Id) = (
                    SELECT MAX(cnt) 
                    FROM (
                        SELECT COUNT(*) AS cnt 
                        FROM Lectures l2 
                        WHERE l2.SubjectId = s.Id 
                        GROUP BY l2.TeacherId
                    )
                );
                """)

    print_query(cursor, "Задание 22. Вывести название дисциплины, по которому читается меньше всего лекций.",
                """
                SELECT s.Name 
                FROM Subjects s 
                JOIN Lectures l ON s.Id = l.SubjectId 
                GROUP BY s.Id 
                ORDER BY COUNT(l.Id) ASC 
                LIMIT 1;
                """)

    print_query(cursor,
                "Задание 23. Вывести количество студентов и читаемых дисциплин на кафедре “Software Development”.",
                """
                SELECT COUNT(DISTINCT gs.StudentId), COUNT(DISTINCT l.SubjectId) 
                FROM Departments d 
                JOIN Teachers t ON d.Id = t.DepartmentId 
                JOIN Lectures l ON t.Id = l.TeacherId 
                JOIN GroupsStudents gs ON gs.GroupId IN (SELECT Id FROM Groups WHERE DepartmentId=d.Id) 
                WHERE d.Name = 'Software Development';
                """)


def main():
    conn = sqlite3.connect("academy.db")
    cursor = conn.cursor()

    create_tables(cursor)
    fill_test_data(cursor)
    run_all_queries(cursor)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
