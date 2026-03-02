# Data Pipelines Golden Rules
**Rules:** DP-01..06, SA-01..02, DA-01..04, DQ-01..04, DI-01..07 | **Count:** 23 | **Version:** 5.4.1

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| DP-01 | Medallion Architecture required | Critical | Three layers: Bronze, Silver, Gold |
| DP-02 | CDF enabled on Bronze tables | Required | `delta.enableChangeDataFeed = true` |
| DP-03 | Preserve source schema in Bronze | Required | No transforms, add metadata only |
| DP-04 | Append-only ingestion for Bronze | Required | Never overwrite Bronze data |
| DP-05 | Prefer Lakeflow Connect managed connectors | Critical | Check connector catalog first |
| DP-06 | Use incremental ingestion (not full loads) | Critical | Auto Loader or CDC, never full scan |
| ~~DA-01~~ | ~~PK/FK constraints~~ → see **DM-02**, **DM-03** | — | Moved to enterprise-architecture |
| DA-01 | Schema extracted from YAML (never generated) | Critical | Read YAML, never hardcode columns |
| SA-01 | Silver must use Lakeflow SDP with expectations | Critical | `@dlt.expect_or_drop` on all tables |
| SA-02 | Expectations must quarantine bad records | Required | Quarantine table captures failures |
| DA-02 | Surrogate keys via MD5 hash | Required | `md5(concat_ws("||", ...))` |
| DA-03 | Always deduplicate before MERGE | Critical | `dropDuplicates()` key = MERGE key |
| DA-04 | SCD Type 2 for historical dimensions | Required | `is_current`, `effective_from/to` |
| ~~DA-06~~ | ~~LLM-friendly documentation~~ → see **DL-07**, **CM-02**, **CM-03** | — | Moved to platform/enterprise |
| DQ-01 | Use `expect_or_drop` for quality-critical rules | Required | Drop invalid rows, not fail |
| DQ-02 | Use `expect_or_fail` for hard business constraints | Required | Pipeline halts on violation |
| DQ-03 | DQX framework for advanced validation | Required | YAML-driven DQX checks |
| DQ-04 | Quality metrics must be queryable | Required | System tables for pass/fail rates |
| DI-01 | Default to ingestion for production analytics | Critical | Data in Delta Lake for dashboards/ML? |
| DI-02 | Reserve federation for ad-hoc access only | Critical | No federation for dashboards/pipelines? |
| DI-03 | Delta Sharing for cross-org data exchange | Required | Cross-org uses sharing, not manual copy? |
| DI-04 | Catalog federation over query federation | Required | Direct storage access when available? |
| DI-05 | Transition federation to ingestion when stable | Required | Federated tables reviewed quarterly? |
| DI-06 | Document data access pattern per source | Required | Data Access Registry maintained? |
| DI-07 | Never federate high-volume joins/aggregations | Critical | No cross-system joins in production? |

---

## Detailed Rules

### DP-01: Medallion Architecture Required
**Severity:** Critical | **Trigger:** When creating any new data pipeline

**Rule:** All data must flow through Bronze (raw), Silver (validated), and Gold (business-ready) layers.
**Why:** Ensures auditability, data quality enforcement at each stage, and separation of concerns between ingestion and analytics.

**Correct:**
```
Bronze (raw, append-only) -> Silver (validated, deduplicated) -> Gold (aggregated, dimensional)
```

**Anti-Pattern:**
```
Source -> Single table with mixed raw and business logic
```

---

### DP-02: CDF Enabled on Bronze Tables
**Severity:** Required | **Trigger:** When creating any Bronze table

**Rule:** Every Bronze table must have Change Data Feed enabled for downstream Silver streaming.
**Why:** Silver Lakeflow SDP pipelines use `dlt.read_stream()` which requires CDF to detect incremental changes.

**Correct:**
```sql
CREATE TABLE catalog.bronze.bronze_orders (
    order_id STRING,
    amount DECIMAL(18,2),
    processed_timestamp TIMESTAMP NOT NULL,
    source_file STRING
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'layer' = 'bronze'
);
```

**Anti-Pattern:**
```sql
-- Missing CDF: Silver DLT will fail
CREATE TABLE catalog.bronze.bronze_orders (...)
USING DELTA;
```

---

### DP-05: Prefer Lakeflow Connect Managed Connectors
**Severity:** Critical | **Trigger:** When ingesting from any external source

**Rule:** Always check Lakeflow Connect for a managed connector before writing custom ingestion code.
**Why:** Managed connectors handle incremental ingestion, schema evolution, and error recovery automatically with no custom code to maintain.

**Correct:**
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

**Anti-Pattern:**
```python
# Custom JDBC pipeline when connector exists
df = spark.read.format("jdbc").option("url", jdbc_url).load()
df.write.mode("overwrite").saveAsTable("bronze_sf_account")
```

