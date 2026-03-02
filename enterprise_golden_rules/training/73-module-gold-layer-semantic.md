# Module 3: Gold Layer & Semantic Layer

## Dimensional Modeling, TVFs, and Metric Views

**Duration:** 13 hours  
**Prerequisites:** Modules 1-2 completed  
**Outcome:** Build business-ready Gold layer with semantic components

---

## Learning Objectives

By the end of this module, you will be able to:

1. Apply the four-step dimensional design process
2. Design star schema dimensional models with proper grain, fact types, and additivity
3. Implement SCD Type 0, 1, 2, 3, and 6 patterns
4. Apply PK/FK constraints in Unity Catalog
5. Build Delta MERGE pipelines
6. Create Table-Valued Functions (TVFs) for Genie
7. Design Metric Views for AI/BI
8. Build an Enterprise Bus Matrix and identify conformed dimensions
9. Avoid the top 10 dimensional modeling mistakes

---

## Section 1: Dimensional Modeling (3 hours)

### Star Schema Fundamentals

The Gold layer follows dimensional modeling:

```
                    ┌──────────────┐
                    │  dim_date    │
                    │  (date_key)  │
                    └──────┬───────┘
                           │
┌──────────────┐     ┌─────┴─────────┐     ┌──────────────┐
│ dim_customer │─────│  fact_sales   │─────│ dim_product  │
│(customer_key)│     │ (fact table)  │     │(product_key) │
└──────────────┘     └───────────────┘     └──────────────┘
                           │
                    ┌──────┴───────┐
                    │  dim_store   │
                    │ (store_key)  │
                    └──────────────┘
```

### Dimensional Design Process

Before writing any SQL, complete these four steps in order:

| Step | Question | Outcome |
|------|----------|---------|
| **1. Select the business process** | What operational activity are we modeling? | e.g., "retail sales" |
| **2. Declare the grain** | What does one row represent? | e.g., "one row per scan of an item at the register" |
| **3. Identify the dimensions** | Who, what, where, when, why, how? | `dim_date`, `dim_customer`, `dim_product`, `dim_store` |
| **4. Identify the facts** | What numeric measurements occur at this grain? | `quantity`, `unit_price`, `net_revenue`, `discount_amount` |

> **The grain is the single most important decision.** Every fact must be true at the declared grain. Mixing grains in one table is the #1 dimensional modeling mistake.

### Key Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Surrogate Key** | System-generated unique ID | `customer_key` (MD5 hash) |
| **Business Key** | Natural key from source | `customer_id` (from CRM) |
| **Fact Table** | Measures + FK references | `fact_sales` (revenue, qty) |
| **Dimension** | Descriptive attributes | `dim_customer` (name, email) |
| **Grain** | Level of detail — what one row represents | One row per transaction |
| **Conformed Dimension** | Shared dimension used across multiple facts | `dim_date` used by sales, inventory, returns |

### Fact Table Types

| Type | Description | Example | Key Characteristic |
|------|-------------|---------|-------------------|
| **Transaction** | One row per business event | `fact_sales` | Append-only, additive measures |
| **Periodic Snapshot** | One row per entity per time period | `fact_account_monthly` | Full reload per period, semi-additive balances |
| **Accumulating Snapshot** | One row per process lifecycle | `fact_order_fulfillment` | Rows are updated as milestones occur |
| **Factless** | No numeric measures | `fact_student_attendance` | Records events or coverage — query with `COUNT(*)` |

### Fact Additivity

| Category | Can SUM Across All Dims? | Example | Rule |
|----------|:------------------------:|---------|------|
| **Additive** | Yes | `total_amount`, `quantity` | SUM always valid |
| **Semi-Additive** | Not across time | `account_balance` | Use AVG or latest across time |
| **Non-Additive** | No | `unit_price`, `discount_pct` | Store numerator + denominator for ratios |

### Dimension Table Design

