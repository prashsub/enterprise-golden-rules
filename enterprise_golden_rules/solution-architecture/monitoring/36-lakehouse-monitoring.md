# Lakehouse Monitoring Patterns

> **Document Owner:** Data Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

Lakehouse Monitoring provides automated data quality monitoring with drift detection, profiling, and custom metrics.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **MO-01** | Use `input_columns=[":table"]` for table-level KPIs | Critical | [OpEx](https://docs.databricks.com/en/data-quality-monitoring/) |
| **MO-02** | Document monitor output tables for Genie | Required | [OpEx](https://docs.databricks.com/en/data-quality-monitoring/) |
| **MO-03** | All related metrics must use same input_columns | Critical | [OpEx](https://docs.databricks.com/en/data-quality-monitoring/) |
| **MO-04** | Implement async wait pattern | Required | [OpEx](https://docs.databricks.com/en/data-quality-monitoring/) |

> **Cross-references:** Platform service limits → see REL-10. Capacity planning → see REL-11.

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Data quality expectations | DQ-03..07 | [09-data-quality](../../enterprise-architecture/09-data-quality.md) |
| LLM-friendly table docs | DL-07 | [12-unity-catalog-tables](../../platform-architecture/12-unity-catalog-tables.md) |
| Platform service limits & capacity | REL-10, REL-11 | [17-reliability-disaster-recovery](../../platform-architecture/17-reliability-disaster-recovery.md) |

---

## Output Tables

Monitor creates two tables:

```
catalog.schema.{table_name}_profile_metrics   # Custom metrics
catalog.schema.{table_name}_drift_metrics     # Drift detection
```

---

## input_columns Pattern

**All related metrics MUST use the same `input_columns` value.**

```python
# ✅ CORRECT: All use :table
custom_metrics = [
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
        name="total_cost",
        input_columns=[":table"],  # Table-level
        definition="SUM(list_cost)"
    ),
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_AGGREGATE,
        name="workspace_count",
        input_columns=[":table"],  # Same!
        definition="COUNT(DISTINCT workspace_id)"
    ),
    MonitorMetric(
        type=MonitorMetricType.CUSTOM_METRIC_TYPE_DERIVED,
        name="cost_per_workspace",
        input_columns=[":table"],  # Same!
        definition="total_cost / NULLIF(workspace_count, 0)"
    )
]
```

**Why:** DERIVED metrics can only reference metrics in the same `column_name` row.

---

## Async Wait Pattern

Monitor creation is async (~15 min for tables).

```python
def wait_for_monitor_tables(table_name, timeout_minutes=30):
    start = time.time()
    while time.time() - start < timeout_minutes * 60:
        try:
            spark.table(f"{table_name}_profile_metrics").limit(1)
            spark.table(f"{table_name}_drift_metrics").limit(1)
            return True
        except:
            time.sleep(30)
    return False
```

---

## Query Patterns

### AGGREGATE Metrics (Require PIVOT)

```sql
SELECT 
    window.start as period_start,
    MAX(CASE WHEN column_name = ':table' THEN total_cost END) as total_cost
FROM catalog.schema.fact_usage_profile_metrics
WHERE column_name = ':table'
GROUP BY window.start
```

### DERIVED Metrics (Direct SELECT)

```sql
SELECT 
    window.start, cost_per_workspace
FROM catalog.schema.fact_usage_profile_metrics
WHERE column_name = ':table'
```

### Drift Detection

```sql
SELECT 
    window.start, column_name, chi_squared_pvalue
FROM catalog.schema.fact_usage_drift_metrics
WHERE chi_squared_pvalue < 0.05
```

---

## Document for Genie

```python
def document_monitor_tables(spark, table_name, metric_descriptions):
    """Add comments for Genie discoverability."""
    profile_table = f"{table_name}_profile_metrics"
    
    for metric, desc in metric_descriptions.items():
        spark.sql(f"ALTER TABLE {profile_table} ALTER COLUMN {metric} COMMENT '{desc}'")
```

---

---

---

## Validation Checklist

- [ ] All related metrics use same input_columns
- [ ] Wait pattern implemented
- [ ] Output tables documented
- [ ] Query patterns tested

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| DERIVED returns NULL | Different input_columns | Use same value |
| Table not found | Async creation | Implement wait |
| Genie can't interpret | Missing docs | Add COMMENTs |

---

## References

- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
- [Custom Metrics](https://docs.databricks.com/lakehouse-monitoring/custom-metrics)
