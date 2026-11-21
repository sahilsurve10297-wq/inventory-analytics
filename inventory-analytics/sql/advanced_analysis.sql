-- ============================================================================
-- ADVANCED SQL ANALYSIS (8 Queries)
-- Covers: Window Functions (RANK, DENSE_RANK, ROW_NUMBER, LAG, LEAD, Running Totals)
-- ============================================================================

-- Q17: Rank products by total revenue within each category (RANK & DENSE_RANK)
WITH prod_rev AS (
    SELECT p.product_id,
           p.product_name,
           p.category,
           ROUND(SUM(s.total_revenue), 2) AS revenue
    FROM products p
    INNER JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT category,
       product_id,
       product_name,
       revenue,
       RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS category_rank,
       DENSE_RANK() OVER (ORDER BY revenue DESC) AS global_dense_rank
FROM prod_rev
ORDER BY category, category_rank;

-- Q18: Monthly sales revenue, MoM growth %, and running cumulative total
WITH monthly_sales AS (
    SELECT SUBSTR(sales_date, 1, 7) AS year_month,
           ROUND(SUM(total_revenue), 2) AS monthly_revenue
    FROM sales
    GROUP BY SUBSTR(sales_date, 1, 7)
)
SELECT year_month,
       monthly_revenue,
       LAG(monthly_revenue) OVER (ORDER BY year_month) AS prev_month_revenue,
       ROUND((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year_month)) * 100.0 /
             NULLIF(LAG(monthly_revenue) OVER (ORDER BY year_month), 0), 2) AS mom_growth_pct,
       ROUND(SUM(monthly_revenue) OVER (ORDER BY year_month), 2) AS cumulative_revenue
FROM monthly_sales
ORDER BY year_month;

-- Q19: Top 3 products per warehouse by units sold (ROW_NUMBER)
WITH wh_prod AS (
    SELECT s.warehouse_id,
           w.warehouse_name,
           s.product_id,
           p.product_name,
           SUM(s.quantity_sold) AS units_sold
    FROM sales s
    INNER JOIN warehouses w ON s.warehouse_id = w.warehouse_id
    INNER JOIN products p ON s.product_id = p.product_id
    GROUP BY s.warehouse_id, w.warehouse_name, s.product_id, p.product_name
)
SELECT warehouse_name, product_id, product_name, units_sold
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY warehouse_id ORDER BY units_sold DESC) AS rn
    FROM wh_prod
) ranked
WHERE rn <= 3
ORDER BY warehouse_name, rn;

-- Q20: Running stock balance over time for a sample product (PRD-0001)
SELECT movement_date,
       warehouse_id,
       movement_type,
       quantity,
       SUM(CASE
           WHEN movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN quantity
           ELSE -quantity
       END) OVER (PARTITION BY warehouse_id ORDER BY movement_date, movement_id) AS running_warehouse_stock
FROM inventory_movements
WHERE product_id = 'PRD-0001'
ORDER BY warehouse_id, movement_date, movement_id;

-- Q21: Product inventory turnover ratio ranked across all SKUs
WITH prod_cogs AS (
    SELECT s.product_id,
           SUM(s.quantity_sold * p.unit_cost) AS cogs
    FROM sales s
    INNER JOIN products p ON s.product_id = p.product_id
    GROUP BY s.product_id
),
prod_stock AS (
    SELECT im.product_id,
           SUM(CASE
               WHEN im.movement_type IN ('Purchase', 'Return', 'Transfer In', 'Adjustment') THEN im.quantity
               ELSE -im.quantity
           END) AS on_hand_qty
    FROM inventory_movements im
    GROUP BY im.product_id
)
SELECT p.product_id,
       p.product_name,
       p.category,
       ROUND(COALESCE(pc.cogs, 0), 2) AS total_cogs,
       ROUND(COALESCE(ps.on_hand_qty, 0) * p.unit_cost, 2) AS ending_inv_value,
       ROUND(COALESCE(pc.cogs, 0) / NULLIF(GREATEST(COALESCE(ps.on_hand_qty, 0) * p.unit_cost, p.unit_cost), 0), 2) AS turnover_ratio,
       RANK() OVER (ORDER BY COALESCE(pc.cogs, 0) / NULLIF(GREATEST(COALESCE(ps.on_hand_qty, 0) * p.unit_cost, p.unit_cost), 0) DESC) AS turnover_rank
FROM products p
LEFT JOIN prod_cogs pc ON p.product_id = pc.product_id
LEFT JOIN prod_stock ps ON p.product_id = ps.product_id
ORDER BY turnover_rank
LIMIT 25;

-- Q22: Supplier lead-time rank and next-best supplier comparison using LEAD
WITH sup_perf AS (
    SELECT sup.supplier_id,
           sup.supplier_name,
           ROUND(AVG(JULIANDAY(po.actual_delivery_date) - JULIANDAY(po.order_date)), 2) AS avg_lead_days
    FROM suppliers sup
    INNER JOIN purchase_orders po ON sup.supplier_id = po.supplier_id
    WHERE po.order_status IN ('Delivered', 'Partial') AND po.actual_delivery_date IS NOT NULL
    GROUP BY sup.supplier_id, sup.supplier_name
)
SELECT supplier_id,
       supplier_name,
       avg_lead_days,
       LEAD(supplier_name) OVER (ORDER BY avg_lead_days ASC) AS next_fastest_supplier,
       RANK() OVER (ORDER BY avg_lead_days ASC) AS speed_rank
FROM sup_perf
ORDER BY speed_rank;

-- Q23: 3-Month moving average of monthly sales revenue
WITH monthly_rev AS (
    SELECT SUBSTR(sales_date, 1, 7) AS year_month,
           ROUND(SUM(total_revenue), 2) AS revenue
    FROM sales
    GROUP BY SUBSTR(sales_date, 1, 7)
)
SELECT year_month,
       revenue,
       ROUND(AVG(revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3m
FROM monthly_rev
ORDER BY year_month;

-- Q24: Pareto (ABC) revenue contribution % per product
WITH prod_rev AS (
    SELECT p.product_id, p.product_name, SUM(s.total_revenue) AS revenue
    FROM products p
    INNER JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.product_id, p.product_name
),
totals AS (
    SELECT SUM(revenue) AS grand_total FROM prod_rev
)
SELECT pr.product_id,
       pr.product_name,
       ROUND(pr.revenue, 2) AS revenue,
       ROUND(SUM(pr.revenue) OVER (ORDER BY pr.revenue DESC) * 100.0 / t.grand_total, 2) AS cumulative_rev_pct
FROM prod_rev pr
CROSS JOIN totals t
ORDER BY pr.revenue DESC
LIMIT 30;