```sql
-- Dimension with SCD Type 2 (history tracking)
CREATE TABLE gold.dim_customer (
    -- Surrogate key (PRIMARY KEY)
    customer_key STRING NOT NULL 
        COMMENT 'Surrogate key - unique per version. Generated from customer_id + effective_from.',
    
    -- Business key
    customer_id BIGINT NOT NULL 
        COMMENT 'Business key from source system. Same across all versions.',
    
    -- Descriptive attributes
    customer_name STRING 
        COMMENT 'Full customer name. Business: For display in reports.',
    email STRING 
        COMMENT 'Primary email address. Contains PII.',
    customer_segment STRING 
        COMMENT 'Customer tier (Gold, Silver, Bronze). Business: For targeting.',
    
    -- SCD Type 2 columns
    effective_from TIMESTAMP NOT NULL 
        COMMENT 'When this version became active.',
    effective_to TIMESTAMP 
        COMMENT 'When this version was superseded. NULL = current.',
    is_current BOOLEAN NOT NULL 
        COMMENT 'TRUE = current version. Use for joins.',
    
    -- Audit columns
    record_created_timestamp TIMESTAMP 
        COMMENT 'When record was created in Gold.',
    record_updated_timestamp TIMESTAMP 
        COMMENT 'When record was last updated.',
    
    -- Constraints
    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'layer' = 'gold',
    'domain' = 'customer',
    'scd_type' = '2',
    'contains_pii' = 'true'
)
COMMENT 'Customer dimension with SCD Type 2 for historical tracking. 
Business: Master customer data for all analytics. 
Technical: Join using customer_key, filter is_current=true for latest.';
```

### Fact Table Design

```sql
-- Fact table with measures and FK references
CREATE TABLE gold.fact_sales (
    -- Surrogate FKs (link to dimensions)
    customer_key STRING NOT NULL 
        COMMENT 'FK to dim_customer.customer_key',
    product_key STRING NOT NULL 
        COMMENT 'FK to dim_product.product_key',
    store_key STRING NOT NULL 
        COMMENT 'FK to dim_store.store_key',
    date_key INT NOT NULL 
        COMMENT 'FK to dim_date.date_key (YYYYMMDD format)',
    
    -- Business keys (for readability)
    customer_id BIGINT NOT NULL 
        COMMENT 'Customer business key',
    product_id BIGINT NOT NULL 
        COMMENT 'Product business key',
    store_id BIGINT NOT NULL 
        COMMENT 'Store business key',
    transaction_date DATE NOT NULL 
        COMMENT 'Transaction date',
    
    -- Measures
    quantity INT NOT NULL 
        COMMENT 'Units sold. Business: For volume analysis.',
    unit_price DECIMAL(18,2) NOT NULL 
        COMMENT 'Price per unit. Technical: Source system price.',
    gross_revenue DECIMAL(18,2) NOT NULL 
        COMMENT 'quantity * unit_price. Business: Pre-discount revenue.',
    discount_amount DECIMAL(18,2) 
        COMMENT 'Total discounts applied. Business: For promotion analysis.',
    net_revenue DECIMAL(18,2) NOT NULL 
        COMMENT 'gross_revenue - discount_amount. Business: Primary KPI.',
    
    -- Audit
    record_created_timestamp TIMESTAMP,
    record_updated_timestamp TIMESTAMP,
    
    -- Constraints
    CONSTRAINT pk_fact_sales PRIMARY KEY (customer_key, product_key, store_key, date_key) NOT ENFORCED,
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_key) REFERENCES gold.dim_customer(customer_key) NOT ENFORCED,
    CONSTRAINT fk_sales_product FOREIGN KEY (product_key) REFERENCES gold.dim_product(product_key) NOT ENFORCED,
    CONSTRAINT fk_sales_store FOREIGN KEY (store_key) REFERENCES gold.dim_store(store_key) NOT ENFORCED,
    CONSTRAINT fk_sales_date FOREIGN KEY (date_key) REFERENCES gold.dim_date(date_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'layer' = 'gold',
    'domain' = 'sales',
    'grain' = 'transaction'
)
COMMENT 'Sales fact table at transaction grain. 
Business: Primary source for sales analytics, dashboards, and reporting.
Technical: Grain is one row per customer-product-store-date combination.';
```

### Hands-On Lab 3.1: Design Star Schema

