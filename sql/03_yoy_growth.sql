-- Q3. Year-over-year growth on a like-for-like window (Jan-Aug 2017 vs Jan-Aug 2018).
SELECT
    YEAR(order_date)                    AS year,
    COUNT(*)                            AS orders,
    ROUND(SUM(product_value), 0)        AS revenue,
    ROUND(AVG(payment_value), 2)        AS avg_order_value
FROM fact_orders
WHERE is_revenue_order
  AND MONTH(order_date) BETWEEN 1 AND 8
  AND YEAR(order_date) IN (2017, 2018)
GROUP BY 1
ORDER BY 1;
