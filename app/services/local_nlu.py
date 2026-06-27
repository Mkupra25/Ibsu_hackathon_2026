"""
ლოკალური NLU ძრავი — Gemini-ს გარეშე ქართული კითხვების SQL-ად გარდაქმნა.

v2: Smart Dynamic NLU
- regex-ით ამოიყვანს სახელებს, კატეგორიებს, ციფრებს კითხვიდან
- dynamic SQL გენერაცია პარამეტრებით
- priority-based matching (specific > general)
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class NLUResult:
    intent: str  # "greeting", "bi_query", "unclear"
    sql: Optional[str] = None
    chart_type: Optional[str] = None
    chart_title: Optional[str] = None
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    explanation: Optional[str] = None
    answer: Optional[str] = None


# ========== მეტა/მისალმება ==========

GREETING_WORDS = [
    "გამარჯობა", "გამარჯობათ", "hello", "hi", "სალამი",
    "მოგესალმებით", "კეთილი", "გაიხარე",
]

META_WORDS = [
    "რა შეგიძლია", "რა კითხვა", "რა შეგიძლებ", "დამეხმარე", "help",
    "რით შეგიძლია", "რა გამოდის", "რა ვიკითხო", "მასწავლე", "ახსენი",
    "რა ხარ", "ვინ ხარ", "შესაძლებლობები",
]

FAREWELL_WORDS = ["ნახვამდის", "კარგად", "bye", "goodbye", "მადლობა", "გმადლობ"]


# ========== კატეგორიების რუქა (ზუსტი DB სახელები) ==========
# DB-ში არსებული კატეგორიები: ელექტრონიკა, საკვები, საყოფაცხოვრებო, სპორტი, ტანსაცმელი

CATEGORY_MAP = {
    # Georgian → exact DB value
    "სპორტ": "სპორტი",
    "ელექტრონ": "ელექტრონიკა",
    "ელექტრო": "ელექტრონიკა",
    "ტექნიკ": "ელექტრონიკა",
    "საყოფ": "საყოფაცხოვრებო",
    "სახლ": "საყოფაცხოვრებო",
    "ყოფაცხ": "საყოფაცხოვრებო",
    "ჩაცმულ": "ტანსაცმელი",
    "ტანსაცმ": "ტანსაცმელი",
    "სამოს": "ტანსაცმელი",
    "ტანი": "ტანსაცმელი",
    "საკვებ": "საკვები",
    "სურსათ": "საკვები",
    "საჭმელ": "საკვები",
    "English": None,
    # English → exact DB value
    "sport": "სპორტი",
    "electron": "ელექტრონიკა",
    "electric": "ელექტრონიკა",
    "techni": "ელექტრონიკა",
    "household": "საყოფაცხოვრებო",
    "cloth": "ტანსაცმელი",
    "fashion": "ტანსაცმელი",
    "apparel": "ტანსაცმელი",
    "food": "საკვები",
    "grocery": "საკვები",
}


def _extract_limit(text: str, default: int = 5) -> int:
    """ამოიყვანს ციფრს კითხვიდან (LIMIT-ისთვის)."""
    m = re.search(r'\b(\d+)\b', text)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 100:
            return n
    return default


def _extract_name(text: str) -> Optional[str]:
    """სახელის ამოყვანა 'სახელით X' ან 'სახელი X' პატერნით."""
    patterns = [
        r'სახელით\s+([ა-ჰa-zA-Z]+)',
        r'სახელი\s+([ა-ჰa-zA-Z]+)',
        r'named?\s+([a-zA-Z]+)',
        r'by name\s+([a-zA-Z]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _extract_category(text: str) -> Optional[str]:
    """კატეგორიის ამოყვანა ტექსტიდან."""
    for kw, cat in CATEGORY_MAP.items():
        if kw in text:
            return cat
    return None


def _extract_city(text: str) -> Optional[str]:
    """ქალაქის ამოყვანა ტექსტიდან."""
    cities = ["თბილის", "ბათუმ", "ქუთაის", "რუსთავ", "გორ", "ზუგდიდ",
              "ფოთ", "სამტრედ", "ქობულეთ", "ხაშურ", "სიღნაღ", "ახალციხ",
              "tbilisi", "batumi", "kutaisi", "rustavi"]
    for city_partial in cities:
        if city_partial.lower() in text:
            full = city_partial.rstrip("ი").rstrip("ო").rstrip("ა")
            # დაბრუნება მთლიანი სახელით
            city_names = {
                "თბილის": "თბილისი", "ბათუმ": "ბათუმი", "ქუთაის": "ქუთაისი",
                "რუსთავ": "რუსთავი", "გორ": "გორი", "ზუგდიდ": "ზუგდიდი",
                "ფოთ": "ფოთი", "სამტრედ": "სამტრედია", "ქობულეთ": "ქობულეთი",
                "ხაშურ": "ხაშური", "სიღნაღ": "სიღნაღი", "ახალციხ": "ახალციხე",
                "tbilisi": "თბილისი", "batumi": "ბათუმი",
                "kutaisi": "ქუთაისი", "rustavi": "რუსთავი",
            }
            return city_names.get(city_partial)
    return None


# ========== DYNAMIC SQL RULES ==========
# priority: მაღალი რიცხვი = პირველი შემოწმება

DYNAMIC_RULES = [

    # ── კომპლექსური: სახელით ძიება ──
    {
        "priority": 100,
        "check": lambda m: _extract_name(m) is not None,
        "build": lambda m: _build_customer_by_name(m),
    },

    # ── კომპლექსური: საშუალო + კატეგორია ──
    {
        "priority": 95,
        "check": lambda m: any(w in m for w in ["საშუალო", "average", "avg"]) and _extract_category(m),
        "build": lambda m: _build_avg_sales_by_category(m),
    },

    # ── კომპლექსური: კატეგორია + ჯამური შემოსავალი ──
    {
        "priority": 90,
        "check": lambda m: any(w in m for w in ["შემოსავალ", "revenue", "გაყიდვა"]) and _extract_category(m) and any(w in m for w in ["ჯამ", "სულ", "total"]),
        "build": lambda m: _build_revenue_by_specific_category(m),
    },

    # ── კომპლექსური: ქალაქი + შემოსავალი ──
    {
        "priority": 88,
        "check": lambda m: _extract_city(m) is not None and any(w in m for w in ["შემოსავ", "revenue", "გაყიდვ"]),
        "build": lambda m: _build_revenue_by_city_filter(m),
    },

    # ── კომპლექსური: კატეგორია + TOP N ──
    {
        "priority": 85,
        "check": lambda m: any(w in m for w in ["ტოპ", "top", "პოპულარ", "საუკეთ", "გაყიდვ"]) and _extract_category(m),
        "build": lambda m: _build_top_products_by_category(m),
    },

    # ── კომპლექსური: კატეგორიის პროდუქტები ──
    {
        "priority": 80,
        "check": lambda m: _extract_category(m) is not None and any(w in m for w in ["პროდუქტ", "ნივთ", "ჩამოთვლ", "გამოიტან", "product", "item"]),
        "build": lambda m: _build_products_by_category(m),
    },

    # ── catch-all: კატეგორია (standalone — sport, electronics, etc.) ──
    {
        "priority": 75,
        "check": lambda m: _extract_category(m) is not None,
        "build": lambda m: _build_top_products_by_category(m),
    },

    # ── TOP N მომხმარებელი (VIP) ──
    {
        "priority": 78,
        "check": lambda m: any(w in m for w in ["ტოპ", "top", "საუკეთ", "vip", "ლიდერ"]) and any(w in m for w in ["მომხმარებ", "კლიენტ", "customer"]),
        "build": lambda m: _build_top_customers(m),
    },

    # ── ჯამური შემოსავალი ──
    {
        "priority": 70,
        "check": lambda m: any(w in m for w in ["ჯამური შემოსავ", "სრული შემოსავ", "total revenue", "ჯამი შემოსავ", "რამდენი შემოვ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT SUM(total_amount) AS ჯამური_შემოსავალი FROM orders WHERE status != 'გაუქმებული'",
            chart_type="none",
            chart_title="ჯამური შემოსავალი",
            explanation="ყველა (გარდა გაუქმებული) შეკვეთის ჯამური შემოსავალი",
        ),
    },

    # ── შემოსავალი ქალაქების მიხედვით ──
    {
        "priority": 68,
        "check": lambda m: any(w in m for w in ["ქალაქ", "city"]) and any(w in m for w in ["შემოსავ", "revenue", "გაყიდვ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="""SELECT c.city AS ქალაქი, SUM(o.total_amount) AS შემოსავალი, COUNT(o.id) AS შეკვეთები
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status != 'გაუქმებული'
GROUP BY c.city
ORDER BY შემოსავალი DESC""",
            chart_type="bar",
            chart_title="შემოსავალი ქალაქების მიხედვით",
            x_axis="ქალაქი",
            y_axis="შემოსავალი",
            explanation="ყოველი ქალაქის ჯამური შემოსავალი",
        ),
    },

    # ── შემოსავალი თვეების მიხედვით ──
    {
        "priority": 66,
        "check": lambda m: any(w in m for w in ["თვ", "month"]) and any(w in m for w in ["შემოსავ", "revenue", "გაყიდვ", "დინამ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="""SELECT TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS თვე,
       SUM(total_amount) AS შემოსავალი
