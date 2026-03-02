# Metric View Patterns

> **Document Owner:** Analytics Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

Metric Views define governed KPIs with flexible aggregation. They are the mandatory foundation for consistent business metrics across dashboards, Genie spaces, and AI/BI.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **MV-01** | All core metrics MUST be in Metric Views | Critical | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-02** | Reference Gold layer tables only | Critical | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-03** | Business context documentation required | Critical | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-04** | Schema validation before creation | Critical | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-05** | No transitive joins | Critical | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-06** | Synonyms for all dimensions/measures | Required | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-07** | Display format for all measures | Required | [Interop](https://docs.databricks.com/en/metric-views/) |
| **MV-08** | Structured comment format | Required | [Interop](https://docs.databricks.com/en/metric-views/) |

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Dimensional modeling in Gold | DM-01 | [06-data-modeling](../../enterprise-architecture/06-data-modeling.md) |
| Table & column comments | CM-02, CM-03 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |
| Naming conventions | NC-01 | [05-naming-conventions](../../enterprise-architecture/05-naming-conventions.md) |

---

## Why Metric Views?

| Problem Without | Benefit With |
|-----------------|--------------|
| Inconsistent "revenue" calculations | Define once, use everywhere |
| Ratio re-aggregation errors | Safe complex measures |
| View proliferation for each cut | Flexible runtime grouping |
| Ad-hoc performance issues | Built-in materialization |

---

## When to Use

| Scenario | Metric View? |
|----------|--------------|
| KPI used in 2+ dashboards | Yes |
| Ratio or distinct count | Yes |
| Flexible dimensional analysis | Yes |
| One-off ad-hoc query | No |
| Complex filtering with params | No (use TVF) |

---

## YAML Structure (v1.1)

**Critical: Name comes from filename, NOT from YAML.**

```yaml
version: "1.1"
comment: >
  PURPOSE: Cost analytics for Databricks billing.
  BEST FOR: Total spend | Cost trends | SKU breakdown
  NOT FOR: Commit tracking (use commit_tracking)
  DIMENSIONS: usage_date, workspace_name, sku_name
  MEASURES: total_cost, total_dbus
  SOURCE: fact_usage (billing domain)
  NOTE: Costs are list prices.

source: ${catalog}.${gold_schema}.fact_usage

joins:
  - name: dim_workspace
    source: ${catalog}.${gold_schema}.dim_workspace
    'on': source.workspace_id = dim_workspace.workspace_id AND dim_workspace.is_current = true

dimensions:
  - name: usage_date
    expr: source.usage_date
    comment: Date of usage
    display_name: Usage Date
    synonyms: [date, day, when]

measures:
  - name: total_cost
    expr: SUM(source.list_cost)
    comment: Total cost at list price
    display_name: Total Cost
    format:
      type: currency
      currency_code: USD
      decimal_places: { type: exact, places: 2 }
      abbreviation: compact
    synonyms: [cost, spend, dollars]
```

---

## Unsupported Fields (v1.1)

| Field | Error | Action |
|-------|-------|--------|
| `name` | Unrecognized field | Never include |
| `time_dimension` | Unrecognized | Remove |
| `window_measures` | Unrecognized | Remove |
| `join_type` | Unsupported | Remove |

---

## No Transitive Joins

Only direct joins from source to dimension are supported.

```yaml
# ❌ WRONG: dim → dim join
joins:
  - name: dim_destination
    'on': dim_property.destination_id = dim_destination.destination_id

# ✅ CORRECT: source → dim only
joins:
  - name: dim_workspace
    'on': source.workspace_id = dim_workspace.workspace_id
```

**Solutions:**
- Use FK directly as dimension
- Denormalize during Gold ETL
- Create enriched view

---

## Validation Checklist

- [ ] No `name` field in YAML
- [ ] All columns verified against Gold YAML
- [ ] Joins are direct (source → dim only)
- [ ] 3+ synonyms per dimension
- [ ] Format specified for measures
- [ ] Structured comment (PURPOSE, BEST FOR, etc.)

---

## References

- [Metric Views YAML](https://docs.databricks.com/metric-views/yaml-ref)
- [Metric Views Joins](https://docs.databricks.com/metric-views/joins)
