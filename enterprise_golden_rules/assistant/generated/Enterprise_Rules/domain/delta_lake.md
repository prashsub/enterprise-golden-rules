# Delta Lake Golden Rules
**Rules:** DL-01..12 | **Operational Tips:** BP-01..10 | **Count:** 22 | **Version:** 5.4.0
> **Note:** BP-prefixed items are operational tips (assistant-only guidelines), not formal golden rules.

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| DL-01 | All tables in Unity Catalog (no HMS) | Critical | No Hive Metastore tables |
| DL-02 | Managed tables are the default | Critical | No LOCATION clause |
| DL-03 | External tables require approval | Required | Approval documented |
| DL-04 | All tables use Delta Lake format | Critical | USING DELTA on all tables |
| DL-05 | CLUSTER BY AUTO on all tables | Critical | No manual ZORDER |
| DL-06 | Standard TBLPROPERTIES required | Required | Layer, domain, PII tags set |
| DL-07 | LLM-friendly COMMENTs required | Required | Business + Technical format |
| DL-08 | Never use Spark caching with Delta | Required | No `.cache()` or `.persist()` |
| DL-09 | Never manually modify Delta data files | Critical | No `aws s3 rm/cp` on Delta paths |
| DL-10 | Remove legacy Delta configurations | Recommended | Unset old table properties |
| DL-11 | Enable UniForm for cross-engine reads | Recommended | `delta.universalFormat.enabledFormats` |
| DL-12 | Run ANALYZE TABLE on critical tables | Recommended | `COMPUTE STATISTICS` |
| | **Operational Tips (BP) — assistant-only guidelines, not formal golden rules** | | |
| BP-01 | Let Delta handle REFRESH TABLE | Required | Never run REFRESH TABLE |
| BP-02 | Let Delta handle partition management | Required | No `ADD PARTITION` or `MSCK REPAIR` |
| BP-03 | Use WHERE clauses, not direct partition reads | Required | Filter predicates for data skipping |
| BP-04 | Use Delta operations for data changes | Required | DELETE/UPDATE/MERGE, not file ops |
| BP-05 | MERGE must include partition filters | Required | Constrain MERGE search space |
| BP-06 | Use VACUUM via predictive optimization | Required | No manual VACUUM scheduling |
| BP-07 | Use OPTIMIZE via predictive optimization | Required | No manual OPTIMIZE jobs |
| BP-08 | Let AQE auto-tune shuffle partitions | Required | Remove `spark.sql.shuffle.partitions` |
| BP-09 | Remove `delta.targetFileSize` | Recommended | Let platform auto-tune file sizes |
| BP-10 | Verify properties after migration | Recommended | `SHOW TBLPROPERTIES` after upgrades |

---

## Detailed Rules

### DL-08: Never Use Spark Caching with Delta Tables
**Severity:** Required | **Trigger:** When you see `.cache()` or `.persist()` on a Delta-sourced DataFrame

**Rule:** Never call `.cache()` or `.persist()` on DataFrames read from Delta tables.
**Why:** Caching bypasses Delta's data skipping optimization, serves stale data after updates, and consumes executor memory unnecessarily. Delta automatically optimizes repeated reads via its own caching layer.

**Correct:**
```python
# Let Delta handle optimization via data skipping
df = spark.table("catalog.schema.my_table")
df.filter("date = '2025-01-01'").count()  # Uses data skipping
```

**Anti-Pattern:**
```python
df = spark.table("catalog.schema.my_table")
df.cache()  # Loses data skipping, may serve stale data
df.filter("date = '2025-01-01'").count()
```

---

### DL-09: Never Manually Modify Delta Data Files
**Severity:** Critical | **Trigger:** When you see any filesystem command targeting a Delta table path

**Rule:** Never directly add, delete, or modify Parquet files in a Delta table's storage location.
**Why:** Delta uses a transaction log for atomic commits. Manual file operations bypass the log, causing data inconsistency, lost records, duplicates, or query failures from missing files.

**Correct:**
```sql
-- Use Delta operations for all data changes
DELETE FROM catalog.schema.my_table WHERE condition;
INSERT INTO catalog.schema.my_table SELECT ...;
UPDATE catalog.schema.my_table SET col = value WHERE condition;
VACUUM catalog.schema.my_table RETAIN 168 HOURS;
```

**Anti-Pattern:**
```bash
# NEVER do this: bypasses transaction log
aws s3 rm s3://bucket/delta-table/part-00001.parquet
aws s3 cp data.parquet s3://bucket/delta-table/
hdfs dfs -rm /delta-table/part-00001.parquet
```

---

### DL-10: Remove Legacy Delta Configurations
**Severity:** Recommended | **Trigger:** When upgrading Databricks Runtime or enabling predictive optimization

**Rule:** Remove explicit legacy Delta configurations and let the platform use optimized defaults.
**Why:** Legacy settings like `delta.targetFileSize` or `delta.autoOptimize.optimizeWrite` may block new optimizations introduced in newer runtimes and create unnecessary configuration maintenance.

**Correct:**
```sql
-- Check current properties
SHOW TBLPROPERTIES catalog.schema.my_table;

-- Remove legacy properties
ALTER TABLE catalog.schema.my_table
UNSET TBLPROPERTIES ('delta.targetFileSize');

ALTER TABLE catalog.schema.my_table
UNSET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite');

ALTER TABLE catalog.schema.my_table
UNSET TBLPROPERTIES ('delta.autoOptimize.autoCompact');
```

**Configurations to Remove:**

