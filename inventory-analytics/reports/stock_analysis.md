# Stock Health, Warehouse & Replenishment Analysis

## Stock Health Classification Summary

| Stock Status | SKU Count | % of SKUs | Total Units | Inventory Value ($) |
| :--- | ---: | ---: | ---: | ---: |
| **Critical Stock** | 7 | 1.4% | 79 | $7,838.90 |
| **Low Stock** | 100 | 20.0% | 6,304 | $594,551.52 |
| **Healthy Stock** | 109 | 21.8% | 12,746 | $1,212,508.76 |
| **Overstocked** | 250 | 50.0% | 60,650 | $5,187,237.91 |
| **Dead Stock** | 34 | 6.8% | 14,644 | $1,400,886.85 |
| **Total** | **500** | **100.0%** | **94,423** | **$8,403,023.94** |

## Warehouse Performance Breakdown

| Warehouse | City | Capacity | Stock Units | Utilization % | Inventory Value | Total Revenue | Stockout SKUs |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Southern Distribution (WH-004)** | Dallas | 95,000 | 19,885 | 20.93% | $1,763,756.26 | $4,948,083.09 | 50 |
| **North Central Fulfillment (WH-001)** | Chicago | 120,000 | 19,151 | 15.96% | $1,707,526.38 | $7,985,497.65 | 97 |
| **West Coast Gateway (WH-003)** | Ontario | 110,000 | 19,444 | 17.68% | $1,705,872.27 | $7,187,743.11 | 72 |
| **East Coast Mega Hub (WH-002)** | Newark | 145,000 | 18,761 | 12.94% | $1,686,648.47 | $8,834,561.49 | 95 |
| **Southeast Regional Depot (WH-005)** | Atlanta | 85,000 | 17,182 | 20.21% | $1,539,220.56 | $2,994,245.63 | 36 |

## Forecasting Limitations
Baseline statistical methods (SMA-3, WMA-3, SES) capture recent level and short-term momentum without future data leakage, but do not model external promotions, sudden supplier disruptions, or multi-year holiday spikes when history is sparse. Forecasts should be paired with safety stock buffers and human planner review.
