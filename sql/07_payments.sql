-- Q7. How do customers pay, and does payment method relate to basket size?
SELECT
    main_payment_type,
    COUNT(*)                                            AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS share_pct,
    ROUND(AVG(payment_value), 2)                        AS avg_order_value,
    ROUND(AVG(max_installments), 1)                     AS avg_installments
FROM fact_orders
WHERE is_revenue_order AND main_payment_type IS NOT NULL
GROUP BY 1
ORDER BY orders DESC;
