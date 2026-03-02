# Module 2: Data Engineering Best Practices

## Bronze Layer, Silver Layer, and Delta Lake Patterns

**Duration:** 12 hours  
**Prerequisites:** Module 1 completed  
**Outcome:** Master Bronze and Silver layer implementation

---

## Learning Objectives

By the end of this module, you will be able to:

1. Design and implement Bronze layer ingestion patterns
2. Enable and consume Change Data Feed (CDF)
3. Build streaming DLT pipelines for Silver layer
4. Implement data quality expectations
5. Design quarantine patterns for failed records
6. Apply deduplication strategies

---

## Section 1: Bronze Layer Patterns (2 hours)

### Bronze Layer Principles

| Principle | Implementation |
|-----------|----------------|
| **Immutable** | Append-only, never update raw data |
| **Complete** | Capture all records including errors |
| **Traceable** | Include ingestion metadata |
| **Performant** | CDF enabled for downstream |

### Standard Bronze Table Template

```sql
CREATE TABLE bronze.raw_orders (
    -- Source data (preserve original format)
    order_id STRING,
    customer_id STRING,
    order_date STRING,
    total_amount STRING,
    status STRING,
    
    -- Ingestion metadata
    _source_file STRING COMMENT 'Source file path',
    _ingestion_timestamp TIMESTAMP COMMENT 'When record was ingested',
    _batch_id STRING COMMENT 'Batch identifier for tracking'
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'layer' = 'bronze',
    'source_system' = 'OrderManagementSystem',
    'domain' = 'sales',
    'business_owner' = 'Sales Operations',
    'technical_owner' = 'Data Engineering'
)
COMMENT 'Bronze layer raw orders from OMS. Append-only with CDF enabled.';
```

### Ingestion Patterns

#### Pattern 1: Auto Loader (Recommended)

```python
# Databricks notebook source
from pyspark.sql.functions import current_timestamp, input_file_name, lit
import uuid

def ingest_bronze_orders(spark, source_path, bronze_table):
    """Ingest raw orders using Auto Loader."""
    
    batch_id = str(uuid.uuid4())
    
    df = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", f"{source_path}/_schema")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(source_path)
        .withColumn("_source_file", input_file_name())
        .withColumn("_ingestion_timestamp", current_timestamp())
        .withColumn("_batch_id", lit(batch_id))
    )
    
    query = (
        df.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{bronze_table}/_checkpoint")
        .trigger(availableNow=True)
        .toTable(bronze_table)
    )
    
    query.awaitTermination()
    print(f"✓ Ingested batch {batch_id} to {bronze_table}")
```

#### Pattern 2: Batch Ingestion

```python
def ingest_bronze_batch(spark, source_df, bronze_table):
    """Ingest batch data to Bronze layer."""
    
    batch_id = str(uuid.uuid4())
    
    bronze_df = (
        source_df
        .withColumn("_ingestion_timestamp", current_timestamp())
        .withColumn("_batch_id", lit(batch_id))
    )
    
    # Always append, never overwrite
    bronze_df.write.format("delta").mode("append").saveAsTable(bronze_table)
    
    print(f"✓ Appended {bronze_df.count()} records to {bronze_table}")
```

### Hands-On Lab 2.1: Create Bronze Layer

```python
# Create Bronze table for customer data
spark.sql("""
CREATE TABLE IF NOT EXISTS bronze.raw_customers (
    customer_id STRING,
    first_name STRING,
    last_name STRING,
    email STRING,
    phone STRING,
    created_date STRING,
    _source_file STRING,
    _ingestion_timestamp TIMESTAMP,
    _batch_id STRING
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'layer' = 'bronze',
    'source_system' = 'CRM'
)
""")

# Insert sample data
spark.sql("""
INSERT INTO bronze.raw_customers VALUES
    ('C001', 'John', 'Doe', 'john.doe@email.com', '555-0101', '2024-01-15', 'sample.json', current_timestamp(), 'batch-001'),
    ('C002', 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', '2024-01-16', 'sample.json', current_timestamp(), 'batch-001'),
    ('C001', 'John', 'Doe', 'john.d@newemail.com', '555-0103', '2024-02-01', 'sample2.json', current_timestamp(), 'batch-002')
""")

-- Note: C001 appears twice (different email) - this is expected in Bronze!
```