FROM orders
WHERE status != 'გაუქმებული'
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY DATE_TRUNC('month', created_at)""",
            chart_type="line",
            chart_title="შემოსავალი თვეების მიხედვით",
            x_axis="თვე",
            y_axis="შემოსავალი",
            explanation="შემოსავლის ტრენდი თვეების მიხედვით",
        ),
    },

    # ── შემოსავალი კატეგორიების მიხედვით (ზოგადი) ──
    {
        "priority": 64,
        "check": lambda m: any(w in m for w in ["კატეგ", "category"]) and any(w in m for w in ["შემოსავ", "revenue"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="""SELECT p.category AS კატეგორია, SUM(oi.quantity * oi.unit_price) AS შემოსავალი
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'გაუქმებული'
GROUP BY p.category
ORDER BY შემოსავალი DESC""",
            chart_type="pie",
            chart_title="შემოსავალი კატეგორიების მიხედვით",
            x_axis="კატეგორია",
            y_axis="შემოსავალი",
            explanation="შემოსავლის განაწილება კატეგორიების მიხედვით",
        ),
    },

    # ── TOP 5 პროდუქტი (ზოგადი) ──
    {
        "priority": 62,
        "check": lambda m: any(w in m for w in ["ტოპ", "top", "პოპულარ", "საუკეთ"]) and any(w in m for w in ["პროდუქტ", "ნივთ", "product"]),
        "build": lambda m: _build_top_products_general(m),
    },

    # ── ყველაზე ძვირი პროდუქტი ──
    {
        "priority": 60,
        "check": lambda m: any(w in m for w in ["ძვირ", "expensive", "მაღალ ფას", "ძვირადღ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql=f"""SELECT name AS პროდუქტი, price AS ფასი, category AS კატეგორია
