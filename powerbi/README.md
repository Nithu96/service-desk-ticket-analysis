# Building the Power BI dashboard (about 20 minutes)

1. Power BI Desktop > Get data > Text/CSV > `data/tickets_simulated.csv` > Transform data.
2. In Power Query: set `created_at` to Date/Time, add a column `Month = Date.StartOfMonth([created_at])`, close and apply.
3. Add these measures (Modeling > New measure):

```
Total Tickets = COUNTROWS(tickets)
SLA Met % = 1 - DIVIDE(SUM(tickets[sla_breached]), [Total Tickets])
Avg Resolution Hours = AVERAGE(tickets[resolution_hours])
Avg First Response (mins) = AVERAGE(tickets[first_response_mins])
Reopen Rate = DIVIDE(SUM(tickets[reopened]), [Total Tickets])
Avg CSAT = AVERAGE(tickets[csat_score])
```

4. Visuals: four KPI cards (Total Tickets, SLA Met %, Avg Resolution Hours, Avg CSAT); column chart of tickets by Month;
   bar chart of tickets by category; clustered column of SLA Met % by priority (add a 90% constant line);
   line chart of tickets by hour; slicers for category, priority and agent.
5. Save as `service-desk-dashboard.pbix`, export a screenshot to `charts/powerbi-dashboard.png`, and add it to the README.