---

## Section 2: Change Data Feed (CDF) (1 hour)

### What is CDF?

Change Data Feed captures row-level changes in Delta tables:

| Change Type | `_change_type` Value |
|-------------|---------------------|
| Insert | `insert` |
| Update (before) | `update_preimage` |
| Update (after) | `update_postimage` |
| Delete | `delete` |

### Enabling CDF

```sql
-- Enable on new table
CREATE TABLE bronze.orders (...)
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Enable on existing table
ALTER TABLE bronze.orders SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');
```

### Reading CDF (Batch)

```python
# Read changes since a specific version
changes_df = (
    spark.read
    .format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", 0)
    .table("bronze.orders")
)

# Read changes since a timestamp
changes_df = (
    spark.read
    .format("delta")
    .option("readChangeFeed", "true")
    .option("startingTimestamp", "2024-01-01 00:00:00")
    .table("bronze.orders")
)
```

### Reading CDF (Streaming)

```python
# Stream changes for real-time processing
stream_df = (
    spark.readStream
    .format("delta")
    .option("readChangeFeed", "true")
    .table("bronze.orders")
)

# Process changes (e.g., filter for new inserts)
new_records = stream_df.filter(col("_change_type") == "insert")
```

### Hands-On Lab 2.2: CDF Processing

```python
# 1. Verify CDF is enabled
spark.sql("SHOW TBLPROPERTIES bronze.raw_customers").show()

# 2. Make some changes to create CDF records
spark.sql("""
UPDATE bronze.raw_customers 
SET email = 'john.updated@email.com'
WHERE customer_id = 'C001' AND email = 'john.doe@email.com'
""")

# 3. Read the change feed
changes = (
    spark.read
    .format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", 0)
    .table("bronze.raw_customers")
)

changes.select("customer_id", "email", "_change_type", "_commit_version").show()
```

---

## Section 3: Delta Live Tables (DLT) Pipeline Design (3 hours)

### DLT Overview

Delta Live Tables provides declarative ETL with automatic:
- Dependency management
- Quality enforcement
- Pipeline orchestration
- Monitoring and recovery

### DLT Table Types

| Type | Use Case | Syntax |
|------|----------|--------|
| **Streaming** | Real-time, incremental | `@dlt.table` with `dlt.read_stream()` |
| **Materialized** | Batch, full refresh | `@dlt.table` with `spark.read()` |
| **Views** | Intermediate logic | `@dlt.view` |

### Standard Silver DLT Pattern

```python
# Databricks notebook source
import dlt
from pyspark.sql.functions import col, current_timestamp, when

# Configuration from pipeline settings
catalog = spark.conf.get("catalog", "enterprise_catalog")
bronze_schema = spark.conf.get("bronze_schema", "bronze")
silver_schema = spark.conf.get("silver_schema", "silver")

@dlt.table(
    name="silver_customers",
    comment="Silver layer customer records - cleaned and deduplicated",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.enableRowTracking": "true",
        "delta.autoOptimize.autoCompact": "true",
        "delta.autoOptimize.optimizeWrite": "true",
        "layer": "silver",
        "source_table": "bronze.raw_customers",
        "domain": "customer"
    }
)
@dlt.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_email", "email IS NOT NULL AND email LIKE '%@%'")
@dlt.expect("valid_name", "first_name IS NOT NULL OR last_name IS NOT NULL")
def silver_customers():
    """Transform raw customers to silver with quality enforcement."""
    
    bronze_table = f"{catalog}.{bronze_schema}.raw_customers"
    
    return (
        dlt.read_stream(bronze_table)
        # Standardize data
        .withColumn("first_name", col("first_name").cast("string"))
        .withColumn("last_name", col("last_name").cast("string"))
        .withColumn("email", col("email").cast("string"))
        # Add processing timestamp
        .withColumn("processed_timestamp", current_timestamp())
        # Select final columns
        .select(
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "created_date",
            "processed_timestamp",
            "_ingestion_timestamp"
        )
    )
```

