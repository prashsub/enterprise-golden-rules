# AI/BI Dashboard Patterns

> **Document Owner:** Analytics Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

AI/BI Dashboards (Lakeview) provide visualization of Gold layer data. This document covers query patterns, widget configuration, and deployment automation.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **DB-03** | fieldName must match query alias | Critical | OpEx |
| **DB-04** | SQL returns raw numbers | Required | OpEx |
| **DB-01** | No hardcoded environment values | Critical | Interop |
| **DB-02** | UPDATE-or-CREATE deployment | Required | OpEx |

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Naming conventions | NC-01 | [05-naming-conventions](../../enterprise-architecture/05-naming-conventions.md) |
| Table & column comments | CM-02 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |

---

## fieldName Must Match Query Alias

Widget fieldName must exactly match SQL column alias.

```json
// Query: SELECT SUM(list_cost) as total_cost FROM fact_usage

// Widget (fieldName must match alias)
{
  "fieldName": "total_cost",  // ✅ Matches "total_cost" alias
  "displayName": "Total Cost"
}
```

| Query Alias | fieldName | Result |
|-------------|-----------|--------|
| `total_cost` | `total_cost` | ✅ Works |
| `total_cost` | `totalCost` | ❌ No data |
| `total_cost` | `Total Cost` | ❌ No data |

---

## SQL Returns Raw Numbers

**Widget formatting handles display. SQL returns raw values.**

```sql
-- ❌ WRONG
SELECT CONCAT('$', FORMAT_NUMBER(SUM(cost), 2)) as total_cost  -- String!

-- ✅ CORRECT
SELECT SUM(cost) as total_cost  -- Number
```

```json
// Widget applies formatting
{
  "fieldName": "total_cost",
  "numberFormat": {"type": "currency", "currency": "USD"}
}
```

---

## No Hardcoded Values

Use variable placeholders for environment portability.

```json
{
  "query": "SELECT * FROM ${catalog}.${gold_schema}.fact_usage WHERE ..."
}
```

```python
# Substitute at deployment
variables = {"catalog": "company_prod", "gold_schema": "gold"}
final_json = substitute_variables(dashboard_json, variables)
```

---

## UPDATE-or-CREATE Pattern

```python
def deploy_dashboard(w, dashboard_json, workspace_path):
    """Idempotent deployment - preserves URLs and permissions."""
    content_b64 = base64.b64encode(dashboard_json.encode()).decode()
    
    w.workspace.import_(
        path=workspace_path,
        content=content_b64,
        format="AUTO",
        overwrite=True  # Key: enables update pattern
    )
```

---

## Query Patterns

### Counter (Single KPI)

```sql
SELECT SUM(list_cost) as total_cost
FROM ${catalog}.${gold_schema}.fact_usage
WHERE usage_date >= DATE_SUB(CURRENT_DATE(), 30)
```

### Time Series

```sql
SELECT usage_date, SUM(list_cost) as daily_cost
FROM ${catalog}.${gold_schema}.fact_usage
WHERE usage_date >= DATE_SUB(CURRENT_DATE(), 90)
GROUP BY usage_date
ORDER BY usage_date
```

### Bar Chart (Category)

```sql
SELECT w.workspace_name, SUM(f.list_cost) as total_cost
FROM ${catalog}.${gold_schema}.fact_usage f
JOIN ${catalog}.${gold_schema}.dim_workspace w 
    ON f.workspace_id = w.workspace_id AND w.is_current = true
GROUP BY w.workspace_name
ORDER BY total_cost DESC
LIMIT 10
```

---

## Pre-Deployment Validation

```python
def validate_queries(spark, dashboard_json, variables):
    """Validate all queries with SELECT LIMIT 1."""
    for dataset in dashboard_json.get("datasets", []):
        query = dataset["query"]
        for key, val in variables.items():
            query = query.replace(f"${{{key}}}", val)
        
        try:
            spark.sql(f"SELECT * FROM ({query}) LIMIT 1").collect()
            print(f"✅ {dataset['name']}")
        except Exception as e:
            print(f"❌ {dataset['name']}: {e}")
```

---

## Validation Checklist

- [ ] All columns have explicit aliases
- [ ] SQL returns raw numbers (not formatted)
- [ ] fieldName matches query alias exactly
- [ ] No hardcoded catalog/schema
- [ ] JOIN conditions include SCD2 filter
- [ ] Pre-deployment validation passes

---

## References

- [AI/BI Dashboards](https://docs.databricks.com/dashboards/)
- [Lakeview Reference](https://docs.databricks.com/dashboards/lakeview/)
