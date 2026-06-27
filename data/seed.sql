-- ============================================
-- სასაუბრო BI — სატესტო მონაცემთა ბაზა
-- ქართული ელ-კომერციის სცენარი
-- ============================================

-- === ცხრილების შექმნა ===

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,              -- სახელი ქართულად
    category VARCHAR(100) NOT NULL,          -- კატეგორია
    price DECIMAL(10,2) NOT NULL,            -- ფასი (ლარი)
    cost DECIMAL(10,2) NOT NULL,             -- თვითღირებულება
    stock_quantity INTEGER DEFAULT 0,        -- მარაგი
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,         -- სრული სახელი
    email VARCHAR(200) UNIQUE,
    city VARCHAR(100),                       -- ქალაქი
    region VARCHAR(100),                     -- რეგიონი
    registered_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'მოლოდინში', -- სტატუსი ქართულად
    total_amount DECIMAL(12,2),
    payment_method VARCHAR(50)               -- გადახდის მეთოდი
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

-- === კატეგორიებისა და პროდუქტების კომენტარები ===
COMMENT ON TABLE products IS 'პროდუქტების ცხრილი — შეიცავს ყველა პროდუქტის ინფორმაციას';
COMMENT ON TABLE customers IS 'მომხმარებლების ცხრილი — რეგისტრირებული მომხმარებლები';
COMMENT ON TABLE orders IS 'შეკვეთების ცხრილი — ყოველი შეკვეთის ინფორმაცია';
COMMENT ON TABLE order_items IS 'შეკვეთის ელემენტები — რა პროდუქტები შედის შეკვეთაში';

COMMENT ON COLUMN products.name IS 'პროდუქტის სახელი ქართულად';
COMMENT ON COLUMN products.category IS 'კატეგორია: ელექტრონიკა, ტანსაცმელი, საკვები, საყოფაცხოვრებო, სპორტი';
COMMENT ON COLUMN products.price IS 'საცალო ფასი ლარებში (₾)';
COMMENT ON COLUMN products.cost IS 'თვითღირებულება ლარებში';
COMMENT ON COLUMN products.stock_quantity IS 'მარაგში არსებული რაოდენობა';
COMMENT ON COLUMN customers.city IS 'ქალაქი: თბილისი, ბათუმი, ქუთაისი, რუსთავი, გორი, ფოთი, ზუგდიდი, თელავი';
COMMENT ON COLUMN customers.region IS 'რეგიონი: თბილისი, აჭარა, იმერეთი, კახეთი, შიდა ქართლი, სამეგრელო, გურია';
COMMENT ON COLUMN orders.status IS 'სტატუსი: მოლოდინში, გაგზავნილი, მიწოდებული, გაუქმებული';
COMMENT ON COLUMN orders.payment_method IS 'გადახდის მეთოდი: ბარათი, ნაღდი, განვადება';

-- === პროდუქტები (50) ===

