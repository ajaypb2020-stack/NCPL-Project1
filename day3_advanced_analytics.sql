-- Day 3 advanced analytics queries for SQL Server
-- Assumptions: RFM snapshot date = 2025-10-31; frequency = distinct purchase dates.
-- A missing customer_id is excluded from customer-level RFM, cohorts, and product pairs.

-- 1. RFM scores and segments for all identifiable customers
WITH customer_rfm AS (
    SELECT customer_id,
        DATEDIFF(DAY, MAX([date]), CAST('2025-10-31' AS date)) AS recency_days,
        COUNT(DISTINCT [date]) AS frequency,
           SUM(total_value) AS monetary
    FROM bm_sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
), scored AS (
    SELECT customer_id, recency_days, frequency, monetary,
           6 - NTILE(5) OVER (ORDER BY recency_days) AS recency_score,
           NTILE(5) OVER (ORDER BY frequency) AS frequency_score,
           NTILE(5) OVER (ORDER BY monetary) AS monetary_score
    FROM customer_rfm
)
SELECT customer_id, recency_days, frequency, ROUND(monetary, 2) AS monetary,
       recency_score, frequency_score, monetary_score,
       CASE WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
            WHEN frequency_score >= 4 AND monetary_score >= 3 THEN 'Loyal'
            WHEN recency_score <= 2 AND (frequency_score >= 3 OR monetary_score >= 3) THEN 'At Risk'
            ELSE 'Lost' END AS rfm_segment
FROM scored
ORDER BY rfm_segment, monetary DESC;

-- 2. Cohort retention by customer signup month and months since signup
WITH customer_activity AS (
    SELECT c.cust_id AS customer_id,
            DATEFROMPARTS(YEAR(c.registration_date), MONTH(c.registration_date), 1) AS cohort_month,
            DATEFROMPARTS(YEAR(s.[date]), MONTH(s.[date]), 1) AS activity_month
    FROM bm_customers AS c
    JOIN bm_sales AS s ON s.customer_id = c.cust_id
                AND s.[date] >= c.registration_date
    GROUP BY c.cust_id, cohort_month, activity_month
), cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_customers
    FROM customer_activity
    GROUP BY cohort_month
)
SELECT ca.cohort_month, ca.activity_month,
    DATEDIFF(MONTH, ca.cohort_month, ca.activity_month) AS months_since_signup,
       cs.cohort_customers, COUNT(DISTINCT ca.customer_id) AS active_customers,
    ROUND(100.0 * COUNT(DISTINCT ca.customer_id) / cs.cohort_customers, 2) AS retention_pct
FROM customer_activity AS ca
JOIN cohort_sizes AS cs ON cs.cohort_month = ca.cohort_month
GROUP BY ca.cohort_month, ca.activity_month, DATEDIFF(MONTH, ca.cohort_month, ca.activity_month), cs.cohort_customers
ORDER BY ca.cohort_month, months_since_signup;

-- 3. Top product pairs bought together on the same customer purchase date
SELECT s1.sku_id AS sku_id_1, p1.sku_name AS product_1,
       s2.sku_id AS sku_id_2, p2.sku_name AS product_2,
    COUNT(DISTINCT CONCAT(CAST(s1.customer_id AS varchar(20)), '|', CONVERT(varchar(10), s1.[date], 23))) AS purchase_occasions,
       COUNT(DISTINCT s1.customer_id) AS customers
FROM bm_sales AS s1
JOIN bm_sales AS s2
  ON s2.customer_id = s1.customer_id
 AND s2.[date] = s1.[date]
 AND s2.sku_id > s1.sku_id
JOIN bm_skus AS p1 ON p1.sku_id = s1.sku_id
JOIN bm_skus AS p2 ON p2.sku_id = s2.sku_id
WHERE s1.customer_id IS NOT NULL
GROUP BY s1.sku_id, p1.sku_name, s2.sku_id, p2.sku_name
ORDER BY purchase_occasions DESC, customers DESC
OFFSET 0 ROWS FETCH NEXT 50 ROWS ONLY;

-- 4. Revenue growth year over year
WITH yearly_revenue AS (
    SELECT YEAR([date]) AS revenue_year, SUM(total_value) AS revenue
    FROM bm_sales
    GROUP BY YEAR([date])
)
SELECT revenue_year, ROUND(revenue, 2) AS revenue,
       ROUND(LAG(revenue) OVER (ORDER BY revenue_year), 2) AS prior_year_revenue,
       ROUND(100 * (revenue - LAG(revenue) OVER (ORDER BY revenue_year)) /
             NULLIF(LAG(revenue) OVER (ORDER BY revenue_year), 0), 2) AS yoy_growth_pct
FROM yearly_revenue
ORDER BY revenue_year;

-- 5. Monthly revenue with running total
WITH monthly_revenue AS (
    SELECT DATEFROMPARTS(YEAR([date]), MONTH([date]), 1) AS revenue_month,
           SUM(total_value) AS monthly_revenue
    FROM bm_sales
    GROUP BY DATEFROMPARTS(YEAR([date]), MONTH([date]), 1)
)
SELECT revenue_month, ROUND(monthly_revenue, 2) AS monthly_revenue,
       ROUND(SUM(monthly_revenue) OVER (ORDER BY revenue_month
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_revenue
FROM monthly_revenue
ORDER BY revenue_month;