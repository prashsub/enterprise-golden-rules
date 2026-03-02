# Genie Space Patterns

> **Document Owner:** Analytics Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

Genie Spaces provide natural language interfaces to data through Metric Views and TVFs. This document covers asset inventory, configuration, and optimization.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **GN-01** | Inventory-first creation | Required | [Interop](https://docs.databricks.com/en/genie/) |
| **GN-02** | v3.0 comment format | Required | [Interop](https://docs.databricks.com/en/genie/) |
| **GN-03** | Curated data for Genie (comments, no nulls) | Required | [Interop](https://docs.databricks.com/en/genie/) |

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Table & column comments | CM-02, CM-03 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |
| LLM-friendly table docs | DL-07 | [12-unity-catalog-tables](../../platform-architecture/12-unity-catalog-tables.md) |
| UC governance | GOV-01..07 | [15-unity-catalog-governance](../../platform-architecture/15-unity-catalog-governance.md) |

---

## Architecture

```
User Question → Genie LLM → Select Asset → Generate SQL → Execute
                    ↓
              Reads COMMENTs to understand:
              - Table/column meaning
              - TVF purpose and parameters
              - Metric View definitions
```

---

## Inventory-First Creation

**Before creating a Genie Space, document:**

1. Questions the space should answer
2. Which asset answers each question
3. Assets to include/exclude

```markdown
# Space Inventory: Cost Analytics

## Questions → Asset Mapping
| Question | Asset | Type |
|----------|-------|------|
| "Total cost this month" | cost_analytics_metrics | Metric View |
| "Daily costs for January" | get_daily_costs | TVF |
| "Top 10 spenders" | get_top_spenders | TVF |
```

---

## Space Configuration

```json
{
  "name": "Cost Analytics",
  "description": "Ask about spend, DBUs, workspaces, trends.",
  "warehouse_id": "your-warehouse-id",
  "trusted_assets": [
    {"type": "METRIC_VIEW", "name": "catalog.semantic.cost_metrics"},
    {"type": "FUNCTION", "name": "catalog.semantic.get_daily_costs"},
    {"type": "TABLE", "name": "catalog.gold.fact_usage"}
  ],
  "sample_questions": [
    "What was our total cost last month?",
    "Which workspace spent the most?"
  ]
}
```

---

## Data Preparation Requirements

### Unity Catalog Prerequisites

| Requirement | Description |
|-------------|-------------|
| **Unity Catalog enabled** | All assets must be registered in Unity Catalog |
| **Curated tables** | Clean data, no nulls in key columns, consistent formatting |
| **Clear column names** | Business-friendly names (not technical abbreviations) |
| **Rich documentation** | Comments on tables and columns for LLM understanding |

### Data Quality Standards

```sql
-- Ensure columns have descriptive comments
ALTER TABLE catalog.schema.fact_sales 
  ALTER COLUMN revenue SET COMMENT 
    'Total revenue in USD. Business: Primary sales metric. Technical: Sum of line items.';

-- Add synonyms for natural language understanding
ALTER TABLE catalog.schema.fact_sales
  ALTER COLUMN revenue SET TAGS ('synonyms' = 'sales,income,earnings');
```

### Metric View vs Table Decision

| Scenario | Use This | Why |
|----------|----------|-----|
| Aggregated KPIs | Metric View | Pre-defined dimensions/measures |
| Complex joins | Metric View | Join logic encapsulated |
| Date-filtered queries | TVF | Parameterized date handling |
| Top-N queries | TVF | LIMIT with parameters |
| Ad-hoc exploration | Table (with caution) | Flexible but risky |

### Privacy & Security Considerations

- **Row-level security**: Apply via Unity Catalog policies
- **Column masking**: Use for PII columns
- **Audit logging**: Track Genie queries via system tables
- **Access control**: Grant permissions through groups, not individuals

---

## Asset Selection Guide

| Scenario | Use |
|----------|-----|
| Standard KPIs, no params | Metric View |
| Date range, top N, filters | TVF |
| Ad-hoc exploration | Table |

---

## Common Misinterpretations

| Problem | Solution |
|---------|----------|
| Wrong asset selected | Add "BEST FOR" to comment |
| Wraps TVF in TABLE() | Add "DO NOT wrap in TABLE()" to NOTE |
| Adds GROUP BY | Add "PRE-AGGREGATED" to RETURNS |

---

## Validation Checklist

### Data Preparation
- [ ] Tables registered in Unity Catalog
- [ ] Column names are business-friendly
- [ ] All tables and columns have comments
- [ ] No null values in key columns
- [ ] Row-level security applied (if needed)

### Asset Configuration
- [ ] Asset inventory created
- [ ] All questions mapped to assets
- [ ] No overlapping coverage
- [ ] Comments follow v3.0 format
- [ ] Sample questions configured

---

## References

- [Genie Spaces](https://docs.databricks.com/genie/)
- [Trusted Assets](https://docs.databricks.com/genie/trusted-assets)
- [AI/BI Genie Overview (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/databricks/genie/)
- [Genie Data Preparation](https://learn.microsoft.com/en-us/azure/databricks/genie/prepare-data)