### DLT Pipeline Configuration (Asset Bundle)

```yaml
# resources/silver/silver_dlt_pipeline.yml
resources:
  pipelines:
    silver_dlt_pipeline:
      name: "[${bundle.target}] Silver Layer Pipeline"
      
      # Unity Catalog integration
      catalog: ${var.catalog}
      schema: ${var.silver_schema}
      
      # Pipeline libraries
      libraries:
        - notebook:
            path: ../src/silver/silver_customers.py
        - notebook:
            path: ../src/silver/silver_orders.py
      
      # Configuration passed to notebooks
      configuration:
        catalog: ${var.catalog}
        bronze_schema: ${var.bronze_schema}
        silver_schema: ${var.silver_schema}
      
      # Compute settings
      serverless: true
      photon: true
      channel: CURRENT
      continuous: false
      development: true
      edition: ADVANCED
      
      # Notifications
      notifications:
        - alerts:
            - on-update-failure
            - on-flow-failure
          email_recipients:
            - data-team@company.com
```

### Hands-On Lab 2.3: Build DLT Pipeline

```python
# 1. Create DLT notebook: silver_customers.py
# Databricks notebook source
import dlt
from pyspark.sql.functions import col, current_timestamp, upper, lower

@dlt.table(
    name="silver_customers",
    comment="Silver customers with quality enforcement",
    table_properties={"layer": "silver"}
)
@dlt.expect_or_drop("valid_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_email", "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'")
def silver_customers():
    return (
        spark.readStream.table("bronze.raw_customers")
        .withColumn("first_name", upper(col("first_name")))
        .withColumn("email", lower(col("email")))
        .withColumn("processed_timestamp", current_timestamp())
    )

# 2. Create quarantine table
@dlt.table(
    name="silver_customers_quarantine",
    comment="Quarantined customer records"
)
def silver_customers_quarantine():
    return (
        spark.readStream.table("bronze.raw_customers")
        .filter(
            col("customer_id").isNull() | 
            ~col("email").rlike("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$")
        )
        .withColumn("quarantine_reason", 
            when(col("customer_id").isNull(), "Missing customer_id")
            .otherwise("Invalid email format"))
        .withColumn("quarantine_timestamp", current_timestamp())
    )
```

---

## Section 4: Data Quality Expectations (2 hours)

### Expectation Types

| Type | Behavior | Use Case |
|------|----------|----------|
| `@dlt.expect` | Warn only | Soft constraints, monitoring |
| `@dlt.expect_or_drop` | Drop failing rows | Hard constraints |
| `@dlt.expect_or_fail` | Fail pipeline | Critical data quality |

### Expectation Examples

```python
# Basic null check
@dlt.expect_or_drop("not_null_id", "id IS NOT NULL")

# Range validation
@dlt.expect("valid_amount", "amount BETWEEN 0 AND 1000000")

# Pattern matching
@dlt.expect_or_drop("valid_phone", "phone RLIKE '^[0-9]{3}-[0-9]{3}-[0-9]{4}$'")

# Business rule
@dlt.expect("valid_date_sequence", "start_date <= end_date")

# Complex condition
@dlt.expect_or_drop("valid_status", 
    "status IN ('pending', 'processing', 'completed', 'cancelled')")
```

### Multiple Expectations

```python
@dlt.table(name="silver_orders")
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_date", "order_date IS NOT NULL")
@dlt.expect("positive_amount", "total_amount > 0")
@dlt.expect("valid_status", "status IN ('pending', 'completed', 'cancelled')")
@dlt.expect("reasonable_quantity", "quantity BETWEEN 1 AND 1000")
def silver_orders():
    return dlt.read_stream("bronze.raw_orders")
```

### Hands-On Lab 2.4: Implement Expectations

