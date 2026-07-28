-- ============================================================================
-- SQL SCRIPT 06: Regional Sales Breakdown & Shipping SLA Performance
-- Analyzes sales distribution by US State, average delivery lead times,
-- on-time delivery percentages, and correlation with customer review ratings.
-- ============================================================================

WITH DeliveryPerformance AS (
    SELECT 
        c.state,
        c.city,
        o.order_id,
        COALESCE(SUM((oi.unit_price - oi.discount_amount) * oi.quantity), 0) AS net_revenue,
        
        -- Lead time calculation in days
        JULIANDAY(o.shipping_date) - JULIANDAY(o.order_date) AS shipping_lead_days,
        JULIANDAY(o.delivery_date) - JULIANDAY(o.shipping_date) AS transit_days,
        JULIANDAY(o.delivery_date) - JULIANDAY(o.estimated_delivery) AS delay_days,
        
        CASE WHEN JULIANDAY(o.delivery_date) > JULIANDAY(o.estimated_delivery) THEN 1 ELSE 0 END AS is_delayed,
        r.review_score
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.state, c.city, o.order_id
)

SELECT 
    state,
    COUNT(DISTINCT order_id) AS total_delivered_orders,
    ROUND(SUM(net_revenue), 2) AS state_net_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_order_value,
    ROUND(AVG(shipping_lead_days), 1) AS avg_shipping_lead_days,
    ROUND(AVG(transit_days), 1) AS avg_transit_days,
    ROUND((SUM(is_delayed) * 100.0) / COUNT(order_id), 2) AS delay_rate_pct,
    ROUND(AVG(review_score), 2) AS avg_customer_rating
FROM DeliveryPerformance
GROUP BY state
ORDER BY state_net_revenue DESC;