FROM products
ORDER BY price DESC
LIMIT {_extract_limit(m, 10)}""",
            chart_type="bar",
            chart_title="ყველაზე ძვირი პროდუქტები",
            x_axis="პროდუქტი",
            y_axis="ფასი",
            explanation="ყველაზე მაღალი ფასის მქონე პროდუქტები",
        ),
    },

    # ── მარაგი / Stock ──
    {
        "priority": 58,
        "check": lambda m: any(w in m for w in ["მარაგ", "stock", "ინვენტ", "inventory", "ნაკლ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT name AS პროდუქტი, category AS კატეგორია, stock AS მარაგი FROM products WHERE stock < 10 ORDER BY stock ASC",
            chart_type="bar",
            chart_title="პროდუქტები მცირე მარაგით",
            x_axis="პროდუქტი",
            y_axis="მარაგი",
            explanation="10-ზე ნაკლები მარაგის პროდუქტები",
        ),
    },

    # ── გაუქმებული შეკვეთები ──
    {
        "priority": 56,
        "check": lambda m: any(w in m for w in ["გაუქმებ", "cancel"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT COUNT(*) AS გაუქმებული_შეკვეთები, SUM(total_amount) AS დაკარგული_შემოსავალი FROM orders WHERE status = 'გაუქმებული'",
            chart_type="none",
            chart_title="გაუქმებული შეკვეთები",
            explanation="გაუქმებული შეკვეთები და დაკარგული შემოსავალი",
        ),
    },

    # ── შეკვეთები სტატუსების მიხედვით ──
    {
        "priority": 54,
        "check": lambda m: any(w in m for w in ["სტატუს", "status", "შეკვეთ", "order"]) and any(w in m for w in ["მიხედვ", "by", "ყველა", "all", "რამდენ", "განაწილ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT status AS სტატუსი, COUNT(*) AS შეკვეთები, SUM(total_amount) AS ჯამი FROM orders GROUP BY status ORDER BY შეკვეთები DESC",
            chart_type="pie",
            chart_title="შეკვეთები სტატუსის მიხედვით",
            x_axis="სტატუსი",
            y_axis="შეკვეთები",
            explanation="შეკვეთათა განაწილება სტატუსების მიხედვით",
        ),
    },

    # ── გადახდის მეთოდები ──
    {
        "priority": 52,
        "check": lambda m: any(w in m for w in ["გადახდ", "payment", "ბარათ", "ნაღდ", "განვად"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT payment_method AS გადახდის_მეთოდი, COUNT(*) AS შეკვეთები, SUM(total_amount) AS ჯამი FROM orders WHERE status != 'გაუქმებული' GROUP BY payment_method ORDER BY ჯამი DESC",
            chart_type="pie",
            chart_title="გადახდის მეთოდები",
            x_axis="გადახდის_მეთოდი",
            y_axis="ჯამი",
            explanation="გადახდის მეთოდების განაწილება",
        ),
    },

    # ── საშუალო შეკვეთა ──
    {
        "priority": 50,
        "check": lambda m: any(w in m for w in ["საშუალო", "average", "avg"]) and any(w in m for w in ["შეკვეთ", "order", "ჩეკ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT ROUND(AVG(total_amount)::numeric, 2) AS საშუალო_შეკვეთის_ღირებულება FROM orders WHERE status != 'გაუქმებული'",
            chart_type="none",
            chart_title="საშუალო შეკვეთის ღირებულება",
            explanation="ყოველი შეკვეთის საშუალო ღირებულება",
        ),
    },

    # ── მომხმარებლები ქალაქების მიხედვით (ზოგადი) ──
    {
        "priority": 46,
        "check": lambda m: any(w in m for w in ["მომხმარებ", "კლიენტ", "customer", "მყიდვ"]) and any(w in m for w in ["ქალაქ", "city", "მიხედვ", "განაწილ"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql="SELECT city AS ქალაქი, COUNT(*) AS მომხმარებლები FROM customers GROUP BY city ORDER BY მომხმარებლები DESC",
            chart_type="bar",
            chart_title="მომხმარებლები ქალაქების მიხედვით",
            x_axis="ქალაქი",
            y_axis="მომხმარებლები",
            explanation="მომხმარებელთა განაწილება ქალაქების მიხედვით",
        ),
    },

    # ── პროდუქტების სია (ზოგადი) ──
    {
        "priority": 30,
        "check": lambda m: any(w in m for w in ["პროდუქტ", "product", "ნივთ", "ჩამოთვლ", "გამოიტან"]) and any(w in m for w in ["ყველა", "all", "სია", "list"]),
        "build": lambda m: NLUResult(
            intent="bi_query",
            sql=f"SELECT name AS პროდუქტი, category AS კატეგორია, price AS ფასი, stock AS მარაგი FROM products ORDER BY category, price DESC LIMIT {_extract_limit(m, 50)}",
            chart_type="table",
            chart_title="პროდუქტების სია",
            x_axis="კატეგორია",
            y_axis="ფასი",
            explanation="პროდუქტების სრული სია",
        ),
    },
]


# ========== Builder functions ==========

def _build_customer_by_name(m: str) -> NLUResult:
    name = _extract_name(m)
    limit = _extract_limit(m, 10)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT c.name AS სახელი, c.email AS ელ_ფოსტა, c.city AS ქალაქი,
       COUNT(o.id) AS შეკვეთები, COALESCE(SUM(o.total_amount), 0) AS ჯამური_ღირებულება
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE c.name ILIKE '%{name}%'
GROUP BY c.id, c.name, c.email, c.city
ORDER BY შეკვეთები DESC
LIMIT {limit}""",
        chart_type="bar",
        chart_title=f"მომხმარებლები სახელით: {name}",
        x_axis="სახელი",
        y_axis="შეკვეთები",
        explanation=f"მომხმარებლები სახელით '{name}'",
    )


