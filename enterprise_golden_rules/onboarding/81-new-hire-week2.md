# New Hire Onboarding - Week 2

## Hands-On Labs

**Duration:** Week 2 (Days 6-10)  
**Goal:** Build real components following our golden rules

---

## Week 2 Overview

| Day | Focus | Lab |
|-----|-------|-----|
| 6 | Bronze Layer | Create Bronze table with Faker data |
| 7 | Silver Layer | Build DLT pipeline with expectations |
| 8 | Gold Layer | YAML-driven table + MERGE |
| 9 | Semantic Layer | Create TVF and Metric View |
| 10 | Integration | Deploy complete pipeline |

---

## Day 6: Bronze Layer Lab

### Objective
Create a Bronze table with synthetic data generation following our standards.

### Lab 6.1: Create Bronze Table

**File:** `src/bronze/lab_setup_tables.py`

```python
# Databricks notebook source

def get_parameters():
    """Get job parameters from widgets."""
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("bronze_schema")
    return catalog, schema


def create_bronze_orders(spark, catalog: str, schema: str):
    """
    Create Bronze orders table following our standards.
    
    RULES APPLIED:
    - DL-04: Delta Lake format
    - DP-02: CDF enabled
    - DL-07: LLM-friendly comments
    """
    spark.sql(f"""
        CREATE OR REPLACE TABLE {catalog}.{schema}.bronze_orders (
            order_id STRING NOT NULL COMMENT 'Unique order identifier',
            customer_id STRING NOT NULL COMMENT 'Customer who placed the order',
            order_date DATE NOT NULL COMMENT 'Date order was placed',
            product_id STRING NOT NULL COMMENT 'Product ordered',
            quantity INT COMMENT 'Number of units ordered',
            unit_price DECIMAL(10,2) COMMENT 'Price per unit in USD',
            total_amount DECIMAL(10,2) COMMENT 'Total order amount',
            processed_timestamp TIMESTAMP COMMENT 'When record was ingested'
        )
        USING DELTA
        CLUSTER BY AUTO
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true',
            'layer' = 'bronze',
            'domain' = 'sales'
        )
        COMMENT 'Bronze layer orders from e-commerce system. Raw data with CDF enabled for Silver layer streaming.'
    """)
    print(f"✓ Created {catalog}.{schema}.bronze_orders")


def main():
    catalog, schema = get_parameters()
    spark = SparkSession.builder.appName("Lab - Bronze Setup").getOrCreate()
    
    create_bronze_orders(spark, catalog, schema)
    
    dbutils.notebook.exit("SUCCESS")


if __name__ == "__main__":
    main()
```

### Lab 6.2: Generate Synthetic Data

**File:** `src/bronze/lab_generate_data.py`

```python
# Databricks notebook source
from faker import Faker
from pyspark.sql.types import *
import random
from datetime import datetime, timedelta


def get_parameters():
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("bronze_schema")
    num_records = int(dbutils.widgets.get("num_records"))
    return catalog, schema, num_records


def generate_orders(spark, num_records: int):
    """
    Generate synthetic order data.
    
    Includes intentional bad data to test Silver layer expectations.
    """
    fake = Faker()
    
    orders = []
    for i in range(num_records):
        # 5% chance of corrupt data (tests DLT expectations)
        is_corrupt = random.random() < 0.05
        
        order = {
            "order_id": f"ORD-{i:06d}",
            "customer_id": f"CUST-{random.randint(1, 1000):04d}",
            "order_date": fake.date_between(start_date="-90d", end_date="today"),
            "product_id": f"PROD-{random.randint(1, 100):03d}",
            "quantity": 0 if is_corrupt else random.randint(1, 10),  # Bad: 0 quantity
            "unit_price": -10.0 if is_corrupt else round(random.uniform(10, 500), 2),  # Bad: negative
            "total_amount": None,  # Calculate in Silver
            "processed_timestamp": datetime.now()
        }
        orders.append(order)
    
    schema = StructType([
        StructField("order_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("order_date", DateType(), False),
        StructField("product_id", StringType(), False),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("total_amount", DoubleType(), True),
        StructField("processed_timestamp", TimestampType(), True),
    ])
    
    return spark.createDataFrame(orders, schema)


def main():
    catalog, schema, num_records = get_parameters()
    spark = SparkSession.builder.appName("Lab - Generate Data").getOrCreate()
    
    orders_df = generate_orders(spark, num_records)
    
    orders_df.write.mode("append").saveAsTable(f"{catalog}.{schema}.bronze_orders")
    
    print(f"✓ Generated {num_records} records")
    print(f"  ~5% have intentional quality issues for testing")
    
    dbutils.notebook.exit("SUCCESS")


if __name__ == "__main__":
    main()
```

