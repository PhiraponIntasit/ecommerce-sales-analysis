-- Q10. When do customers shop? (weekday x hour heatmap source)
SELECT
    purchase_weekday,
    purchase_hour,
    COUNT(*) AS orders
FROM fact_orders
GROUP BY 1, 2
ORDER BY 1, 2;