def _build_avg_sales_by_category(m: str) -> NLUResult:
    cat = _extract_category(m)
    if cat:
        return NLUResult(
            intent="bi_query",
            sql=f"""SELECT p.name AS პროდუქტი,
       ROUND(AVG(oi.unit_price)::numeric, 2) AS საშუალო_ფასი,
       SUM(oi.quantity) AS გაყიდული_რაოდენობა,
       SUM(oi.quantity * oi.unit_price) AS ჯამური_შემოსავალი
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE p.category ILIKE '%{cat}%'
  AND o.status != 'გაუქმებული'
GROUP BY p.id, p.name
ORDER BY ჯამური_შემოსავალი DESC
LIMIT 10""",
            chart_type="bar",
            chart_title=f"საშუალო გაყიდვა: {cat}",
            x_axis="პროდუქტი",
            y_axis="ჯამური_შემოსავალი",
            explanation=f"{cat} კატეგორიის პროდუქტების გაყიდვები",
        )
    # fallback
    return NLUResult(
        intent="bi_query",
        sql="SELECT ROUND(AVG(total_amount)::numeric, 2) AS საშუალო_შეკვეთის_ღირებულება FROM orders WHERE status != 'გაუქმებული'",
        chart_type="none",
        chart_title="საშუალო შეკვეთა",
        explanation="ყოველი შეკვეთის საშუალო ღირებულება",
    )


