-- ============================================================================
-- SQL SCRIPT 02: Advanced Customer Analytics & CLV Ranking
-- Performs SQL Window Functions (NTILE, DENSE_RANK, SUM OVER) to segment
-- high-value customers, calculate customer lifetime value, and RFM scores.
-- ============================================================================

WITH CustomerAggregates AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email,
        c.state,
        c.segment AS customer_segment,
        c.signup_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(SUM((oi.unit_price - oi.discount_amount) * oi.quantity), 0) AS total_lifetime_spend,
        MAX(o.order_date) AS last_order_date,
        MIN(o.order_date) AS first_order_date
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status != 'Cancelled'
    GROUP BY c.customer_id
),

RFM_Scoring AS (
    SELECT 
        customer_id,
        customer_name,
        email,
        state,
        customer_segment,
        total_orders,
        ROUND(total_lifetime_spend, 2) AS total_lifetime_spend,
        ROUND(total_lifetime_spend / NULLIF(total_orders, 0), 2) AS avg_order_value,
        CAST((JULIANDAY('now') - JULIANDAY(last_order_date)) AS INTEGER) AS recency_days,
        
        -- Window functions for quantile scoring (1 to 5)
        NTILE(5) OVER (ORDER BY last_order_date ASC) AS r_score,
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY total_lifetime_spend ASC) AS m_score,
        
        DENSE_RANK() OVER (ORDER BY total_lifetime_spend DESC) AS spend_rank
    FROM CustomerAggregates
)

SELECT 
    spend_rank,
    customer_id,
    customer_name,
    customer_segment,
    state,
    total_orders,
    total_lifetime_spend,
    avg_order_value,
    recency_days,
    r_score,
    f_score,
    m_score,
    (r_score || f_score || m_score) AS rfm_cell,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating / Lost'
        ELSE 'General Customers'
    END AS customer_tier
FROM RFM_Scoring
ORDER BY spend_rank ASC
LIMIT 100;