```sql
-- Design a star schema for an e-commerce domain

-- 1. Date Dimension (conformed dimension)
CREATE TABLE gold.dim_date (
    date_key INT NOT NULL COMMENT 'YYYYMMDD format - PK',
    date DATE NOT NULL COMMENT 'Calendar date',
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name STRING NOT NULL,
    day_of_week INT NOT NULL,
    day_name STRING NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN,
    CONSTRAINT pk_dim_date PRIMARY KEY (date_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;

-- 2. Product Dimension
CREATE TABLE gold.dim_product (
    product_key STRING NOT NULL,
    product_id BIGINT NOT NULL,
    product_name STRING NOT NULL,
    category STRING,
    brand STRING,
    unit_cost DECIMAL(18,2),
    is_current BOOLEAN NOT NULL,
    CONSTRAINT pk_dim_product PRIMARY KEY (product_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;

-- 3. Populate dim_date
INSERT INTO gold.dim_date
SELECT
    CAST(DATE_FORMAT(date_col, 'yyyyMMdd') AS INT) as date_key,
    date_col as date,
    YEAR(date_col) as year,
    QUARTER(date_col) as quarter,
    MONTH(date_col) as month,
    DATE_FORMAT(date_col, 'MMMM') as month_name,
    DAYOFWEEK(date_col) as day_of_week,
    DATE_FORMAT(date_col, 'EEEE') as day_name,
    DAYOFWEEK(date_col) IN (1, 7) as is_weekend,
    false as is_holiday
FROM (
    SELECT explode(sequence(DATE'2020-01-01', DATE'2030-12-31', INTERVAL 1 DAY)) as date_col
);
```

---

## Section 2: Slowly Changing Dimensions (2 hours)

### SCD Type Overview

| Type | Name | Behavior | When to Use |
|------|------|----------|-------------|
| **Type 0** | Retain Original | Never overwrite | Immutable attributes (date of birth, original credit score) |
| **Type 1** | Overwrite | Replace old value in place | Corrections, non-audited attributes |
| **Type 2** | Add Row | Insert new row; expire previous | Full history tracking (default for business-critical attributes) |
| **Type 3** | Add Column | Store prior + current value | Only most recent change matters |
| **Type 6** | Hybrid (1+2+3) | New row + overwrite current on all rows | Fast current-state queries with full history |

> **Rule of thumb:** Default to Type 2. Only use Type 1 for corrections that should not create history.

### SCD Type 1 (Overwrite)

**Use when:** History doesn't matter, always want latest value.

```python
def merge_scd_type1(spark, silver_df, gold_table, business_key):
    """SCD Type 1 - Overwrite with latest values."""
    
    from delta.tables import DeltaTable
    from pyspark.sql.functions import current_timestamp
    
    updates = (
        silver_df
        .withColumn("record_updated_timestamp", current_timestamp())
    )
    
    delta_gold = DeltaTable.forName(spark, gold_table)
    
    delta_gold.alias("target").merge(
        updates.alias("source"),
        f"target.{business_key} = source.{business_key}"
    ).whenMatchedUpdateAll(  # Update ALL columns
    ).whenNotMatchedInsertAll(
    ).execute()
```

### SCD Type 2 (Historical)

**Use when:** Need to track changes over time.

```python
def merge_scd_type2(spark, silver_df, gold_table, business_key, surrogate_key):
    """SCD Type 2 - Insert new version, keep history."""
    
    from delta.tables import DeltaTable
    from pyspark.sql.functions import current_timestamp, lit, md5, concat_ws
    
    # Generate surrogate key for new records
    updates = (
        silver_df
        .withColumn(surrogate_key, 
            md5(concat_ws("||", col(business_key), current_timestamp())))
        .withColumn("effective_from", current_timestamp())
        .withColumn("effective_to", lit(None).cast("timestamp"))
        .withColumn("is_current", lit(True))
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
    )
    
    delta_gold = DeltaTable.forName(spark, gold_table)
    
    # Merge: Only update timestamp for current records
    # Insert all as new current versions
    delta_gold.alias("target").merge(
        updates.alias("source"),
        f"target.{business_key} = source.{business_key} AND target.is_current = true"
    ).whenMatchedUpdate(set={
        "record_updated_timestamp": "source.record_updated_timestamp"
        # Note: is_current stays true, we're not closing the old record
    }).whenNotMatchedInsertAll(
    ).execute()
```

