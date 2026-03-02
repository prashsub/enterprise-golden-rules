# Silver Layer Patterns

> **Document Owner:** Data Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

The Silver layer transforms raw Bronze data into validated, cleaned, and deduplicated datasets using **Lakeflow Spark Declarative Pipelines (SDP)** (formerly known as Delta Live Tables/DLT) with data quality expectations.

> **Reference:** [Lakeflow Spark Declarative Pipelines](https://learn.microsoft.com/en-us/azure/databricks/ldp/)

**Why Lakeflow SDP?**
- **Open Source:** Built on Apache Spark Declarative Pipelines
- **Managed Service:** Automatic checkpointing, recovery, and scaling
- **Built-in Quality:** Expectations for declarative data quality enforcement
- **Disaster Recovery:** Managed checkpoint state for RPO/RTO compliance

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **SA-01** | Silver must use Lakeflow SDP with expectations | Critical | [Performance](https://docs.databricks.com/en/delta-live-tables/expectations) |
| **SA-02** | Expectations must quarantine bad records | Required | [Performance](https://docs.databricks.com/en/delta-live-tables/expectations) |

> **Cross-references:** DQX advanced validation → see DQ-02. Pure Python files → see PY-02.

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Unity Catalog managed tables | DL-01..05 | [12-unity-catalog-tables](../../platform-architecture/12-unity-catalog-tables.md) |
| DLT expectations & DQX | DQ-01, DQ-02, DQ-04 | [09-data-quality](../../enterprise-architecture/09-data-quality.md) |
| Pure Python files | PY-02 | [16-python-development](../../platform-architecture/16-python-development.md) |
| Table & column comments | CM-02, CM-03 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |

---

## Silver Layer Purpose

| Characteristic | Description |
|----------------|-------------|
| **Data cleaning** | Deduplication, normalization |
| **Quality enforcement** | Schema, nulls, validation rules |
| **Non-aggregated** | At least one validated view per entity |
| **Streaming** | Incremental from Bronze via CDF |

---

## Lakeflow SDP Pattern

```python
import dlt  # Lakeflow SDP uses the 'dlt' module
from pyspark.sql.functions import col, current_timestamp

@dlt.table(
    name="silver_customers",
    comment="Validated customer records from Bronze.",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "layer": "silver"
    },
    cluster_by_auto=True
)
@dlt.expect_all_or_drop({
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_email": "email LIKE '%@%'"
})
def silver_customers():
    return (
        dlt.read_stream("bronze_customers")
        .select(
            col("customer_id"),
            col("email"),
            current_timestamp().alias("processed_timestamp")
        )
    )
```

---

## Expectation Types

| Type | Behavior | Use When |
|------|----------|----------|
| `@dlt.expect` | Log, keep record | Warning only |
| `@dlt.expect_or_drop` | Drop violating rows | Quality critical |
| `@dlt.expect_or_fail` | Fail pipeline | Hard constraint |
| `@dlt.expect_all_or_drop` | Multiple rules | Multiple checks |

---

## Quarantine Pattern

```python
@dlt.table(name="silver_orders")
@dlt.expect_all_or_drop({
    "valid_order_id": "order_id IS NOT NULL",
    "valid_amount": "amount > 0"
})
def silver_orders():
    return dlt.read_stream("bronze_orders")


@dlt.table(name="silver_orders_quarantine")
def silver_orders_quarantine():
    return (
        dlt.read_stream("bronze_orders")
        .filter((col("order_id").isNull()) | (col("amount") <= 0))
        .withColumn("quarantine_reason",
            when(col("order_id").isNull(), "null_order_id")
            .otherwise("invalid_amount"))
    )
```

---

## DQX Framework

Use DQX for advanced validation with detailed diagnostics.

### Installation

```yaml
environments:
  - environment_key: "default"
    spec:
      environment_version: "4"
      dependencies:
        - "dqx"
```

### Check Definition (YAML)

```yaml
checks:
  - name: amount_positive
    criticality: error
    check:
      function: is_not_less_than
      arguments:
        column: amount
        limit: 0
```

### DQX API Reference

| Function | Parameters |
|----------|------------|
| `is_not_null` | `column` |
| `is_not_less_than` | `column`, `limit` |
| `is_in_list` | `column`, `allowed` |
| `matches_regex` | `column`, `regex` |

---

## Pure Python Modules

Shared code must be pure Python (no notebook header):

```python
# ❌ WRONG: Cannot import
# Databricks notebook source
def helper(): pass

# ✅ CORRECT: Can import
"""Utility functions."""
def helper(): pass
```

---

## Table Properties

```python
table_properties={
    "quality": "silver",
    "delta.enableChangeDataFeed": "true",
    "delta.enableRowTracking": "true",
    "delta.autoOptimize.optimizeWrite": "true",
    "layer": "silver",
    "source_table": "bronze_orders",
    "domain": "sales"
}
```

---

## Validation Checklist

- [ ] Pipeline uses Direct Publishing Mode
- [ ] All tables have `cluster_by_auto=True`
- [ ] Critical rules use `expect_or_drop`
- [ ] Quarantine tables capture failures
- [ ] Shared modules are pure Python

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Notebook header | Remove `# Databricks notebook source` |
| Stream vs batch mismatch | Wrong read method | Use `read_stream` |
| DQX function error | Wrong name | Use exact API names |

---

## References

### Lakeflow SDP (Primary)
- [Lakeflow Spark Declarative Pipelines](https://learn.microsoft.com/en-us/azure/databricks/ldp/)
- [Manage data quality with expectations](https://learn.microsoft.com/en-us/azure/databricks/ldp/expectations)
- [Lakeflow SDP Concepts](https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts)
- [Configure pipelines](https://learn.microsoft.com/en-us/azure/databricks/ldp/configure-pipeline)

### Architecture & Quality
- [Medallion Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion)
- [DQX Framework](https://databrickslabs.github.io/dqx/)

### Related Patterns
- [Streaming Production Patterns](28-streaming-production-patterns.md)