---

### SA-01: Silver Must Use Lakeflow SDP with Expectations
**Severity:** Critical | **Trigger:** When building any Silver layer transformation

**Rule:** All Silver tables must be defined as Lakeflow SDP (formerly DLT) tables with data quality expectations.
**Why:** SDP provides managed checkpointing, automatic recovery, and declarative quality enforcement that eliminates custom error-handling code.

**Correct:**
```python
import dlt
from pyspark.sql.functions import col, current_timestamp

@dlt.table(
    name="silver_customers",
    table_properties={"quality": "silver", "delta.enableChangeDataFeed": "true"},
    cluster_by_auto=True
)
@dlt.expect_all_or_drop({
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_email": "email LIKE '%@%'"
})
def silver_customers():
    return (
        dlt.read_stream("bronze_customers")
        .select(col("customer_id"), col("email"),
                current_timestamp().alias("processed_timestamp"))
    )
```

**Anti-Pattern:**
```python
# Raw Spark without quality enforcement
df = spark.readStream.table("bronze_customers")
df.writeStream.toTable("silver_customers")
```

---

### SA-02: Expectations Must Quarantine Bad Records
**Severity:** Required | **Trigger:** When using `expect_or_drop`

**Rule:** Every table that drops records via expectations must have a companion quarantine table capturing rejected rows with a reason.
**Why:** Dropped records without quarantine are silently lost, making data reconciliation and debugging impossible.

**Correct:**
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

### DA-01: Schema Extracted from YAML
**Severity:** Critical | **Trigger:** When defining Gold layer columns

**Rule:** Gold table column names and types must be extracted from YAML definitions, never generated from memory or hardcoded.
**Why:** Hardcoded column lists drift from the schema contract, causing silent data loss or incorrect joins.

**Correct:**
```python
import yaml
from pathlib import Path

def get_gold_schema(domain: str, table_name: str) -> dict:
    yaml_file = Path(f"gold_layer_design/yaml/{domain}/{table_name}.yaml")
    with open(yaml_file) as f:
        return yaml.safe_load(f)

gold_columns = [c['name'] for c in get_gold_schema("billing", "fact_usage")['columns']]
```

**Anti-Pattern:**
```python
# Hardcoded columns may be incomplete or stale
gold_columns = ["usage_date", "workspace_id"]
```

---

### DA-03: Always Deduplicate Before MERGE
**Severity:** Critical | **Trigger:** When writing a MERGE INTO statement

**Rule:** The deduplication key must match the MERGE join key, and deduplication must happen before the MERGE executes.
**Why:** Without dedup, MERGE throws `DELTA_MULTIPLE_SOURCE_ROW_MATCHING` when multiple source rows match a single target row.

**Correct:**
```python
silver_df = (
    spark.table(silver_table)
    .orderBy(col("processed_timestamp").desc())
    .dropDuplicates(["store_number"])
)
delta_gold = DeltaTable.forName(spark, gold_table)
delta_gold.alias("target").merge(
    silver_df.alias("source"),
    "target.store_number = source.store_number"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

**Anti-Pattern:**
```python
# Dedup key != MERGE key causes silent mismatches
silver_df.dropDuplicates(["store_id"])
merge_condition = "target.store_number = source.store_number"
```

---

### ~~DA-01~~: PK/FK Constraints → See DM-02, DM-03
**Severity:** Critical | **Trigger:** After Gold tables are created

> **Relocated:** This rule is now DM-02 (PRIMARY KEY) and DM-03 (FOREIGN KEY) in enterprise-architecture/04-data-modeling.md. The code pattern below is retained for reference.

**Correct:**
```sql
ALTER TABLE catalog.gold.dim_workspace
ADD CONSTRAINT pk_dim_workspace PRIMARY KEY (workspace_id) NOT ENFORCED;

ALTER TABLE catalog.gold.fact_usage
ADD CONSTRAINT fk_usage_workspace
FOREIGN KEY (workspace_id)
REFERENCES catalog.gold.dim_workspace(workspace_id) NOT ENFORCED;
```

---

### DA-02: Surrogate Keys via MD5 Hash
**Severity:** Required | **Trigger:** When creating dimension or fact surrogate keys

**Rule:** Generate surrogate keys using `md5(concat_ws("||", ...))` over the business key columns plus the effective timestamp for dimensions.
**Why:** Deterministic hash keys ensure idempotent loads and enable reproducible joins without auto-increment sequences.

**Correct:**
```python
from pyspark.sql.functions import md5, concat_ws, col

