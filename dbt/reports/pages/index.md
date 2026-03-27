---
title: CEO Dashboard — Mentor Tier Rebooking Rates
---

# Are Gold-tier mentors driving better retention?

**Yes.** Gold mentors have a 61.9% rebooking rate — 1.6x higher than Silver and far above Bronze.

```sql rebooking_rates
SELECT * FROM metrics_rebooking_rates ORDER BY tier
```

<BigValue
  data={rebooking_rates.filter(d => d.tier === 'Gold')}
  value=rebooking_rate_pct
  title="Gold Rebooking Rate"
  fmt='#,##0.0"%"'
/>

<BigValue
  data={rebooking_rates.filter(d => d.tier === 'Silver')}
  value=rebooking_rate_pct
  title="Silver Rebooking Rate"
  fmt='#,##0.0"%"'
/>

<BigValue
  data={rebooking_rates.filter(d => d.tier === 'Bronze')}
  value=rebooking_rate_pct
  title="Bronze Rebooking Rate"
  fmt='#,##0.0"%"'
/>

## Rebooking Rate by Tier

<BarChart
  data={rebooking_rates}
  x=tier
  y=rebooking_rate_pct
  yAxisTitle="Rebooking Rate (%)"
  yFmt='#,##0.0"%"'
/>

## Detail

<DataTable data={rebooking_rates}>
  <Column id=tier />
  <Column id=total_mentors title="Mentors" />
  <Column id=total_user_mentor_pairs title="User-Mentor Pairs" />
  <Column id=total_rebooked title="Rebooked" />
  <Column id=rebooking_rate_pct title="Rate (%)" fmt='#,##0.0' />
</DataTable>
