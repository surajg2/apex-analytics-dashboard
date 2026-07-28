-- ============================================================================
-- SQL SCRIPT 04: Sales Trends & MoM Growth Analysis
-- Uses LAG() window function to calculate Month-over-Month (MoM) revenue growth
-- and order volume trajectory across the dataset timeline.
-- ============================================================================

WITH MonthlySales AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_date) AS sales_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS active_customers,
        COALESCE(SUM((oi.unit_price - oi.discount_amount) * oi.quantity), 0) AS net_revenue,
        COALESCE(SUM((oi.unit_price - oi.discount_amount - p.cost) * oi.quantity), 0) AS total_profit
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY STRFTIME('%Y-%m', o.order_date)
),

SalesWithLag AS (
    SELECT 
        sales_month,
        total_orders,
        active_customers,
        ROUND(net_revenue, 2) AS net_revenue,
        ROUND(total_profit, 2) AS total_profit,
        ROUND(net_revenue / NULLIF(total_orders, 0), 2) AS avg_order_value,
        LAG(net_revenue, 1) OVER (ORDER BY sales_month ASC) AS prev_month_revenue
    FROM MonthlySales
)

SELECT 
    sales_month,
    total_orders,
    active_customers,
    net_revenue,
    total_profit,
    avg_order_value,
    COALESCE(prev_month_revenue, 0) AS prev_month_revenue,
    ROUND(((net_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0)) * 100, 2) AS mom_growth_pct
FROM SalesWithLag
ORDER BY sales_month ASC;
