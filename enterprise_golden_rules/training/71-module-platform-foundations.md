# Module 1: Platform Foundations

## Unity Catalog, Governance, and Architecture

**Duration:** 8 hours  
**Prerequisites:** Basic SQL, Cloud concepts  
**Outcome:** Understand enterprise data platform architecture and governance

---

## Learning Objectives

By the end of this module, you will be able to:

1. Navigate Unity Catalog hierarchy (Catalog → Schema → Tables)
2. Apply data governance tags and classification
3. Implement access control using grants
4. Understand data lineage and auditing
5. Design solutions following medallion architecture
6. Apply the 10 Golden Rules

---

## Section 1: Unity Catalog Overview (1 hour)

### What is Unity Catalog?

Unity Catalog is Databricks' unified governance solution for all data and AI assets.

**Key Capabilities:**
- Centralized metadata management
- Fine-grained access control
- Data lineage tracking
- Audit logging
- Cross-workspace data sharing

### Unity Catalog Hierarchy

```
Metastore (One per region)
└── Catalog (One per environment/domain)
    └── Schema (One per data layer/domain)
        ├── Tables (Bronze, Silver, Gold)
        ├── Views (Materialized, Standard)
        ├── Functions (UDFs, TVFs)
        └── ML Models
```

**Naming Conventions:**

| Level | Convention | Example |
|-------|------------|---------|
| Catalog | `{company}_{env}` or `{domain}_{env}` | `enterprise_prod`, `sales_dev` |
| Schema | `{layer}` or `{domain}_{layer}` | `bronze`, `silver`, `gold` |
| Table | `{layer}_{entity}` or `{entity}` | `bronze_orders`, `dim_customer` |

### Hands-On Lab 1.1: Explore Unity Catalog

```sql
-- 1. List available catalogs
SHOW CATALOGS;

-- 2. Explore a catalog
USE CATALOG enterprise_catalog;
SHOW SCHEMAS;

-- 3. Explore a schema
USE SCHEMA gold;
SHOW TABLES;

-- 4. Describe a table
DESCRIBE EXTENDED dim_customer;

-- 5. View table properties
SHOW TBLPROPERTIES dim_customer;
```

---

## Section 2: Access Control & RBAC (1 hour)

### Grant Model

Unity Catalog uses a hierarchical grant model:

```
Metastore → Catalog → Schema → Table → Column
    ↓           ↓        ↓        ↓        ↓
  ADMIN    ALL PRIVILEGES  USE   SELECT  COLUMN MASKING
```

**Principal Types:**
- Users (individual accounts)
- Groups (collections of users)
- Service Principals (automation)

### Common Permissions

| Permission | Scope | Use Case |
|------------|-------|----------|
| `USE CATALOG` | Catalog | Access catalog |
| `USE SCHEMA` | Schema | Access schema |
| `SELECT` | Table/View | Read data |
| `MODIFY` | Table | Write data |
| `CREATE TABLE` | Schema | Create objects |
| `ALL PRIVILEGES` | Any | Full control |

### Hands-On Lab 1.2: Access Control

```sql
-- 1. Grant schema access to a group
GRANT USE SCHEMA ON SCHEMA gold TO `data_analysts`;

-- 2. Grant read access to specific tables
GRANT SELECT ON TABLE gold.dim_customer TO `data_analysts`;
GRANT SELECT ON TABLE gold.fact_sales TO `data_analysts`;

-- 3. Grant write access to data engineers
GRANT MODIFY ON SCHEMA gold TO `data_engineers`;

-- 4. Revoke access
REVOKE SELECT ON TABLE gold.fact_sales FROM `intern_group`;

-- 5. View grants
SHOW GRANTS ON TABLE gold.dim_customer;
```

**Best Practice:** Grant to groups, not individuals. Use principle of least privilege.

---

## Section 3: Data Classification & Tags (1 hour)

### Data Classification Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **Public** | Safe for external sharing | Product catalog, public metrics |
| **Internal** | Business data, no PII | Sales aggregates, inventory |
| **Confidential** | Contains PII or sensitive | Customer data, financial records |
| **Restricted** | Highly sensitive | SSN, payment cards, health data |

### Standard Tags

| Tag | Purpose | Values |
|-----|---------|--------|
| `layer` | Medallion layer | bronze, silver, gold |
| `domain` | Business domain | sales, finance, hr |
| `contains_pii` | PII indicator | true, false |
| `data_classification` | Sensitivity | public, internal, confidential |
| `business_owner` | Ownership | Team name |
| `technical_owner` | Technical ownership | Team name |

### Applying Tags

