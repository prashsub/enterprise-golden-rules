# Gold Layer Patterns

> **Document Owner:** Data Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

The Gold layer contains business-ready dimensional models optimized for analytics. This document defines patterns for YAML-driven table creation, MERGE operations, and constraint management.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **DA-01** | Schema extracted from YAML (never generated) | Critical | Performance |
| **DA-02** | Surrogate keys via MD5 hash | Required | [Performance](https://docs.databricks.com/en/transform/data-modeling) |
| **DA-03** | Always deduplicate before MERGE | Critical | [Performance](https://docs.databricks.com/en/delta/merge) |
| **DA-04** | SCD Type 2 for historical dimensions | Required | [Performance](https://docs.databricks.com/en/ingestion/lakeflow-connect/scd) |

> **Cross-references:** PK/FK constraints → see DM-02, DM-03. LLM-friendly documentation → see DL-07, CM-02, CM-03.

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Unity Catalog managed tables | DL-01..05 | [12-unity-catalog-tables](../../platform-architecture/12-unity-catalog-tables.md) |
| Dimensional modeling in Gold | DM-01..03 | [06-data-modeling](../../enterprise-architecture/06-data-modeling.md) |
| LLM-friendly table/column docs | DL-07, CM-02, CM-03 | [12-unity-catalog-tables](../../platform-architecture/12-unity-catalog-tables.md) |
| Naming conventions | NC-01, NC-02 | [05-naming-conventions](../../enterprise-architecture/05-naming-conventions.md) |

---

## Gold Layer Purpose

| Characteristic | Description |
|----------------|-------------|
| **Aggregated** | Tailored for analytics |
| **Business logic** | Domain-aligned |
| **Optimized** | For query performance |
| **Dimensional** | Facts + dimensions model |

---

## YAML-Driven Schema

**Extract column names from YAML. Never generate from memory.**

```yaml
# gold_layer_design/yaml/billing/fact_usage.yaml
table_name: fact_usage
primary_key:
  columns: ['usage_id']
foreign_keys:
  - columns: ['workspace_id']
    references: 'catalog.gold.dim_workspace'
    ref_columns: ['workspace_id']
columns:
  - name: usage_id
    type: STRING
    nullable: false
    description: "MD5 hash of workspace_id + date + sku"
  - name: workspace_id
    type: STRING
    nullable: false
```

### Extract Schema Pattern

```python
import yaml
from pathlib import Path

def get_gold_schema(domain: str, table_name: str) -> dict:
    yaml_file = Path(f"gold_layer_design/yaml/{domain}/{table_name}.yaml")
    with open(yaml_file) as f:
        return yaml.safe_load(f)

# ✅ CORRECT
gold_columns = [col['name'] for col in get_gold_schema("billing", "fact_usage")['columns']]

# ❌ WRONG
gold_columns = ["usage_date", "workspace_id"]  # Might be incomplete
```

---

## MERGE with Deduplication

**Always deduplicate Silver source before MERGE.**

```python
from delta.tables import DeltaTable

# Step 1: Deduplicate - keep latest record
silver_df = (
    spark.table(silver_table)
    .orderBy(col("processed_timestamp").desc())
    .dropDuplicates([business_key])
)

# Step 2: MERGE
delta_gold = DeltaTable.forName(spark, gold_table)

delta_gold.alias("target").merge(
    silver_df.alias("source"),
    f"target.{business_key} = source.{business_key}"
).whenMatchedUpdateAll(
).whenNotMatchedInsertAll(
).execute()
```

### Critical Rule

Deduplication key MUST match MERGE key:

```python
# ✅ CORRECT
silver_df.dropDuplicates(["store_number"])
merge_condition = "target.store_number = source.store_number"

# ❌ WRONG
silver_df.dropDuplicates(["store_id"])  # Different key!
merge_condition = "target.store_number = source.store_number"
```

---

## PK/FK Constraints

> **Note:** PK/FK constraint standards are defined in DM-02 and DM-03. The pattern below shows the Gold layer implementation.

**Apply constraints AFTER all tables exist.**

```python
def apply_constraints(spark, catalog: str, schema: str):
    # Step 1: Primary Keys
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.dim_workspace
        ADD CONSTRAINT pk_dim_workspace 
        PRIMARY KEY (workspace_id) NOT ENFORCED
    """)
    
    # Step 2: Foreign Keys (after PKs exist)
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.fact_usage
        ADD CONSTRAINT fk_usage_workspace 
        FOREIGN KEY (workspace_id) 
        REFERENCES {catalog}.{schema}.dim_workspace(workspace_id) 
        NOT ENFORCED
    """)
```

---

## Surrogate Keys

```python
from pyspark.sql.functions import md5, concat_ws

# Dimension: business key + effective timestamp
dim_df = dim_df.withColumn(
    "store_key",
    md5(concat_ws("||", col("store_number"), col("effective_from")))
)

# Fact: all grain columns
fact_df = fact_df.withColumn(
    "usage_id",
    md5(concat_ws("||", col("workspace_id"), col("usage_date"), col("sku_id")))
)
```

---

## SCD Type 2 Pattern

```python
updates_df = (
    silver_df
    .orderBy(col("processed_timestamp").desc())
    .dropDuplicates([business_key])
    .withColumn("surrogate_key", 
               md5(concat_ws("||", col(business_key), col("processed_timestamp"))))
    .withColumn("effective_from", col("processed_timestamp"))
    .withColumn("effective_to", lit(None).cast("timestamp"))
    .withColumn("is_current", lit(True))
)

delta_gold.alias("target").merge(
    updates_df.alias("source"),
    f"target.{business_key} = source.{business_key} AND target.is_current = true"
).whenMatchedUpdate(set={
    "record_updated_timestamp": "source.record_updated_timestamp"
}).whenNotMatchedInsertAll(
).execute()
```

---

## SCD Type 1 Pattern (Overwrite)

Use for corrections or attributes where history is not needed.

```python
# SCD Type 1: simple overwrite — no effective_from/to columns needed
delta_gold.alias("target").merge(
    updates_df.alias("source"),
    f"target.{business_key} = source.{business_key}"
).whenMatchedUpdateAll(
).whenNotMatchedInsertAll(
).execute()
```

---

## SCD Type 3 Pattern (Previous Value Column)

Stores only the most recent prior value alongside the current value.

```sql
CREATE TABLE gold.dim_customer_type3 (
    customer_key STRING NOT NULL,
    customer_id STRING NOT NULL,
    current_segment STRING NOT NULL COMMENT 'Current customer segment.',
    previous_segment STRING COMMENT 'Segment before most recent change.',
    segment_change_date DATE COMMENT 'Date of most recent segment change.',
    CONSTRAINT pk_dim_customer_type3 PRIMARY KEY (customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

```python
delta_gold.alias("target").merge(
    updates_df.alias("source"),
    "target.customer_id = source.customer_id"
).whenMatchedUpdate(
    condition="target.current_segment != source.current_segment",
    set={
        "previous_segment": "target.current_segment",
        "current_segment": "source.current_segment",
        "segment_change_date": "current_date()",
    }
).whenNotMatchedInsert(values={
    "customer_key": "source.customer_key",
    "customer_id": "source.customer_id",
    "current_segment": "source.current_segment",
    "previous_segment": "lit(None)",
    "segment_change_date": "lit(None)",
}).execute()
```

---

## SCD Type 6 Pattern (Hybrid 1+2+3)

Combines Type 2 history rows with a `current_<attr>` column overwritten on all rows for fast current-state queries.

```sql
CREATE TABLE gold.dim_customer_type6 (
    customer_key STRING NOT NULL COMMENT 'Surrogate key. MD5 of customer_id + effective_from.',
    customer_id STRING NOT NULL COMMENT 'Business key.',
    historical_segment STRING NOT NULL COMMENT 'Segment as of this row version (Type 2 value).',
    current_segment STRING NOT NULL COMMENT 'Latest segment, updated on ALL rows for this customer (Type 1 overwrite).',
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    is_current BOOLEAN NOT NULL,
    CONSTRAINT pk_dim_customer_type6 PRIMARY KEY (customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

```python
# Step 1: Expire current rows and insert new version (standard Type 2)
delta_gold.alias("target").merge(
    updates_df.alias("source"),
    "target.customer_id = source.customer_id AND target.is_current = true"
).whenMatchedUpdate(set={
    "is_current": "lit(False)",
    "effective_to": "source.effective_from",
}).whenNotMatchedInsertAll(
).execute()

# Step 2: Overwrite current_segment on ALL rows for changed customers (Type 1 overwrite)
spark.sql("""
    UPDATE gold.dim_customer_type6 t
    SET t.current_segment = (
        SELECT s.historical_segment
        FROM gold.dim_customer_type6 s
        WHERE s.customer_id = t.customer_id AND s.is_current = true
    )
    WHERE t.customer_id IN (
        SELECT customer_id FROM gold.dim_customer_type6 WHERE is_current = true
    )
""")
```

---

## Periodic Snapshot Fact Pattern

One row per entity per time period. Used for balances, inventory levels, and other measurements that are valid at a point in time.

```sql
CREATE TABLE gold.fact_account_monthly (
    snapshot_month DATE NOT NULL COMMENT 'First day of month. Grain: one row per account per month.',
    account_key STRING NOT NULL,
    account_balance DECIMAL(18,2) NOT NULL COMMENT 'Semi-additive: do not SUM across time.',
    total_deposits DECIMAL(18,2) NOT NULL COMMENT 'Additive: deposits during this month.',
    total_withdrawals DECIMAL(18,2) NOT NULL COMMENT 'Additive: withdrawals during this month.',
    transaction_count INT NOT NULL,
    CONSTRAINT pk_fact_account_monthly
        PRIMARY KEY (snapshot_month, account_key) NOT ENFORCED,
    CONSTRAINT fk_account
        FOREIGN KEY (account_key) REFERENCES gold.dim_account(account_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

```python
# Periodic snapshot: full reload of the period slice, not a MERGE
snapshot_df = (
    spark.table("silver.transactions")
    .filter(col("txn_date").between(period_start, period_end))
    .groupBy("account_key")
    .agg(
        last("balance").alias("account_balance"),
        sum("deposit_amount").alias("total_deposits"),
        sum("withdrawal_amount").alias("total_withdrawals"),
        count("*").alias("transaction_count"),
    )
    .withColumn("snapshot_month", lit(period_start))
)

snapshot_df.write.mode("append").saveAsTable("gold.fact_account_monthly")
```

---

## Accumulating Snapshot Fact Pattern

One row per process instance (e.g., an order). Rows are **updated** as the process progresses through milestones.

```sql
CREATE TABLE gold.fact_order_fulfillment (
    order_key STRING NOT NULL COMMENT 'Grain: one row per order lifecycle.',
    order_date_key DATE NOT NULL,
    ship_date_key DATE COMMENT 'NULL until shipped.',
    delivery_date_key DATE COMMENT 'NULL until delivered.',
    return_date_key DATE COMMENT 'NULL unless returned.',
    customer_key STRING NOT NULL,
    order_total DECIMAL(18,2) NOT NULL,
    days_to_ship INT COMMENT 'Calculated: ship_date - order_date.',
    days_to_deliver INT COMMENT 'Calculated: delivery_date - ship_date.',
    current_status STRING NOT NULL COMMENT 'ordered | shipped | delivered | returned',
    CONSTRAINT pk_fact_order PRIMARY KEY (order_key) NOT ENFORCED,
    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_key) REFERENCES gold.dim_customer(customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

```python
# Accumulating snapshot: MERGE to update milestone columns as events arrive
delta_gold.alias("target").merge(
    milestone_df.alias("source"),
    "target.order_key = source.order_key"
).whenMatchedUpdate(set={
    "ship_date_key": "COALESCE(source.ship_date_key, target.ship_date_key)",
    "delivery_date_key": "COALESCE(source.delivery_date_key, target.delivery_date_key)",
    "return_date_key": "COALESCE(source.return_date_key, target.return_date_key)",
    "days_to_ship": "DATEDIFF(COALESCE(source.ship_date_key, target.ship_date_key), target.order_date_key)",
    "days_to_deliver": "DATEDIFF(COALESCE(source.delivery_date_key, target.delivery_date_key), COALESCE(source.ship_date_key, target.ship_date_key))",
    "current_status": "source.current_status",
}).whenNotMatchedInsertAll(
).execute()
```

---

## Factless Fact Table Pattern

Records events or coverage where the occurrence itself is the measurement — no numeric facts.

```sql
-- Event-tracking factless fact: student attended a class session
CREATE TABLE gold.fact_student_attendance (
    attendance_date_key DATE NOT NULL,
    student_key STRING NOT NULL,
    class_key STRING NOT NULL,
    instructor_key STRING NOT NULL,
    CONSTRAINT pk_fact_attendance
        PRIMARY KEY (attendance_date_key, student_key, class_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;

-- Coverage factless fact: which promotions apply to which products
CREATE TABLE gold.fact_promo_coverage (
    promotion_key STRING NOT NULL,
    product_key STRING NOT NULL,
    store_key STRING NOT NULL,
    start_date_key DATE NOT NULL,
    end_date_key DATE NOT NULL,
    CONSTRAINT pk_fact_promo_coverage
        PRIMARY KEY (promotion_key, product_key, store_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

> **Querying factless facts:** Use `COUNT(*)` to measure activity. To find what did **not** happen, LEFT JOIN from a coverage factless fact and filter for NULLs.

---

## Degenerate Dimension Pattern

High-cardinality identifiers (order number, invoice number) that have no additional attributes live directly on the fact table.

```sql
CREATE TABLE gold.fact_order_line (
    order_line_key STRING NOT NULL,
    order_number STRING NOT NULL COMMENT 'Degenerate dimension — no separate dim table.',
    invoice_number STRING COMMENT 'Degenerate dimension.',
    order_date_key DATE NOT NULL,
    customer_key STRING NOT NULL,
    product_key STRING NOT NULL,
    quantity INT NOT NULL,
    line_amount DECIMAL(18,2) NOT NULL,
    CONSTRAINT pk_fact_order_line PRIMARY KEY (order_line_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

---

## Junk Dimension Pattern

Consolidate low-cardinality flags and indicators into a single dimension to keep the fact table lean.

```sql
CREATE TABLE gold.junk_order_flags (
    order_flags_key STRING NOT NULL
        COMMENT 'Surrogate key. MD5 hash of all flag values.',
    is_gift_wrapped BOOLEAN NOT NULL,
    is_expedited BOOLEAN NOT NULL,
    is_taxable BOOLEAN NOT NULL,
    payment_method STRING NOT NULL COMMENT 'credit_card | debit | cash | check',
    order_channel STRING NOT NULL COMMENT 'web | mobile | store | phone',
    CONSTRAINT pk_junk_order_flags PRIMARY KEY (order_flags_key) NOT ENFORCED
)
USING DELTA;
```

```python
# Build junk dimension from distinct flag combinations
junk_df = (
    spark.table("silver.orders")
    .select("is_gift_wrapped", "is_expedited", "is_taxable", "payment_method", "order_channel")
    .distinct()
    .withColumn("order_flags_key",
        md5(concat_ws("||",
            col("is_gift_wrapped").cast("string"),
            col("is_expedited").cast("string"),
            col("is_taxable").cast("string"),
            col("payment_method"),
            col("order_channel"),
        ))
    )
)

junk_df.write.mode("overwrite").saveAsTable("gold.junk_order_flags")
```

---

## Conformed Dimension Pattern

Conformed dimensions are shared across multiple fact tables. Build them once, reference them everywhere.

```sql
-- Conformed dim_date: used by fact_sales, fact_inventory, fact_returns, etc.
CREATE TABLE gold.dim_date (
    date_key DATE NOT NULL COMMENT 'Conformed date key. Join target for all fact tables.',
    day_of_week INT NOT NULL,
    day_name STRING NOT NULL,
    month_number INT NOT NULL,
    month_name STRING NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    fiscal_quarter INT NOT NULL,
    fiscal_year INT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    CONSTRAINT pk_dim_date PRIMARY KEY (date_key) NOT ENFORCED
)
USING DELTA;
```

```sql
-- Role-playing: same conformed dim_date joined under different roles
SELECT
    f.order_total,
    od.month_name AS order_month,
    sd.month_name AS ship_month,
    dd.month_name AS delivery_month
FROM gold.fact_order_fulfillment f
JOIN gold.dim_date od ON f.order_date_key = od.date_key
LEFT JOIN gold.dim_date sd ON f.ship_date_key = sd.date_key
LEFT JOIN gold.dim_date dd ON f.delivery_date_key = dd.date_key;
```

---

## LLM-Friendly Documentation

> **Note:** Documentation standards are defined in DL-07, CM-02, and CM-03. The patterns below show Gold layer examples.

### Table Comment Pattern

```
[Description]. Business: [use cases]. Technical: [grain, source].
```

```sql
COMMENT 'Daily usage fact at workspace-SKU-day grain. 
Business: Cost analytics and billing reports. 
Technical: MD5 surrogate key, incremental from Silver.';
```

### Column Comment Pattern

```sql
workspace_id STRING NOT NULL COMMENT 
'FK to dim_workspace. Business: Cost allocation grouping. 
Technical: Immutable after creation.';
```

---

## Validation Checklist

### Pre-Development
- [ ] Gold YAML exists
- [ ] All columns defined
- [ ] PK/FK specified

### Pre-Merge
- [ ] Schema validation passed
- [ ] Deduplication key = MERGE key
- [ ] All columns mapped

### Post-Deployment
- [ ] Table has COMMENT
- [ ] PK constraint applied
- [ ] FK constraints applied

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Column does not exist` | Generated name | Extract from YAML |
| `DELTA_MULTIPLE_SOURCE_ROW_MATCHING` | No dedup | Add `dropDuplicates()` |
| `Table does not have PK` | FK before PK | Apply PKs first |

---

## References

- [Medallion Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion)
- [Delta MERGE](https://docs.delta.io/latest/delta-update.html)
- [SCD Type 2](https://www.databricks.com/blog/dimensional-modeling-delta-lake)
- [Data Modeling Standards](../../enterprise-architecture/04-data-modeling.md)