### Day 6 Checklist
- [ ] Bronze table created with all required properties
- [ ] CDF enabled (`delta.enableChangeDataFeed = true`)
- [ ] CLUSTER BY AUTO applied
- [ ] Table has COMMENT
- [ ] All columns have COMMENT
- [ ] Synthetic data generated with ~5% bad records

---

## Day 7: Silver Layer Lab

### Objective
Create a DLT pipeline with expectations to validate Bronze data.

### Lab 7.1: DLT Pipeline with Expectations

**File:** `src/silver/lab_silver_orders.py`

```python
# Databricks notebook source
import dlt
from pyspark.sql.functions import col, when, current_timestamp


# Get configuration (DLT uses spark.conf, not widgets!)
catalog = spark.conf.get("catalog")
bronze_schema = spark.conf.get("bronze_schema")
silver_schema = spark.conf.get("silver_schema")


@dlt.table(
    name="silver_orders",
    comment="""
    Validated orders from Bronze layer.
    Business: Clean, validated orders for analytics. Invalid records quarantined.
    Technical: Streaming from Bronze with DLT expectations. Calculates total_amount.
    """,
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.enableRowTracking": "true",
        "layer": "silver",
        "source_table": "bronze_orders"
    },
    cluster_by_auto=True
)
@dlt.expect_all_or_drop({
    "valid_order_id": "order_id IS NOT NULL",
    "valid_customer_id": "customer_id IS NOT NULL",
    "positive_quantity": "quantity > 0",
    "positive_price": "unit_price > 0"
})
def silver_orders():
    """
    Transform Bronze orders to Silver with validation.
    
    RULES APPLIED:
    - DP-03: DLT with expectations
    - DA-04: Quarantine bad records (expect_or_drop)
    """
    return (
        dlt.read_stream(f"{catalog}.{bronze_schema}.bronze_orders")
        .withColumn(
            "total_amount",
            col("quantity") * col("unit_price")
        )
        .withColumn("processed_timestamp", current_timestamp())
    )


@dlt.table(
    name="silver_orders_quarantine",
    comment="Quarantined orders that failed validation"
)
def silver_orders_quarantine():
    """Capture failed records for investigation."""
    return (
        dlt.read_stream(f"{catalog}.{bronze_schema}.bronze_orders")
        .filter(
            (col("order_id").isNull()) |
            (col("quantity") <= 0) |
            (col("unit_price") <= 0)
        )
        .withColumn(
            "quarantine_reason",
            when(col("order_id").isNull(), "null_order_id")
            .when(col("quantity") <= 0, "invalid_quantity")
            .when(col("unit_price") <= 0, "invalid_price")
            .otherwise("unknown")
        )
        .withColumn("quarantine_timestamp", current_timestamp())
    )
```

### Lab 7.2: DLT Pipeline YAML

**File:** `resources/lab/silver_dlt_pipeline.yml`

```yaml
resources:
  pipelines:
    lab_silver_pipeline:
      name: "[${bundle.target}] Lab - Silver DLT Pipeline"
      
      catalog: ${var.catalog}
      schema: ${var.silver_schema}
      
      libraries:
        - notebook:
            path: ../src/silver/lab_silver_orders.py
      
      configuration:
        catalog: ${var.catalog}
        bronze_schema: ${var.bronze_schema}
        silver_schema: ${var.silver_schema}
      
      serverless: true
      photon: true
      channel: CURRENT
      development: true
      edition: ADVANCED
      
      tags:
        layer: silver
        lab: week2
```

### Day 7 Checklist
- [ ] DLT pipeline created
- [ ] Uses `spark.conf.get()` for parameters (not widgets)
- [ ] Expectations validate all business rules
- [ ] `expect_all_or_drop` drops invalid records
- [ ] Quarantine table captures failed records
- [ ] Pipeline runs successfully
- [ ] ~5% of records quarantined (from intentional bad data)