def _build_revenue_by_specific_category(m: str) -> NLUResult:
    cat = _extract_category(m)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT p.name AS პროდუქტი, SUM(oi.quantity * oi.unit_price) AS შემოსავალი
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE p.category ILIKE '%{cat}%'
  AND o.status != 'გაუქმებული'
GROUP BY p.name
ORDER BY შემოსავალი DESC
LIMIT 10""",
        chart_type="bar",
        chart_title=f"შემოსავალი: {cat}",
        x_axis="პროდუქტი",
        y_axis="შემოსავალი",
        explanation=f"{cat} კატეგორიის შემოსავალი",
    )


def _build_revenue_by_city_filter(m: str) -> NLUResult:
    city = _extract_city(m)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT TO_CHAR(DATE_TRUNC('month', o.created_at), 'YYYY-MM') AS თვე,
       SUM(o.total_amount) AS შემოსავალი
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.city = '{city}'
  AND o.status != 'გაუქმებული'
GROUP BY DATE_TRUNC('month', o.created_at)
ORDER BY DATE_TRUNC('month', o.created_at)""",
        chart_type="line",
        chart_title=f"შემოსავალი: {city}",
        x_axis="თვე",
        y_axis="შემოსავალი",
        explanation=f"{city}-ის შემოსავლის ტრენდი",
    )


def _build_top_products_by_category(m: str) -> NLUResult:
    cat = _extract_category(m)
    limit = _extract_limit(m, 5)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT p.name AS პროდუქტი,
       SUM(oi.quantity) AS გაყიდული_რაოდენობა,
       SUM(oi.quantity * oi.unit_price) AS შემოსავალი
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE p.category ILIKE '%{cat}%'
  AND o.status != 'გაუქმებული'
GROUP BY p.id, p.name
ORDER BY გაყიდული_რაოდენობა DESC
LIMIT {limit}""",
        chart_type="bar",
        chart_title=f"ტოპ {limit} პროდუქტი: {cat}",
        x_axis="პროდუქტი",
        y_axis="გაყიდული_რაოდენობა",
        explanation=f"{cat} კატეგორიის ყველაზე გაყიდვადი {limit} პროდუქტი",
    )


def _build_products_by_category(m: str) -> NLUResult:
    cat = _extract_category(m)
    limit = _extract_limit(m, 10)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT name AS პროდუქტი, price AS ფასი, stock AS მარაგი
FROM products
WHERE category ILIKE '%{cat}%'
ORDER BY price DESC
LIMIT {limit}""",
        chart_type="bar",
        chart_title=f"პროდუქტები: {cat}",
        x_axis="პროდუქტი",
        y_axis="ფასი",
        explanation=f"{cat} კატეგორიის პროდუქტები",
    )


