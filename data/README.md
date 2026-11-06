# Data

The raw and processed CSV files are **not committed** (≈120 MB raw, licence CC BY-NC-SA 4.0).

## Get the raw data
Option A — Kaggle API: `python src/download_data.py` (see the docstring for the token setup)

Option B — manual: download the zip from
<https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce> and extract the 9 CSV files into `data/raw/`.

Expected files in `data/raw/`:

| File | Rows | Content |
|---|---:|---|
| olist_orders_dataset.csv | 99,441 | order status & timestamps |
| olist_order_items_dataset.csv | 112,650 | items per order, price, freight, seller |
| olist_order_payments_dataset.csv | 103,886 | payment type, instalments, value |
| olist_order_reviews_dataset.csv | 99,224 | review score & comments |
| olist_customers_dataset.csv | 99,441 | customer id & location |
| olist_products_dataset.csv | 32,951 | product category & dimensions |
| olist_sellers_dataset.csv | 3,095 | seller location |
| olist_geolocation_dataset.csv | 1,000,163 | zip code → lat/lng (not used) |
| product_category_name_translation.csv | 71 | Portuguese → English category |

## Build the processed tables
`python src/prepare_data.py` writes the star schema to `data/processed/`:

| Table | Grain | Key columns |
|---|---|---|
| `fact_orders` | 1 row per order | revenue/payment, delivery days, late flag, review score |
| `fact_order_items` | 1 row per item | product, seller, price, freight |
| `dim_customer` | 1 row per real customer (`customer_unique_id`) | city, state, region |
| `dim_product` | 1 row per product | English category, size/weight |
| `dim_seller` | 1 row per seller | city, state, region |
| `dim_date` | 1 row per day 2016–2018 | year, quarter, month, weekday |
| `customer_rfm` | 1 row per purchasing customer | recency, frequency, monetary, segment |
