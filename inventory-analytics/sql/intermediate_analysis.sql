-- ============================================================================
-- INTERMEDIATE SQL ANALYSIS (8 Queries)
-- Covers: INNER JOIN, LEFT JOIN, CASE WHEN, Subqueries, CTEs, Aggregates
-- ============================================================================

-- Q9: Reconcile current on-hand stock per product and warehouse using CASE WHEN
SELECT im.product_id,
       p.product_name,
       w.warehouse_name,
       SUM(CASE
           WHEN im.movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN im.quantity
           WHEN im.movement_type IN ('Sale', 'Transfer Out') THEN -im.quantity
           ELSE 0
       END) AS current_stock
FROM inventory_movements im
INNER JOIN products p ON im.product_id = p.product_id
INNER JOIN warehouses w ON im.warehouse_id = w.warehouse_id
GROUP BY im.product_id, p.product_name, w.warehouse_name
ORDER BY current_stock ASC;

-- Q10: Classify every product into Stock Health Status using a CTE
WITH product_stock AS (
    SELECT product_id,
           SUM(CASE
               WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity
               ELSE -quantity
           END) AS on_hand_qty
    FROM inventory_movements
    GROUP BY product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       COALESCE(ps.on_hand_qty, 0) AS on_hand_qty,
       p.reorder_level,
       p.safety_stock,
       CASE
           WHEN COALESCE(ps.on_hand_qty, 0) = 0 OR COALESCE(ps.on_hand_qty, 0) < p.safety_stock * 0.5 THEN 'Critical Stock'
           WHEN COALESCE(ps.on_hand_qty, 0) <= p.reorder_level THEN 'Low Stock'
           WHEN COALESCE(ps.on_hand_qty, 0) > p.reorder_level * 2.5 THEN 'Overstocked'
           ELSE 'Healthy Stock'
       END AS stock_status
FROM products p
LEFT JOIN product_stock ps ON p.product_id = ps.product_id
ORDER BY on_hand_qty ASC;

-- Q11: Identify products with above-average unit cost using a scalar subquery
SELECT product_id, product_name, category, unit_cost, selling_price
FROM products
WHERE unit_cost > (SELECT AVG(unit_cost) FROM products)
ORDER BY unit_cost DESC;

-- Q12: Warehouse revenue, profit, and gross margin percentage
SELECT w.warehouse_id,
       w.warehouse_name,
       w.region,
       COUNT(s.sales_id) AS transaction_count,
       SUM(s.quantity_sold) AS units_sold,
       ROUND(SUM(s.total_revenue), 2) AS total_revenue,
       ROUND(SUM(s.profit), 2) AS total_profit,
       ROUND(SUM(s.profit) * 100.0 / NULLIF(SUM(s.total_revenue), 0), 2) AS gross_margin_pct
FROM warehouses w
LEFT JOIN sales s ON w.warehouse_id = s.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.region
ORDER BY total_revenue DESC;

-- Q13: Supplier delivery performance (On-Time vs Delayed POs)
SELECT sup.supplier_id,
       sup.supplier_name,
       sup.supplier_rating,
       COUNT(po.purchase_order_id) AS delivered_pos,
       SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) AS on_time_pos,
       ROUND(SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) * 100.0 /
             NULLIF(COUNT(po.purchase_order_id), 0), 2) AS on_time_rate_pct
FROM suppliers sup
INNER JOIN purchase_orders po ON sup.supplier_id = po.supplier_id
WHERE po.order_status IN ('Delivered', 'Partial')
GROUP BY sup.supplier_id, sup.supplier_name, sup.supplier_rating
ORDER BY on_time_rate_pct DESC;

-- Q14: Discount impact on sales volume and profit margin
SELECT CASE
           WHEN discount = 0 THEN 'No Discount (0%)'
           WHEN discount <= 0.10 THEN 'Low Discount (1-10%)'
           ELSE 'High Discount (>10%)'
       END AS discount_tier,
       COUNT(*) AS order_count,
       SUM(quantity_sold) AS total_units,
       ROUND(SUM(total_revenue), 2) AS total_revenue,
       ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY 1
ORDER BY total_revenue DESC;

-- Q15: Open (Pending/Partial) Purchase Order quantities by product
SELECT p.product_id,
       p.product_name,
       SUM(po.quantity_ordered - po.quantity_received) AS open_po_units,
       COUNT(po.purchase_order_id) AS open_po_count
FROM purchase_orders po
INNER JOIN products p ON po.product_id = p.product_id
WHERE po.order_status IN ('Pending', 'Partial')
GROUP BY p.product_id, p.product_name
ORDER BY open_po_units DESC;

-- Q16: Category profitability and average order value
SELECT p.category,
       COUNT(s.sales_id) AS transactions,
       ROUND(AVG(s.total_revenue), 2) AS avg_order_value,
       ROUND(SUM(s.total_revenue), 2) AS total_revenue,
       ROUND(SUM(s.profit), 2) AS total_profit
FROM sales s
INNER JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY total_profit DESC;
