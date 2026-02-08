import sqlite3

DB_NAME = "academy.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Curators (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL CHECK(Name <> ''),
        Surname TEXT NOT NULL CHECK(Surname <> '')
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Faculties (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Financing REAL NOT NULL CHECK(Financing >= 0) DEFAULT 0,
        Name TEXT NOT NULL UNIQUE CHECK(Name <> '')
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Financing REAL NOT NULL CHECK(Financing >= 0) DEFAULT 0,
        Name TEXT NOT NULL UNIQUE CHECK(Name <> ''),
        FacultyId INTEGER NOT NULL,
        FOREIGN KEY (FacultyId) REFERENCES Faculties(Id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Groups (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE CHECK(Name <> ''),
        Year INTEGER NOT NULL CHECK(Year BETWEEN 1 AND 5),
        DepartmentId INTEGER NOT NULL,
        FOREIGN KEY (DepartmentId) REFERENCES Departments(Id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GroupsCurators (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        CuratorId INTEGER NOT NULL,
        GroupId INTEGER NOT NULL,
        FOREIGN KEY (CuratorId) REFERENCES Curators(Id),
        FOREIGN KEY (GroupId) REFERENCES Groups(Id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Teachers (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL CHECK(Name <> ''),
        Surname TEXT NOT NULL CHECK(Surname <> ''),
        Salary REAL NOT NULL CHECK(Salary > 0)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Subjects (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE CHECK(Name <> '')
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Lectures (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        LectureRoom TEXT NOT NULL CHECK(LectureRoom <> ''),
        SubjectId INTEGER NOT NULL,
        TeacherId INTEGER NOT NULL,
        FOREIGN KEY (SubjectId) REFERENCES Subjects(Id),
        FOREIGN KEY (TeacherId) REFERENCES Teachers(Id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GroupsLectures (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        GroupId INTEGER NOT NULL,
        LectureId INTEGER NOT NULL,
        FOREIGN KEY (GroupId) REFERENCES Groups(Id),
        FOREIGN KEY (LectureId) REFERENCES Lectures(Id)
    )
    """)

    conn.commit()
    conn.close()


def insert_test_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany("""
    INSERT OR IGNORE INTO Faculties (Id, Name, Financing)
    VALUES (?, ?, ?)
    """, [
        (1, "Computer Science", 100000),
        (2, "Engineering", 80000)
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO Departments (Id, Name, Financing, FacultyId)
    VALUES (?, ?, ?, ?)
    """, [
        (1, "Software Development", 120000, 1),
        (2, "Networks", 50000, 1),
        (3, "Mechanical Engineering", 90000, 2)
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO Groups (Id, Name, Year, DepartmentId)
    VALUES (?, ?, ?, ?)
    """, [
        (1, "P107", 2, 1),
        (2, "P205", 5, 1),
        (3, "E501", 5, 3)
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO Curators (Id, Name, Surname)
    VALUES (?, ?, ?)
    """, [
        (1, "Anna", "Ivanova"),
        (2, "Oleg", "Petrov")
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO GroupsCurators (CuratorId, GroupId)
    VALUES (?, ?)
    """, [
        (1, 1),
        (2, 2),
        (2, 3)
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO Teachers (Id, Name, Surname, Salary)
    VALUES (?, ?, ?, ?)
    """, [
        (1, "Samantha", "Adams", 5000),
        (2, "John", "Smith", 4500),
        (3, "Emily", "Clark", 4800)
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO Subjects (Id, Name)
    VALUES (?, ?)
    """, [
        (1, "Database Theory"),
        (2, "Python Programming"),
        (3, "Computer Networks")
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO Lectures (Id, LectureRoom, SubjectId, TeacherId)
    VALUES (?, ?, ?, ?)
    """, [
        (1, "B103", 1, 1),
        (2, "A201", 2, 2),
        (3, "B103", 3, 3)
    ])

    cursor.executemany("""
    INSERT OR IGNORE INTO GroupsLectures (GroupId, LectureId)
    VALUES (?, ?)
    """, [
        (1, 1),
        (1, 2),
        (2, 1),
        (3, 3)
    ])

    conn.commit()
    conn.close()


def run_queries():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    queries = [
        ("1. Все пары преподавателей и групп",
         """SELECT Teachers.Surname, Groups.Name FROM Teachers, Groups"""),

        ("2. Факультеты с кафедрами, финансирование которых больше факультета",
         """SELECT DISTINCT Faculties.Name
            FROM Faculties
            JOIN Departments ON Departments.FacultyId = Faculties.Id
            WHERE Departments.Financing > Faculties.Financing"""),

        ("3. Кураторы и группы",
         """SELECT Curators.Surname, Groups.Name
            FROM Curators
            JOIN GroupsCurators ON Curators.Id = GroupsCurators.CuratorId
            JOIN Groups ON Groups.Id = GroupsCurators.GroupId"""),

        ("4. Преподаватели группы P107",
         """SELECT Teachers.Name, Teachers.Surname
            FROM Teachers
            JOIN Lectures ON Teachers.Id = Lectures.TeacherId
            JOIN GroupsLectures ON Lectures.Id = GroupsLectures.LectureId
            JOIN Groups ON Groups.Id = GroupsLectures.GroupId
            WHERE Groups.Name = 'P107'"""),

        ("5. Преподаватели и факультеты",
         """SELECT DISTINCT Teachers.Surname, Faculties.Name
            FROM Teachers
            JOIN Lectures ON Teachers.Id = Lectures.TeacherId
            JOIN GroupsLectures ON Lectures.Id = GroupsLectures.LectureId
            JOIN Groups ON Groups.Id = GroupsLectures.GroupId
            JOIN Departments ON Groups.DepartmentId = Departments.Id
            JOIN Faculties ON Departments.FacultyId = Faculties.Id"""),

        ("6. Кафедры и группы",
         """SELECT Departments.Name, Groups.Name
            FROM Departments
            JOIN Groups ON Groups.DepartmentId = Departments.Id"""),

        ("7. Дисциплины Samantha Adams",
         """SELECT Subjects.Name
            FROM Subjects
            JOIN Lectures ON Subjects.Id = Lectures.SubjectId
            JOIN Teachers ON Teachers.Id = Lectures.TeacherId
            WHERE Teachers.Name = 'Samantha' AND Teachers.Surname = 'Adams'"""),

        ("8. Кафедры с дисциплиной Database Theory",
         """SELECT DISTINCT Departments.Name
            FROM Departments
            JOIN Groups ON Groups.DepartmentId = Departments.Id
            JOIN GroupsLectures ON Groups.Id = GroupsLectures.GroupId
            JOIN Lectures ON Lectures.Id = GroupsLectures.LectureId
            JOIN Subjects ON Subjects.Id = Lectures.SubjectId
            WHERE Subjects.Name = 'Database Theory'"""),

        ("9. Группы факультета Computer Science",
         """SELECT Groups.Name
            FROM Groups
            JOIN Departments ON Groups.DepartmentId = Departments.Id
            JOIN Faculties ON Departments.FacultyId = Faculties.Id
            WHERE Faculties.Name = 'Computer Science'"""),

        ("10. Группы 5 курса и факультеты",
         """SELECT Groups.Name, Faculties.Name
            FROM Groups
            JOIN Departments ON Groups.DepartmentId = Departments.Id
            JOIN Faculties ON Departments.FacultyId = Faculties.Id
            WHERE Groups.Year = 5"""),

        ("11. Лекции в аудитории B103",
         """SELECT Teachers.Name || ' ' || Teachers.Surname,
                   Subjects.Name,
                   Groups.Name
            FROM Teachers
            JOIN Lectures ON Teachers.Id = Lectures.TeacherId
            JOIN Subjects ON Subjects.Id = Lectures.SubjectId
            JOIN GroupsLectures ON Lectures.Id = GroupsLectures.LectureId
            JOIN Groups ON Groups.Id = GroupsLectures.GroupId
            WHERE Lectures.LectureRoom = 'B103'""")
    ]

    for title, query in queries:
        print(f"\n{title}:")
        cursor.execute(query)
        for row in cursor.fetchall():
            print(row)

    conn.close()


if __name__ == "__main__":
    create_database()
    insert_test_data()
    run_queries()

