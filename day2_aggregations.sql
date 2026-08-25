-- Day 2 retail analysis queries for SQL Server
-- Assumptions: region = bm_stores.city; revenue = SUM(bm_sales.total_value).
-- Promotions are identified by bm_sales.discount_pct > 0 because sales has no promo_id.

-- 1. Revenue by region and store type
SELECT st.city AS region, st.store_type,
       ROUND(SUM(sa.total_value), 2) AS revenue
FROM bm_sales AS sa
JOIN bm_stores AS st ON st.store_id = sa.store_id
GROUP BY st.city, st.store_type
ORDER BY st.city, revenue DESC;

-- 2. Top 5 product categories by revenue
SELECT sk.category,
       ROUND(SUM(sa.total_value), 2) AS revenue
FROM bm_sales AS sa
JOIN bm_skus AS sk ON sk.sku_id = sa.sku_id
GROUP BY sk.category
ORDER BY revenue DESC
OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY;

-- 3. Customer spend tiers: High = top third, Low = bottom third, Medium = middle third
WITH customer_spend AS (
    SELECT customer_id, SUM(total_value) AS total_spend
    FROM bm_sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
), ranked_spend AS (
    SELECT customer_id, total_spend,
           NTILE(3) OVER (ORDER BY total_spend) AS spend_third
    FROM customer_spend
)
SELECT customer_id, ROUND(total_spend, 2) AS total_spend,
       CASE WHEN spend_third = 3 THEN 'High'
            WHEN spend_third = 1 THEN 'Low'
            ELSE 'Medium' END AS spend_tier
FROM ranked_spend
ORDER BY total_spend DESC;

-- 4. Promotion comparison: discounted versus non-discounted sales
SELECT CASE WHEN discount_pct > 0 THEN 'Promotion' ELSE 'No promotion' END AS promotion_status,
       COUNT(*) AS sales_lines,
       SUM(quantity) AS units,
       ROUND(SUM(total_value), 2) AS revenue,
       ROUND(AVG(total_value), 2) AS average_line_value
FROM bm_sales
GROUP BY promotion_status
ORDER BY promotion_status;

-- 5. Customers whose total spend is above the overall average customer spend
WITH customer_spend AS (
    SELECT customer_id, SUM(total_value) AS total_spend
    FROM bm_sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT customer_id, ROUND(total_spend, 2) AS total_spend,
       ROUND((SELECT AVG(total_spend) FROM customer_spend), 2) AS average_customer_spend
FROM customer_spend
WHERE total_spend > (SELECT AVG(total_spend) FROM customer_spend)
ORDER BY total_spend DESC;

-- 6. Products with falling month-over-month sales (latest month versus prior month)
WITH monthly_product_sales AS (
    SELECT sku_id, DATEFROMPARTS(YEAR([date]), MONTH([date]), 1) AS sales_month,
           SUM(quantity) AS units, SUM(total_value) AS revenue
    FROM bm_sales
    GROUP BY sku_id, DATEFROMPARTS(YEAR([date]), MONTH([date]), 1)
), latest_two_months AS (
    SELECT sku_id, sales_month, units, revenue,
           LAG(units) OVER (PARTITION BY sku_id ORDER BY sales_month) AS prior_units,
           LAG(revenue) OVER (PARTITION BY sku_id ORDER BY sales_month) AS prior_revenue,
           ROW_NUMBER() OVER (PARTITION BY sku_id ORDER BY sales_month DESC) AS month_rank
    FROM monthly_product_sales
)
SELECT p.sku_id, sk.sku_name, sk.category, p.sales_month AS latest_month,
       p.units AS latest_units, p.prior_units,
       ROUND(p.revenue, 2) AS latest_revenue, ROUND(p.prior_revenue, 2) AS prior_revenue,
       ROUND(100 * (p.units - p.prior_units) / NULLIF(p.prior_units, 0), 2) AS unit_change_pct
FROM latest_two_months AS p
JOIN bm_skus AS sk ON sk.sku_id = p.sku_id
WHERE p.month_rank = 1 AND p.prior_units IS NOT NULL AND p.units < p.prior_units
ORDER BY unit_change_pct, p.sku_id;

-- 7. Rank stores within each region by revenue
WITH store_revenue AS (
    SELECT st.city AS region, st.store_id, st.store_name, st.store_type,
           SUM(sa.total_value) AS revenue
    FROM bm_sales AS sa
    JOIN bm_stores AS st ON st.store_id = sa.store_id
    GROUP BY st.city, st.store_id, st.store_name, st.store_type
)
SELECT region, store_id, store_name, store_type, ROUND(revenue, 2) AS revenue,
       DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS region_rank
FROM store_revenue
ORDER BY region, region_rank, store_id;

-- 8. Data quality checks: nulls, invalid values, and referential integrity
SELECT 'bm_sales' AS table_name, 'customer_id' AS field_name,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS issue_count, 'nullable customer ID' AS check_description
FROM bm_sales
UNION ALL
SELECT 'bm_sales', 'quantity', SUM(CASE WHEN quantity IS NULL OR quantity <= 0 THEN 1 ELSE 0 END), 'must be positive'
FROM bm_sales
UNION ALL
SELECT 'bm_sales', 'unit_price', SUM(CASE WHEN unit_price IS NULL OR unit_price < 0 THEN 1 ELSE 0 END), 'must be non-negative'
FROM bm_sales
UNION ALL
SELECT 'bm_sales', 'total_value', SUM(CASE WHEN total_value IS NULL OR total_value < 0 THEN 1 ELSE 0 END), 'must be non-negative'
FROM bm_sales
UNION ALL
SELECT 'bm_sales', 'discount_pct', SUM(CASE WHEN discount_pct IS NULL OR discount_pct < 0 OR discount_pct > 100 THEN 1 ELSE 0 END), 'must be 0 to 100'
FROM bm_sales
UNION ALL
SELECT 'bm_sales', 'store_id FK', COUNT(*), 'missing store reference'
FROM bm_sales sa LEFT JOIN bm_stores st ON st.store_id = sa.store_id
WHERE st.store_id IS NULL
UNION ALL
SELECT 'bm_sales', 'sku_id FK', COUNT(*), 'missing SKU reference'
FROM bm_sales sa LEFT JOIN bm_skus sk ON sk.sku_id = sa.sku_id
WHERE sk.sku_id IS NULL
UNION ALL
SELECT 'bm_customers', 'cust_id duplicate', COUNT(*) - COUNT(DISTINCT cust_id), 'duplicate primary key values'
FROM bm_customers;

-- 9. Repeat purchase rate: customers with at least two distinct purchase dates / purchasing customers
WITH customer_purchase_days AS (
    SELECT customer_id, COUNT(DISTINCT [date]) AS purchase_days
    FROM bm_sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT COUNT(*) AS purchasing_customers,
       SUM(CASE WHEN purchase_days >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN purchase_days >= 2 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS repeat_purchase_rate_pct
FROM customer_purchase_days;

-- 10. Category mix for each region
WITH region_category_revenue AS (
    SELECT st.city AS region, sk.category, SUM(sa.total_value) AS revenue
    FROM bm_sales AS sa
    JOIN bm_stores AS st ON st.store_id = sa.store_id
    JOIN bm_skus AS sk ON sk.sku_id = sa.sku_id
    GROUP BY st.city, sk.category
)
SELECT region, category, ROUND(revenue, 2) AS revenue,
       ROUND(100 * revenue / SUM(revenue) OVER (PARTITION BY region), 2) AS region_mix_pct
FROM region_category_revenue
ORDER BY region, revenue DESC;