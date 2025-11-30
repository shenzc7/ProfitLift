# How to Get Data

ProfitLift works best with transactional data. You can use public datasets for testing.

## Instacart Dataset
1. Go to [Instacart Market Basket Analysis](https://www.kaggle.com/c/instacart-market-basket-analysis/data).
2. Download `order_products__prior.csv` and `orders.csv`.
3. Merge them to create a format with `order_id`, `product_id`, and `order_dow` (day of week).

## Dunnhumby Dataset
1. Go to [Dunnhumby - The Complete Journey](https://www.kaggle.com/frtgnn/dunnhumby-the-complete-journey).
2. Download `transaction_data.csv`.
3. Rename columns to match ProfitLift requirements (see `DATA_FORMAT.md`).

## Your Own Data
Export a CSV from your POS (Point of Sale) system. Ensure it is transaction-level (one row per item in a basket).
