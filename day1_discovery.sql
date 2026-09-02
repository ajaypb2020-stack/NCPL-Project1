-- Day 1 Discovery SQL (SQL Server)
-- Target database: retail_db

USE retail_db;

-- ---------------------------------------------------------------------------
-- A) Connect and explore all 6 tables
-- ---------------------------------------------------------------------------
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME LIKE 'bm[_]%'
ORDER BY TABLE_NAME;

EXEC sp_help 'bm_customers';
EXEC sp_help 'bm_inventory';
EXEC sp_help 'bm_promotions';
EXEC sp_help 'bm_sales';
EXEC sp_help 'bm_skus';
EXEC sp_help 'bm_stores';

-- ---------------------------------------------------------------------------
-- B) Row counts and missing values in each table
-- ---------------------------------------------------------------------------
SELECT 'bm_customers' AS table_name,
       COUNT(*) AS row_count,
      SUM(CASE WHEN cust_id IS NULL THEN 1 ELSE 0 END) AS missing_cust_id,
      SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS missing_age,
      SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS missing_gender,
      SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) AS missing_city,
      SUM(CASE WHEN loyalty_segment IS NULL THEN 1 ELSE 0 END) AS missing_loyalty_segment,
      SUM(CASE WHEN preferred_channel IS NULL THEN 1 ELSE 0 END) AS missing_preferred_channel,
      SUM(CASE WHEN registration_date IS NULL THEN 1 ELSE 0 END) AS missing_registration_date
FROM bm_customers
UNION ALL
SELECT 'bm_inventory',
       COUNT(*),
      SUM(CASE WHEN store_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN sku_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN stock_on_hand IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN reorder_point IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN safety_stock IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN last_restock_date IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN snapshot_date IS NULL THEN 1 ELSE 0 END)
FROM bm_inventory
UNION ALL
SELECT 'bm_promotions',
       COUNT(*),
      SUM(CASE WHEN promo_name IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN start_date IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN end_date IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN discount_pct IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN promo_type IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN promo_id IS NULL THEN 1 ELSE 0 END),
       0
FROM bm_promotions
UNION ALL
SELECT 'bm_sales',
       COUNT(*),
      SUM(CASE WHEN [date] IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN store_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN sku_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN unit_price IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN total_value IS NULL THEN 1 ELSE 0 END)
FROM bm_sales
UNION ALL
SELECT 'bm_skus',
       COUNT(*),
      SUM(CASE WHEN sku_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN sku_name IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN category IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN subcategory IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN unit_price IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN cost_price IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END)
FROM bm_skus
UNION ALL
SELECT 'bm_stores',
       COUNT(*),
      SUM(CASE WHEN store_id IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN store_name IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN store_type IS NULL THEN 1 ELSE 0 END),
      SUM(CASE WHEN opening_date IS NULL THEN 1 ELSE 0 END),
       0,
       0
FROM bm_stores;

-- ---------------------------------------------------------------------------
-- C) 15 required queries
-- ---------------------------------------------------------------------------

-- 1) Simple SELECT + WHERE: customers in Dubai with Gold loyalty
SELECT cust_id, age, gender, city, loyalty_segment
FROM bm_customers
WHERE city = 'Dubai' AND loyalty_segment = 'Gold'
ORDER BY cust_id;

-- 2) Simple SELECT + WHERE: discounted sales in 2025
SELECT TOP (200) [date], store_id, sku_id, customer_id, quantity, total_value, discount_pct
FROM bm_sales
WHERE [date] >= '2025-01-01' AND discount_pct > 0
ORDER BY [date], store_id;

-- 3) Simple SELECT + WHERE: electronics SKUs above AED 100
SELECT sku_id, sku_name, category, subcategory, unit_price
FROM bm_skus
WHERE category = 'Electronics' AND unit_price > 100
ORDER BY unit_price DESC;

-- 4) INNER JOIN (2 tables): sales with store attributes for Mall stores
SELECT TOP (300) sa.[date], sa.store_id, st.store_name, st.city, st.store_type,
       sa.sku_id, sa.quantity, sa.total_value
FROM bm_sales AS sa
INNER JOIN bm_stores AS st ON st.store_id = sa.store_id
WHERE st.store_type = 'Mall'
ORDER BY sa.[date] DESC;

-- 5) INNER JOIN (2 tables): sales lines with SKU category in Snacks
SELECT TOP (300) sa.[date], sa.sku_id, sk.sku_name, sk.category, sa.quantity, sa.total_value
FROM bm_sales AS sa
INNER JOIN bm_skus AS sk ON sk.sku_id = sa.sku_id
WHERE sk.category = 'Snacks'
ORDER BY sa.total_value DESC;

-- 6) INNER JOIN (2 tables): customer spend for Platinum customers
SELECT cu.cust_id, cu.city, cu.loyalty_segment,
       ROUND(SUM(sa.total_value), 2) AS total_spend