```sql
-- Apply tags during table creation
CREATE TABLE gold.dim_customer (
    customer_key STRING NOT NULL,
    customer_id BIGINT NOT NULL,
    customer_name STRING,
    email STRING
)
TBLPROPERTIES (
    'layer' = 'gold',
    'domain' = 'customer',
    'contains_pii' = 'true',
    'data_classification' = 'confidential',
    'business_owner' = 'Customer Success',
    'technical_owner' = 'Data Engineering'
);

-- Add tags to existing table
ALTER TABLE gold.dim_customer SET TBLPROPERTIES (
    'retention_period' = '7_years',
    'compliance_framework' = 'GDPR'
);
```

### Hands-On Lab 1.3: Data Classification

```sql
-- 1. Create a table with proper classification
CREATE TABLE gold.fact_orders (
    order_id BIGINT NOT NULL,
    customer_key STRING NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(18,2)
)
TBLPROPERTIES (
    'layer' = 'gold',
    'domain' = 'sales',
    'contains_pii' = 'false',
    'data_classification' = 'internal',
    'business_owner' = 'Sales Analytics'
);

-- 2. Query tables by classification
SELECT 
    table_name,
    tbl_properties
FROM system.information_schema.tables
WHERE table_schema = 'gold';

-- 3. Find all PII-containing tables
-- (Implement as custom query against table properties)
```

---

## Section 4: Lineage & Auditing (1 hour)

### Data Lineage

Unity Catalog automatically tracks data lineage:

```
Source Table → Transformation → Target Table
     ↓              ↓              ↓
  Upstream      Pipeline       Downstream
```

**Lineage Captures:**
- Table-to-table dependencies
- Column-level transformations
- Pipeline execution history
- Query patterns

### Viewing Lineage

1. **UI Method:** Table details → Lineage tab
2. **SQL Method:** Query system tables
3. **API Method:** REST API calls

```sql
-- Query lineage information
SELECT 
    source_table_full_name,
    target_table_full_name,
    last_updated
FROM system.access.table_lineage
WHERE target_table_full_name = 'enterprise_catalog.gold.dim_customer';
```

### Audit Logging

Unity Catalog logs all access and modifications:

| Event Type | What's Logged |
|------------|---------------|
| Authentication | Login attempts, token usage |
| Authorization | Permission checks, denials |
| Data Access | SELECT queries, data exports |
| Modifications | CREATE, ALTER, DROP |
| Admin Actions | Grant, revoke, schema changes |

```sql
-- Query audit logs
SELECT 
    event_time,
    action_name,
    request_params,
    response
FROM system.access.audit
WHERE event_date >= current_date - 7
    AND action_name LIKE '%TABLE%'
ORDER BY event_time DESC
LIMIT 100;
```

### Hands-On Lab 1.4: Lineage and Auditing

```sql
-- 1. Create a pipeline to demonstrate lineage
-- Bronze to Silver transformation
CREATE TABLE silver.customers AS
SELECT 
    customer_id,
    UPPER(customer_name) as customer_name,
    LOWER(email) as email,
    current_timestamp() as processed_at
FROM bronze.raw_customers
WHERE customer_id IS NOT NULL;

-- 2. View the lineage (in UI: Table → Lineage tab)

-- 3. Query your recent access history
SELECT 
    event_time,
    action_name,
    request_params.full_name_arg as table_name
FROM system.access.audit
WHERE user_name = current_user()
    AND event_date = current_date
ORDER BY event_time DESC;
```

---

## Section 5: Medallion Architecture (2 hours)

### Architecture Overview

The medallion architecture provides a structured approach to data quality:

| Layer | Purpose | Characteristics | Quality |
|-------|---------|-----------------|---------|
| **Bronze** | Raw ingestion | Immutable, append-only | Low |
| **Silver** | Cleaned data | Validated, deduplicated | Medium |
| **Gold** | Business data | Aggregated, modeled | High |

### Layer Design Principles

#### Bronze Layer
```
✓ Append-only (never modify)
✓ Source system format preserved
✓ Change Data Feed enabled
✓ Minimal transformation
✓ All records captured (including errors)
```

#### Silver Layer
```
✓ Streaming DLT pipelines
✓ Data quality expectations
✓ Deduplication applied
✓ Cleansed and standardized
✓ Quarantine for failures
```

#### Gold Layer
```
✓ Star schema design
✓ Pre-aggregated metrics
✓ PK/FK constraints
✓ Semantic layer ready
✓ Business documentation
```

### Data Flow Pattern