---

## Day 8: Gold Layer Lab

### Objective
Create Gold table from YAML schema and implement MERGE pattern.

### Lab 8.1: Create YAML Schema

**File:** `gold_layer_design/yaml/lab/fact_orders.yaml`

```yaml
table_name: fact_orders
comment: "Gold layer orders fact table. Business: Validated order metrics for sales analysis."

primary_key:
  columns: ['order_key']

foreign_keys:
  - columns: ['customer_id']
    references: 'catalog.gold.dim_customer'
    ref_columns: ['customer_id']

columns:
  - name: order_key
    type: STRING
    nullable: false
    description: "Surrogate key. MD5 hash of order_id."
  
  - name: order_id
    type: STRING
    nullable: false
    description: "Business key from source system."
  
  - name: customer_id
    type: STRING
    nullable: false
    description: "Foreign key to dim_customer."
  
  - name: order_date
    type: DATE
    nullable: false
    description: "Date order was placed."
  
  - name: product_id
    type: STRING
    nullable: false
    description: "Product ordered."
  
  - name: quantity
    type: INT
    nullable: false
    description: "Units ordered."
  
  - name: unit_price
    type: DECIMAL(10,2)
    nullable: false
    description: "Price per unit in USD."
  
  - name: total_amount
    type: DECIMAL(10,2)
    nullable: false
    description: "Total order value (quantity * unit_price)."
  
  - name: record_created_timestamp
    type: TIMESTAMP
    nullable: false
    description: "When record was created in Gold."
  
  - name: record_updated_timestamp
    type: TIMESTAMP
    nullable: false
    description: "When record was last updated."
```

### Lab 8.2: Create Gold Table from YAML

**File:** `src/gold/lab_setup_gold.py`

```python
# Databricks notebook source
import yaml
from pathlib import Path


def get_parameters():
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("gold_schema")
    return catalog, schema


def load_schema(yaml_path: str) -> dict:
    """Load table schema from YAML (Rule DP-04: Never generate!)"""
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def create_table_from_yaml(spark, catalog: str, schema: str, yaml_path: str):
    """
    Create Gold table from YAML schema.
    
    RULES APPLIED:
    - DP-04: Schema from YAML (never generate)
    - DP-06: PK/FK constraints
    """
    config = load_schema(yaml_path)
    
    # Build column definitions
    col_defs = []
    for col in config['columns']:
        nullable = "" if col.get('nullable', True) == False else ""
        if not col.get('nullable', True):
            nullable = "NOT NULL"
        desc = col.get('description', '').replace("'", "''")
        col_defs.append(f"{col['name']} {col['type']} {nullable} COMMENT '{desc}'")
    
    columns_sql = ",\n        ".join(col_defs)
    
    table_name = config['table_name']
    comment = config.get('comment', '').replace("'", "''")
    
    ddl = f"""
        CREATE OR REPLACE TABLE {catalog}.{schema}.{table_name} (
            {columns_sql}
        )
        USING DELTA
        CLUSTER BY AUTO
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'layer' = 'gold'
        )
        COMMENT '{comment}'
    """
    
    spark.sql(ddl)
    print(f"✓ Created {catalog}.{schema}.{table_name}")
    
    # Add PK constraint
    pk_cols = config.get('primary_key', {}).get('columns', [])
    if pk_cols:
        pk_sql = f"""
            ALTER TABLE {catalog}.{schema}.{table_name}
            ADD CONSTRAINT pk_{table_name} 
            PRIMARY KEY ({', '.join(pk_cols)}) NOT ENFORCED
        """
        spark.sql(pk_sql)
        print(f"✓ Added PK constraint on {pk_cols}")


def main():
    catalog, schema = get_parameters()
    spark = SparkSession.builder.appName("Lab - Gold Setup").getOrCreate()
    
    # Create table from YAML
    create_table_from_yaml(
        spark, catalog, schema,
        "gold_layer_design/yaml/lab/fact_orders.yaml"
    )
    
    dbutils.notebook.exit("SUCCESS")


if __name__ == "__main__":
    main()
```

### Lab 8.3: MERGE with Deduplication

**File:** `src/gold/lab_merge_gold.py`

