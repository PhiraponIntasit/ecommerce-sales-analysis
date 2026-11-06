-- Q5. Where are customers, and how does delivery performance differ by state?
SELECT
    c.customer_state                                       AS state,
    c.customer_region                                      AS region,
    COUNT(*)                                               AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)     AS order_share_pct,
    ROUND(SUM(o.product_value), 0)                         AS revenue,
    ROUND(AVG(o.delivery_days), 1)                         AS avg_delivery_days,
    ROUND(100 * AVG(o.is_late), 1)                         AS late_pct,
    ROUND(100 * SUM(o.freight_value) / SUM(o.product_value), 1) AS freight_to_price_pct,
    ROUND(AVG(o.review_score), 2)                          AS avg_review
FROM fact_orders o
JOIN dim_customer c USING (customer_unique_id)
WHERE o.is_revenue_order
GROUP BY 1, 2
ORDER BY orders DESC;