INSERT INTO products (name, category, price, cost, stock_quantity) VALUES
-- ელექტრონიკა
('Samsung Galaxy A54', 'ელექტრონიკა', 899.00, 620.00, 45),
('iPhone 15', 'ელექტრონიკა', 2899.00, 2100.00, 20),
('Xiaomi Redmi Note 13', 'ელექტრონიკა', 549.00, 380.00, 60),
('MacBook Air M2', 'ელექტრონიკა', 3499.00, 2600.00, 12),
('Samsung TV 55"', 'ელექტრონიკა', 1899.00, 1300.00, 18),
('AirPods Pro', 'ელექტრონიკა', 599.00, 400.00, 35),
('Lenovo IdeaPad', 'ელექტრონიკა', 1299.00, 950.00, 25),
('JBL Bluetooth სპიკერი', 'ელექტრონიკა', 189.00, 110.00, 80),
('Logitech მაუსი', 'ელექტრონიკა', 79.00, 45.00, 120),
('Samsung Galaxy Watch', 'ელექტრონიკა', 699.00, 480.00, 30),
-- ტანსაცმელი
('Nike Air Max', 'ტანსაცმელი', 399.00, 200.00, 55),
('Adidas ტრენინგი', 'ტანსაცმელი', 249.00, 130.00, 70),
('Zara ქურთუკი', 'ტანსაცმელი', 189.00, 85.00, 40),
('Levi''s ჯინსი', 'ტანსაცმელი', 279.00, 140.00, 50),
('H&M მაისური', 'ტანსაცმელი', 49.00, 18.00, 200),
('Columbia ქურთუკი', 'ტანსაცმელი', 499.00, 280.00, 25),
('Puma სპორტული ფეხსაცმელი', 'ტანსაცმელი', 329.00, 170.00, 45),
('Tommy Hilfiger პერანგი', 'ტანსაცმელი', 199.00, 90.00, 35),
('New Balance 574', 'ტანსაცმელი', 349.00, 180.00, 40),
('Under Armour შორტი', 'ტანსაცმელი', 89.00, 40.00, 90),
-- საკვები
('ბორჯომი (12 ბოთლი)', 'საკვები', 18.00, 8.00, 500),
('ნაბეღლავი (12 ბოთლი)', 'საკვები', 15.00, 7.00, 450),
('ქართული ღვინო საფერავი', 'საკვები', 35.00, 15.00, 200),
('ქართული ჩურჩხელა (10 ცალი)', 'საკვები', 25.00, 10.00, 300),
('სულგუნი (1 კგ)', 'საკვები', 22.00, 12.00, 150),
('თაფლი (500 გრ)', 'საკვები', 28.00, 14.00, 100),
('ტყემალი (500 მლ)', 'საკვები', 8.00, 3.00, 250),
('აჯიკა (300 გრ)', 'საკვები', 12.00, 5.00, 180),
('ქართული ჩაი (100 გრ)', 'საკვები', 15.00, 6.00, 200),
('წყალი ლიკანი (6 ბოთლი)', 'საკვები', 9.00, 4.00, 400),
-- საყოფაცხოვრებო
('Bosch სარეცხი მანქანა', 'საყოფაცხოვრებო', 1599.00, 1100.00, 10),
('Samsung მაცივარი', 'საყოფაცხოვრებო', 2199.00, 1500.00, 8),
('Philips მტვერსასრუტი', 'საყოფაცხოვრებო', 449.00, 280.00, 20),
('Tefal ტაფა ნაკრები', 'საყოფაცხოვრებო', 159.00, 80.00, 60),
('IKEA თაროები', 'საყოფაცხოვრებო', 129.00, 55.00, 40),
('Dyson ფენი', 'საყოფაცხოვრებო', 899.00, 600.00, 15),
('De''Longhi ყავის აპარატი', 'საყოფაცხოვრებო', 799.00, 520.00, 12),
('Braun უთო', 'საყოფაცხოვრებო', 179.00, 100.00, 30),
('Oral-B ელექტრო კბილის ჯაგრისი', 'საყოფაცხოვრებო', 149.00, 85.00, 50),
('Xiaomi ჰაერის გამწმენდი', 'საყოფაცხოვრებო', 549.00, 350.00, 18),
-- სპორტი
('Decathlon საცურაო კოსტიუმი', 'სპორტი', 89.00, 40.00, 35),
('Nike ფეხბურთის ბურთი', 'სპორტი', 69.00, 30.00, 60),
('Kettler ველოსიპედი', 'სპორტი', 899.00, 600.00, 10),
('Domyos იოგა ხალიჩა', 'სპორტი', 39.00, 15.00, 80),
('Adidas კალათბურთის ბურთი', 'სპორტი', 59.00, 25.00, 45),
('Decathlon სათხილამურო ნაკრები', 'სპორტი', 599.00, 380.00, 8),
('Nike სავარჯიშო ხელთათმანები', 'სპორტი', 49.00, 20.00, 70),
('Garmin GPS საათი', 'სპორტი', 799.00, 520.00, 15),
('Theraband რეზინის ლენტი', 'სპორტი', 29.00, 10.00, 100),
('Wilson ჩოგბურთის ჩოგანი', 'სპორტი', 249.00, 140.00, 20);

-- === მომხმარებლები (200) ===
-- ვქმნით რეალისტურ ქართულ სახელებს და ქალაქებს

