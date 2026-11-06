-- Q4. Which product categories drive revenue? (Pareto / 80-20 analysis)
WITH cat AS (
    SELECT p.category,
           SUM(i.price)               AS revenue,
           COUNT(*)                   AS items_sold,
           AVG(i.price)               AS avg_price
    FROM fact_order_items i
    JOIN dim_product p USING (product_id)
    WHERE i.is_revenue_order
    GROUP BY 1
)
SELECT
    ROW_NUMBER() OVER (ORDER BY revenue DESC)                        AS rank,
    category,
    ROUND(revenue, 0)                                                AS revenue,
    items_sold,
    ROUND(avg_price, 2)                                              AS avg_price,
    ROUND(100 * revenue / SUM(revenue) OVER (), 2)                   AS revenue_share_pct,
    ROUND(100 * SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER (), 1) AS cumulative_pct
FROM cat
ORDER BY revenue DESC
LIMIT 20;