### Hands-On Lab 3.2: Implement SCD Patterns

```python
# SCD Type 1 Example
from pyspark.sql.functions import col, current_timestamp
from delta.tables import DeltaTable

# Create dimension
spark.sql("""
CREATE TABLE IF NOT EXISTS gold.dim_product_type1 (
    product_key STRING NOT NULL,
    product_id BIGINT NOT NULL,
    product_name STRING,
    category STRING,
    record_updated_timestamp TIMESTAMP,
    CONSTRAINT pk_product PRIMARY KEY (product_key) NOT ENFORCED
)
USING DELTA
""")

# Load sample data
silver_products = spark.createDataFrame([
    ("P001", 1001, "Widget A", "Electronics"),
    ("P002", 1002, "Widget B", "Electronics")
], ["product_key", "product_id", "product_name", "category"])

# SCD Type 1 MERGE
updates = silver_products.withColumn("record_updated_timestamp", current_timestamp())

DeltaTable.forName(spark, "gold.dim_product_type1").alias("t").merge(
    updates.alias("s"),
    "t.product_key = s.product_key"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

---

## Section 3: PK/FK Constraints (1 hour)

### Constraint Rules

| Rule | Requirement |
|------|-------------|
| **PK on surrogate** | PRIMARY KEY on surrogate key column |
| **FK references PK** | FOREIGN KEY must reference PK column |
| **NOT NULL** | PK columns must be NOT NULL |
| **NOT ENFORCED** | All constraints are informational |

### Applying Constraints

```python
def add_constraints(spark, catalog, schema):
    """Apply PK/FK constraints after all tables exist."""
    
    # Step 1: Add Primary Keys to dimensions
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.dim_customer
        ADD CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) NOT ENFORCED
    """)
    
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.dim_product
        ADD CONSTRAINT pk_dim_product PRIMARY KEY (product_key) NOT ENFORCED
    """)
    
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.dim_date
        ADD CONSTRAINT pk_dim_date PRIMARY KEY (date_key) NOT ENFORCED
    """)
    
    # Step 2: Add Primary Key to fact (composite)
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.fact_sales
        ADD CONSTRAINT pk_fact_sales 
        PRIMARY KEY (customer_key, product_key, date_key) NOT ENFORCED
    """)
    
    # Step 3: Add Foreign Keys (AFTER all PKs exist)
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.fact_sales
        ADD CONSTRAINT fk_sales_customer 
        FOREIGN KEY (customer_key) 
        REFERENCES {catalog}.{schema}.dim_customer(customer_key) NOT ENFORCED
    """)
    
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.fact_sales
        ADD CONSTRAINT fk_sales_product 
        FOREIGN KEY (product_key) 
        REFERENCES {catalog}.{schema}.dim_product(product_key) NOT ENFORCED
    """)
    
    spark.sql(f"""
        ALTER TABLE {catalog}.{schema}.fact_sales
        ADD CONSTRAINT fk_sales_date 
        FOREIGN KEY (date_key) 
        REFERENCES {catalog}.{schema}.dim_date(date_key) NOT ENFORCED
    """)
    
    print("✓ All constraints applied successfully")
```

### Constraint Timing Pattern

```yaml
# Job dependency ensures correct order
tasks:
  - task_key: create_dimensions
    notebook_task:
      notebook_path: ../src/gold/create_dimensions.py
  
  - task_key: create_facts
    depends_on:
      - task_key: create_dimensions
    notebook_task:
      notebook_path: ../src/gold/create_facts.py
  
  - task_key: add_constraints
    depends_on:
      - task_key: create_facts  # Run AFTER all tables exist
    notebook_task:
      notebook_path: ../src/gold/add_constraints.py
