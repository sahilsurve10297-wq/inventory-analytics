-- ============================================================================
-- Import Cleaned CSV Datasets into PostgreSQL (psql \copy)
-- Run from the project root directory after creating tables with create_tables.sql
-- ============================================================================

\copy warehouses(warehouse_id, warehouse_name, city, region, warehouse_capacity, warehouse_type) FROM 'data/processed/warehouses.csv' WITH (FORMAT csv, HEADER true);

\copy suppliers(supplier_id, supplier_name, supplier_region, supplier_rating, average_delivery_days, supplier_status) FROM 'data/processed/suppliers.csv' WITH (FORMAT csv, HEADER true);

\copy products(product_id, product_name, category, subcategory, brand, unit_cost, selling_price, reorder_level, safety_stock, lead_time_days, supplier_id) FROM 'data/processed/products.csv' WITH (FORMAT csv, HEADER true);

\copy purchase_orders(purchase_order_id, supplier_id, product_id, warehouse_id, order_date, expected_delivery_date, actual_delivery_date, quantity_ordered, quantity_received, purchase_cost, order_status) FROM 'data/processed/purchase_orders.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy inventory_movements(movement_id, product_id, warehouse_id, movement_date, movement_type, quantity, unit_cost, reference_id) FROM 'data/processed/inventory_movements.csv' WITH (FORMAT csv, HEADER true);

\copy sales(sales_id, product_id, warehouse_id, sales_date, quantity_sold, unit_price, discount, total_revenue, profit) FROM 'data/processed/sales.csv' WITH (FORMAT csv, HEADER true);
