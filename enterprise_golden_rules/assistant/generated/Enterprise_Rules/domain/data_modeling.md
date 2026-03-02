# Data Modeling Golden Rules
**Rules:** DM-01..09 | **Count:** 9 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| DM-01 | Use dimensional modeling (star/snowflake) for Gold layer | Critical | Gold tables use dim_/fact_ prefixes |
| DM-02 | Declare PRIMARY KEY constraints on all dimension and fact tables | Critical | Every table has PK constraint |
| DM-03 | Declare FOREIGN KEY constraints to document relationships | Required | Fact tables reference dim PKs |
| DM-04 | Avoid heavily normalized models (3NF) in analytical layers | Required | Gold queries need 2-5 joins max |
| DM-05 | Design for minimal joins in common query patterns | Required | High-frequency attrs pre-joined |
| DM-06 | Use enforced constraints (NOT NULL, CHECK) for data integrity | Required | Critical columns have NOT NULL |
| DM-07 | Handle semi-structured data with appropriate complex types | Recommended | STRUCT/ARRAY/MAP, not JSON strings |
| DM-08 | Design for single-table transactions | Critical | Each MERGE is independent txn |
| DM-09 | Design Gold layer for both BI and AI consumption | Required | Numeric cols NOT NULL + DEFAULT |

---

## Detailed Rules

### DM-01: Dimensional Modeling for Gold Layer
**Severity:** Critical | **Trigger:** When designing or reviewing a Gold layer data model

**Rule:** All Gold layer data models must use dimensional modeling patterns (star schema preferred, snowflake acceptable) rather than heavily normalized relational models.
**Why:** Star schemas require fewer joins for faster queries, enable better data skipping, and align with BI tools and semantic layers that expect dimension/fact structures.

**Correct:**
```sql
-- Star schema: fact with direct FK references to dimensions
CREATE TABLE gold.fact_sales (
    sale_id BIGINT NOT NULL,
    sale_date DATE NOT NULL,
    customer_key STRING NOT NULL,
    product_key STRING NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(18,2) NOT NULL,
    CONSTRAINT pk_fact_sales PRIMARY KEY (sale_id) NOT ENFORCED,
    CONSTRAINT fk_customer FOREIGN KEY (customer_key)
        REFERENCES gold.dim_customer(customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

**Anti-Pattern:**
```
-- 3NF in Gold: too many joins, poor analytical performance
customer -> customer_address -> city -> state -> region -> country
         -> customer_contact -> contact_type
         -> customer_segment -> segment_category