```

---

## Section 4: Delta MERGE Operations (2 hours)

### Complete MERGE Pattern

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, md5, concat_ws
from delta.tables import DeltaTable

def merge_dimension(
    spark: SparkSession,
    silver_table: str,
    gold_table: str,
    business_key: str,
    surrogate_key: str
):
    """Complete dimension MERGE with deduplication."""
    
    print(f"Merging {gold_table}...")
    
    # Step 1: Read and deduplicate Silver
    silver_raw = spark.table(silver_table)
    original_count = silver_raw.count()
    
    silver_df = (
        silver_raw
        .orderBy(col("processed_timestamp").desc())
        .dropDuplicates([business_key])
    )
    
    dedupe_count = silver_df.count()
    print(f"  Deduplicated: {original_count} → {dedupe_count}")
    
    # Step 2: Prepare updates
    updates = (
        silver_df
        .withColumn(surrogate_key, 
            md5(concat_ws("||", col(business_key), col("processed_timestamp"))))
        .withColumn("effective_from", col("processed_timestamp"))
        .withColumn("effective_to", lit(None).cast("timestamp"))
        .withColumn("is_current", lit(True))
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
    )
    
    # Step 3: Execute MERGE
    delta_gold = DeltaTable.forName(spark, gold_table)
    
    delta_gold.alias("target").merge(
        updates.alias("source"),
        f"target.{business_key} = source.{business_key} AND target.is_current = true"
    ).whenMatchedUpdate(set={
        "record_updated_timestamp": "source.record_updated_timestamp"
    }).whenNotMatchedInsertAll(
    ).execute()
    
    print(f"✓ Merged {dedupe_count} records into {gold_table}")
```

### Hands-On Lab 3.4: Build MERGE Pipeline

```python
# Complete Gold MERGE pipeline

from pyspark.sql.functions import *
from delta.tables import DeltaTable

# Configuration
catalog = "enterprise_catalog"
silver_schema = "silver"
gold_schema = "gold"

# 1. Merge dim_customer
def merge_dim_customer(spark):
    silver_table = f"{catalog}.{silver_schema}.silver_customers"
    gold_table = f"{catalog}.{gold_schema}.dim_customer"
    
    silver_df = (
        spark.table(silver_table)
        .orderBy(col("processed_timestamp").desc())
        .dropDuplicates(["customer_id"])
    )
    
    updates = (
        silver_df
        .withColumn("customer_key", 
            md5(concat_ws("||", col("customer_id"), col("processed_timestamp"))))
        .withColumn("effective_from", col("processed_timestamp"))
        .withColumn("is_current", lit(True))
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
    )
    
    DeltaTable.forName(spark, gold_table).alias("t").merge(
        updates.alias("s"),
        "t.customer_id = s.customer_id AND t.is_current = true"
    ).whenMatchedUpdate(set={
        "record_updated_timestamp": "s.record_updated_timestamp"
    }).whenNotMatchedInsertAll(
    ).execute()
    
    print(f"✓ Merged dim_customer")

# 2. Merge fact_sales
def merge_fact_sales(spark):
    silver_table = f"{catalog}.{silver_schema}.silver_transactions"
    gold_table = f"{catalog}.{gold_schema}.fact_sales"
    dim_customer = f"{catalog}.{gold_schema}.dim_customer"
    dim_product = f"{catalog}.{gold_schema}.dim_product"
    dim_date = f"{catalog}.{gold_schema}.dim_date"
    
    # Join Silver with dimensions to get surrogate keys
    transactions = spark.table(silver_table)
    customers = spark.table(dim_customer).filter("is_current = true")
    products = spark.table(dim_product).filter("is_current = true")
    dates = spark.table(dim_date)
    
    fact_df = (
        transactions
        .join(customers, "customer_id")
        .join(products, "product_id")
        .join(dates, transactions.transaction_date == dates.date)
        .select(
            customers.customer_key,
            products.product_key,
            "store_key",  # Assume already has key
            dates.date_key,
            transactions.customer_id,
            transactions.product_id,
            "store_id",
            transactions.transaction_date,
            "quantity",
            "unit_price",
            "gross_revenue",
            "discount_amount",
            "net_revenue"
        )
        .withColumn("record_created_timestamp", current_timestamp())
        .withColumn("record_updated_timestamp", current_timestamp())
    )
    
    DeltaTable.forName(spark, gold_table).alias("t").merge(
        fact_df.alias("s"),
        """t.customer_key = s.customer_key 
           AND t.product_key = s.product_key 
           AND t.date_key = s.date_key"""
    ).whenMatchedUpdateAll(
    ).whenNotMatchedInsertAll(
    ).execute()
    
    print(f"✓ Merged fact_sales")

# Run pipeline
merge_dim_customer(spark)
merge_fact_sales(spark)
```