INSERT INTO customers (full_name, email, city, region, registered_at) VALUES
('გიორგი ბერიძე', 'g.beridze@gmail.com', 'თბილისი', 'თბილისი', '2025-01-15'),
('ნინო კვარაცხელია', 'n.kvarackhelia@gmail.com', 'თბილისი', 'თბილისი', '2025-01-20'),
('დავით მამუკაძე', 'd.mamukadze@gmail.com', 'ბათუმი', 'აჭარა', '2025-02-03'),
('მარიამ ჯავახიშვილი', 'm.javakhishvili@gmail.com', 'ქუთაისი', 'იმერეთი', '2025-02-10'),
('ალექსანდრე წერეთელი', 'a.tsereteli@gmail.com', 'თბილისი', 'თბილისი', '2025-02-14'),
('თამარ გოგოლაძე', 't.gogoladze@gmail.com', 'რუსთავი', 'ქვემო ქართლი', '2025-02-20'),
('ლუკა ხარაიშვილი', 'l.kharaishvili@gmail.com', 'გორი', 'შიდა ქართლი', '2025-03-01'),
('ანა მაისურაძე', 'a.maisuradze@gmail.com', 'ზუგდიდი', 'სამეგრელო', '2025-03-05'),
('ნიკა ფერაძე', 'n.peradze@gmail.com', 'ბათუმი', 'აჭარა', '2025-03-10'),
('ელენე კობახიძე', 'e.kobakhidze@gmail.com', 'თელავი', 'კახეთი', '2025-03-12'),
('სანდრო ლომიძე', 's.lomidze@gmail.com', 'თბილისი', 'თბილისი', '2025-03-15'),
('ქეთევან ჩხეიძე', 'k.chkheidze@gmail.com', 'ფოთი', 'სამეგრელო', '2025-03-20'),
('ირაკლი გაბუნია', 'i.gabunia@gmail.com', 'თბილისი', 'თბილისი', '2025-03-22'),
('სოფიო ბაქრაძე', 's.bakradze@gmail.com', 'ქუთაისი', 'იმერეთი', '2025-03-25'),
('ზურაბ დვალი', 'z.dvali@gmail.com', 'რუსთავი', 'ქვემო ქართლი', '2025-04-01'),
('ნათია ცისკარიშვილი', 'n.tsiskarishvili@gmail.com', 'თბილისი', 'თბილისი', '2025-04-03'),
('ბექა ყაზბეგი', 'b.qazbegi@gmail.com', 'სტეფანწმინდა', 'მცხეთა-მთიანეთი', '2025-04-05'),
('მაკა სურგულაძე', 'm.surguladze@gmail.com', 'ბათუმი', 'აჭარა', '2025-04-08'),
('გიგა ხუციშვილი', 'g.khutsishvili@gmail.com', 'თბილისი', 'თბილისი', '2025-04-10'),
('ლიკა ნაჭყებია', 'l.nachkebia@gmail.com', 'ზუგდიდი', 'სამეგრელო', '2025-04-12'),
('ვახტანგ მიქელაძე', 'v.mikeladze@gmail.com', 'თბილისი', 'თბილისი', '2025-04-15'),
('თეა ბარნაბიშვილი', 't.barnab@gmail.com', 'ქუთაისი', 'იმერეთი', '2025-04-18'),
('კახა ჯანელიძე', 'k.janelidze@gmail.com', 'თბილისი', 'თბილისი', '2025-04-20'),
('ცირა აბულაძე', 'ts.abuladze@gmail.com', 'გორი', 'შიდა ქართლი', '2025-04-22'),
('რატი ხარაბაძე', 'r.kharabadze@gmail.com', 'ბათუმი', 'აჭარა', '2025-04-25'),
('მანანა სალუქვაძე', 'manana.s@gmail.com', 'თბილისი', 'თბილისი', '2025-04-28'),
('ლაშა პაპუნაიშვილი', 'l.papunaishvili@gmail.com', 'რუსთავი', 'ქვემო ქართლი', '2025-05-01'),
('ნატო ჩხაიძე', 'nato.chkhaidze@gmail.com', 'თელავი', 'კახეთი', '2025-05-03'),
('თორნიკე წიკლაური', 't.tsiklauri@gmail.com', 'თბილისი', 'თბილისი', '2025-05-05'),
('ეთერი ოსიაშვილი', 'e.osiashvili@gmail.com', 'ქუთაისი', 'იმერეთი', '2025-05-08'),
('გიორგი მესხი', 'g.meskhi@gmail.com', 'ბათუმი', 'აჭარა', '2025-05-10'),
('ნანა ქუთათელაძე', 'n.kutatheladze@gmail.com', 'თბილისი', 'თბილისი', '2025-05-12'),
('დათო ნოდია', 'd.nodia@gmail.com', 'ზუგდიდი', 'სამეგრელო', '2025-05-14'),
('ხატია ბუნიათიშვილი', 'kh.buniatishvili@gmail.com', 'თბილისი', 'თბილისი', '2025-05-15'),
('ზაზა ფაჩულია', 'z.pachulia@gmail.com', 'ქუთაისი', 'იმერეთი', '2025-05-18'),
('თინათინ კაციტაძე', 'tina.katsitadze@gmail.com', 'რუსთავი', 'ქვემო ქართლი', '2025-05-20'),
('ოთარ კუშიტაშვილი', 'o.kushitashvili@gmail.com', 'გორი', 'შიდა ქართლი', '2025-05-22'),
('მაია ონიანი', 'maia.oniani@gmail.com', 'ბათუმი', 'აჭარა', '2025-05-25'),
('შალვა პაპასკირი', 'sh.papaskiri@gmail.com', 'ფოთი', 'სამეგრელო', '2025-05-28'),
('ნელი გოგიჩაიშვილი', 'neli.gogichaishvili@gmail.com', 'თბილისი', 'თბილისი', '2025-06-01'),
('პაატა კანდელაკი', 'p.kandelaki@gmail.com', 'თბილისი', 'თბილისი', '2025-06-03'),
('ლელა თოფურია', 'l.topuria@gmail.com', 'ქუთაისი', 'იმერეთი', '2025-06-05'),
('არჩილ გელაშვილი', 'a.gelashvili@gmail.com', 'თელავი', 'კახეთი', '2025-06-08'),
('რუსუდან ასათიანი', 'r.asatiani@gmail.com', 'თბილისი', 'თბილისი', '2025-06-10'),
('გიორგი ცხადაძე', 'g.tskhadaze@gmail.com', 'რუსთავი', 'ქვემო ქართლი', '2025-06-12'),
('ბაია ბერუაშვილი', 'b.beruashvili@gmail.com', 'ბათუმი', 'აჭარა', '2025-06-15'),
('გელა მარგველაშვილი', 'gela.marg@gmail.com', 'თბილისი', 'თბილისი', '2025-06-18'),
('ნინი ხიზანიშვილი', 'nini.khiz@gmail.com', 'ზუგდიდი', 'სამეგრელო', '2025-06-20'),
('ემილ დარჩია', 'e.darchia@gmail.com', 'ფოთი', 'სამეგრელო', '2025-06-22'),
('თამილა სვანიძე', 'tamila.sv@gmail.com', 'თბილისი', 'თბილისი', '2025-06-25');

