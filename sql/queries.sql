-- IT Service Desk Ticket Analysis (SIMULATED DATA) - SQLite
-- Table: tickets (loaded from data/tickets_simulated.csv)

-- Q1. Monthly ticket volume and average resolution time
-- name: q1_monthly_volume
SELECT substr(created_at, 1, 7)               AS month,
       COUNT(*)                                AS tickets,
       ROUND(AVG(resolution_hours), 2)         AS avg_resolution_hours
FROM tickets
GROUP BY month
ORDER BY month;

-- Q2. Top issue categories by volume, with share of all tickets
-- name: q2_top_categories
SELECT category,
       COUNT(*)                                                AS tickets,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM tickets), 1) AS pct_of_total,
       ROUND(AVG(resolution_hours), 2)                          AS avg_resolution_hours
FROM tickets
GROUP BY category
ORDER BY tickets DESC;

-- Q3. SLA compliance by priority
-- name: q3_sla_by_priority
SELECT priority,
       COUNT(*)                                              AS tickets,
       SUM(sla_breached)                                     AS breaches,
       ROUND(100.0 * (1 - AVG(sla_breached)), 1)             AS sla_met_pct
FROM tickets
GROUP BY priority
ORDER BY priority;

-- Q4. Categories with the worst SLA performance
-- name: q4_sla_by_category
SELECT category,
       COUNT(*)                                  AS tickets,
       ROUND(100.0 * AVG(sla_breached), 1)       AS breach_pct,
       ROUND(100.0 * AVG(reopened), 1)           AS reopen_pct
FROM tickets
GROUP BY category
HAVING COUNT(*) >= 50
ORDER BY breach_pct DESC;

-- Q5. Busiest hours of the day (staffing insight)
-- name: q5_tickets_by_hour
SELECT CAST(substr(created_at, 12, 2) AS INTEGER) AS hour_of_day,
       COUNT(*)                                    AS tickets
FROM tickets
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- Q6. Busiest weekday
-- name: q6_tickets_by_weekday
SELECT CASE strftime('%w', created_at)
         WHEN '1' THEN '1 Mon' WHEN '2' THEN '2 Tue' WHEN '3' THEN '3 Wed'
         WHEN '4' THEN '4 Thu' WHEN '5' THEN '5 Fri' END AS weekday,
       COUNT(*) AS tickets
FROM tickets
GROUP BY weekday
ORDER BY weekday;

-- Q7. Agent workload, speed and customer satisfaction
-- name: q7_agent_performance
SELECT agent,
       COUNT(*)                              AS tickets,
       ROUND(AVG(resolution_hours), 2)       AS avg_resolution_hours,
       ROUND(100.0 * AVG(sla_breached), 1)   AS breach_pct,
       ROUND(AVG(csat_score), 2)             AS avg_csat
FROM tickets
GROUP BY agent
ORDER BY avg_resolution_hours;

-- Q8. Does a missed SLA or a reopened ticket hurt satisfaction?
-- name: q8_csat_impact
SELECT sla_breached, reopened,
       COUNT(*)                          AS tickets,
       ROUND(AVG(csat_score), 2)         AS avg_csat
FROM tickets
GROUP BY sla_breached, reopened
ORDER BY sla_breached, reopened;

-- Q9. First response time by channel (window function: rank channels)
-- name: q9_channel_response
SELECT channel,
       COUNT(*)                              AS tickets,
       ROUND(AVG(first_response_mins), 1)    AS avg_first_response_mins,
       RANK() OVER (ORDER BY AVG(first_response_mins)) AS speed_rank
FROM tickets
GROUP BY channel;

-- Q10. Self-service opportunity: password and account tickets as % of volume per month
-- name: q10_password_share
SELECT substr(created_at, 1, 7) AS month,
       SUM(CASE WHEN category LIKE 'Password%' THEN 1 ELSE 0 END)                  AS password_tickets,
       ROUND(100.0 * SUM(CASE WHEN category LIKE 'Password%' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_of_month
FROM tickets
GROUP BY month
ORDER BY month;