---

## Section 5: Table-Valued Functions (TVFs) (2 hours)

### TVF Design Principles

| Principle | Implementation |
|-----------|----------------|
| **STRING dates** | Parameters as STRING, CAST internally |
| **Required first** | Required params before optional |
| **WHERE not LIMIT** | Use `WHERE rank <= N` not `LIMIT` |
| **LLM-friendly** | Structured COMMENT for Genie |

### TVF Template

```sql
CREATE OR REPLACE FUNCTION get_top_customers(
    -- Required parameters first
    start_date STRING COMMENT 'Start date (YYYY-MM-DD)',
    end_date STRING COMMENT 'End date (YYYY-MM-DD)',
    -- Optional parameters last
    top_n INT DEFAULT 10 COMMENT 'Number of customers to return'
)
RETURNS TABLE(
    rank INT COMMENT 'Customer rank by revenue',
    customer_id BIGINT COMMENT 'Customer identifier',
    customer_name STRING COMMENT 'Customer name',
    total_revenue DECIMAL(18,2) COMMENT 'Total revenue for period',
    order_count BIGINT COMMENT 'Number of orders'
)
COMMENT '
• PURPOSE: Top customers by revenue for a date range
• BEST FOR: "Top customers this month" | "Best customers" | "VIP customers"
• RETURNS: Individual rows (rank, customer_id, customer_name, total_revenue, order_count)
• PARAMS: start_date, end_date (YYYY-MM-DD), top_n (default: 10)
• SYNTAX: SELECT * FROM get_top_customers(''2024-01-01'', ''2024-12-31'')
• NOTE: DO NOT wrap in TABLE() | Already ranked by revenue DESC
'
RETURN
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            c.customer_name,
            SUM(f.net_revenue) as total_revenue,
            COUNT(*) as order_count
        FROM gold.fact_sales f
        JOIN gold.dim_customer c ON f.customer_key = c.customer_key AND c.is_current = true
        JOIN gold.dim_date d ON f.date_key = d.date_key
        WHERE d.date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
        GROUP BY c.customer_id, c.customer_name
    ),
    ranked AS (
        SELECT 
            ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as rank,
            customer_id,
            customer_name,
            total_revenue,
            order_count
        FROM customer_metrics
    )
    SELECT * FROM ranked
    WHERE rank <= top_n
    ORDER BY rank;
```

### Hands-On Lab 3.5: Create TVFs

```sql
-- TVF 1: Sales by Product Category
CREATE OR REPLACE FUNCTION get_sales_by_category(
    start_date STRING COMMENT 'Start date (YYYY-MM-DD)',
    end_date STRING COMMENT 'End date (YYYY-MM-DD)'
)
RETURNS TABLE(
    category STRING,
    total_revenue DECIMAL(18,2),
    total_units BIGINT,
    avg_price DECIMAL(18,2)
)
COMMENT '
• PURPOSE: Sales metrics by product category
• BEST FOR: "Sales by category" | "Category performance" | "Which categories sell best"
• RETURNS: Pre-aggregated rows (category, total_revenue, total_units, avg_price)
• PARAMS: start_date, end_date (YYYY-MM-DD)
• SYNTAX: SELECT * FROM get_sales_by_category(''2024-01-01'', ''2024-12-31'')
'
RETURN
    SELECT 
        p.category,
        SUM(f.net_revenue) as total_revenue,
        SUM(f.quantity) as total_units,
        AVG(f.unit_price) as avg_price
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key AND p.is_current = true
    JOIN gold.dim_date d ON f.date_key = d.date_key
    WHERE d.date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY p.category
    ORDER BY total_revenue DESC;

-- TVF 2: Daily Sales Trend
CREATE OR REPLACE FUNCTION get_daily_sales_trend(
    start_date STRING COMMENT 'Start date (YYYY-MM-DD)',
    end_date STRING COMMENT 'End date (YYYY-MM-DD)'
)
RETURNS TABLE(
    sale_date DATE,
    day_name STRING,
    total_revenue DECIMAL(18,2),
    order_count BIGINT
)
COMMENT '
• PURPOSE: Daily sales trend with day-of-week
• BEST FOR: "Daily sales trend" | "Sales by day" | "Week over week"
• RETURNS: One row per day (sale_date, day_name, total_revenue, order_count)
• PARAMS: start_date, end_date (YYYY-MM-DD)
• SYNTAX: SELECT * FROM get_daily_sales_trend(''2024-01-01'', ''2024-01-31'')
'
RETURN
    SELECT 
        d.date as sale_date,
        d.day_name,
        SUM(f.net_revenue) as total_revenue,
        COUNT(*) as order_count
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON f.date_key = d.date_key
    WHERE d.date BETWEEN CAST(start_date AS DATE) AND CAST(end_date AS DATE)
    GROUP BY d.date, d.day_name
    ORDER BY sale_date;
```

