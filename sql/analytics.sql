-- Monthly revenue and active customers
SELECT month, ROUND(SUM(revenue)::numeric, 2) AS revenue, COUNT(DISTINCT customer_id) AS active_customers
FROM transactions GROUP BY month ORDER BY month;

-- Highest-value product categories (product descriptions are the source's available product taxonomy)
SELECT description, ROUND(SUM(revenue)::numeric, 2) AS revenue, SUM(quantity) AS units_sold
FROM transactions GROUP BY description ORDER BY revenue DESC LIMIT 20;

-- Customer segment value and observed final-90-day repeat rate
SELECT rfm_segment, COUNT(*) AS customers, ROUND(AVG(monetary)::numeric, 2) AS avg_historical_revenue,
       ROUND(AVG(repeat_purchase)::numeric, 3) AS repeat_purchase_rate
FROM customer_features GROUP BY rfm_segment ORDER BY avg_historical_revenue DESC;

-- Country contribution
SELECT country, ROUND(SUM(revenue)::numeric, 2) AS revenue, COUNT(DISTINCT customer_id) AS customers
FROM transactions GROUP BY country ORDER BY revenue DESC LIMIT 15;