FROM bm_customers AS cu
INNER JOIN bm_sales AS sa ON sa.customer_id = cu.cust_id
WHERE cu.loyalty_segment = 'Platinum'
GROUP BY cu.cust_id, cu.city, cu.loyalty_segment
ORDER BY total_spend DESC;

-- 7) Join 3+ tables: transaction details with store and SKU metadata
SELECT TOP (500) sa.[date], sa.customer_id,
       st.city AS region, st.store_name, st.store_type,
       sk.sku_name, sk.category, sa.quantity, sa.total_value
FROM bm_sales AS sa
INNER JOIN bm_stores AS st ON st.store_id = sa.store_id
INNER JOIN bm_skus AS sk ON sk.sku_id = sa.sku_id
WHERE sa.[date] BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY sa.[date] DESC;

-- 8) Join 3+ tables: revenue by region and category
SELECT st.city AS region, sk.category,
       ROUND(SUM(sa.total_value), 2) AS revenue
FROM bm_sales AS sa
INNER JOIN bm_stores AS st ON st.store_id = sa.store_id
INNER JOIN bm_skus AS sk ON sk.sku_id = sa.sku_id
GROUP BY st.city, sk.category
ORDER BY st.city, revenue DESC;

-- 9) Join 3+ tables: customer spend by preferred channel and store type
SELECT cu.preferred_channel, st.store_type,
       COUNT(DISTINCT cu.cust_id) AS customers,
       ROUND(SUM(sa.total_value), 2) AS revenue
FROM bm_sales AS sa
INNER JOIN bm_customers AS cu ON cu.cust_id = sa.customer_id
INNER JOIN bm_stores AS st ON st.store_id = sa.store_id
GROUP BY cu.preferred_channel, st.store_type
ORDER BY revenue DESC;

-- 10) LEFT JOIN: customers and their purchase summary (includes no-purchase customers)
SELECT cu.cust_id, cu.city, cu.loyalty_segment,
       COUNT(sa.sku_id) AS sales_lines,
       ROUND(COALESCE(SUM(sa.total_value), 0), 2) AS total_spend
FROM bm_customers AS cu
LEFT JOIN bm_sales AS sa ON sa.customer_id = cu.cust_id
GROUP BY cu.cust_id, cu.city, cu.loyalty_segment
ORDER BY total_spend DESC;

-- 11) LEFT JOIN: SKUs and sales coverage (includes unsold SKUs)
SELECT sk.sku_id, sk.sku_name, sk.category,
       COUNT(sa.sku_id) AS sales_lines,
       ROUND(COALESCE(SUM(sa.quantity), 0), 2) AS units_sold,
       ROUND(COALESCE(SUM(sa.total_value), 0), 2) AS revenue
FROM bm_skus AS sk
LEFT JOIN bm_sales AS sa ON sa.sku_id = sk.sku_id
GROUP BY sk.sku_id, sk.sku_name, sk.category
ORDER BY revenue DESC;

-- 12) LEFT JOIN: promotions matched to discounted sales by date and approximate discount
SELECT pr.promo_id, pr.promo_name, pr.promo_type,
       COUNT(sa.sku_id) AS matched_sales_lines,
       ROUND(COALESCE(SUM(sa.total_value), 0), 2) AS matched_revenue
FROM bm_promotions AS pr
LEFT JOIN bm_sales AS sa
      ON sa.[date] BETWEEN pr.start_date AND pr.end_date
      AND sa.discount_pct > 0
      AND ABS(sa.discount_pct - pr.discount_pct) <= 10
GROUP BY pr.promo_id, pr.promo_name, pr.promo_type
ORDER BY matched_revenue DESC;

-- 13) Top records: top 10 customers by spend
SELECT TOP (10) sa.customer_id,
       ROUND(SUM(sa.total_value), 2) AS total_spend
FROM bm_sales AS sa
WHERE sa.customer_id IS NOT NULL
GROUP BY sa.customer_id
ORDER BY total_spend DESC;

-- 14) Top records: top 10 stores by revenue
SELECT TOP (10) st.store_id, st.store_name, st.city, st.store_type,
       ROUND(SUM(sa.total_value), 2) AS revenue
FROM bm_sales AS sa
INNER JOIN bm_stores AS st ON st.store_id = sa.store_id
GROUP BY st.store_id, st.store_name, st.city, st.store_type
ORDER BY revenue DESC;

-- 15) Top records: top 10 products by units sold
SELECT TOP (10) sk.sku_id, sk.sku_name, sk.category,
       SUM(sa.quantity) AS units_sold,
       ROUND(SUM(sa.total_value), 2) AS revenue
FROM bm_sales AS sa
INNER JOIN bm_skus AS sk ON sk.sku_id = sa.sku_id
GROUP BY sk.sku_id, sk.sku_name, sk.category
ORDER BY units_sold DESC, revenue DESC;