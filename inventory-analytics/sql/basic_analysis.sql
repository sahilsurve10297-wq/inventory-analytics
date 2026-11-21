-- ============================================================================
-- BASIC SQL ANALYSIS (8 Queries)
-- Covers: SELECT, WHERE, ORDER BY, GROUP BY, HAVING, DISTINCT
-- ============================================================================

-- Q1: List all distinct product categories and subcategories
SELECT DISTINCT category, subcategory
FROM products
ORDER BY category, subcategory;

-- Q2: Count products and average unit cost per category
SELECT category,
       COUNT(*) AS product_count,
       ROUND(AVG(unit_cost), 2) AS avg_unit_cost,
       ROUND(AVG(selling_price), 2) AS avg_selling_price
FROM products
GROUP BY category
ORDER BY product_count DESC;

-- Q3: Identify high-cost products (unit cost > $150) ordered by price
SELECT product_id, product_name, category, unit_cost, selling_price
FROM products
WHERE unit_cost > 150
ORDER BY unit_cost DESC;

-- Q4: Summarize total warehouse capacity by warehouse type
SELECT warehouse_type,
       COUNT(*) AS warehouse_count,
       SUM(warehouse_capacity) AS total_capacity
FROM warehouses
GROUP BY warehouse_type
ORDER BY total_capacity DESC;

-- Q5: List suppliers with rating below 3.5 or status On Hold
SELECT supplier_id, supplier_name, supplier_region, supplier_rating, average_delivery_days, supplier_status
FROM suppliers
WHERE supplier_rating < 3.5 OR supplier_status = 'On Hold'
ORDER BY supplier_rating ASC;

-- Q6: Count inventory movements by movement type
SELECT movement_type,
       COUNT(*) AS movement_count,
       SUM(quantity) AS total_units
FROM inventory_movements
GROUP BY movement_type
ORDER BY total_units DESC;

-- Q7: Find categories with total sales revenue exceeding $4,000,000
SELECT p.category,
       SUM(s.quantity_sold) AS total_units_sold,
       ROUND(SUM(s.total_revenue), 2) AS total_revenue
FROM sales s
INNER JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
HAVING SUM(s.total_revenue) > 4000000
ORDER BY total_revenue DESC;

-- Q8: Summarize purchase order counts and spend by order status
SELECT order_status,
       COUNT(*) AS po_count,
       SUM(quantity_ordered) AS units_ordered,
       SUM(quantity_received) AS units_received,
       ROUND(SUM(purchase_cost), 2) AS total_spend
FROM purchase_orders
GROUP BY order_status
ORDER BY po_count DESC;
