# Semantic Layer Overview

> **Document Owner:** Analytics Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

The Semantic Layer provides business-friendly interfaces to the Gold layer through Metric Views, TVFs, and Genie Spaces. This document serves as a navigation hub — all golden rules are defined in the component-specific documents below.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 CONSUMPTION LAYER                        │
│   Dashboards  │  Genie Spaces  │  Alerts  │  APIs       │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│                  SEMANTIC LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │METRIC VIEWS │  │    TVFs     │  │GENIE SPACES │      │
│  │(KPI Defs)   │  │(Params)     │  │(NL Query)   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│                    GOLD LAYER                            │
│      Dimension Tables (SCD2)  │  Fact Tables            │
└─────────────────────────────────────────────────────────┘
```

---

## Component Rules

> This document is a **navigation hub** with no rules of its own. All Semantic Layer rules are defined in the component-specific documents below.

| Component | Purpose | Rules | Document |
|-----------|---------|-------|----------|
| **Metric Views** | Governed KPIs with flexible aggregation | MV-01..08 | [30-metric-view-patterns](30-metric-view-patterns.md) |
| **TVFs** | Parameterized queries with filtering | TF-01..06 | [31-tvf-patterns](31-tvf-patterns.md) |
| **Genie Spaces** | Natural language interface | GN-01..03 | [32-genie-space-patterns](32-genie-space-patterns.md) |

---

## Platform & Enterprise Prerequisites

> The following EA/PA rules are prerequisites for all Semantic Layer components.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Dimensional modeling in Gold | DM-01 | [06-data-modeling](../../enterprise-architecture/06-data-modeling.md) |
| Table & column comments | CM-02, CM-03 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |
| Naming conventions | NC-01 | [05-naming-conventions](../../enterprise-architecture/05-naming-conventions.md) |
| Unity Catalog governance | GOV-01..07 | [15-unity-catalog-governance](../../platform-architecture/15-unity-catalog-governance.md) |

---

## When to Use Each

| Question Type | Asset | Why |
|---------------|-------|-----|
| Aggregate KPIs | Metric View | Flexible re-aggregation |
| Filtered results | TVF | Parameter support |
| Complex analysis | TVF | Multi-step logic |
| Business chat | Genie Space | Natural language |

---

## Schema Validation

**Always verify columns against Gold YAML before writing SQL.**

```sql
-- ❌ WRONG: Assumed column
SELECT workspace_owner FROM dim_workspace;  -- Column doesn't exist!

-- ✅ CORRECT: Verified against YAML
SELECT workspace_admin FROM dim_workspace;  -- Actual column name
```

---

## References

- [Metric Views](https://docs.databricks.com/metric-views/)
- [TVFs](https://docs.databricks.com/sql/language-manual/sql-ref-syntax-qry-select-tvf)
- [Genie Spaces](https://docs.databricks.com/genie/)
