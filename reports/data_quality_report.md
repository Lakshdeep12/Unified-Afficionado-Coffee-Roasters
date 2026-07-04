# Data Quality & Preprocessing Report

## 1. Dataset Overview
- **Total Transactions**: 149116
- **Initial Columns**: 11
- **Final Processed Columns**: 18

### Column Data Types:
| Column | Data Type |
| --- | --- |
| transaction_id | int64 |
| year | int64 |
| transaction_time | str |
| transaction_qty | int64 |
| store_id | int64 |
| store_location | str |
| product_id | int64 |
| unit_price | float64 |
| product_category | str |
| product_type | str |
| product_detail | str |

## 2. Integrity Checks
- **Missing Values Detected**: 0
- **Duplicate Transaction IDs**: 0
- **Invalid (Non-positive) Quantities**: 0
- **Invalid (Non-positive) Unit Prices**: 0
- **Invalid Timestamp Format (HH:MM:SS)**: 0

## 3. Date Reconstruction Analysis
- **Start Date**: 2025-01-01
- **End Date**: 2025-06-30
- **Total Unique Days Implied**: 181
- **Day Transitions Detected**: 180

## 4. Outlier Analysis (IQR Method)
| Variable | Q1 | Q3 | IQR | Lower Bound | Upper Bound | Outlier Count | Outlier % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unit_price | 2.50 | 3.75 | 1.25 | 0.62 | 5.62 | 4212 | 2.82% |
| transaction_qty | 1.00 | 2.00 | 1.00 | -0.50 | 3.50 | 36 | 0.02% |
| revenue | 3.00 | 6.00 | 3.00 | -1.50 | 10.50 | 3273 | 2.19% |

> **Note on Outliers**: While statistical outliers are present (especially bulk orders of expensive coffee beans or multiple quantity purchases), these represent valid, genuine customer transactions rather than data entry errors. Therefore, they are retained in the processed dataset to ensure full financial accuracy.

| Statistic | transaction_qty | unit_price | revenue | hour |
| --- | --- | --- | --- | --- |
| count | 149116.0000 | 149116.0000 | 149116.0000 | 149116.0000 |
| mean | 1.4383 | 3.3822 | 4.6864 | 11.7358 |
| std | 0.5425 | 2.6587 | 4.2271 | 3.7647 |
| min | 1.0000 | 0.8000 | 0.8000 | 6.0000 |
| 25% | 1.0000 | 2.5000 | 3.0000 | 9.0000 |
| 50% | 1.0000 | 3.0000 | 3.7500 | 11.0000 |
| 75% | 2.0000 | 3.7500 | 6.0000 | 15.0000 |
| max | 8.0000 | 45.0000 | 360.0000 | 20.0000 |


### Categorical Variables Overview
- **Unique Store Locations**: 3
  - Hell's Kitchen: 50735 transactions
  - Astoria: 50599 transactions
  - Lower Manhattan: 47782 transactions
- **Unique Product Categories**: 9
  - Coffee: 58416 transactions
  - Tea: 45449 transactions
  - Bakery: 22796 transactions
  - Drinking Chocolate: 11468 transactions
  - Flavours: 6790 transactions
  - ...