---

## Section 6: Metric Views (2 hours)

### Metric View YAML Structure

```yaml
version: "1.1"
comment: >
  PURPOSE: Sales performance metrics for executive dashboards.
  BEST FOR: Total sales | Revenue by region | Monthly trends | Category analysis
  NOT FOR: Individual transaction details (use fact_sales)
  DIMENSIONS: date, region, category, customer_segment
  MEASURES: total_revenue, order_count, avg_order_value, customer_count
  SOURCE: fact_sales (sales domain)
  JOINS: dim_date, dim_customer, dim_product, dim_store

source: ${catalog}.${schema}.fact_sales

joins:
  - name: dim_customer
    source: ${catalog}.${schema}.dim_customer
    'on': source.customer_key = dim_customer.customer_key AND dim_customer.is_current = true
  
  - name: dim_date
    source: ${catalog}.${schema}.dim_date
    'on': source.date_key = dim_date.date_key
  
  - name: dim_product
    source: ${catalog}.${schema}.dim_product
    'on': source.product_key = dim_product.product_key AND dim_product.is_current = true

dimensions:
  - name: transaction_date
    expr: dim_date.date
    comment: Transaction date for time-based analysis
    display_name: Date
    synonyms:
      - date
      - sale date
  
  - name: month_name
    expr: dim_date.month_name
    comment: Month name for monthly analysis
    display_name: Month
    synonyms:
      - month
  
  - name: category
    expr: dim_product.category
    comment: Product category
    display_name: Category
    synonyms:
      - product category

measures:
  - name: total_revenue
    expr: SUM(source.net_revenue)
    comment: Total net revenue after discounts
    display_name: Total Revenue
    format:
      type: currency
      currency_code: USD
    synonyms:
      - revenue
      - sales
      - net revenue
  
  - name: order_count
    expr: COUNT(*)
    comment: Number of transactions
    display_name: Order Count
    format:
      type: number
    synonyms:
      - orders
      - transactions
  
  - name: avg_order_value
    expr: AVG(source.net_revenue)
    comment: Average revenue per order
    display_name: Avg Order Value
    format:
      type: currency
      currency_code: USD
    synonyms:
      - AOV
      - average order
```

### Creating Metric View

```python
def create_metric_view(spark, catalog, schema, view_name, yaml_content):
    """Create metric view from YAML."""
    
    fqn = f"{catalog}.{schema}.{view_name}"
    
    # Drop existing view/table
    try:
        spark.sql(f"DROP VIEW IF EXISTS {fqn}")
        spark.sql(f"DROP TABLE IF EXISTS {fqn}")
    except:
        pass
    
    # Escape comment for SQL
    comment = yaml_content.get('comment', '').replace("'", "''")
    
    # Convert YAML to string
    yaml_str = yaml.dump(yaml_content, default_flow_style=False)
    
    create_sql = f"""
    CREATE VIEW {fqn}
    WITH METRICS
    LANGUAGE YAML
    COMMENT '{comment}'
    AS $$
{yaml_str}
    $$
    """
    
    spark.sql(create_sql)
    print(f"✓ Created metric view: {view_name}")
```