| Configuration | Reason |
|---------------|--------|
| `delta.autoOptimize.optimizeWrite` | Predictive optimization handles this |
| `delta.autoOptimize.autoCompact` | Predictive optimization handles this |
| `spark.sql.shuffle.partitions` | AQE auto-tunes this |
| `delta.targetFileSize` | Automatic tuning is superior |

---

### DL-11: Enable UniForm for Cross-Engine Interoperability
**Severity:** Recommended | **Trigger:** When tables are read by non-Databricks engines (Snowflake, BigQuery, Trino)

**Rule:** Enable Delta UniForm to generate Iceberg-compatible metadata alongside Delta metadata for tables consumed by external engines.
**Why:** UniForm enables multi-engine access without data duplication while keeping Delta as the single source of truth, with no performance overhead on writes.

**Correct:**
```sql
-- New table with UniForm
CREATE TABLE catalog.schema.shared_table (...)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.universalFormat.enabledFormats' = 'iceberg'
);

-- Enable on existing table
ALTER TABLE catalog.schema.existing_table
SET TBLPROPERTIES ('delta.universalFormat.enabledFormats' = 'iceberg');
```

**When to Enable:**

| Scenario | Enable? |
|----------|---------|
| Consumed only by Databricks | No |
| Shared via Delta Sharing | No (Delta Sharing handles it) |
| Read by Snowflake, BigQuery, Trino | Yes |
| Open lakehouse with multiple engines | Yes |

---

### DL-12: Run ANALYZE TABLE on Critical Tables
**Severity:** Recommended | **Trigger:** When complex queries with multiple joins underperform

**Rule:** Run `ANALYZE TABLE ... COMPUTE STATISTICS` on performance-critical tables to collect statistics for better query optimization.
**Why:** The query optimizer uses table statistics for join ordering and predicate pushdown, improving performance of complex multi-join queries.

**Correct:**
```sql
-- Full table statistics
ANALYZE TABLE catalog.schema.fact_orders COMPUTE STATISTICS;

-- Column-specific statistics
ANALYZE TABLE catalog.schema.fact_orders
COMPUTE STATISTICS FOR COLUMNS order_date, customer_id, total_amount;

-- Verify collection
DESCRIBE EXTENDED catalog.schema.fact_orders;
```

---

## Operational Tips (BP) — Assistant-Only Guidelines

> The BP tips below are operational guidelines maintained for assistant use only. They are **not** formal golden rules.

### BP-05: MERGE Must Include Partition Filters
**Severity:** Required | **Trigger:** When writing any MERGE INTO statement

**Rule:** Add a date or partition filter to the MERGE condition to reduce the search space and avoid full table scans.
**Why:** Unconstrained MERGE scans the entire target table, resulting in slow performance and excessive I/O on large tables.

**Correct:**
```sql
-- Constrained MERGE: scans only today's data
MERGE INTO events AS target
USING updates AS source
ON target.id = source.id
   AND target.event_date = current_date()
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

**Anti-Pattern:**
```sql
-- Full table scan: slow on large tables
MERGE INTO events AS target
USING updates AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

---

## Operations You Don't Need (Operational Tips)

Delta handles these automatically — do not run them manually:

| Operation | Why Not Needed |
|-----------|----------------|
| `REFRESH TABLE` | Delta always returns current data (BP-01) |
| `ALTER TABLE ADD PARTITION` | Partitions tracked automatically (BP-02) |
| `MSCK REPAIR TABLE` | Not applicable to Delta (BP-02) |
| Direct partition reads | Use WHERE clause for data skipping (BP-03) |
| Manual `VACUUM` | Predictive optimization handles it (BP-06) |
| Manual `OPTIMIZE` | Predictive optimization handles it (BP-07) |
| `spark.sql.shuffle.partitions` | AQE auto-tunes this (BP-08) |
| `delta.targetFileSize` | Platform auto-tunes file sizes (BP-09) |

---

## Checklist
- [ ] DL-01: All tables registered in Unity Catalog (no HMS)
- [ ] DL-02: Using managed tables (no LOCATION clause) unless approved exception
- [ ] DL-03: External tables have documented approval
- [ ] DL-04: All tables use Delta Lake format (USING DELTA)
- [ ] DL-05: CLUSTER BY AUTO applied on all tables
- [ ] DL-06: Required TBLPROPERTIES set (layer, domain, contains_pii)
- [ ] DL-07: Table and column COMMENTs in LLM-friendly format
- [ ] DL-08: No `.cache()` or `.persist()` calls on Delta DataFrames
- [ ] DL-09: No direct filesystem operations on Delta table paths
- [ ] DL-10: Legacy configs (`targetFileSize`, `autoOptimize`) removed after upgrade
- [ ] DL-11: UniForm enabled on tables consumed by non-Databricks engines
- [ ] DL-12: `ANALYZE TABLE` run on performance-critical multi-join tables
- [ ] BP-01: No `REFRESH TABLE` commands (Delta always returns current data)
- [ ] BP-02: No `ADD PARTITION` or `MSCK REPAIR TABLE` commands
- [ ] BP-03: Using WHERE clauses for filtering, not direct partition reads
- [ ] BP-04: All data changes via SQL DML (DELETE/UPDATE/MERGE), not file ops
- [ ] BP-05: MERGE includes partition or date filter in join condition
- [ ] BP-06: No manual VACUUM scheduling (predictive optimization handles it)
- [ ] BP-07: No manual OPTIMIZE jobs (predictive optimization handles it)
- [ ] BP-08: `spark.sql.shuffle.partitions` removed (AQE auto-tunes)
- [ ] BP-09: `delta.targetFileSize` removed from table properties
- [ ] BP-10: `SHOW TBLPROPERTIES` verified after runtime migration