dim_df = dim_df.withColumn(
    "store_key",
    md5(concat_ws("||", col("store_number"), col("effective_from")))
)
fact_df = fact_df.withColumn(
    "usage_id",
    md5(concat_ws("||", col("workspace_id"), col("usage_date"), col("sku_id")))
)
```

---

### ~~DA-06~~: LLM-Friendly Documentation → See DL-07, CM-02, CM-03
**Severity:** Required | **Trigger:** When creating any table or column

> **Relocated:** This rule is now DL-07 (table docs) and CM-02/CM-03 (comment standards). The code pattern below is retained for reference.

**Correct:**
```sql
COMMENT 'Daily usage fact at workspace-SKU-day grain.
Business: Cost analytics and billing reports.
Technical: MD5 surrogate key, incremental from Silver.';

workspace_id STRING NOT NULL COMMENT
'FK to dim_workspace. Business: Cost allocation grouping.
Technical: Immutable after creation.';
```

---

## Data Access Decision Tree (DI-01..DI-07)

```
External data source identified
├── Owned by another org/separate metastore? → Delta Sharing (DI-03)
├── External RDBMS/DW with your credentials?
│   ├── Production dashboards/ML/pipelines? → Ingest (DI-01) via DP-05
│   ├── Ad-hoc exploration/POC? → Federate (DI-02) via PA-04
│   └── Legacy migration? → Federate first (DI-02), then ingest (DI-05)
├── Cloud storage (S3/ADLS/GCS)? → Ingest via Auto Loader (DP-05)
└── SaaS APIs? → Ingest via Lakeflow Connect (DP-05)
```

### DI-01: Default to Ingestion for Production Analytics
**Severity:** Critical | **Trigger:** When choosing how to access external data for production workloads

**Rule:** Data must reside in Delta Lake for production analytics. Use Lakeflow Connect first, then DLT + Auto Loader, then Structured Streaming.
**Why:** Only ingested Delta data gets Photon, clustering, time travel, quality expectations, and SLA-backed performance.

### DI-02: Reserve Federation for Ad-Hoc Access
**Severity:** Critical | **Trigger:** When considering Lakehouse Federation for any workload

**Rule:** Federation is for ad-hoc exploration (<1M rows, <10 queries/day) and migration staging only. Never use as primary source for dashboards or recurring pipelines.
**Why:** JDBC pushdown adds latency, loads source systems, and bypasses all Delta Lake optimizations.

**Anti-Pattern:**
```sql
-- WRONG: Recurring job reading from federated source
CREATE OR REPLACE TABLE gold.customer_360 AS
SELECT c.*, o.total_revenue
FROM legacy_crm.public.customers c  -- federated
JOIN gold.fact_orders o ON c.customer_id = o.customer_id;
-- Fix: Ingest legacy_crm.public.customers into Bronze first
```

### DI-07: Never Federate High-Volume Joins
**Severity:** Critical | **Trigger:** When joining federated tables with local Delta tables

**Rule:** Never join federated foreign tables with local Delta tables in production. Cross-system joins pull the entire federated table over JDBC.
**Why:** Performance degrades non-linearly; the federated side is fully scanned regardless of filters.

---

## Checklist
- [ ] DP-01: Pipeline follows Bronze -> Silver -> Gold medallion architecture
- [ ] DP-02: All Bronze tables have `delta.enableChangeDataFeed = true`
- [ ] DP-03: Bronze preserves source schema with metadata columns only
- [ ] DP-04: Bronze uses append-only ingestion (no overwrites)
- [ ] DP-05: Checked Lakeflow Connect catalog before custom ingestion
- [ ] DP-06: Using incremental ingestion (Auto Loader, CDC, or watermark)
- [ ] DA-01: Gold columns extracted from YAML, not hardcoded
- [ ] SA-01: Silver tables use Lakeflow SDP with expectations
- [ ] SA-02: Quarantine tables exist for all `expect_or_drop` tables
- [ ] DA-02: Surrogate keys use `md5(concat_ws("||", ...))` pattern
- [ ] DA-03: `dropDuplicates()` key matches MERGE join key
- [ ] DA-04: SCD Type 2 uses `is_current`, `effective_from`, `effective_to`
- [ ] DQ-01: Quality-critical fields use `expect_or_drop`
- [ ] DQ-02: Hard business constraints use `expect_or_fail`
- [ ] DQ-03: Advanced validations use DQX with YAML check definitions
- [ ] DQ-04: Quality metrics queryable via system tables
- [ ] DI-01: Production analytics use ingested Delta tables (not federation)
- [ ] DI-02: Federated sources are ad-hoc/exploration only (no dashboards, no jobs)
- [ ] DI-03: Cross-org data exchange uses Delta Sharing
- [ ] DI-04: Catalog federation preferred over query federation where available
- [ ] DI-05: Federated sources reviewed quarterly for transition to ingestion
- [ ] DI-06: Every external source documented in Data Access Registry
- [ ] DI-07: No cross-system joins between federated and local Delta in production