---

## Section 7: Enterprise Bus Matrix & Common Pitfalls (1 hour)

### Hands-On Lab 3.7: Build a Bus Matrix

Map the business processes in your domain to shared dimensions:

| Business Process (Fact) | dim_date | dim_customer | dim_product | dim_store | dim_employee | dim_promotion |
|------------------------|:--------:|:------------:|:-----------:|:---------:|:------------:|:-------------:|
| **Sales** (`fact_sales`) | ✅ | ✅ | ✅ | ✅ | | ✅ |
| **Inventory** (`fact_inventory`) | ✅ | | ✅ | ✅ | | |
| **Returns** (`fact_returns`) | ✅ | ✅ | ✅ | ✅ | ✅ | |
| *(your process here)* | | | | | | |

**Exercise:**
1. Identify 3-5 business processes (fact tables) in your domain
2. List the conformed dimensions each process shares
3. Identify reuse opportunities — dimensions that appear in 3+ processes are highest priority for conformance
4. Submit your bus matrix for architecture review

### Common Dimensional Modeling Mistakes

| # | Mistake | Consequence | Prevention |
|---|---------|-------------|------------|
| 1 | **Failing to declare the grain** | Ambiguous rows, double-counting | Document grain first, before any columns |
| 2 | **Mixing grains in one fact table** | Incorrect aggregations | One grain per fact table |
| 3 | **Putting text attributes in fact tables** | Bloated storage, broken aggregation | Move text to dimensions; use degenerate dims for identifiers |
| 4 | **Using operational keys for joins** | Broken joins when source keys change | Use surrogate keys (MD5 hash) |
| 5 | **Building report-specific models** | Silos, duplication, maintenance burden | Build reusable dimensional models |
| 6 | **Neglecting conformed dimensions** | Can't drill across processes | Conform shared dimensions enterprise-wide |
| 7 | **Splitting hierarchies into separate tables** | Unnecessary joins | Flatten hierarchies into the dimension |
| 8 | **Loading facts before dimensions** | Orphan foreign key references | Always load dimensions first |
| 9 | **Not tracking SCD history** | Destroyed analytical context | Default to SCD Type 2 |
| 10 | **Designing for a single analytic need** | Limited reuse, costly rework | Design for the business process, not one dashboard |

### Special Dimension Patterns (Reference)

| Pattern | Description | Example |
|---------|-------------|---------|
| **Degenerate Dimension** | Identifier on fact table with no separate dim | Order number, invoice number |
| **Junk Dimension** | Consolidation of low-cardinality flags | `junk_order_flags` (is_gift_wrapped, payment_method) |
| **Role-Playing Dimension** | Same dim joined under different roles | `dim_date` as order_date, ship_date, delivery_date |
| **Conformed Dimension** | Shared identically across fact tables | `dim_date`, `dim_customer` |

---

## Module 3 Assessment

### Quiz (25 questions, 80% to pass)

1. What key type should be used as PRIMARY KEY in dimensions?
   - a) Business key
   - b) Surrogate key ✓
   - c) Natural key

2. Which constraint type does Unity Catalog use?
   - a) ENFORCED
   - b) NOT ENFORCED ✓
   - c) VALIDATED

3. What must happen before adding FOREIGN KEY constraints?
   - a) Nothing
   - b) Referenced table must have PRIMARY KEY ✓
   - c) Table must be empty

### Practical Project

**Build Complete Gold Layer:**

1. Complete the four-step design process: select process, declare grain, identify dimensions, identify facts
2. Design star schema (1 fact, 4 dimensions) — classify all facts by additivity
3. Implement SCD Type 2 for 2 dimensions and SCD Type 1 for 1 dimension
4. Apply PK/FK constraints
5. Build an Enterprise Bus Matrix showing your fact table and at least 2 conformed dimensions
6. Create 3 TVFs for common queries
7. Build 1 Metric View

---

## Next Module

[Module 4: Operations & Deployment](./74-module-operations-deployment.md)
