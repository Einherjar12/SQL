-- Прошлое домашнее задание: создается однотабличная база данных «Овощи и фрукты»
CREATE DATABASE VegFruits;
USE VegFruits;
CREATE TABLE Products(
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	type_prod VARCHAR(30) NOT NULL,
	color VARCHAR(30) NOT NULL,
	calories DECIMAL(5,1) NOT NULL,
	description TEXT
);

INSERT INTO Products (name, type_prod, color, calories, description)
VALUES
('Яблоко', 'фрукт', 'зелёный', 52.1, 'Сладкий и сочный фрукт.'),
('Банан', 'фрукт', 'жёлтый', 89, 'Мягкий и питательный.'),
('Морковь', 'овощ', 'оранжевый', 41.7, 'Полезна для зрения.'),
('Капуста', 'овощ', 'зелёный', 25, 'Полезна при диетическом питании.'),
('Апельсин', 'фрукт', 'оранжевый', 43, 'Содержит витамин C, укрепляет иммунитет.'),
('Редис', 'овощ', 'розовый', 16, 'Помогает пищеварению, освежает.'),
('Огурец', 'овощ', 'зелёный', 16.5, 'Свежий и водянистый.');

-- Задание 1.1. Отображение всех овощей с калорийностью меньше, указанной калорийности.
SELECT name 
FROM Products
WHERE type_prod = 'овощ' AND calories < 50 ORDER BY calories;

-- Задание 1.2. Отображение всех фруктов с калорийностью в указанном диапазоне.
SELECT name 
FROM Products 
WHERE type_prod = 'фрукт' AND calories BETWEEN 20 AND 80 ORDER BY calories;

-- Задание 1.3. Отображение всех овощей в названии, которых есть указанное слово. Например, слово: Морковь.
SELECT name 
FROM Products 
WHERE type_prod = 'овощ' AND name LIKE "Морковь%";

-- Задание 1.4. Отображение всех овощей и фруктов в кратком описании, которых есть указанное слово. Например, слово: гемоглобин.
SELECT name 
FROM Products 
WHERE description LIKE "%Полезна%";

-- Задание 1.5. Показать все овощи и фрукты, у которых цвет желтый или красный.
SELECT name 
FROM Products 
WHERE color IN ('жёлтый','красный');

-- Задание 2.1. Показать количество овощей.
SELECT COUNT(name) 
FROM Products 
WHERE type_prod = 'овощ';

-- Задание 2.2. Показать количество фруктов.
SELECT COUNT(name)
FROM Products 
WHERE type_prod = 'фрукт';

-- Задание 2.3. Показать количество овощей и фруктов заданного цвета.
SELECT COUNT(*) 
FROM Products 
WHERE color = 'зелёный';

-- Задание 2.4. Показать количество овощей и фруктов каждого цвета.
SELECT color, COUNT(*) 
FROM Products 
GROUP BY color;

-- Задание 2.5. Показать цвет с минимальным количеством овощей и фруктов.
SELECT color
FROM Products
GROUP BY color
ORDER BY COUNT(*)
LIMIT 1;

-- Задание 2.6. Показать цвет с максимальным количеством овощей и фруктов.
SELECT color
FROM Products
GROUP BY color
ORDER BY COUNT(*) DESC
LIMIT 1;

-- Задание 2.7. Показать минимальную калорийность овощей и фруктов.
SELECT MIN(calories)
FROM Products;

-- Задание 2.8. Показать максимальную калорийность овощей и фруктов.
SELECT MAX(calories)
FROM Products;

-- Задание 2.9. Показать среднюю калорийность овощей и фруктов.
SELECT AVG(calories)
FROM Products;

-- Задание 2.10. Показать фрукт с минимальной калорийностью.
SELECT name, calories
FROM Products
WHERE type_prod = 'фрукт'
ORDER BY calories
LIMIT 1;

-- Задание 2.11. Показать фрукт с максимальной калорийностью.
SELECT name, calories
FROM Products
WHERE type_prod = 'фрукт'
ORDER BY calories DESC
LIMIT 1;