"""
Clean the raw Olist CSVs and build a star schema for Power BI.

Input : data/raw/*.csv              (the 9 files from Kaggle, unchanged)
Output: data/processed/*.csv        (fact + dimension tables, ready to import)

Run:
    python src/prepare_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# Orders in these statuses never turned into a sale, so they are excluded from revenue.
NON_REVENUE_STATUSES = {"canceled", "unavailable"}

# Brazilian state -> macro-region (IBGE). Useful for a cleaner map / slicer in Power BI.
STATE_REGION = {
    "AC": "North", "AP": "North", "AM": "North", "PA": "North", "RO": "North", "RR": "North", "TO": "North",
    "AL": "Northeast", "BA": "Northeast", "CE": "Northeast", "MA": "Northeast", "PB": "Northeast",
    "PE": "Northeast", "PI": "Northeast", "RN": "Northeast", "SE": "Northeast",
    "DF": "Central-West", "GO": "Central-West", "MT": "Central-West", "MS": "Central-West",
    "ES": "Southeast", "MG": "Southeast", "RJ": "Southeast", "SP": "Southeast",
    "PR": "South", "RS": "South", "SC": "South",
}

STATE_NAME = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará",
    "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}


def read(name: str, **kw) -> pd.DataFrame:
    path = RAW / f"{name}.csv"
    if not path.exists():
        raise SystemExit(
            f"Missing {path}. Download the dataset first (see data/README.md or run src/download_data.py)."
        )
    return pd.read_csv(path, **kw)


def build_orders(orders, items, payments, reviews, customers) -> pd.DataFrame:
    """One row per order with value, delivery and satisfaction metrics."""
    ts_cols = [
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
    orders = orders.copy()
    for c in ts_cols:
        orders[c] = pd.to_datetime(orders[c])

    item_agg = items.groupby("order_id").agg(
        item_count=("order_item_id", "count"),
        product_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
        seller_count=("seller_id", "nunique"),
    )

    pay_agg = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        max_installments=("payment_installments", "max"),
    )
    # Main payment type = the one that paid the largest share of the order.
    main_pay = (
        payments.sort_values("payment_value", ascending=False)
        .drop_duplicates("order_id")
        .set_index("order_id")["payment_type"]
        .rename("main_payment_type")
    )

    # A few orders have more than one review; keep the most recent one.
    rev = (
        reviews.assign(review_answer_timestamp=pd.to_datetime(reviews["review_answer_timestamp"]))
        .sort_values("review_answer_timestamp")
        .drop_duplicates("order_id", keep="last")
        .set_index("order_id")[["review_score"]]
    )

    df = (
        orders.merge(customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left")
        .join(item_agg, on="order_id")
        .join(pay_agg, on="order_id")
        .join(main_pay, on="order_id")
        .join(rev, on="order_id")
    )

    df["order_date"] = df["order_purchase_timestamp"].dt.normalize()
    df["is_revenue_order"] = ~df["order_status"].isin(NON_REVENUE_STATUSES) & df["item_count"].notna()
    df["is_delivered"] = df["order_status"].eq("delivered") & df["order_delivered_customer_date"].notna()

    delivered = df["is_delivered"]
    df["delivery_days"] = np.where(
        delivered,
        (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400,
        np.nan,
    ).round(1)
    df["estimated_days"] = (
        (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400
    ).round(1)
    # Positive = arrived N days after the promised date.
    df["days_late"] = np.where(
        delivered,
        (df["order_delivered_customer_date"].dt.normalize() - df["order_estimated_delivery_date"]).dt.days,
        np.nan,
    )
    # 1 = late, 0 = on time, blank = not delivered (so AVERAGE() in DAX gives the late rate directly).
    df["is_late"] = pd.Series(np.where(delivered, (df["days_late"] > 0).astype(int), np.nan)).astype("Int64")
    df["days_late"] = df["days_late"].astype("Int64")

    df["purchase_hour"] = df["order_purchase_timestamp"].dt.hour
    df["purchase_weekday"] = df["order_purchase_timestamp"].dt.day_name()

    for c in ["item_count", "seller_count", "max_installments"]:
        df[c] = df[c].astype("Int64")

    cols = [
        "order_id", "customer_unique_id", "order_status", "order_date", "order_purchase_timestamp",
        "purchase_hour", "purchase_weekday", "item_count", "seller_count", "product_value",
        "freight_value", "payment_value", "main_payment_type", "max_installments", "review_score",
        "is_revenue_order", "is_delivered", "delivery_days", "estimated_days", "days_late", "is_late",
    ]
    return df[cols]


def build_order_items(items, orders_fact) -> pd.DataFrame:
    df = items.merge(
        orders_fact[["order_id", "order_date", "customer_unique_id", "is_revenue_order"]],
        on="order_id",
        how="left",
    )
    df["line_total"] = df["price"] + df["freight_value"]
    return df[
        ["order_id", "order_item_id", "product_id", "seller_id", "customer_unique_id", "order_date",
         "price", "freight_value", "line_total", "is_revenue_order"]
    ]


def build_products(products, translation) -> pd.DataFrame:
    df = products.merge(translation, on="product_category_name", how="left")
    # Two categories exist in products but are missing from the translation file.
    df["category"] = (
        df["product_category_name_english"]
        .fillna(df["product_category_name"])
        .fillna("unknown")
        .str.replace("_", " ")
        .str.title()
    )
    df = df.rename(columns={
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length",
    })
    return df[
        ["product_id", "category", "product_photos_qty", "product_weight_g",
         "product_length_cm", "product_height_cm", "product_width_cm"]
    ]


def build_customers(customers, orders_fact) -> pd.DataFrame:
    # customer_id is per-order; customer_unique_id is the real person. Use the latest known address.
    latest = (
        customers.merge(
            orders_fact[["customer_unique_id", "order_purchase_timestamp"]].drop_duplicates("customer_unique_id"),
            on="customer_unique_id", how="left",
        )
        .drop_duplicates("customer_unique_id", keep="last")
    )
    df = latest[["customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix"]].copy()
    df["customer_city"] = df["customer_city"].str.title()
    df["customer_state_name"] = df["customer_state"].map(STATE_NAME)
    df["customer_region"] = df["customer_state"].map(STATE_REGION)
    df["country"] = "Brazil"
    return df


def build_sellers(sellers) -> pd.DataFrame:
    df = sellers.copy()
    df["seller_city"] = df["seller_city"].str.title()
    df["seller_state_name"] = df["seller_state"].map(STATE_NAME)
    df["seller_region"] = df["seller_state"].map(STATE_REGION)
    return df


def build_rfm(orders_fact) -> pd.DataFrame:
    """Recency / Frequency / Monetary segmentation on revenue orders."""
    rev = orders_fact[orders_fact["is_revenue_order"]]
    snapshot = rev["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = rev.groupby("customer_unique_id").agg(
        last_order=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("payment_value", "sum"),
    )
    rfm["recency_days"] = (snapshot - rfm["last_order"]).dt.days

    # Quintile scores. ~97% of customers buy once, so frequency is scored by rule instead of quintile.
    rfm["r_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["f_score"] = np.select([rfm["frequency"] >= 3, rfm["frequency"] == 2], [5, 3], default=1)

    def segment(r):
        if r.f_score >= 3 and r.r_score >= 4:
            return "Champions"
        if r.f_score >= 3:
            return "Loyal - At Risk"
        if r.r_score >= 4 and r.m_score >= 4:
            return "New High-Value"
        if r.r_score >= 4:
            return "New / Recent"
        if r.r_score == 3:
            return "Needs Attention"
        if r.m_score >= 4:
            return "Can't Lose (High-Value, Lapsed)"
        return "Hibernating"

    rfm["segment"] = rfm.apply(segment, axis=1)
    rfm["monetary"] = rfm["monetary"].round(2)
    return rfm.reset_index().drop(columns="last_order")


def build_date(start, end) -> pd.DataFrame:
    d = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    d["year"] = d["date"].dt.year
    d["quarter"] = "Q" + d["date"].dt.quarter.astype(str)
    d["month_num"] = d["date"].dt.month
    d["month_name"] = d["date"].dt.strftime("%b")
    d["year_month"] = d["date"].dt.strftime("%Y-%m")
    d["weekday_num"] = d["date"].dt.weekday + 1
    d["weekday_name"] = d["date"].dt.strftime("%a")
    d["is_weekend"] = d["weekday_num"] >= 6
    return d


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    orders = read("olist_orders_dataset")
    items = read("olist_order_items_dataset")
    payments = read("olist_order_payments_dataset")
    reviews = read("olist_order_reviews_dataset")
    customers = read("olist_customers_dataset")
    products = read("olist_products_dataset")
    sellers = read("olist_sellers_dataset")
    translation = read("product_category_name_translation")

    fact_orders = build_orders(orders, items, payments, reviews, customers)
    fact_items = build_order_items(items, fact_orders)
    dim_product = build_products(products, translation)
    dim_customer = build_customers(customers, fact_orders)
    dim_seller = build_sellers(sellers)
    customer_rfm = build_rfm(fact_orders)
    dim_date = build_date(
        fact_orders["order_date"].min().replace(month=1, day=1),
        fact_orders["order_date"].max().replace(month=12, day=31),
    )

    tables = {
        "fact_orders": fact_orders,
        "fact_order_items": fact_items,
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_seller": dim_seller,
        "dim_date": dim_date,
        "customer_rfm": customer_rfm,
    }

    # Basic integrity checks so broken relationships are caught before Power BI.
    assert fact_orders["order_id"].is_unique
    assert dim_customer["customer_unique_id"].is_unique
    assert dim_product["product_id"].is_unique
    assert set(fact_items["product_id"]) <= set(dim_product["product_id"])
    assert set(fact_items["seller_id"]) <= set(dim_seller["seller_id"])
    assert set(fact_orders["customer_unique_id"]) <= set(dim_customer["customer_unique_id"])

    # Write pure dates (no 00:00:00) so Power BI detects them as Date type.
    for df, col in [(fact_orders, "order_date"), (fact_items, "order_date"), (dim_date, "date")]:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    for name, df in tables.items():
        path = OUT / f"{name}.csv"
        df.to_csv(path, index=False, date_format="%Y-%m-%d %H:%M:%S")
        print(f"{name:<18} {len(df):>8,} rows  -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
