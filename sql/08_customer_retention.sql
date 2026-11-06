-- Q8. How many customers come back? Repeat-purchase rate and RFM segment value.
SELECT
    ROUND(100.0 * SUM((frequency > 1)::INT) / COUNT(*), 2) AS repeat_customer_pct,
    COUNT(*)                                               AS customers
FROM customer_rfm;

SELECT
    segment,
    COUNT(*)                                                 AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)       AS customer_pct,
    ROUND(SUM(monetary), 0)                                  AS revenue,
    ROUND(100 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS revenue_pct,
    ROUND(AVG(recency_days), 0)                              AS avg_recency_days
FROM customer_rfm
GROUP BY 1
ORDER BY revenue DESC;