def _build_top_customers(m: str) -> NLUResult:
    limit = _extract_limit(m, 10)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT c.name AS მომხმარებელი, c.city AS ქალაქი,
       COUNT(o.id) AS შეკვეთები, SUM(o.total_amount) AS ჯამური_ღირებულება
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status != 'გაუქმებული'
GROUP BY c.id, c.name, c.city
ORDER BY ჯამური_ღირებულება DESC
LIMIT {limit}""",
        chart_type="bar",
        chart_title=f"VIP მომხმარებლები (ტოპ {limit})",
        x_axis="მომხმარებელი",
        y_axis="ჯამური_ღირებულება",
        explanation=f"ყველაზე მეტი ხარჯის მქონე {limit} მომხმარებელი",
    )


def _build_top_products_general(m: str) -> NLUResult:
    limit = _extract_limit(m, 5)
    return NLUResult(
        intent="bi_query",
        sql=f"""SELECT p.name AS პროდუქტი,
       SUM(oi.quantity) AS გაყიდული_რაოდენობა,
       SUM(oi.quantity * oi.unit_price) AS შემოსავალი
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'გაუქმებული'
GROUP BY p.id, p.name
ORDER BY გაყიდული_რაოდენობა DESC
LIMIT {limit}""",
        chart_type="bar",
        chart_title=f"ტოპ {limit} პროდუქტი გაყიდვებით",
        x_axis="პროდუქტი",
        y_axis="გაყიდული_რაოდენობა",
        explanation=f"ყველაზე მეტად გაყიდული {limit} პროდუქტი",
    )


# ========== მთავარი NLU ფუნქცია ==========

def classify_and_generate(message: str) -> NLUResult:
    """
    ქართული ტექსტის კლასიფიკაცია + SQL გენერაცია.
    Priority-based matching — highest priority rule wins.
    """
    m = message.strip().lower()

    # 1. მისალმება
    if any(w in m for w in GREETING_WORDS):
        return NLUResult(
            intent="greeting",
            answer=(
                "გამარჯობა! BeeEye -- ბიზნეს-ანალიტიკის AI ასისტენტი.\n\n"
                "შემიძლია ვუპასუხო ქართულ კითხვებს ბიზნეს-მონაცემების შესახებ!\n\n"
                "ნიმუშები:\n"
                "- ჯამური შემოსავალი\n"
                "- ტოპ 5 პროდუქტი\n"
                "- შემოსავალი ქალაქების მიხედვით\n"
                "- სპორტის კატეგორიის ტოპ 3 პროდუქტი\n"
                "- გამოიტანე 5 მომხმარებელი სახელით გიორგი\n"
                "- საშუალო გაყიდვა ელექტრონიკაში\n"
                "- გადახდის მეთოდები\n"
                "- პროდუქტები მცირე მარაგით\n\n"
                "რით შემიძლია დაგეხმაროთ?"
            ),
        )

    # 2. დამშვიდობება
    if any(w in m for w in FAREWELL_WORDS):
        return NLUResult(
            intent="greeting",
            answer="გმადლობთ! BeeEye-ით სარგებლობისთვის. კარგად იყავით!",
        )

    # 3. მეტა-კითხვები
    if any(w in m for w in META_WORDS):
        return NLUResult(
            intent="greeting",
            answer=(
                "მე BeeEye-ი ვარ -- AI ასისტენტი SQL ბაზაზე.\n\n"
                "ასეთ კითხვებს ვამუშავებ:\n\n"
                "- შემოსავალი: ჯამური, ქალაქების, თვეების, კატეგორიების მიხედვით\n"
                "- პროდუქტები: ტოპ N, კატეგორიით, ფასით, მარაგით\n"
                "- მომხმარებლები: სახელით, ქალაქით, VIP-ები\n"
                "- შეკვეთები: სტატუსით, გაუქმებული, საშუალო ღირებულება\n"
                "- გადახდა: მეთოდების განაწილება\n"
                "- საშუალო: გაყიდვა კატეგორიით, შეკვეთის ღირებულება\n"
            ),
        )

    # 4. Dynamic rules — priority order
    sorted_rules = sorted(DYNAMIC_RULES, key=lambda r: r["priority"], reverse=True)

    for rule in sorted_rules:
        try:
            if rule["check"](m):
                result = rule["build"](m)
                if result and result.sql:
                    return result
        except Exception:
            continue

    # 5. ვერ ვცნო
    return NLUResult(
        intent="unclear",
        answer=None,
    )