```python
# Create comprehensive expectation set for orders
@dlt.table(
    name="silver_orders",
    comment="Silver orders with full quality enforcement",
    table_properties={"layer": "silver"}
)
# Critical - must have these
@dlt.expect_or_drop("has_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("has_customer", "customer_id IS NOT NULL")
@dlt.expect_or_drop("has_date", "order_date IS NOT NULL")

# Important - monitor but don't drop
@dlt.expect("positive_total", "total_amount > 0")
@dlt.expect("valid_status", "status IN ('new', 'processing', 'shipped', 'delivered', 'cancelled')")
@dlt.expect("reasonable_total", "total_amount < 100000")

# Nice to have - just for monitoring
@dlt.expect("has_shipping", "shipping_address IS NOT NULL")
def silver_orders():
    return (
        dlt.read_stream("bronze.raw_orders")
        .withColumn("order_date", col("order_date").cast("date"))
        .withColumn("total_amount", col("total_amount").cast("decimal(18,2)"))
        .withColumn("processed_timestamp", current_timestamp())
    )
```

---

## Section 5: Quarantine Patterns (2 hours)

### Quarantine Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                     QUARANTINE PATTERN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Bronze Data                                                   │
│       │                                                         │
│       ▼                                                         │
│   ┌───────────────────────────────────────┐                    │
│   │         Quality Checks                 │                    │
│   │   @dlt.expect_or_drop conditions       │                    │
│   └───────────────┬───────────────────────┘                    │
│                   │                                             │
│         ┌────────┴────────┐                                    │
│         ▼                 ▼                                    │
│   ┌──────────┐      ┌──────────────┐                          │
│   │ PASSED   │      │  FAILED      │                          │
│   │ Records  │      │  Records     │                          │
│   └────┬─────┘      └──────┬───────┘                          │
│        │                   │                                   │
│        ▼                   ▼                                   │
│   Silver Table      Quarantine Table                          │
│   (production)      (investigation)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Complete Quarantine Implementation

```python
# Main table with expectations
@dlt.table(
    name="silver_customers",
    comment="Production silver customers"
)
@dlt.expect_or_drop("valid_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_email", "email IS NOT NULL AND email LIKE '%@%'")
def silver_customers():
    return (
        dlt.read_stream("bronze.raw_customers")
        .withColumn("processed_timestamp", current_timestamp())
    )

# Quarantine table for failed records
@dlt.table(
    name="silver_customers_quarantine",
    comment="Quarantined customer records for investigation",
    table_properties={"layer": "silver", "purpose": "quarantine"}
)
def silver_customers_quarantine():
    """Capture all records that fail quality checks."""
    
    from pyspark.sql.functions import when, array, lit
    
    return (
        dlt.read_stream("bronze.raw_customers")
        # Apply inverse of main table's conditions
        .filter(
            col("customer_id").isNull() | 
            col("email").isNull() | 
            ~col("email").like("%@%")
        )
        # Add quarantine metadata
        .withColumn("quarantine_reasons", 
            array(
                when(col("customer_id").isNull(), lit("Missing customer_id")),
                when(col("email").isNull(), lit("Missing email")),
                when(~col("email").like("%@%"), lit("Invalid email format"))
            )
        )
        .withColumn("quarantine_timestamp", current_timestamp())
        .withColumn("original_source", col("_source_file"))
    )
```

### Quarantine Monitoring

```sql
-- Check quarantine volume
SELECT 
    DATE(quarantine_timestamp) as quarantine_date,
    COUNT(*) as quarantine_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM silver.customers_quarantine
GROUP BY DATE(quarantine_timestamp)
ORDER BY quarantine_date DESC;

-- Analyze failure reasons
SELECT 
    explode(quarantine_reasons) as reason,
    COUNT(*) as count
FROM silver.customers_quarantine
WHERE quarantine_timestamp >= current_date - 7
GROUP BY 1
ORDER BY count DESC;
```

---

## Section 6: Deduplication Strategies (2 hours)

### Why Deduplication Matters

| Problem | Impact |
|---------|--------|
| Duplicate source records | Inflated metrics |
| Multiple versions | MERGE failures |
| Late-arriving data | Processing conflicts |

### Golden Rule: Deduplicate Before MERGE

