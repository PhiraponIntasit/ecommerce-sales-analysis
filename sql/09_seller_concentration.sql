-- Q9. How concentrated is revenue among sellers?
WITH s AS (
    SELECT seller_id, SUM(price) AS revenue
    FROM fact_order_items
    WHERE is_revenue_order
    GROUP BY 1
), ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY revenue DESC)                     AS rn,
           COUNT(*) OVER ()                                              AS n_sellers,
           SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER () AS cum_share
    FROM s
)
SELECT
    MIN(rn)                                   AS sellers_for_80pct_revenue,
    MAX(n_sellers)                            AS total_sellers,
    ROUND(100.0 * MIN(rn) / MAX(n_sellers), 1) AS pct_of_sellers
FROM ranked
WHERE cum_share >= 0.8;
