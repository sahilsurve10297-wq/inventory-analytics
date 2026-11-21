# Power BI DAX Measures Library

All 19 core measures follow the exact KPI definitions used in Python, SQL, and Excel.

```dax
// 1. Total Stock Quantity (reconciled from movements up to max selected date)
Total Stock Quantity =
VAR MaxDate = MAX(DimDate[date_key])
RETURN
CALCULATE(
    SUMX(
        FactInventoryMovements,
        SWITCH(
            FactInventoryMovements[movement_type],
            "Purchase", FactInventoryMovements[quantity],
            "Return", FactInventoryMovements[quantity],
            "Transfer In", FactInventoryMovements[quantity],
            "Adjustment", FactInventoryMovements[quantity],
            "Sale", -FactInventoryMovements[quantity],
            "Transfer Out", -FactInventoryMovements[quantity],
            0
        )
    ),
    FILTER(ALL(DimDate), DimDate[date_key] <= MaxDate)
)

// 2. Total Inventory Value
Total Inventory Value =
SUMX(
    DimProduct,
    VAR Qty = [Total Stock Quantity]
    RETURN MAX(0, Qty) * DimProduct[unit_cost]
)

// 3. Total Products
Total Products = DISTINCTCOUNT(DimProduct[product_id])

// 4. Total Revenue
Total Revenue = SUM(FactSales[total_revenue])

// 5. Total Profit
Total Profit = SUM(FactSales[profit])

// 6. Total COGS
Total COGS =
SUMX(
    FactSales,
    FactSales[quantity_sold] * RELATED(DimProduct[unit_cost])
)

// 7. Average Inventory
Average Inventory =
VAR EndVal = [Total Inventory Value]
VAR StartVal =
    CALCULATE(
        [Total Inventory Value],
        DATEADD(DimDate[date_key], -365, DAY)
    )
RETURN DIVIDE(EndVal + COALESCE(StartVal, EndVal), 2, EndVal)

// 8. Inventory Turnover
Inventory Turnover =
DIVIDE([Total COGS], [Average Inventory], 0)

// 9. Days Inventory Outstanding
Days Inventory Outstanding =
VAR DaysInPeriod = DATEDIFF(MIN(DimDate[date_key]), MAX(DimDate[date_key]), DAY) + 1
RETURN DIVIDE([Average Inventory], [Total COGS], 0) * DaysInPeriod

// 10. Stockout Rate (%)
Stockout Rate =
VAR TotalPairs = COUNTROWS(CROSSJOIN(VALUES(DimProduct[product_id]), VALUES(DimWarehouse[warehouse_id])))
VAR ZeroPairs =
    COUNTROWS(
        FILTER(
            CROSSJOIN(VALUES(DimProduct[product_id]), VALUES(DimWarehouse[warehouse_id])),
            [Total Stock Quantity] <= 0
        )
    )
RETURN DIVIDE(ZeroPairs, TotalPairs, 0)

// 11. Overstock Rate (%)
Overstock Rate =
VAR OverstockedCount =
    COUNTROWS(
        FILTER(
            VALUES(DimProduct[product_id]),
            [Total Stock Quantity] > SELECTEDVALUE(DimProduct[reorder_level]) * 2.5
        )
    )
RETURN DIVIDE(OverstockedCount, [Total Products], 0)

// 12. Dead Stock Value (0 sales in last 180 days)
Dead Stock Value =
VAR MaxDate = MAX(DimDate[date_key])
RETURN
SUMX(
    VALUES(DimProduct[product_id]),
    VAR RecentSales =
        CALCULATE(
            SUM(FactSales[quantity_sold]),
            DATESINPERIOD(DimDate[date_key], MaxDate, -180, DAY)
        )
    RETURN IF(COALESCE(RecentSales, 0) = 0, [Total Inventory Value], 0)
)

// 13. Slow-Moving Inventory Value (<= 5 units sold in last 90 days)
Slow-Moving Inventory Value =
VAR MaxDate = MAX(DimDate[date_key])
RETURN
SUMX(
    VALUES(DimProduct[product_id]),
    VAR Sales90 =
        CALCULATE(
            SUM(FactSales[quantity_sold]),
            DATESINPERIOD(DimDate[date_key], MaxDate, -90, DAY)
        )
    RETURN IF(COALESCE(Sales90, 0) <= 5, [Total Inventory Value], 0)
)

// 14. Reorder Required Products
Reorder Required Products =
COUNTROWS(
    FILTER(
        VALUES(DimProduct[product_id]),
        [Total Stock Quantity] <= CALCULATE(MAX(DimProduct[reorder_level]))
    )
)

// 15. Supplier On-Time Delivery Rate
Supplier On-Time Delivery Rate =
VAR DeliveredPOs =
    CALCULATE(
        COUNTROWS(FactPurchaseOrders),
        FactPurchaseOrders[order_status] IN {"Delivered", "Partial"}
    )
VAR OnTimePOs =
    CALCULATE(
        COUNTROWS(FactPurchaseOrders),
        FactPurchaseOrders[order_status] IN {"Delivered", "Partial"},
        FactPurchaseOrders[actual_delivery_date] <= FactPurchaseOrders[expected_delivery_date]
    )
RETURN DIVIDE(OnTimePOs, DeliveredPOs, 0)

// 16. Warehouse Capacity Utilization
Warehouse Capacity Utilization =
DIVIDE([Total Stock Quantity], SUM(DimWarehouse[warehouse_capacity]), 0)

// 17. Previous Month Revenue
Previous Month Revenue =
CALCULATE([Total Revenue], DATEADD(DimDate[date_key], -1, MONTH))

// 18. Monthly Sales Growth (%)
Monthly Sales Growth =
VAR Prev = [Previous Month Revenue]
RETURN DIVIDE([Total Revenue] - Prev, Prev, 0)

// 19. Year-to-Date Sales
Year-to-Date Sales =
TOTALYTD([Total Revenue], DimDate[date_key])
```