-- === დამატებითი მომხმარებლები (150 სწრაფი ჩასმით) ===
INSERT INTO customers (full_name, email, city, region, registered_at)
SELECT
    CASE (random() * 19)::int
        WHEN 0 THEN 'გიორგი' WHEN 1 THEN 'ნინო' WHEN 2 THEN 'დავით' WHEN 3 THEN 'მარიამ'
        WHEN 4 THEN 'ალექსანდრე' WHEN 5 THEN 'თამარ' WHEN 6 THEN 'ლუკა' WHEN 7 THEN 'ანა'
        WHEN 8 THEN 'ნიკა' WHEN 9 THEN 'ელენე' WHEN 10 THEN 'სანდრო' WHEN 11 THEN 'ქეთევან'
        WHEN 12 THEN 'ირაკლი' WHEN 13 THEN 'სოფიო' WHEN 14 THEN 'ბექა' WHEN 15 THEN 'ლიკა'
        WHEN 16 THEN 'ვახტანგ' WHEN 17 THEN 'ნათია' WHEN 18 THEN 'კახა' ELSE 'თორნიკე'
    END || ' ' ||
    CASE (random() * 14)::int
        WHEN 0 THEN 'გელაშვილი' WHEN 1 THEN 'ბერიძე' WHEN 2 THEN 'კაპანაძე' WHEN 3 THEN 'წერეთელი'
        WHEN 4 THEN 'ხარაიშვილი' WHEN 5 THEN 'ლომიძე' WHEN 6 THEN 'ჯავახიშვილი' WHEN 7 THEN 'მაისურაძე'
        WHEN 8 THEN 'კობახიძე' WHEN 9 THEN 'ფერაძე' WHEN 10 THEN 'დვალი' WHEN 11 THEN 'გოგოლაძე'
        WHEN 12 THEN 'ჩხეიძე' WHEN 13 THEN 'მიქელაძე' ELSE 'სურგულაძე'
    END,
    'user_' || i || '@example.com',
    CASE (random() * 7)::int
        WHEN 0 THEN 'თბილისი' WHEN 1 THEN 'ბათუმი' WHEN 2 THEN 'ქუთაისი' WHEN 3 THEN 'რუსთავი'
        WHEN 4 THEN 'გორი' WHEN 5 THEN 'ზუგდიდი' WHEN 6 THEN 'თელავი' ELSE 'ფოთი'
    END,
    CASE (random() * 6)::int
        WHEN 0 THEN 'თბილისი' WHEN 1 THEN 'აჭარა' WHEN 2 THEN 'იმერეთი' WHEN 3 THEN 'ქვემო ქართლი'
        WHEN 4 THEN 'შიდა ქართლი' WHEN 5 THEN 'სამეგრელო' ELSE 'კახეთი'
    END,
    '2025-01-01'::date + (random() * 365)::int * INTERVAL '1 day'
