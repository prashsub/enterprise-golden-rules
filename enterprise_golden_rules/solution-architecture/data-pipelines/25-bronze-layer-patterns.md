# Bronze Layer Patterns

> **Document Owner:** Data Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

The Bronze layer is the raw data landing zone in the Medallion Architecture. This document defines patterns for ingestion, table creation, and configuration for downstream streaming.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **DP-01** | Medallion Architecture required | Critical | [OpEx](https://docs.databricks.com/en/lakehouse/medallion) |
| **DP-02** | CDF enabled on Bronze tables | Required | [Reliability](https://docs.databricks.com/en/delta/delta-change-data-feed) |
| **DP-03** | Preserve source schema | Required | [OpEx](https://docs.databricks.com/en/lakehouse/medallion) |
| **DP-04** | Append-only ingestion | Required | [OpEx](https://docs.databricks.com/en/lakehouse/medallion) |
| **DP-05** | Prefer Lakeflow Connect managed connectors | Critical | [OpEx](https://docs.databricks.com/en/ingestion/overview) |
| **DP-06** | Use incremental ingestion (not full loads) | Critical | [OpEx](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader) |

> **Cross-reference:** All tables use Delta Lake format — see [DL-04](../../platform-architecture/12-unity-catalog-tables.md).

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Unity Catalog managed tables | DL-01..05 | [12-unity-catalog-tables](../../platform-architecture/12-unity-catalog-tables.md) |
| DLT expectations | DQ-01 | [09-data-quality](../../enterprise-architecture/09-data-quality.md) |
| Table & column comments | CM-02, CM-03 | [07-metadata-comments](../../enterprise-architecture/07-metadata-comments.md) |
| Required tags | TG-01 | [04-tagging-strategy](../../enterprise-architecture/04-tagging-strategy.md) |
| Data access pattern decisions | DI-01, DI-06 | [16-data-access-patterns](../../platform-architecture/16-data-access-patterns.md) |

---

## Bronze Layer Purpose

| Characteristic | Description |
|----------------|-------------|
| **Raw state** | Maintains original formats from source |
| **Append-only** | Grows over time, never modified |
| **Single source of truth** | Preserves data for audit |
| **Minimal transformation** | Only add metadata columns |

---

## Ingestion Strategy

**Always prefer managed connectors over custom pipelines:**

| Priority | Approach | Use For |
|----------|----------|---------|
| 1 | **Lakeflow Connect** | Salesforce, ServiceNow, SQL Server, Workday |
| 2 | **DLT + Auto Loader** | Files, message buses |
| 3 | **Structured Streaming** | Complex real-time only |

**Avoid:** Custom batch pipelines with full loads.

### Ingestion Decision Tree

```
Has Lakeflow Connect connector?
├── YES → Use managed connector (incremental by default)
└── NO → Does source support CDC?
    ├── YES → Use Streaming or DLT with CDC
    └── NO → Use watermark-based incremental
```

---

## Table Template

```sql
CREATE OR REPLACE TABLE ${catalog}.${bronze_schema}.bronze_orders (
    -- Business columns (preserve source)
    order_id STRING,
    customer_id STRING,
    amount DECIMAL(18,2),
    
    -- Metadata columns (always include)
    processed_timestamp TIMESTAMP NOT NULL,
    source_file STRING,
    batch_id STRING
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'layer' = 'bronze',
    'source_system' = 'retail',
    'domain' = 'sales'
)
COMMENT 'Bronze layer orders from POS. CDF enabled for Silver streaming.';
```

---

## Ingestion Patterns

### Pattern 1: Lakeflow Connect (Preferred)

```yaml
resources:
  pipelines:
    salesforce_ingestion:
      name: "[${bundle.target}] Salesforce Bronze"
      catalog: ${var.catalog}
      schema: ${var.bronze_schema}
      serverless: true
      
      ingestion_definition:
        connection_name: "salesforce_prod"
        objects:
          - table:
              source_table: "Account"
              destination_table: "bronze_sf_account"
```

### Pattern 2: Auto Loader (Triggered)

```python
stream = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .load(source_path)
    .withColumn("processed_timestamp", current_timestamp())
    .withColumn("source_file", input_file_name())
)

stream.writeStream \
    .format("delta") \
    .option("checkpointLocation", checkpoint_path) \
    .trigger(availableNow=True) \
    .toTable(target_table)
```

### Pattern 3: DLT Auto Loader

```python
@dlt.table(
    name="bronze_events",
    table_properties={
        "delta.enableChangeDataFeed": "true",
        "layer": "bronze"
    }
)
def bronze_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("s3://landing/events/")
        .withColumn("_ingested_at", current_timestamp())
    )
```

---

## Synthetic Data (Faker)

For development, use Faker with intentional test scenarios:

```python
from faker import Faker

fake = Faker()
Faker.seed(42)  # Reproducible

# Include ~5% invalid data for testing DLT expectations
is_invalid = random.random() < 0.05

customer = {
    "customer_id": f"CUST-{i:08d}",
    "email": None if is_invalid else fake.email(),
    "processed_timestamp": datetime.now()
}
```

---

## Validation Checklist

### Ingestion Strategy
- [ ] Evaluated Lakeflow Connect for this source
- [ ] Using incremental (not full load)
- [ ] Checkpointing configured

### Table Configuration
- [ ] CDF enabled
- [ ] CLUSTER BY AUTO
- [ ] Metadata columns included
- [ ] Table and column COMMENTs

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Silver DLT fails | CDF not enabled | Add `delta.enableChangeDataFeed` |
| Data loss | Using overwrite | Always use append |
| Schema errors | Auto Loader drift | Configure `schemaEvolutionMode` |

---

## Related Documents

- [Silver Layer Patterns](26-silver-layer-patterns.md)
- [Gold Layer Patterns](27-gold-layer-patterns.md)

---

## References

- [Medallion Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion)
- [Lakeflow Connect](https://learn.microsoft.com/en-us/azure/databricks/ingestion/overview)
- [Auto Loader](https://docs.databricks.com/ingestion/auto-loader/)
