# Naming & Tagging Golden Rules
**Rules:** NC-01..03, CM-01..04, TG-01..03 | **Count:** 10 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| NC-01 | All object names use snake_case | Critical | No camelCase, PascalCase, or spaces |
| NC-02 | Tables prefixed by layer or entity type | Critical | dim_, fact_, bronze_, silver_ present |
| NC-03 | No abbreviations except approved list | Required | Only id, ts, dt, amt, qty, pct, etc. |
| CM-01 | SQL block comments (`/* */`) for all DDL | Required | Every CREATE/ALTER has block comment |
| CM-02 | Table COMMENT follows dual-purpose format | Critical | Business + Technical sections present |
| CM-03 | Column COMMENT required for all columns | Critical | Every column has a COMMENT clause |
| CM-04 | TVF COMMENT follows v3.0 structured format | Critical | PURPOSE/BEST FOR/NOT FOR/RETURNS/PARAMS/SYNTAX/NOTE |
| TG-01 | All workflows must have required tags | Critical | team, cost_center, environment on jobs |
| TG-02 | Use Governed Tags for UC securables | Critical | cost_center on catalogs, pii on columns |
| TG-03 | Serverless resources must use approved budget policies | Critical | Budget policy with required tags assigned |

---

## Detailed Rules

### NC-01: Snake Case Standard
**Severity:** Critical | **Trigger:** When naming any database object (catalog, schema, table, column, function, job)

**Rule:** All database objects must use `snake_case` (lowercase with underscores) -- never camelCase, PascalCase, SCREAMING_CASE, kebab-case, or spaces.
**Why:** Inconsistent casing breaks SQL references (Unity Catalog is case-sensitive in some contexts), confuses LLMs in Genie, and makes cross-team collaboration error-prone.

**Correct:**
```sql
-- Tables
CREATE TABLE gold.dim_customer ...
CREATE TABLE gold.fact_daily_usage ...

-- Columns
customer_id STRING, order_date DATE, total_amount DECIMAL(18,2)

-- Functions
CREATE FUNCTION gold.get_daily_sales(...)

-- Constraints
CONSTRAINT pk_dim_customer PRIMARY KEY ...
CONSTRAINT fk_orders_customer FOREIGN KEY ...
```

**Anti-Pattern:**
```sql
CREATE TABLE gold.DimCustomer ...        -- PascalCase
CREATE TABLE gold."Daily Usage" ...      -- spaces
customer_id STRING, orderDate DATE ...   -- mixed camelCase
CREATE FUNCTION gold.GetDailySales(...)  -- PascalCase
```

---

### NC-02: Table Naming Prefixes
**Severity:** Critical | **Trigger:** When creating tables in any medallion layer

**Rule:** Bronze and Silver tables use layer prefixes (`bronze_`, `silver_`). Gold tables use entity-type prefixes (`dim_`, `fact_`, `bridge_`, `agg_`, `stg_`).
**Why:** Prefixes make table purpose instantly clear in Unity Catalog lineage views, query editors, and Genie asset discovery. Missing prefixes force consumers to read documentation to understand table roles.

**Correct:**
```sql
-- Bronze/Silver: layer prefix
CREATE TABLE bronze.bronze_raw_orders ...
CREATE TABLE silver.silver_orders ...

-- Gold: entity-type prefix
CREATE TABLE gold.dim_customer ...
CREATE TABLE gold.fact_sales ...
CREATE TABLE gold.bridge_customer_product ...
CREATE TABLE gold.agg_daily_sales ...
```

**Anti-Pattern:**
```sql
CREATE TABLE gold.customers ...          -- missing dim_ prefix
CREATE TABLE gold.sales_data ...         -- ambiguous, no fact_ prefix
CREATE TABLE bronze.orders ...           -- missing bronze_ prefix
```

---

### NC-03: Approved Abbreviations Only
**Severity:** Required | **Trigger:** When choosing column or object names

**Rule:** Only use abbreviations from the approved list (id, ts, dt, amt, qty, pct, num, cnt, avg, min, max, pk, fk, dim, fact, agg, stg). All other words must be spelled out.
**Why:** Unapproved abbreviations are ambiguous across teams and confuse Genie's LLM when generating SQL from natural language.

**Correct:**
```sql
customer_id STRING,        -- 'id' approved
created_ts TIMESTAMP,      -- 'ts' approved
total_amt DECIMAL(18,2),   -- 'amt' approved
order_qty INT,             -- 'qty' approved
discount_pct DECIMAL(5,2)  -- 'pct' approved
```

**Anti-Pattern:**
```sql
cust_name STRING,    -- 'cust' NOT approved, use 'customer'
prod_id STRING,      -- 'prod' NOT approved, use 'product'
inv_qty INT,         -- 'inv' NOT approved, use 'inventory'
trans_date DATE      -- 'trans' NOT approved, use 'transaction'
```

