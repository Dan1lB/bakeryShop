-- Create tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(255),
    phone VARCHAR(20),
    login VARCHAR(50),
    password VARCHAR(50)
);

CREATE TABLE administrators (
    admin_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    login VARCHAR(50),
    password VARCHAR(50)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    release_year INT,
    performer VARCHAR(100)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT,
    product_id INT,
    quantity INT,
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(255),
    work_schedule VARCHAR(255)
);

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact_person VARCHAR(100),
    address VARCHAR(255)
);

CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    delivery_time DATE,
    product_id INT,
    supplier_id INT,
    quantity INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- Insert sample data
INSERT INTO customers (name, address, phone, login, password) VALUES 
('John Doe', '123 Main St', '123-456-7890', 'johndoe', 'password123'),
('Jane Smith', '456 Elm St', '098-765-4321', 'janesmith', 'password456');

INSERT INTO administrators (name, login, password) VALUES 
('Admin User', 'admin', 'adminpassword');

INSERT INTO products (name, price, release_year, performer) VALUES 
('Product A', 19.99, 2021, 'Artist A'),
('Product B', 29.99, 2020, 'Artist B');

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES 
(1, 1, 2, '2024-01-01'),
(2, 2, 1, '2024-02-01');

INSERT INTO stores (name, address, work_schedule) VALUES 
('Store A', '789 Maple St', '9am-9pm'),
('Store B', '101 Oak St', '10am-8pm');

INSERT INTO suppliers (name, contact_person, address) VALUES 
('Supplier A', 'Alice Johnson', '234 Pine St'),
('Supplier B', 'Bob Brown', '567 Cedar St');

INSERT INTO deliveries (delivery_time, product_id, supplier_id) VALUES 
('2024-03-01', 1, 1),
('2024-04-01', 2, 2);

-- Provided SQL queries

-- 1. Вибір з декількох таблиць із сортуванням
SELECT 
    c.customer_id, 
    c.name AS customer_name, 
    p.product_id, 
    p.name AS product_name, 
    o.order_id, 
    o.order_date
FROM 
    customers c
JOIN 
    orders o ON c.customer_id = o.customer_id
JOIN 
    products p ON o.product_id = p.product_id
ORDER BY 
    c.name, o.order_date;

-- 2. Завдання умови відбору з використанням предиката LIKE
SELECT 
    customer_id, 
    name, 
    address 
FROM 
    customers 
WHERE 
    name LIKE 'А%';

-- 3. Завдання умови відбору з використанням предиката BETWEEN
SELECT 
    order_id, 
    product_id, 
    quantity, 
    order_date 
FROM 
    orders 
WHERE 
    order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- 4. Агрегатна функція без угруповання
SELECT 
    COUNT(*) AS total_orders 
FROM 
    orders 
WHERE 
    order_date >= CURRENT_DATE - interval '7 days';

-- 5. Агрегатна функція з угрупованням
SELECT 
    customer_id, 
    COUNT(order_id) AS total_orders 
FROM 
    orders 
GROUP BY 
    customer_id;

-- 6. Використання предиката ALL або ANY
SELECT 
    customer_id, 
    name 
FROM 
    customers 
WHERE 
    customer_id = (SELECT customer_id FROM orders GROUP BY customer_id ORDER BY COUNT(order_id) DESC LIMIT 1);

-- 7. Корельований підзапит
SELECT 
    c.customer_id, 
    c.name, 
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) AS total_orders 
FROM 
    customers c;

-- 8. Запит на заперечення (три варіанти)
-- 8.1 З використанням LEFT JOIN
SELECT 
    c.customer_id, 
    c.name 
FROM 
    customers c 
LEFT JOIN 
    orders o ON c.customer_id = o.customer_id 
WHERE 
    o.order_id IS NULL;

-- 8.2 З використанням предиката IN
SELECT 
    customer_id, 
    name 
FROM 
    customers 
WHERE 
    customer_id NOT IN (SELECT customer_id FROM orders);

-- 8.3 З використанням предиката EXISTS
SELECT 
    c.customer_id, 
    c.name 
FROM 
    customers c 
WHERE 
    NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

-- 9. Операція об'єднання UNION із включенням коментарю в кожен рядок
SELECT 
    customer_id, 
    name, 
    'Має максимальну кількість замовлень' AS comment 
FROM 
    customers 
WHERE 
    customer_id = (SELECT customer_id FROM orders GROUP BY customer_id ORDER BY COUNT(order_id) DESC LIMIT 1)
UNION
SELECT 
    customer_id, 
    name, 
    'Не має в цей час замовлень' AS comment 
FROM 
    customers 
WHERE 
    customer_id NOT IN (SELECT customer_id FROM orders);
