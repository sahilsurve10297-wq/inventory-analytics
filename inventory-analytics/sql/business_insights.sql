-- ============================================================================
-- BUSINESS INSIGHTS SQL QUERIES (10 Management Questions)
-- Answers all executive questions directly from normalized tables
-- ============================================================================

-- Q25: Top 10 selling products by revenue and units sold
SELECT p.product_id,
       p.product_name,
       p.category,
       SUM(s.quantity_sold) AS total_units_sold,
       ROUND(SUM(s.total_revenue), 2) AS total_revenue,
       ROUND(SUM(s.profit), 2) AS total_profit
FROM sales s
INNER JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Q26: Products currently below their reorder level requiring restocking
WITH stock AS (
    SELECT product_id,
           SUM(CASE WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity ELSE -quantity END) AS current_stock
    FROM inventory_movements
    GROUP BY product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       COALESCE(s.current_stock, 0) AS current_stock,
       p.reorder_level,
       p.safety_stock,
       (p.reorder_level - COALESCE(s.current_stock, 0)) AS deficit_to_rop
FROM products p
LEFT JOIN stock s ON p.product_id = s.product_id
WHERE COALESCE(s.current_stock, 0) <= p.reorder_level
ORDER BY deficit_to_rop DESC;

-- Q27: Overstocked products (stock > 2.5x reorder_level) and blocked capital
WITH stock AS (
    SELECT product_id,
           SUM(CASE WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity ELSE -quantity END) AS current_stock
    FROM inventory_movements
    GROUP BY product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       s.current_stock,
       p.reorder_level,
       ROUND(s.current_stock * p.unit_cost, 2) AS inventory_value
FROM products p
INNER JOIN stock s ON p.product_id = s.product_id
WHERE s.current_stock > p.reorder_level * 2.5
ORDER BY inventory_value DESC;

-- Q28: Inventory value and capacity utilization by warehouse
WITH wh_stock AS (
    SELECT im.warehouse_id,
           SUM(CASE WHEN im.movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN im.quantity ELSE -im.quantity END) AS units_on_hand,
           SUM(CASE WHEN im.movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN im.quantity * p.unit_cost ELSE -im.quantity * p.unit_cost END) AS inv_value
    FROM inventory_movements im
    INNER JOIN products p ON im.product_id = p.product_id
    GROUP BY im.warehouse_id
)
SELECT w.warehouse_id,
       w.warehouse_name,
       w.warehouse_capacity,
       ws.units_on_hand,
       ROUND(ws.inv_value, 2) AS inventory_value,
       ROUND(ws.units_on_hand * 100.0 / w.warehouse_capacity, 2) AS capacity_utilization_pct
FROM warehouses w
INNER JOIN wh_stock ws ON w.warehouse_id = ws.warehouse_id
ORDER BY inventory_value DESC;

-- Q29: Slow-moving products (5 or fewer units sold in last 90 days) with stock on hand
WITH recent_sales AS (
    SELECT product_id, SUM(quantity_sold) AS units_90d
    FROM sales
    WHERE sales_date >= '2026-08-02'
    GROUP BY product_id
),
stock AS (
    SELECT product_id,
           SUM(CASE WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity ELSE -quantity END) AS current_stock
    FROM inventory_movements
    GROUP BY product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       COALESCE(rs.units_90d, 0) AS units_sold_90d,
       s.current_stock,
       ROUND(s.current_stock * p.unit_cost, 2) AS blocked_capital
FROM products p
INNER JOIN stock s ON p.product_id = s.product_id
LEFT JOIN recent_sales rs ON p.product_id = rs.product_id
WHERE s.current_stock > 0 AND COALESCE(rs.units_90d, 0) <= 5
ORDER BY blocked_capital DESC;

-- Q30: Products with zero sales in the last 180 days (Dead Stock)
WITH sales_180 AS (
    SELECT DISTINCT product_id
    FROM sales
    WHERE sales_date >= '2026-05-04'
),
stock AS (
    SELECT product_id,
           SUM(CASE WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity ELSE -quantity END) AS current_stock
    FROM inventory_movements
    GROUP BY product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       s.current_stock,
       ROUND(s.current_stock * p.unit_cost, 2) AS dead_stock_value
FROM products p
INNER JOIN stock s ON p.product_id = s.product_id
LEFT JOIN sales_180 s180 ON p.product_id = s180.product_id
WHERE s180.product_id IS NULL AND s.current_stock > 0
ORDER BY dead_stock_value DESC;

-- Q31: Suppliers with highest delayed delivery counts
SELECT sup.supplier_id,
       sup.supplier_name,
       sup.supplier_region,
       COUNT(po.purchase_order_id) AS total_delivered,
       SUM(CASE WHEN po.actual_delivery_date > po.expected_delivery_date THEN 1 ELSE 0 END) AS delayed_orders,
       ROUND(SUM(CASE WHEN po.actual_delivery_date > po.expected_delivery_date THEN 1 ELSE 0 END) * 100.0 /
             NULLIF(COUNT(po.purchase_order_id), 0), 2) AS delay_rate_pct
FROM suppliers sup
INNER JOIN purchase_orders po ON sup.supplier_id = po.supplier_id
WHERE po.order_status IN ('Delivered', 'Partial')
GROUP BY sup.supplier_id, sup.supplier_name, sup.supplier_region
ORDER BY delay_rate_pct DESC;

-- Q32: Monthly purchase vs sales quantities
WITH m_sales AS (
    SELECT SUBSTR(sales_date, 1, 7) AS ym, SUM(quantity_sold) AS units_sold
    FROM sales
    GROUP BY SUBSTR(sales_date, 1, 7)
),
m_purch AS (
    SELECT SUBSTR(movement_date, 1, 7) AS ym, SUM(quantity) AS units_purchased
    FROM inventory_movements
    WHERE movement_type = 'Purchase'
    GROUP BY SUBSTR(movement_date, 1, 7)
)
SELECT COALESCE(ms.ym, mp.ym) AS year_month,
       COALESCE(mp.units_purchased, 0) AS units_purchased,
       COALESCE(ms.units_sold, 0) AS units_sold,
       (COALESCE(mp.units_purchased, 0) - COALESCE(ms.units_sold, 0)) AS net_unit_change
FROM m_sales ms
LEFT JOIN m_purch mp ON ms.ym = mp.ym
ORDER BY year_month;

-- Q33: Warehouse-product stockout locations (current_stock = 0)
WITH pw_stock AS (
    SELECT product_id, warehouse_id,
           SUM(CASE WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity ELSE -quantity END) AS current_stock
    FROM inventory_movements
    GROUP BY product_id, warehouse_id
)
SELECT w.warehouse_name,
       COUNT(*) AS stockout_sku_count
FROM pw_stock pws
INNER JOIN warehouses w ON pws.warehouse_id = w.warehouse_id
WHERE pws.current_stock = 0
GROUP BY w.warehouse_name
ORDER BY stockout_sku_count DESC;

-- Q34: High-value inventory items (Top 20 SKUs by capital tied up)
WITH stock AS (
    SELECT product_id,
           SUM(CASE WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity ELSE -quantity END) AS current_stock
    FROM inventory_movements
    GROUP BY product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       s.current_stock,
       p.unit_cost,
       ROUND(s.current_stock * p.unit_cost, 2) AS total_inventory_value
FROM products p
INNER JOIN stock s ON p.product_id = s.product_id
ORDER BY total_inventory_value DESC
LIMIT 20;