```
┌────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   Source     ───[Ingestion]───>  Bronze  ───[CDF Stream]───>      │
│   Systems                        Tables                            │
│                                    │                               │
│                                    ▼                               │
│                              ┌─────────┐                          │
│                              │Silver   │                          │
│                              │DLT      │◄──[Expectations]         │
│                              │Pipeline │                          │
│                              └────┬────┘                          │
│                                   │                               │
│                         ┌────────┴────────┐                       │
│                         ▼                 ▼                       │
│                    Silver Tables    Quarantine Tables             │
│                         │                                         │
│                         ▼                                         │
│                    ┌─────────┐                                    │
│                    │  Gold   │◄──[Delta MERGE]                    │
│                    │ Tables  │                                    │
│                    └────┬────┘                                    │
│                         │                                         │
│            ┌────────────┼────────────┐                           │
│            ▼            ▼            ▼                           │
│       Metric Views    TVFs      Dashboards                       │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Hands-On Lab 1.5: Design a Medallion Pipeline

**Scenario:** Design a pipeline for e-commerce order data.

```
Source: Order Management System (REST API)
Data: Orders, Line Items, Customers

Task:
1. Design Bronze tables (raw data)
2. Design Silver tables (cleaned, validated)
3. Design Gold tables (star schema)
```

**Solution Template:**

```sql
-- Bronze Layer
CREATE TABLE bronze.raw_orders (
    payload STRING,  -- Raw JSON
    source_file STRING,
    ingestion_timestamp TIMESTAMP
)
USING DELTA
CLUSTER BY AUTO
TBLPROPERTIES ('layer' = 'bronze', 'delta.enableChangeDataFeed' = 'true');

-- Silver Layer (via DLT)
-- @dlt.table with expectations

-- Gold Layer
CREATE TABLE gold.fact_orders (
    order_key STRING NOT NULL,
    customer_key STRING NOT NULL,
    date_key INT NOT NULL,
    order_amount DECIMAL(18,2),
    CONSTRAINT pk_fact_orders PRIMARY KEY (order_key) NOT ENFORCED,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_key)
        REFERENCES gold.dim_customer(customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
```

---

## Section 6: Golden Rules Review (2 hours)

### The 10 Golden Rules Summary

| # | Rule | Key Requirement |
|---|------|-----------------|
| 1 | Unity Catalog Everywhere | All assets in UC |
| 2 | Medallion Architecture | Bronze → Silver → Gold |
| 3 | Data Quality by Design | DLT expectations |
| 4 | Delta Lake Everywhere | CLUSTER BY AUTO |
| 5 | Dimensional Modeling | Surrogate keys, PK/FK |
| 6 | Serverless-First | Default compute |
| 7 | Infrastructure as Code | Asset Bundles |
| 8 | LLM-Friendly Docs | Comments everywhere |
| 9 | Schema-First Dev | Extract from YAML |
| 10 | Deduplication | Before every MERGE |

### Self-Assessment Checklist

For each rule, verify you can:

- [ ] **Rule 1:** Create a UC-managed table with proper grants
- [ ] **Rule 2:** Explain the purpose of each medallion layer
- [ ] **Rule 3:** Write a DLT expectation
- [ ] **Rule 4:** Configure Delta table properties
- [ ] **Rule 5:** Design a star schema
- [ ] **Rule 6:** Configure serverless compute in YAML
- [ ] **Rule 7:** Create an Asset Bundle job definition
- [ ] **Rule 8:** Write an LLM-friendly table comment
- [ ] **Rule 9:** Extract schema from YAML file
- [ ] **Rule 10:** Implement deduplication before MERGE

---

## Module 1 Assessment

### Quiz (20 questions, 80% to pass)

**Sample Questions:**

1. What is the correct Unity Catalog hierarchy?
   - a) Schema → Catalog → Table
   - b) Catalog → Schema → Table ✓
   - c) Metastore → Table → Schema

2. Which layer should use DLT streaming pipelines?
   - a) Bronze
   - b) Silver ✓
   - c) Gold

3. What constraint type is used in Databricks Unity Catalog?
   - a) ENFORCED
   - b) NOT ENFORCED ✓
   - c) VALIDATED

### Practical Lab

**Assignment:** Create a complete medallion architecture for a retail sales domain.

**Requirements:**
1. Create Bronze table with CDF enabled
2. Define Silver DLT expectation rules
3. Design Gold star schema (1 fact, 3 dimensions)
4. Apply proper tags and documentation

**Submission:** Screenshot of tables + SQL scripts

---

## Next Module

[Module 2: Data Engineering Best Practices](./72-module-data-engineering.md)

---

**Module 1 Complete!**

You now understand:
- Unity Catalog governance framework
- Access control and RBAC
- Data classification and tagging
- Lineage and auditing capabilities
- Medallion architecture design
- The 10 Golden Rules foundation
