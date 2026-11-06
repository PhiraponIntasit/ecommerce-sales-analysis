-- Q6. Does late delivery hurt customer satisfaction?
SELECT
    CASE
        WHEN days_late <= -10 THEN '1. 10+ days early'
        WHEN days_late <=   0 THEN '2. 0-9 days early'
        WHEN days_late <=   3 THEN '3. 1-3 days late'
        WHEN days_late <=   7 THEN '4. 4-7 days late'
        ELSE                       '5. 8+ days late'
    END                                                AS delivery_bucket,
    COUNT(*)                                           AS orders,
    ROUND(AVG(review_score), 2)                        AS avg_review,
    ROUND(100 * AVG((review_score <= 2)::INT), 1)      AS negative_review_pct
FROM fact_orders
WHERE is_delivered AND review_score IS NOT NULL
GROUP BY 1
ORDER BY 1;
