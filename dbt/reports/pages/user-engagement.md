---
title: User Engagement
---

# User Engagement

```sql users
SELECT * FROM user_metrics ORDER BY cumulative_sessions DESC
```

```sql summary
SELECT
  COUNT(*) AS total_users,
  ROUND(AVG(cumulative_sessions), 1) AS avg_sessions_per_user,
  ROUND(AVG(avg_session_duration_minutes), 1) AS avg_session_duration
FROM user_metrics
```

<BigValue data={summary} value=total_users title="Total Users" />
<BigValue data={summary} value=avg_sessions_per_user title="Avg Sessions per User" />
<BigValue data={summary} value=avg_session_duration title="Avg Session Duration (min)" />

## Session Distribution

<Histogram
  data={users}
  x=cumulative_sessions
  xAxisTitle="Sessions per User"
/>

## User Detail

<DataTable data={users}>
  <Column id=user_id title="User" />
  <Column id=cumulative_sessions title="Sessions" />
  <Column id=first_session_at title="First Session" />
  <Column id=last_session_at title="Last Session" />
  <Column id=avg_session_duration_minutes title="Avg Duration (min)" fmt="0.0" />
  <Column id=avg_days_between_sessions title="Avg Days Between" fmt="0.0" />
</DataTable>
