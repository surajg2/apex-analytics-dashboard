-- ============================================================================
-- SQL SCRIPT 01: KPI Overview & Executive Summary Metrics
-- Calculates Core Business KPIs: Gross Sales, Net Sales, AOV, Order Count,
-- Profit Margin, Repeat Customer Rate, Return/Refund Rate.
-- ============================================================================

WITH OrderMetrics AS (
    SELECT 
        o.order_id,
        o.customer_id,
        o.order_status,
        COALESCE(SUM((oi.unit_price - oi.discount_amount) * oi.quantity), 0) AS net_revenue,
        COALESCE(SUM(oi.unit_price * oi.quantity), 0) AS gross_revenue,
        COALESCE(SUM(oi.discount_amount * oi.quantity), 0) AS total_discount,
        COALESCE(SUM((oi.unit_price - oi.discount_amount - p.cost) * oi.quantity), 0) AS total_profit
    FROM orders o
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id, o.customer_id, o.order_status
),

CustomerOrders AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    WHERE order_status != 'Cancelled'
    GROUP BY customer_id
)

SELECT 
    -- 1. Financial KPIs
    ROUND(SUM(CASE WHEN order_status != 'Cancelled' THEN net_revenue ELSE 0 END), 2) AS total_net_revenue,
    ROUND(SUM(CASE WHEN order_status != 'Cancelled' THEN gross_revenue ELSE 0 END), 2) AS total_gross_revenue,
    ROUND(SUM(CASE WHEN order_status != 'Cancelled' THEN total_profit ELSE 0 END), 2) AS total_net_profit,
    ROUND((SUM(CASE WHEN order_status != 'Cancelled' THEN total_profit ELSE 0 END) / 
           NULLIF(SUM(CASE WHEN order_status != 'Cancelled' THEN net_revenue ELSE 0 END), 0)) * 100, 2) AS profit_margin_percentage,
    
    -- 2. Volume KPIs
    COUNT(DISTINCT CASE WHEN order_status != 'Cancelled' THEN order_id END) AS total_completed_orders,
    COUNT(DISTINCT customer_id) AS total_active_customers,
    
    -- 3. AOV & Order Performance
    ROUND(SUM(CASE WHEN order_status != 'Cancelled' THEN net_revenue ELSE 0 END) / 
          NULLIF(COUNT(DISTINCT CASE WHEN order_status != 'Cancelled' THEN order_id END), 0), 2) AS average_order_value_aov,

    -- 4. Repeat Customer Rate
    ROUND((COUNT(DISTINCT CASE WHEN co.order_count > 1 THEN co.customer_id END) * 100.0) / 
          NULLIF(COUNT(DISTINCT co.customer_id), 0), 2) AS repeat_customer_rate_pct,

    -- 5. Cancellation / Refund Rate
    ROUND((COUNT(DISTINCT CASE WHEN order_status = 'Cancelled' THEN order_id END) * 100.0) / 
          NULLIF(COUNT(DISTINCT order_id), 0), 2) AS cancellation_rate_pct

FROM OrderMetrics om
LEFT JOIN CustomerOrders co ON om.customer_id = co.customer_id;
