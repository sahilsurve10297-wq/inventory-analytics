-- ============================================================================
-- Inventory Analytics PostgreSQL Schema (Normalized 3NF)
-- Database: inventory_analytics
-- ============================================================================

DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS inventory_movements CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;

CREATE TABLE warehouses (
    warehouse_id        VARCHAR(20) PRIMARY KEY,
    warehouse_name      VARCHAR(120) NOT NULL UNIQUE,
    city                VARCHAR(80)  NOT NULL,
    region              VARCHAR(60)  NOT NULL,
    warehouse_capacity  INTEGER      NOT NULL CHECK (warehouse_capacity > 0),
    warehouse_type      VARCHAR(60)  NOT NULL
);

CREATE TABLE suppliers (
    supplier_id           VARCHAR(20) PRIMARY KEY,
    supplier_name         VARCHAR(120) NOT NULL UNIQUE,
    supplier_region       VARCHAR(60)  NOT NULL,
    supplier_rating       NUMERIC(3,2) NOT NULL CHECK (supplier_rating BETWEEN 0 AND 5),
    average_delivery_days INTEGER      NOT NULL CHECK (average_delivery_days > 0),
    supplier_status       VARCHAR(30)  NOT NULL CHECK (supplier_status IN ('Preferred', 'Active', 'On Hold', 'Inactive'))
);

CREATE TABLE products (
    product_id      VARCHAR(20) PRIMARY KEY,
    product_name    VARCHAR(150) NOT NULL,
    category        VARCHAR(80)  NOT NULL,
    subcategory     VARCHAR(80)  NOT NULL,
    brand           VARCHAR(80)  NOT NULL,
    unit_cost       NUMERIC(10,2) NOT NULL CHECK (unit_cost >= 0),
    selling_price   NUMERIC(10,2) NOT NULL CHECK (selling_price >= 0),
    reorder_level   INTEGER       NOT NULL CHECK (reorder_level >= 0),
    safety_stock    INTEGER       NOT NULL CHECK (safety_stock >= 0),
    lead_time_days  INTEGER       NOT NULL CHECK (lead_time_days > 0),
    supplier_id     VARCHAR(20)   NOT NULL REFERENCES suppliers(supplier_id)
);

CREATE TABLE purchase_orders (
    purchase_order_id      VARCHAR(25) PRIMARY KEY,
    supplier_id            VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id),
    product_id             VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse_id           VARCHAR(20) NOT NULL REFERENCES warehouses(warehouse_id),
    order_date             DATE        NOT NULL,
    expected_delivery_date DATE        NOT NULL,
    actual_delivery_date   DATE,
    quantity_ordered       INTEGER     NOT NULL CHECK (quantity_ordered > 0),
    quantity_received      INTEGER     NOT NULL CHECK (quantity_received >= 0),
    purchase_cost          NUMERIC(12,2) NOT NULL CHECK (purchase_cost >= 0),
    order_status           VARCHAR(30) NOT NULL CHECK (order_status IN ('Delivered', 'Partial', 'Pending', 'Cancelled'))
);

CREATE TABLE inventory_movements (
    movement_id   VARCHAR(25) PRIMARY KEY,
    product_id    VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse_id  VARCHAR(20) NOT NULL REFERENCES warehouses(warehouse_id),
    movement_date DATE        NOT NULL,
    movement_type VARCHAR(30) NOT NULL CHECK (movement_type IN ('Purchase', 'Sale', 'Return', 'Adjustment', 'Transfer In', 'Transfer Out')),
    quantity      INTEGER     NOT NULL CHECK (quantity > 0),
    unit_cost     NUMERIC(10,2) NOT NULL CHECK (unit_cost >= 0),
    reference_id  VARCHAR(40) NOT NULL
);

CREATE TABLE sales (
    sales_id      VARCHAR(25) PRIMARY KEY,
    product_id    VARCHAR(20) NOT NULL REFERENCES products(product_id),
    warehouse_id  VARCHAR(20) NOT NULL REFERENCES warehouses(warehouse_id),
    sales_date    DATE        NOT NULL,
    quantity_sold INTEGER     NOT NULL CHECK (quantity_sold > 0),
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    discount      NUMERIC(5,4)  NOT NULL DEFAULT 0 CHECK (discount BETWEEN 0 AND 1),
    total_revenue NUMERIC(12,2) NOT NULL CHECK (total_revenue >= 0),
    profit        NUMERIC(12,2) NOT NULL
);

-- Performance Indexes
CREATE INDEX idx_products_category      ON products(category);
CREATE INDEX idx_products_supplier      ON products(supplier_id);
CREATE INDEX idx_mov_product_warehouse  ON inventory_movements(product_id, warehouse_id);
CREATE INDEX idx_mov_date_type          ON inventory_movements(movement_date, movement_type);
CREATE INDEX idx_sales_product_date     ON sales(product_id, sales_date);
CREATE INDEX idx_sales_warehouse        ON sales(warehouse_id);
CREATE INDEX idx_po_supplier_status     ON purchase_orders(supplier_id, order_status);
