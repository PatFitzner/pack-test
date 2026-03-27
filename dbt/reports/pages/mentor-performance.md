---
title: Mentor Performance
---

# Mentor Performance

```sql mentors
SELECT * FROM mentor_metrics ORDER BY tier, mentor_id
```

```sql tiers
SELECT DISTINCT tier FROM mentor_metrics ORDER BY tier
```

<Dropdown
  name=tier_filter
  data={tiers}
  value=tier
  title="Filter by Tier"
>
  <DropdownOption value="%" valueLabel="All Tiers" />
</Dropdown>

```sql filtered_mentors
SELECT * FROM mentor_metrics
WHERE tier LIKE '${inputs.tier_filter.value}'
ORDER BY rebooking_rate DESC
```

## Rebooking Rate by Mentor

<BarChart
  data={filtered_mentors}
  x=mentor_id
  y=rebooking_rate
  series=tier
  yAxisTitle="Rebooking Rate (%)"
  yFmt='#,##0.0"%"'
/>

## Mentor Detail

<DataTable data={filtered_mentors}>
  <Column id=mentor_id title="Mentor" />
  <Column id=tier />
  <Column id=rebooking_rate title="Rebooking Rate (%)" fmt='#,##0.0' />
  <Column id=total_user_mentor_pairs title="Users" />
  <Column id=total_rebooked title="Rebooked" />
  <Column id=cumulative_sessions title="Total Sessions" />
  <Column id=avg_sessions_per_day title="Avg Sessions/Day" fmt='0.00' />
</DataTable>