---

### CM-01: SQL Block Comments for DDL
**Severity:** Required | **Trigger:** When writing any CREATE TABLE, ALTER TABLE, or CREATE FUNCTION statement

**Rule:** All DDL operations must include `/* */` block comments explaining purpose, domain, grain (for tables), and change history.
**Why:** Block comments provide context for code reviewers, future maintainers, and automated documentation generators. Inline comments are insufficient for complex DDL.

**Correct:**
```sql
/*
 * Table: dim_customer
 * Layer: Gold
 * Domain: Sales
 *
 * Purpose: Customer dimension with SCD Type 2 history tracking.
 * Grain: One row per customer per effective period.
 * Source: Silver layer silver_customers table.
 *
 * Change History:
 *   2026-02-01 - Initial creation (jsmith)
 */
CREATE TABLE gold.dim_customer (
    customer_key STRING NOT NULL,
    customer_id STRING NOT NULL,
    customer_name STRING,
    is_current BOOLEAN NOT NULL
)
USING DELTA
CLUSTER BY AUTO;
```

**Anti-Pattern:**
```sql
-- Creating customer table
CREATE TABLE gold.dim_customer (...)  -- single-line comment is insufficient
```

---

### CM-02: Table COMMENT Dual-Purpose Format
**Severity:** Critical | **Trigger:** When creating or updating any table

**Rule:** Every table must have a COMMENT following the format: `[Description]. Business: [use cases, consumers]. Technical: [grain, source, update frequency].`
**Why:** Genie and AI/BI tools read table COMMENTs to understand context. A dual-purpose format serves both human readers (Business section) and LLMs (Technical section).

**Correct:**
```sql
COMMENT ON TABLE gold.dim_customer IS
'Customer dimension with SCD Type 2 history tracking for all customer attributes.
Business: Primary customer reference for segmentation, lifetime value, and cohort analysis.
Technical: MD5 surrogate key, is_current flag for active records, daily merge from Silver.';

COMMENT ON TABLE gold.fact_orders IS
'Daily order facts aggregated at customer-product-day grain.
Business: Primary source for revenue reporting, conversion analysis, and sales dashboards.
Technical: Composite PK (order_date, customer_key, product_key), incremental merge, CDF enabled.';
```

**Anti-Pattern:**
```sql
COMMENT ON TABLE gold.dim_customer IS 'Customer table';  -- too vague, no Business/Technical
```

---

### CM-03: Column COMMENT Required
**Severity:** Critical | **Trigger:** When adding any column to a table

**Rule:** Every column must have a COMMENT in dual-purpose format: `[Definition]. Business: [usage, rules]. Technical: [type notes, source, calculation].`
**Why:** Column COMMENTs are the primary way Genie understands what data means. Missing comments cause Genie to guess incorrectly and generate wrong SQL.

**Correct:**
```sql
customer_key STRING NOT NULL
COMMENT 'Surrogate key for SCD Type 2 versioning. Business: Used for joining fact tables. Technical: MD5 hash of customer_id + effective_from.';

total_amount DECIMAL(18,2)
COMMENT 'Total order amount after discounts in USD. Business: Primary revenue metric. Technical: SUM(quantity * unit_price * (1 - discount_pct)).';

is_current BOOLEAN NOT NULL DEFAULT TRUE
COMMENT 'Current version flag. Business: Filter to is_current=true for current state. Technical: Set to false when new SCD2 version inserted.';
```

**Anti-Pattern:**
```sql
customer_key STRING NOT NULL,   -- No COMMENT: Genie cannot infer meaning
total_amount DECIMAL(18,2)      -- No COMMENT: "amount of what?" is ambiguous
```

---

### CM-04: TVF v3.0 Structured Comment
**Severity:** Critical | **Trigger:** When creating any Table-Valued Function

**Rule:** All TVFs must include a structured COMMENT with seven required sections: PURPOSE, BEST FOR, NOT FOR, RETURNS, PARAMS, SYNTAX, and NOTE.
**Why:** Genie reads the COMMENT to decide which TVF to invoke. Missing sections cause wrong asset selection ("BEST FOR"), TABLE() wrapping errors ("NOTE"), or unwanted GROUP BY ("RETURNS: PRE-AGGREGATED").

**Correct:**
```sql
CREATE OR REPLACE FUNCTION gold.get_daily_cost_summary(
    start_date STRING COMMENT 'Start date (YYYY-MM-DD)',
    end_date STRING DEFAULT NULL COMMENT 'End date (YYYY-MM-DD)'
)
RETURNS TABLE (...)
COMMENT '
* PURPOSE: Get daily cost summary by workspace and SKU.
* BEST FOR: Total spend by workspace | Cost breakdown by SKU | Daily trends
* NOT FOR: Real-time alerts (use get_cost_alerts instead)
* RETURNS: PRE-AGGREGATED rows (one per workspace-SKU-day)
* PARAMS: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD, optional)
* SYNTAX: SELECT * FROM get_daily_cost_summary(''2025-01-01'', ''2025-01-31'')
* NOTE: DO NOT wrap in TABLE(). DO NOT add GROUP BY. Already aggregated.
'
RETURN (...);
```