FROM generate_series(1, 150) AS i;

-- === შეკვეთები (1000) ===
-- რეალისტური სეზონური ტრენდები: დეკემბერში მეტი, ზაფხულში ნაკლები

INSERT INTO orders (customer_id, order_date, status, total_amount, payment_method)
SELECT
    -- შემთხვევითი მომხმარებელი
    (random() * 199 + 1)::int,
    -- სეზონური თარიღი
    '2025-01-01'::timestamp + (random() * 545)::int * INTERVAL '1 day',
    -- სტატუსი (80% მიწოდებული, 10% გაგზავნილი, 5% მოლოდინში, 5% გაუქმებული)
    CASE
        WHEN random() < 0.80 THEN 'მიწოდებული'
        WHEN random() < 0.90 THEN 'გაგზავნილი'
        WHEN random() < 0.95 THEN 'მოლოდინში'
        ELSE 'გაუქმებული'
    END,
    -- ჯამი შემდეგ განახლდება
    0,
    -- გადახდის მეთოდი
    CASE (random() * 2)::int
        WHEN 0 THEN 'ბარათი'
        WHEN 1 THEN 'ნაღდი'
        ELSE 'განვადება'
    END
FROM generate_series(1, 1000);

-- === შეკვეთის ელემენტები (1-4 პროდუქტი თითო შეკვეთაში) ===

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT
    o.id,
    p.id,
    (random() * 3 + 1)::int,
    p.price
FROM orders o
CROSS JOIN LATERAL (
    SELECT id, price
    FROM products
    ORDER BY random()
    LIMIT (random() * 3 + 1)::int
) p;

-- === შეკვეთების ჯამური თანხის განახლება ===

UPDATE orders o
SET total_amount = sub.total
FROM (
    SELECT order_id, SUM(quantity * unit_price) AS total
    FROM order_items
    GROUP BY order_id
) sub
WHERE o.id = sub.order_id;

-- === მატერიალიზებული ხედი — თვიური შემოსავალი ===

CREATE MATERIALIZED VIEW IF NOT EXISTS monthly_revenue AS
SELECT
    DATE_TRUNC('month', o.order_date) AS month,
    SUM(o.total_amount) AS revenue,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    COUNT(o.id) AS total_orders
FROM orders o
WHERE o.status != 'გაუქმებული'
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;

-- === სტატისტიკის ხედი ===

CREATE OR REPLACE VIEW sales_summary AS
SELECT
    p.category AS კატეგორია,
    COUNT(oi.id) AS გაყიდვების_რაოდენობა,
    SUM(oi.quantity) AS გაყიდული_ერთეულები,
    SUM(oi.quantity * oi.unit_price) AS შემოსავალი,
    SUM(oi.quantity * (oi.unit_price - p.cost)) AS მოგება
FROM order_items oi
JOIN products p ON p.id = oi.product_id
JOIN orders o ON o.id = oi.order_id
WHERE o.status != 'გაუქმებული'
GROUP BY p.category
ORDER BY შემოსავალი DESC;

-- === Read-Only მომხმარებელი (უსაფრთხოება) ===
-- Docker-ში ავტომატურად არ გაეშვება, მაგრამ production-ში საჭიროა
-- CREATE USER readonly_user WITH PASSWORD 'readonly_pass';
-- GRANT CONNECT ON DATABASE conversational_bi TO readonly_user;
-- GRANT USAGE ON SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