```python
# Databricks notebook source
from pyspark.sql.functions import col, md5, concat_ws, current_timestamp
from delta.tables import DeltaTable


def get_parameters():
    catalog = dbutils.widgets.get("catalog")
    silver_schema = dbutils.widgets.get("silver_schema")
    gold_schema = dbutils.widgets.get("gold_schema")
    return catalog, silver_schema, gold_schema


def merge_fact_orders(spark, catalog: str, silver_schema: str, gold_schema: str):
    """
    Merge orders from Silver to Gold with deduplication.
    
    RULES APPLIED:
    - DP-05: Always deduplicate before MERGE
    - DP-04: Schema from YAML
    """
    silver_table = f"{catalog}.{silver_schema}.silver_orders"
    gold_table = f"{catalog}.{gold_schema}.fact_orders"
    
    # Read Silver
    silver_raw = spark.table(silver_table)
    
    # CRITICAL: Deduplicate before MERGE (Rule DP-05)
    silver_df = (
        silver_raw
        .orderBy(col("processed_timestamp").desc())
        .dropDuplicates(["order_id"])  # Business key
    )
    
    # Prepare updates
    updates_df = (
        silver_df
        .withColumn("order_key", md5(col("order_id")))
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
        .select(
            "order_key", "order_id", "customer_id", "order_date",
            "product_id", "quantity", "unit_price", "total_amount",
            "record_created_timestamp", "record_updated_timestamp"
        )
    )
    
    # MERGE
    delta_gold = DeltaTable.forName(spark, gold_table)
    
    delta_gold.alias("target").merge(
        updates_df.alias("source"),
        "target.order_id = source.order_id"
    ).whenMatchedUpdate(set={
        "quantity": "source.quantity",
        "unit_price": "source.unit_price",
        "total_amount": "source.total_amount",
        "record_updated_timestamp": "source.record_updated_timestamp"
    }).whenNotMatchedInsertAll(
    ).execute()
    
    count = updates_df.count()
    print(f"✓ Merged {count} records into fact_orders")


def main():
    catalog, silver_schema, gold_schema = get_parameters()
    spark = SparkSession.builder.appName("Lab - Gold Merge").getOrCreate()
    
    merge_fact_orders(spark, catalog, silver_schema, gold_schema)
    
    dbutils.notebook.exit("SUCCESS")


if __name__ == "__main__":
    main()
```

### Day 8 Checklist
- [ ] YAML schema created
- [ ] Table created from YAML (not hardcoded)
- [ ] PK constraint applied
- [ ] Deduplication before MERGE (orderBy + dropDuplicates)
- [ ] Dedup key matches MERGE key
- [ ] MERGE runs successfully

---

## Day 9: Semantic Layer Lab

### Objective
Create a TVF and Metric View following our patterns.

### Lab 9.1: Create TVF

**File:** `src/semantic/lab_tvf.sql`

```sql
-- Lab: Create TVF following v3.0 comment format
CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.get_order_summary(
    start_date STRING DEFAULT '2024-01-01',
    end_date STRING DEFAULT '2024-12-31',
    limit_rows STRING DEFAULT '100'
)
RETURNS TABLE (
    order_date DATE,
    order_count BIGINT,
    total_revenue DECIMAL(18,2),
    avg_order_value DECIMAL(18,2)
)
COMMENT '
• PURPOSE: Get daily order summary metrics for a date range.

• BEST FOR: Daily sales | Revenue trends | Order volume | Average order value

• NOT FOR: Individual order details (query fact_orders directly)

• RETURNS: PRE-AGGREGATED rows (order_date, order_count, total_revenue, avg_order_value)

• PARAMS: start_date (YYYY-MM-DD, default: 2024-01-01), end_date (YYYY-MM-DD, default: 2024-12-31), limit_rows (default: 100)

• SYNTAX: SELECT * FROM get_order_summary(''2024-01-01'', ''2024-12-31'', ''30'')

• NOTE: DO NOT wrap in TABLE(). DO NOT add GROUP BY - data is already aggregated.
'
RETURN
WITH daily_metrics AS (
    SELECT 
        order_date,
        COUNT(*) as order_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value,
        ROW_NUMBER() OVER (ORDER BY order_date DESC) as rn
    FROM ${catalog}.${gold_schema}.fact_orders
    WHERE order_date >= CAST(start_date AS DATE)
      AND order_date <= CAST(end_date AS DATE)
    GROUP BY order_date
)
SELECT 
    order_date,
    order_count,
    total_revenue,
    avg_order_value
FROM daily_metrics
WHERE rn <= CAST(limit_rows AS INT);
```

