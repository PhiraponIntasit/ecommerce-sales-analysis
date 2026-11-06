-- Q1. What are the headline KPIs of the business?
-- Revenue = item price of orders that were not canceled / unavailable (freight excluded).
SELECT
    COUNT(*)                                                     AS total_orders,
    SUM(is_revenue_order::INT)                                   AS revenue_orders,
    ROUND(SUM(CASE WHEN is_revenue_order THEN product_value END), 0) AS revenue_brl,
    ROUND(AVG(CASE WHEN is_revenue_order THEN payment_value END), 2) AS avg_order_value_brl,
    COUNT(DISTINCT customer_unique_id)                           AS customers,
    ROUND(AVG(review_score), 2)                                  AS avg_review_score,
    ROUND(100 * AVG(is_late), 1)                                 AS late_delivery_pct,
    ROUND(MEDIAN(delivery_days), 1)                              AS median_delivery_days
FROM fact_orders;
