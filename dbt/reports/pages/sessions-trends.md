---
title: Session Trends
---

# Session Trends

```sql sessions
SELECT
  *,
  EXTRACT(HOUR FROM started_at) AS hour_of_day,
  DAYNAME(started_at) AS day_of_week,
  EXTRACT(DOW FROM started_at) AS dow_num
FROM fct_sessions
```

```sql summary
SELECT
  COUNT(*) AS total_sessions,
  ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT started_at::DATE), 1) AS avg_daily_volume,
  (SELECT DAYNAME(started_at)
   FROM fct_sessions
   GROUP BY DAYNAME(started_at)
   ORDER BY COUNT(*) DESC
   LIMIT 1) AS busiest_day
FROM fct_sessions
```

<BigValue data={summary} value=total_sessions title="Total Sessions" />
<BigValue data={summary} value=avg_daily_volume title="Avg Sessions / Day" />
<BigValue data={summary} value=busiest_day title="Busiest Day" />

## Weekly Volume

```sql weekly
SELECT
  DATE_TRUNC('week', started_at)::DATE AS week,
  COUNT(*) AS sessions
FROM fct_sessions
GROUP BY 1
ORDER BY 1
```

<BarChart
  data={weekly}
  x=week
  y=sessions
  xAxisTitle="Week"
  yAxisTitle="Sessions"
/>

## Sessions by Hour of Day

```sql by_hour
SELECT
  EXTRACT(HOUR FROM started_at)::INT AS hour,
  COUNT(*) AS sessions
FROM fct_sessions
GROUP BY 1
ORDER BY 1
```

<BarChart
  data={by_hour}
  x=hour
  y=sessions
  xAxisTitle="Hour of Day"
  yAxisTitle="Sessions"
/>

## Sessions by Day of Week

<!-- DuckDB DOW: Sunday=0. Shift with +6 mod 7 so Monday=0, Sunday=6 -->
```sql by_dow
SELECT
  DAYNAME(started_at) AS day,
  (EXTRACT(DOW FROM started_at) + 6) % 7 AS dow_mon,
  COUNT(*) AS sessions
FROM fct_sessions
GROUP BY ALL
ORDER BY dow_mon
```

<!-- sort=false preserves the SQL's dow_num ordering instead of alphabetical -->
<BarChart
  data={by_dow}
  x=day
  y=sessions
  sort=false
  xAxisTitle="Day of Week"
  yAxisTitle="Sessions"
/>