### Day 9 Checklist
- [ ] TVF uses STRING for date parameters
- [ ] Required params before optional
- [ ] Uses ROW_NUMBER + WHERE (not LIMIT with param)
- [ ] v3.0 comment format complete
- [ ] NOTE includes "DO NOT wrap in TABLE()"
- [ ] TVF executes successfully

---

## Day 10: Integration Lab

### Objective
Deploy the complete pipeline using Asset Bundles.

### Lab 10.1: Create Asset Bundle Job

**File:** `resources/lab/lab_complete_pipeline.yml`

```yaml
resources:
  jobs:
    lab_complete_pipeline:
      name: "[${bundle.target}] Lab - Complete Pipeline"
      
      # Serverless environment (Rule PA-03)
      environments:
        - environment_key: "default"
          spec:
            environment_version: "4"
            dependencies:
              - "Faker==22.0.0"
      
      tasks:
        # Step 1: Setup Bronze
        - task_key: setup_bronze
          environment_key: default
          notebook_task:
            notebook_path: ../src/bronze/lab_setup_tables.py
            base_parameters:
              catalog: ${var.catalog}
              bronze_schema: ${var.bronze_schema}
        
        # Step 2: Generate Data
        - task_key: generate_data
          depends_on:
            - task_key: setup_bronze
          environment_key: default
          notebook_task:
            notebook_path: ../src/bronze/lab_generate_data.py
            base_parameters:
              catalog: ${var.catalog}
              bronze_schema: ${var.bronze_schema}
              num_records: "1000"
        
        # Step 3: Run Silver DLT
        - task_key: run_silver_dlt
          depends_on:
            - task_key: generate_data
          pipeline_task:
            pipeline_id: ${resources.pipelines.lab_silver_pipeline.id}
        
        # Step 4: Setup Gold
        - task_key: setup_gold
          depends_on:
            - task_key: run_silver_dlt
          environment_key: default
          notebook_task:
            notebook_path: ../src/gold/lab_setup_gold.py
            base_parameters:
              catalog: ${var.catalog}
              gold_schema: ${var.gold_schema}
        
        # Step 5: Merge Gold
        - task_key: merge_gold
          depends_on:
            - task_key: setup_gold
          environment_key: default
          notebook_task:
            notebook_path: ../src/gold/lab_merge_gold.py
            base_parameters:
              catalog: ${var.catalog}
              silver_schema: ${var.silver_schema}
              gold_schema: ${var.gold_schema}
      
      tags:
        lab: week2
        layer: all
```

### Lab 10.2: Deploy and Run

```bash
# Validate bundle
databricks bundle validate

# Deploy
databricks bundle deploy -t dev

# Run complete pipeline
databricks bundle run -t dev lab_complete_pipeline
```

### Day 10 Checklist
- [ ] Bundle validates successfully
- [ ] Deployment succeeds
- [ ] Pipeline runs end-to-end
- [ ] Bronze → Silver → Gold data flows correctly
- [ ] ~5% bad records in quarantine
- [ ] TVF returns data

---

## Week 2 Assessment

### Self-Review Questions

1. Why do we use `CLUSTER BY AUTO` instead of specifying columns?
2. What happens if you skip deduplication before MERGE?
3. Why do DLT pipelines use `spark.conf.get()` instead of `dbutils.widgets.get()`?
4. What is the purpose of the quarantine table?
5. Why must TVF date parameters be STRING type?

### Practical Assessment

Your mentor will review your code for:
- [ ] All golden rules followed
- [ ] Code is properly documented
- [ ] Error handling is in place
- [ ] Naming conventions followed
- [ ] YAML schema used (no hardcoding)

---

## Next Steps

After completing Week 2:
1. Schedule review with mentor
2. Begin working on first assigned project
3. Join #data-platform-help for questions
4. Complete [Certification Assessment](42-certification-assessment.md)

---

## Resources

- [Golden Rules Reference](../README.md)
- [Quick Reference Cards](../appendix/quick-reference-cards.md)
- [Deployment Checklist](../templates/deployment-checklist.md)
