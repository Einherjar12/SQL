-- Задание 1. Создание и удаление базы данных Birds.
CREATE DATABASE Birds; 
DROP DATABASE Birds;

-- Задание 2-3. Создание и удаление базы данных Cats.
CREATE DATABASE Cats;
DROP DATABASE Cats;

-- Задание 4. Создайте однотабличную базу данных «Овощи и фрукты».
CREATE DATABASE VegFruits;
USE VegFruits;
CREATE TABLE Products(
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	type_prod ENUM('овощ', 'фрукт') NOT NULL,
	color VARCHAR(30) NOT NULL,
	calories DECIMAL(5,1) NOT NULL,
	description TEXT
);

INSERT INTO Products (name, type_prod, color, calories, description)
VALUES
('Яблоко', 'фрукт', 'красный', 52.1, 'Сладкий и сочный фрукт.'),
('Банан', 'фрукт', 'жёлтый', 89, 'Мягкий и питательный.'),
('Морковь', 'овощ', 'оранжевый', 41.7, 'Полезна для зрения.'),
('Огурец', 'овощ', 'зелёный', 16.5, 'Свежий и водянистый.');

-- Задание 5. Создайте следующие запросы для таблицы:
-- 1. Отображение всей информации
SELECT * FROM Products;
-- 2. Все овощи
SELECT * FROM Products WHERE type_prod = 'овощ';
-- 3. Все фрукты
SELECT * FROM Products WHERE type_prod = 'фрукт';
-- 4. Все названия овощей и фруктов
SELECT name FROM Products;
-- 5. Все уникальные цвета
SELECT DISTINCT color FROM Products;
-- 6. Фрукты конкретного цвета
SELECT * FROM Products WHERE type_prod = 'фрукт' AND color = 'красный';
-- 7. Овощи конкретного цвета
SELECT * FROM Products WHERE type_prod = 'овощ' AND color = 'зелёный';

