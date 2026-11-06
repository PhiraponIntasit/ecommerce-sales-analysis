-- Q2. How did orders and revenue grow month by month? (with month-over-month growth)
-- Note: 2016 and Sep-Oct 2018 are incomplete months in the dataset - exclude them from trend claims.
WITH monthly AS (
    SELECT
        strftime(order_date, '%Y-%m')        AS year_month,
        COUNT(*)                             AS orders,
        ROUND(SUM(product_value), 0)         AS revenue
    FROM fact_orders
    WHERE is_revenue_order
      AND order_date BETWEEN DATE '2017-01-01' AND DATE '2018-08-31'
    GROUP BY 1
)
SELECT
    year_month,
    orders,
    revenue,
    ROUND(100.0 * (revenue / LAG(revenue) OVER (ORDER BY year_month) - 1), 1) AS revenue_mom_pct
FROM monthly
ORDER BY year_month;
