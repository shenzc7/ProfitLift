# Data Format Specification

ProfitLift expects a CSV file with the following columns.

## Required Columns

| Column Name | Type | Description |
|-------------|------|-------------|
| `transaction_id` | String/Int | Unique ID for the shopping basket. |
| `timestamp` | String | Date/Time (ISO 8601 preferred, e.g., `2023-01-01 14:30:00`). |
| `store_id` | String | Identifier for the store. |
| `item_id` | String | Identifier for the product. |
| `price` | Float | Price paid for the item. |

## Optional Columns

| Column Name | Type | Default | Description |
|-------------|------|---------|-------------|
| `margin_pct` | Float | 0.25 | Profit margin (0.0 to 1.0). |
| `quantity` | Int | 1 | Number of units purchased. |
| `customer_id_hash` | String | - | Hashed customer ID for loyalty analysis. |
| `category` | String | - | Product category hierarchy. |

## Example CSV

```csv
transaction_id,timestamp,store_id,item_id,price,margin_pct
1001,2023-10-25 08:30:00,STORE_1,MILK_2L,2.50,0.20
1001,2023-10-25 08:30:00,STORE_1,BREAD_WHT,1.80,0.35
1002,2023-10-25 09:15:00,STORE_1,COFFEE_BEAN,12.00,0.40
```
