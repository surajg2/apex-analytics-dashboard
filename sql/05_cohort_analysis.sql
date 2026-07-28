-- ============================================================================
-- SQL SCRIPT 05: Customer Cohort Acquisition & Retention Matrix
-- Groups customers by signup cohort month and tracks repeat purchasing activity over time.
-- ============================================================================

WITH CustomerCohorts AS (
    SELECT 
        customer_id,
        STRFTIME('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE order_status != 'Cancelled'
    GROUP BY customer_id
),

OrderActivities AS (
    SELECT 
        o.customer_id,
        c.cohort_month,
        STRFTIME('%Y-%m', o.order_date) AS order_month,
        (CAST(STRFTIME('%Y', o.order_date) AS INT) - CAST(STRFTIME('%Y', c.cohort_month || '-01') AS INT)) * 12 +
        (CAST(STRFTIME('%m', o.order_date) AS INT) - CAST(STRFTIME('%m', c.cohort_month || '-01') AS INT)) AS month_number
    FROM orders o
    JOIN CustomerCohorts c ON o.customer_id = c.customer_id
    WHERE o.order_status != 'Cancelled'
),

CohortSizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_customers
    FROM CustomerCohorts
    GROUP BY cohort_month
)

SELECT 
    a.cohort_month,
    s.total_cohort_customers,
    a.month_number AS months_since_acquisition,
    COUNT(DISTINCT a.customer_id) AS active_retained_customers,
    ROUND((COUNT(DISTINCT a.customer_id) * 100.0) / s.total_cohort_customers, 2) AS retention_rate_pct
FROM OrderActivities a
JOIN CohortSizes s ON a.cohort_month = s.cohort_month
GROUP BY a.cohort_month, s.total_cohort_customers, a.month_number
ORDER BY a.cohort_month ASC, a.month_number ASC;