```python
# Standard deduplication pattern
silver_df = (
    spark.table("bronze.raw_customers")
    .orderBy(col("_ingestion_timestamp").desc())  # Latest first
    .dropDuplicates(["customer_id"])  # Keep first (latest)
)
```

### Deduplication Patterns

#### Pattern 1: Simple Business Key

```python
def deduplicate_by_business_key(df, business_key, timestamp_col):
    """Keep latest record per business key."""
    return (
        df
        .orderBy(col(timestamp_col).desc())
        .dropDuplicates([business_key])
    )

# Usage
deduped_df = deduplicate_by_business_key(
    silver_df, 
    "customer_id", 
    "processed_timestamp"
)
```

#### Pattern 2: Composite Key

```python
def deduplicate_composite_key(df, key_columns, timestamp_col):
    """Deduplicate on composite business key."""
    return (
        df
        .orderBy(col(timestamp_col).desc())
        .dropDuplicates(key_columns)
    )

# Usage for fact tables
deduped_df = deduplicate_composite_key(
    fact_df,
    ["store_id", "product_id", "transaction_date"],
    "processed_timestamp"
)
```

#### Pattern 3: With Logging

```python
def deduplicate_with_metrics(spark, table_name, business_key, timestamp_col):
    """Deduplicate and log metrics."""
    
    raw_df = spark.table(table_name)
    original_count = raw_df.count()
    
    deduped_df = (
        raw_df
        .orderBy(col(timestamp_col).desc())
        .dropDuplicates([business_key])
    )
    
    dedupe_count = deduped_df.count()
    duplicates_removed = original_count - dedupe_count
    
    print(f"Deduplication Results:")
    print(f"  Original: {original_count:,}")
    print(f"  After:    {dedupe_count:,}")
    print(f"  Removed:  {duplicates_removed:,} ({duplicates_removed/original_count*100:.1f}%)")
    
    return deduped_df
```

### Hands-On Lab 2.6: Implement Deduplication

```python
# 1. Check for duplicates
duplicate_check = spark.sql("""
    SELECT customer_id, COUNT(*) as cnt
    FROM bronze.raw_customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
""")
duplicate_check.show()

# 2. Implement deduplication
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

# Method 1: orderBy + dropDuplicates (recommended)
deduped_df = (
    spark.table("bronze.raw_customers")
    .orderBy(col("_ingestion_timestamp").desc())
    .dropDuplicates(["customer_id"])
)

# 3. Verify deduplication
print(f"Original count: {spark.table('bronze.raw_customers').count()}")
print(f"Deduplicated count: {deduped_df.count()}")

# 4. Complete MERGE with deduplication
from delta.tables import DeltaTable

gold_table = "gold.dim_customer"
delta_gold = DeltaTable.forName(spark, gold_table)

delta_gold.alias("target").merge(
    deduped_df.alias("source"),
    "target.customer_id = source.customer_id"
).whenMatchedUpdateAll(
).whenNotMatchedInsertAll(
).execute()
```

---

## Module 2 Assessment

### Quiz (25 questions, 80% to pass)

**Sample Questions:**

1. What table property enables Change Data Feed?
   - a) `delta.cdf.enabled`
   - b) `delta.enableChangeDataFeed` ✓
   - c) `delta.changeDataFeed`

2. Which expectation type drops failing records?
   - a) `@dlt.expect`
   - b) `@dlt.expect_or_drop` ✓
   - c) `@dlt.expect_or_warn`

3. What must happen before every Delta MERGE?
   - a) Schema validation
   - b) Deduplication ✓
   - c) Compression

### Practical Project

**Build a Complete Silver Pipeline:**

1. Create Bronze table with CDF
2. Build DLT pipeline with 5+ expectations
3. Implement quarantine pattern
4. Add deduplication before MERGE
5. Document all transformations

---

## Next Module

[Module 3: Gold Layer & Semantic](./73-module-gold-layer-semantic.md)

---

**Module 2 Complete!**

You now can:
- Build Bronze ingestion patterns
- Use Change Data Feed effectively
- Create DLT streaming pipelines
- Implement data quality expectations
- Design quarantine patterns
- Apply deduplication strategies
