-- ============================================================================
-- SQL SCRIPT 03: Product Performance, Category Profitability & Inventory Health
-- Analyzes best/worst sellers, high margin products, and slow-moving inventory.
-- ============================================================================

WITH ProductSales AS (
    SELECT 
        p.product_id,
        p.product_name,
        c.category_name,
        c.department,
        p.price AS unit_list_price,
        p.cost AS unit_cost,
        p.stock_quantity AS current_stock,
        COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
        COALESCE(SUM((oi.unit_price - oi.discount_amount) * oi.quantity), 0) AS net_revenue,
        COALESCE(SUM((oi.unit_price - oi.discount_amount - p.cost) * oi.quantity), 0) AS net_profit
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status != 'Cancelled'
    GROUP BY p.product_id, p.product_name, c.category_name, c.department, p.price, p.cost, p.stock_quantity
)

SELECT 
    product_id,
    product_name,
    category_name,
    department,
    current_stock,
    total_units_sold,
    ROUND(net_revenue, 2) AS net_revenue,
    ROUND(net_profit, 2) AS net_profit,
    ROUND((net_profit / NULLIF(net_revenue, 0)) * 100, 2) AS profit_margin_pct,
    
    -- Stock Health Flag: High Stock with low 90-day sales velocity
    CASE 
        WHEN current_stock > 150 AND total_units_sold < 20 THEN 'Slow-Moving / Overstocked'
        WHEN current_stock < 15 THEN 'Low Stock Alert'
        ELSE 'Healthy Stock'
    END AS inventory_status,
    
    DENSE_RANK() OVER (ORDER BY net_revenue DESC) AS revenue_rank
FROM ProductSales
ORDER BY net_revenue DESC;