**Anti-Pattern:**
```sql
COMMENT 'Returns daily costs'  -- Missing all 7 required sections
```

---

### TG-01: Workflow Tags
**Severity:** Critical | **Trigger:** When defining jobs or pipelines in Asset Bundles

**Rule:** All jobs and pipelines must include three required tags: `team`, `cost_center`, and `environment`. Recommended: `project`, `layer`, `job_type`.
**Why:** Missing tags make cost allocation impossible. Untagged workflows cannot be attributed in `system.billing.usage`, creating blind spots in showback/chargeback reporting.

**Correct:**
```yaml
resources:
  jobs:
    gold_merge_job:
      name: "[${bundle.target}] Gold Merge Job"
      tags:
        team: data-engineering
        cost_center: CC-1234
        environment: ${bundle.target}
        project: customer-360
        layer: gold
        job_type: merge
```

**Anti-Pattern:**
```yaml
resources:
  jobs:
    gold_merge_job:
      name: "Gold Merge Job"
      # No tags -- invisible in billing reports
```

---

### TG-02: Governed Tags for Unity Catalog
**Severity:** Critical | **Trigger:** When creating or managing catalogs, schemas, tables, or PII columns

**Rule:** Apply governed tags at every UC level: `cost_center` + `business_unit` on catalogs, `data_owner` on schemas, `data_classification` on sensitive tables, `pii` + `pii_type` on PII columns.
**Why:** Governed tags have enforced allowed values, account-level consistency, and inheritance. Without them, PII columns go untracked and cost centers are unattributable.

**Correct:**
```sql
-- Catalog level
ALTER CATALOG sales_data SET TAGS ('cost_center' = 'CC-1234');
ALTER CATALOG sales_data SET TAGS ('business_unit' = 'Sales');

-- Schema level
ALTER SCHEMA sales_data.gold SET TAGS ('data_owner' = 'analytics-team@company.com');

-- Table level
ALTER TABLE gold.dim_customer SET TAGS ('data_classification' = 'confidential');

-- Column level (PII)
ALTER TABLE gold.dim_customer
ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');

ALTER TABLE gold.dim_customer
ALTER COLUMN ssn SET TAGS ('pii' = 'true', 'pii_type' = 'ssn');
```

**Anti-Pattern:**
```sql
-- No tags at any level -- PII is invisible, costs unattributed
CREATE TABLE gold.dim_customer (
    email STRING,
    ssn STRING
);
```

---

### TG-03: Serverless Budget Policies
**Severity:** Critical | **Trigger:** When provisioning serverless notebooks, jobs, pipelines, or model serving

**Rule:** All serverless compute must use an approved budget policy that enforces `team`, `cost_center`, and `environment` tags.
**Why:** Serverless resources without budget policies bypass cost governance entirely. Untagged serverless usage appears as unattributed spend in billing reports.

**Correct:**
```
1. Settings -> Compute -> Serverless budget policies
2. Create policy: "Data Engineering - Prod"
   Required tags: team, cost_center, environment
3. Assign User/Manager permission to team groups
4. Users select policy when creating serverless resources
```

```sql
-- Query serverless costs by policy tags
SELECT
    usage_date, sku_name,
    custom_tags:team AS team,
    custom_tags:cost_center AS cost_center,
    SUM(list_cost) AS total_cost
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS%'
  AND custom_tags:cost_center IS NOT NULL
GROUP BY 1, 2, 3, 4
ORDER BY usage_date DESC, total_cost DESC;
```

**Anti-Pattern:**
```
-- User creates serverless notebook with no budget policy
-- Cost appears as "unattributed" in billing -- no team, no cost center
```

---

## Checklist
- [ ] NC-01: All object names use snake_case (no camelCase, PascalCase, spaces)
- [ ] NC-02: Tables prefixed correctly (dim_, fact_, bronze_, silver_, agg_, stg_)
- [ ] NC-03: Only approved abbreviations used (id, ts, dt, amt, qty, pct, etc.)
- [ ] CM-01: Every DDL statement has a `/* */` block comment with purpose and history
- [ ] CM-02: Every table has a COMMENT with Business + Technical sections
- [ ] CM-03: Every column has a COMMENT with definition and usage context
- [ ] CM-04: Every TVF has v3.0 structured COMMENT (7 sections: PURPOSE through NOTE)
- [ ] TG-01: All jobs and pipelines have team, cost_center, environment tags
- [ ] TG-02: Catalogs, schemas, tables, and PII columns have governed tags
- [ ] TG-03: All serverless resources use approved budget policies with required tags
