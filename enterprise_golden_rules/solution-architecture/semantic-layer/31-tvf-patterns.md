# Table-Valued Function (TVF) Patterns

> **Document Owner:** Analytics Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

TVFs provide parameterized, reusable SQL queries optimized for Genie Spaces. They complement Metric Views for complex filtering and parameterized analysis.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **TF-01** | STRING for date parameters | Critical | Interop |
| **TF-02** | Schema validation before SQL | Critical | Interop |
| **TF-03** | v3.0 comment format | Required | [Interop](https://docs.databricks.com/en/genie/) |
| **TF-04** | Required parameters before optional | Critical | Interop |
| **TF-05** | No LIMIT with parameters | Critical | Interop |
| **TF-06** | Single aggregation pass | Critical | Interop |

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Dimensional modeling in Gold | DM-01 | [06-data-modeling](../../enterprise-architecture/06-data-modeling.md) |
| Column comments (v3.0 format) | CM-04 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |
| Naming conventions | NC-01 | [05-naming-conventions](../../enterprise-architecture/05-naming-conventions.md) |

---

## STRING for Date Parameters

Genie cannot pass DATE types. Always use STRING + CAST.

```sql
-- ✅ CORRECT
CREATE FUNCTION get_costs(
    start_date STRING COMMENT 'Format: YYYY-MM-DD'
)
...
WHERE usage_date >= CAST(start_date AS DATE)

-- ❌ WRONG
CREATE FUNCTION get_costs(start_date DATE)  -- Genie can't pass this!
```

---

## Parameter Order

Required parameters must come before optional.

```sql
-- ✅ CORRECT
CREATE FUNCTION get_workspace_costs(
    workspace_name STRING,              -- Required (no DEFAULT)
    start_date STRING DEFAULT '2024-01-01'  -- Optional
)

-- ❌ WRONG
CREATE FUNCTION get_workspace_costs(
    start_date STRING DEFAULT '2024-01-01',  -- Optional first!
    workspace_name STRING                     -- Required after!
)
```

---

## No LIMIT with Parameters

Use ROW_NUMBER + WHERE instead of LIMIT.

```sql
-- ❌ WRONG
SELECT * FROM results LIMIT limit_rows;  -- Compilation error!

-- ✅ CORRECT
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY cost DESC) AS rn
    FROM results
)
SELECT * FROM ranked WHERE rn <= CAST(limit_rows AS INT);
```

---

## Single Aggregation Pass

Avoid Cartesian products from multiple reads of same table.

```sql
-- ❌ WRONG: Reads fact_usage twice → Cartesian
WITH costs AS (SELECT workspace_id, SUM(cost) FROM fact_usage GROUP BY 1),
     dbus AS (SELECT workspace_id, SUM(dbus) FROM fact_usage GROUP BY 1)
SELECT c.*, d.* FROM costs c JOIN dbus d ON c.workspace_id = d.workspace_id;

-- ✅ CORRECT: Single read
WITH metrics AS (
    SELECT workspace_id, SUM(cost), SUM(dbus)
    FROM fact_usage
    GROUP BY workspace_id
)
SELECT * FROM metrics;
```

---

## v3.0 Comment Format

```sql
CREATE FUNCTION get_cost_summary(
    start_date STRING DEFAULT '2024-01-01',
    end_date STRING DEFAULT '2024-12-31'
)
RETURNS TABLE (...)
COMMENT '
• PURPOSE: Get summarized cost metrics by workspace.

• BEST FOR: Total spend | Cost summary | Workspace comparison

• NOT FOR: Daily details (use get_daily_costs)

• RETURNS: PRE-AGGREGATED rows (workspace_name, total_cost)

• PARAMS: start_date (YYYY-MM-DD, default: 2024-01-01)

• SYNTAX: SELECT * FROM get_cost_summary(''2024-01-01'', ''2024-12-31'')

• NOTE: DO NOT wrap in TABLE(). DO NOT add GROUP BY.
'
RETURN ...
```

---

## TVF Template

```sql
CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_workspace_costs(
    start_date STRING DEFAULT '2024-01-01',
    end_date STRING DEFAULT '2024-12-31',
    limit_rows STRING DEFAULT '100'
)
RETURNS TABLE (
    workspace_name STRING,
    total_cost DECIMAL(18,2),
    cost_rank INT
)
COMMENT '...'  -- v3.0 format
RETURN
WITH metrics AS (
    SELECT 
        f.workspace_id,
        SUM(f.list_cost) as total_cost
    FROM ${catalog}.${gold_schema}.fact_usage f
    WHERE f.usage_date >= CAST(start_date AS DATE)
      AND f.usage_date <= CAST(end_date AS DATE)
    GROUP BY f.workspace_id
),
ranked AS (
    SELECT 
        w.workspace_name,
        m.total_cost,
        ROW_NUMBER() OVER (ORDER BY m.total_cost DESC) as cost_rank
    FROM metrics m
    JOIN ${catalog}.${gold_schema}.dim_workspace w 
        ON m.workspace_id = w.workspace_id 
        AND w.is_current = true
)
SELECT workspace_name, total_cost, cost_rank
FROM ranked
WHERE cost_rank <= CAST(limit_rows AS INT);
```

---

## Validation Checklist

- [ ] All columns verified against Gold YAML
- [ ] Date parameters use STRING
- [ ] Required parameters before optional
- [ ] Uses ROW_NUMBER, not LIMIT parameter
- [ ] Single aggregation pass per source table
- [ ] v3.0 comment format complete
- [ ] NOTE includes "DO NOT wrap in TABLE()"

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `UNRESOLVED_COLUMN` | Column not in table | Check Gold YAML |
| `NOT_A_SCALAR_FUNCTION` | Wrapped in TABLE() | Add warning to NOTE |
| `INVALID_LIMIT_LIKE_EXPRESSION` | Parameter in LIMIT | Use ROW_NUMBER + WHERE |
| Results inflated 100x+ | Cartesian product | Single aggregation |

---

## References

- [TVF SQL Reference](https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-tvf)
- [Genie Trusted Assets](https://docs.databricks.com/genie/trusted-assets)
