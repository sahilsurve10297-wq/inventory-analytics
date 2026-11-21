# Power BI Star Schema Data Model

## Overview
The Power BI model uses a clean **Star Schema** exported directly to `data/exports/powerbi/` (and/or connected directly to PostgreSQL `inventory_analytics`).

## Tables

### Dimension Tables
1. **DimProduct** (`product_id` PK)
   - `product_name`, `category`, `subcategory`, `brand`, `unit_cost`, `selling_price`, `reorder_level`, `safety_stock`, `lead_time_days`, `supplier_id`
2. **DimWarehouse** (`warehouse_id` PK)
   - `warehouse_name`, `city`, `region`, `warehouse_capacity`, `warehouse_type`
3. **DimSupplier** (`supplier_id` PK)
   - `supplier_name`, `supplier_region`, `supplier_rating`, `average_delivery_days`, `supplier_status`
4. **DimDate** (`date_key` PK, Date)
   - `year`, `quarter`, `month_num`, `month_name`, `year_month`, `day_of_week`, `is_weekend`

### Fact Tables
1. **FactSales** (`sales_id` PK)
   - `product_id` (FK), `warehouse_id` (FK), `sales_date` (FK -> `DimDate[date_key]`), `quantity_sold`, `unit_price`, `discount`, `total_revenue`, `profit`
2. **FactInventoryMovements** (`movement_id` PK)
   - `product_id` (FK), `warehouse_id` (FK), `movement_date` (FK -> `DimDate[date_key]`), `movement_type`, `quantity`, `unit_cost`, `reference_id`
3. **FactPurchaseOrders** (`purchase_order_id` PK)
   - `supplier_id` (FK), `product_id` (FK), `warehouse_id` (FK), `order_date` (FK -> `DimDate[date_key]`), `expected_delivery_date`, `actual_delivery_date`, `quantity_ordered`, `quantity_received`, `purchase_cost`, `order_status`

## Relationships & Cardinality

| From (Many) | To (One) | Cardinality | Cross-Filter Direction |
| :--- | :--- | :--- | :--- |
| `FactSales[product_id]` | `DimProduct[product_id]` | Many-to-One (`*:1`) | Single |
| `FactSales[warehouse_id]` | `DimWarehouse[warehouse_id]` | Many-to-One (`*:1`) | Single |
| `FactSales[sales_date]` | `DimDate[date_key]` | Many-to-One (`*:1`) | Single |
| `FactInventoryMovements[product_id]` | `DimProduct[product_id]` | Many-to-One (`*:1`) | Single |
| `FactInventoryMovements[warehouse_id]` | `DimWarehouse[warehouse_id]` | Many-to-One (`*:1`) | Single |
| `FactInventoryMovements[movement_date]` | `DimDate[date_key]` | Many-to-One (`*:1`) | Single |
| `FactPurchaseOrders[product_id]` | `DimProduct[product_id]` | Many-to-One (`*:1`) | Single |
| `FactPurchaseOrders[warehouse_id]` | `DimWarehouse[warehouse_id]` | Many-to-One (`*:1`) | Single |
| `FactPurchaseOrders[supplier_id]` | `DimSupplier[supplier_id]` | Many-to-One (`*:1`) | Single |
| `FactPurchaseOrders[order_date]` | `DimDate[date_key]` | Many-to-One (`*:1`) | Single |
| `DimProduct[supplier_id]` | `DimSupplier[supplier_id]` | Many-to-One (`*:1`) | Single (Inactive or Bridge if needed; keep `FactPurchaseOrders[supplier_id]` active) |
