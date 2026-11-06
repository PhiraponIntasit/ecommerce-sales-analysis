-- Register the processed CSVs as views (DuckDB).
-- Run from the project root:  python src/run_sql.py
CREATE OR REPLACE VIEW fact_orders      AS SELECT * FROM read_csv_auto('data/processed/fact_orders.csv');
CREATE OR REPLACE VIEW fact_order_items AS SELECT * FROM read_csv_auto('data/processed/fact_order_items.csv');
CREATE OR REPLACE VIEW dim_customer     AS SELECT * FROM read_csv_auto('data/processed/dim_customer.csv');
CREATE OR REPLACE VIEW dim_product      AS SELECT * FROM read_csv_auto('data/processed/dim_product.csv');
CREATE OR REPLACE VIEW dim_seller       AS SELECT * FROM read_csv_auto('data/processed/dim_seller.csv');
CREATE OR REPLACE VIEW customer_rfm     AS SELECT * FROM read_csv_auto('data/processed/customer_rfm.csv');
