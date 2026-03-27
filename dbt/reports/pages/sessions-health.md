---
title: Session Health
---

# Session Health

<!-- Evidence converts NULL timestamps to 1970-01-01 during parquet serialization.
     Cast ended_at to VARCHAR and show '—' for synthetic endings to avoid this. -->
```sql sessions
SELECT
  session_id, user_id, mentor_id, started_at,
  CASE WHEN is_synthetic_ending THEN '—' ELSE ended_at::VARCHAR END AS ended_at,
  is_synthetic_ending, duration_minutes
FROM fct_sessions ORDER BY started_at DESC
```

```sql summary
SELECT
  COUNT(*) AS total_sessions,
  SUM(CASE WHEN is_synthetic_ending THEN 1 ELSE 0 END) AS missing_end,
  ROUND(SUM(CASE WHEN is_synthetic_ending THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS missing_end_pct,
  ROUND(MEDIAN(duration_minutes), 0) AS median_duration
FROM fct_sessions
```

<BigValue data={summary} value=total_sessions title="Total Sessions" />
<BigValue data={summary} value=missing_end title="Missing End Events" />
<BigValue data={summary} value=missing_end_pct title="Missing End %" fmt='#,##0.0"%"' />
<BigValue data={summary} value=median_duration title="Median Duration (min)" />

## Duration Distribution

```sql duration_buckets
SELECT
  (FLOOR(duration_minutes / 30) * 30)::INT AS bucket_start,
  (FLOOR(duration_minutes / 30) * 30)::INT || '-' || ((FLOOR(duration_minutes / 30) + 1) * 30)::INT || ' min' AS bucket,
  COUNT(*) AS sessions
FROM fct_sessions
GROUP BY ALL
ORDER BY bucket_start
```

<BarChart
  data={duration_buckets}
  x=bucket
  y=sessions
  xAxisTitle="Duration Range"
  yAxisTitle="Sessions"
/>

## Sessions per Week

```sql weekly
SELECT
  DATE_TRUNC('week', started_at)::DATE AS week,
  COUNT(*) AS sessions
FROM fct_sessions
GROUP BY 1
ORDER BY 1
```

<LineChart
  data={weekly}
  x=week
  y=sessions
  xAxisTitle="Week"
  yAxisTitle="Sessions"
/>

## All Sessions

<DataTable data={sessions} search=true>
  <Column id=session_id title="Session ID" />
  <Column id=user_id title="User" />
  <Column id=mentor_id title="Mentor" />
  <Column id=started_at title="Started" />
  <Column id=ended_at title="Ended" />
  <Column id=duration_minutes title="Duration (min)" />
  <Column id=is_synthetic_ending title="Synthetic Ending" />
</DataTable>