-- Result: 7+ joins for a simple customer query
```

---

### DM-02: Primary Key Constraints
**Severity:** Critical | **Trigger:** When creating any Gold layer table

**Rule:** All Gold dimension and fact tables must declare PRIMARY KEY constraints to establish entity identity and enable query optimizer join ordering.
**Why:** Databricks uses PK/FK metadata for join optimization. Metric Views and Genie auto-detect relationships from declared PKs. Missing PKs break semantic layer relationship discovery.

**Correct:**
```sql
-- Dimension: surrogate key PK
CREATE TABLE gold.dim_customer (
    customer_key STRING NOT NULL
        COMMENT 'Surrogate key. Technical: MD5 hash of customer_id + effective_from.',
    customer_id STRING NOT NULL
        COMMENT 'Business key. Stable across SCD2 versions.',
    customer_name STRING,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    is_current BOOLEAN NOT NULL,
    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;

-- Fact: composite key PK
CREATE TABLE gold.fact_sales_daily (
    sale_date DATE NOT NULL,
    customer_key STRING NOT NULL,
    product_key STRING NOT NULL,
    total_revenue DECIMAL(18,2) NOT NULL,
    CONSTRAINT pk_fact_sales_daily
        PRIMARY KEY (sale_date, customer_key, product_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

**Anti-Pattern:**
```sql
-- No PK declared -- optimizer cannot infer identity or join strategy
CREATE TABLE gold.dim_customer (
    customer_key STRING,
    customer_name STRING
) USING DELTA;
```

---

### DM-03: Foreign Key Constraints
**Severity:** Required | **Trigger:** When creating fact tables that reference dimensions

**Rule:** All Gold fact tables must declare FOREIGN KEY constraints to document relationships with dimension tables. Apply constraints in order: create all tables first, then all PKs, then all FKs.
**Why:** FK metadata enables optimizer join planning, Metric View auto-relationship detection, and automated data lineage tracking.

**Correct:**
```sql
-- Step 1: Tables and PKs already created
-- Step 2: Add FKs (target PKs must exist first)
ALTER TABLE gold.fact_sales
ADD CONSTRAINT fk_sales_customer
    FOREIGN KEY (customer_key) REFERENCES gold.dim_customer(customer_key) NOT ENFORCED;

ALTER TABLE gold.fact_sales
ADD CONSTRAINT fk_sales_product
    FOREIGN KEY (product_key) REFERENCES gold.dim_product(product_key) NOT ENFORCED;
```

**Anti-Pattern:**
```sql
-- FK applied before target PK exists
ALTER TABLE fact_sales ADD CONSTRAINT fk_customer
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key);
-- Error: dim_customer does not have a primary key
```

---

### DM-05: Minimize Joins in Common Queries
**Severity:** Required | **Trigger:** When query audit shows frequent multi-table joins

**Rule:** Pre-join frequently accessed dimension attributes into fact tables when performance requires it, reducing common queries from 5+ joins to 2-3.
**Why:** Every join adds processing overhead and challenges the optimizer. Filters on joined tables may not push down efficiently.

**Correct:**
```sql
-- Denormalize high-frequency attributes into enriched fact
CREATE TABLE gold.fact_sales_enriched (
    sale_date DATE,
    customer_key STRING,
    customer_segment STRING,  -- Denormalized from dim_customer
    customer_region STRING,   -- Denormalized from dim_customer
    product_category STRING,  -- Denormalized from dim_product
    total_amount DECIMAL(18,2)
)
USING DELTA
CLUSTER BY AUTO;
```

**Anti-Pattern:**
```sql
-- Every dashboard query requires 5 joins to get basic attributes
SELECT f.*, c.segment, c.region, p.category, s.store_name, d.quarter
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_store s ON f.store_key = s.store_key
JOIN dim_date d ON f.sale_date = d.date_key;
```

---

### DM-06: Enforced Constraints (NOT NULL, CHECK)
**Severity:** Required | **Trigger:** When defining column data quality requirements

**Rule:** Use NOT NULL on required columns and CHECK constraints for business rules. These are enforced at write time (unlike PK/FK which are informational only).
**Why:** Prevents invalid data from entering tables, ensuring downstream consumers can trust data validity without defensive null-checking.

**Correct:**
```sql
CREATE TABLE gold.fact_sales (
    sale_id BIGINT NOT NULL,
    sale_date DATE NOT NULL,
    customer_key STRING NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    discount_pct DECIMAL(5,2)         -- Optional: may be null
) USING DELTA;

ALTER TABLE gold.fact_sales
ADD CONSTRAINT valid_amount CHECK (amount >= 0);

ALTER TABLE gold.fact_sales
ADD CONSTRAINT valid_discount CHECK (discount_pct BETWEEN 0 AND 100);
```

**Anti-Pattern:**
```sql
-- No constraints: nulls and negative amounts slip through
CREATE TABLE gold.fact_sales (
    sale_id BIGINT,
    amount DECIMAL(18,2)
) USING DELTA;
```

---

### DM-08: Single-Table Transactions
**Severity:** Critical | **Trigger:** When designing multi-table ETL pipelines

**Rule:** Design pipelines knowing that each table MERGE/INSERT is an independent transaction. Multi-table atomicity requires application-level handling with dimension-first ordering and idempotent operations.
**Why:** Failed multi-table operations leave intermediate inconsistent states. Downstream queries may see partial updates between independent table transactions.

**Correct:**
```python
try:
    # Transaction 1: Update dimension FIRST (FK validity)
    spark.sql("""
        MERGE INTO gold.dim_customer AS target
        USING staging.customer_updates AS source
        ON target.customer_id = source.customer_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
    # Transaction 2: Update fact SECOND (separate transaction)
    spark.sql("""
        MERGE INTO gold.fact_sales AS target
        USING staging.sales_updates AS source
        ON target.sale_id = source.sale_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
except Exception as e:
    # Application-level error handling required
    raise
```

**Anti-Pattern:**
```python
# Assuming both tables update atomically -- they do NOT
spark.sql("INSERT INTO gold.dim_customer ...")
spark.sql("INSERT INTO gold.fact_sales ...")
# If fact insert fails, dim is updated but fact is not -- inconsistent state
```

---

### DM-09: Design for BI and AI Dual-Use
**Severity:** Required | **Trigger:** When designing Gold layer dimension or fact tables

**Rule:** Gold tables must serve both BI (dashboards, Genie, Metric Views) and AI (feature engineering, model training) workloads by using NOT NULL with DEFAULT values on numeric columns and clear COMMENTs.
**Why:** Eliminates duplicate ML pipelines, ensures BI and AI use the same governed data, and reduces time-to-model since feature tables derived from Gold are immediately production-quality.

**Correct:**
```sql
CREATE TABLE gold.dim_customer (
    customer_key STRING NOT NULL,
    customer_segment STRING COMMENT 'Business segment. Used in dashboards and Genie.',
    -- ML-friendly: NOT NULL + DEFAULT eliminates NaN handling at training time
    lifetime_value DECIMAL(18,2) NOT NULL DEFAULT 0
        COMMENT 'Total spend in USD. ML: numeric feature, no nulls.',
    order_count INT NOT NULL DEFAULT 0
        COMMENT 'Total orders. ML: numeric feature, no nulls.',
    days_since_last_order INT
        COMMENT 'Recency metric. ML: numeric feature for churn prediction.',
    is_current BOOLEAN NOT NULL,
    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) NOT ENFORCED
) USING DELTA CLUSTER BY AUTO;
```

**Anti-Pattern:**
```sql
-- Nullable numerics force ML teams to build separate imputation pipelines
CREATE TABLE gold.dim_customer (
    customer_key STRING,
    lifetime_value DECIMAL(18,2),  -- NULLs break ML training
    order_count INT                -- NULLs require imputation
) USING DELTA;
```

---

## Checklist
- [ ] DM-01: Gold layer uses star or snowflake schema (dim_/fact_ tables)
- [ ] DM-02: Every dimension and fact table has a PRIMARY KEY constraint
- [ ] DM-03: Every fact table has FOREIGN KEY constraints to its dimensions
- [ ] DM-04: No 3NF normalization in Gold; common queries need 2-5 joins max
- [ ] DM-05: High-frequency dimension attributes pre-joined into enriched facts
- [ ] DM-06: Critical columns have NOT NULL; business rules use CHECK constraints
- [ ] DM-07: Semi-structured data uses STRUCT/ARRAY/MAP, not JSON strings
- [ ] DM-08: Multi-table pipelines update dimensions first, facts second
- [ ] DM-09: Numeric columns have NOT NULL + DEFAULT for BI and AI dual-use
