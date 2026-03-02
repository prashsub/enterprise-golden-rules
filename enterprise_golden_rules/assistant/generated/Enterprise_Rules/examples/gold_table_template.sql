-- =============================================================================
-- GOLD TABLE DDL TEMPLATE
-- =============================================================================
-- Enterprise Golden Rules Satisfied:
--   DM-01  : Dimensional modeling (star schema) for Gold layer
--   DM-02  : PRIMARY KEY constraints on all dimension and fact tables
--   DM-03  : FOREIGN KEY constraints to document relationships
--   DM-06  : NOT NULL enforced constraints for data integrity
--   DM-09  : Designed for both BI and AI consumption
--   DA-01  : Gold tables define PK/FK constraints
--   DA-08  : LLM-friendly documentation (business + technical)
--   NC-01  : All object names use snake_case
--   NC-02  : Tables prefixed by entity type (dim_, fact_)
--   CM-01  : SQL block comments for all DDL operations
--   CM-02  : Table COMMENT follows dual-purpose format
--   CM-03  : Column COMMENT required for all columns
--   PA-02  : All tables use Delta Lake
--   DP-02  : CDF enabled via table properties
-- =============================================================================
--
-- INSTRUCTIONS:
--   1. Replace ${catalog} and ${schema} with your target catalog and schema.
--   2. Customize columns to match your Gold YAML definition (DA-02).
--   3. Run Part 1 (dimension) first, then Part 2 (fact), then Part 3 (constraints).
--   4. Constraint application order: tables -> PKs -> FKs (DM-03).
-- =============================================================================


-- *****************************************************************************
-- PART 1: DIMENSION TABLE (SCD Type 2)
-- *****************************************************************************

/*
 * Table: dim_customer
 * Layer: Gold
 * Domain: ${domain}
 *
 * Purpose: Customer dimension with SCD Type 2 history tracking.
 *          Primary reference for all customer analytics and segmentation.
 *
 * Grain: One row per customer per effective period.
 * Source: Silver layer silver_customers table.
 * SCD Strategy: Type 2 -- new row on attribute change, is_current flag.
 *
 * Rules Satisfied:
 *   DM-01  (star schema dimension)
 *   DM-02  (PRIMARY KEY declared)
 *   DM-06  (NOT NULL on required columns)
 *   DM-09  (ML-friendly numeric attributes with NOT NULL + DEFAULT)
 *   DA-05  (surrogate key via MD5 hash)
 *   DA-07  (SCD Type 2 with effective_from/to, is_current)
 *   CM-02  (table COMMENT: business + technical)
 *   CM-03  (column COMMENT: business + technical on every column)
 *
 * Change History:
 *   YYYY-MM-DD - Initial creation (your_name)
 */
CREATE TABLE IF NOT EXISTS ${catalog}.${schema}.dim_customer (

    -- Surrogate key (DA-05: MD5 hash of business key + effective_from)
    customer_key STRING NOT NULL
        COMMENT 'Surrogate key for SCD Type 2 versioning. Business: Used for joining fact tables to this dimension. Technical: MD5 hash of customer_id + effective_from timestamp.',

    -- Business key (immutable across SCD2 versions)
    customer_id STRING NOT NULL
        COMMENT 'Natural business key identifying the customer. Business: Stable identifier used by CRM and support teams. Technical: Immutable, same across all SCD2 versions.',

    -- Descriptive attributes
    customer_name STRING NOT NULL
        COMMENT 'Full legal name of the customer. Business: Display name in reports and correspondence. Technical: Source from silver_customers.full_name, trimmed and title-cased.',

    email STRING
        COMMENT 'Primary email address. Business: Used for communication and marketing segmentation. Technical: Validated format in Silver layer, may be NULL for legacy records.',

    phone STRING
        COMMENT 'Primary phone number. Business: Contact number for customer service. Technical: Normalized to E.164 format in Silver layer.',

    customer_segment STRING NOT NULL
        COMMENT 'Business segment classification. Business: Used for cohort analysis, dashboard filtering, and Genie queries. Technical: Derived from annual spend tiers in Silver.',

    region STRING NOT NULL
        COMMENT 'Geographic region of the customer. Business: Regional sales reporting and territory analysis. Technical: Mapped from postal code in Silver layer.',

    -- ML-friendly numeric attributes (DM-09: NOT NULL + DEFAULT for AI consumption)
    lifetime_value DECIMAL(18,2) NOT NULL DEFAULT 0
        COMMENT 'Total historical spend in USD. Business: Key metric for customer value segmentation. Technical: ML-friendly numeric feature, no nulls, updated daily from fact_orders.',

    order_count INT NOT NULL DEFAULT 0
        COMMENT 'Total number of orders placed. Business: Frequency metric for RFM analysis. Technical: ML-friendly numeric feature, no nulls, count of fact_orders rows.',

    days_since_last_order INT
        COMMENT 'Days since most recent order. Business: Recency metric for churn prediction. Technical: ML feature calculated as DATEDIFF(CURRENT_DATE, MAX(order_date)).',

    -- SCD Type 2 tracking columns (DA-07)
    effective_from TIMESTAMP NOT NULL
        COMMENT 'Record effective start timestamp. Business: When this version of the customer record became active. Technical: Set from source processed_timestamp during MERGE.',

    effective_to TIMESTAMP
        COMMENT 'Record effective end timestamp. Business: When this version was superseded (NULL means current). Technical: Set when a new version is inserted; NULL indicates active record.',

    is_current BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indicates if this is the current version of the record. Business: Filter to is_current=true for current-state queries. Technical: Set to false when new SCD2 version inserted.',

    -- Audit metadata
    record_created_timestamp TIMESTAMP NOT NULL
        COMMENT 'Timestamp when this row was first created. Business: Audit trail for data lineage. Technical: Set to current_timestamp() during INSERT.',

    record_updated_timestamp TIMESTAMP NOT NULL
        COMMENT 'Timestamp when this row was last modified. Business: Audit trail for data freshness. Technical: Updated to current_timestamp() during MERGE WHEN MATCHED.',

    -- Primary key constraint (DM-02: NOT ENFORCED, informational for optimizer)
    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO
COMMENT 'Customer dimension with SCD Type 2 history tracking for all customer attributes. Business: Primary customer reference for segmentation, lifetime value, cohort analysis, and churn prediction. Technical: MD5 surrogate key, is_current flag for active records, daily merge from Silver, CDF enabled.'
TBLPROPERTIES (
    'quality' = 'gold',
    'layer' = 'gold',
    'delta.enableChangeDataFeed' = 'true',
    'domain' = '${domain}',
    'scd_type' = '2'
);


-- *****************************************************************************
-- PART 2: FACT TABLE
-- *****************************************************************************

/*
 * Table: fact_orders
 * Layer: Gold
 * Domain: ${domain}
 *
 * Purpose: Daily order facts capturing all completed transactions at
 *          customer-product-day grain. Primary source for revenue reporting.
 *
 * Grain: One row per order_date + customer_key + product_key.
 * Source: Silver layer silver_orders table.
 * Update Strategy: Incremental MERGE with deduplication (DA-06).
 *
 * Rules Satisfied:
 *   DM-01  (star schema fact table)
 *   DM-02  (composite PRIMARY KEY)
 *   DM-06  (NOT NULL on required columns, CHECK on business rules)
 *   DA-06  (deduplicate before MERGE)
 *   CM-02  (table COMMENT: business + technical)
 *   CM-03  (column COMMENT: business + technical on every column)
 *
 * Change History:
 *   YYYY-MM-DD - Initial creation (your_name)
 */
CREATE TABLE IF NOT EXISTS ${catalog}.${schema}.fact_orders (

    -- Degenerate dimension / natural key
    order_id BIGINT NOT NULL
        COMMENT 'Unique order identifier. Business: Order reference number for tracking and support. Technical: Source system PK, used as deduplication key before MERGE.',

    -- Time dimension FK
    order_date DATE NOT NULL
        COMMENT 'Date when order was placed. Business: Primary time dimension for trend analysis and reporting. Technical: Truncated from order_timestamp, FK to dim_date.',

    -- Dimension foreign keys
    customer_key STRING NOT NULL
        COMMENT 'FK to dim_customer dimension. Business: Links orders to customer for segmentation and lifetime value analysis. Technical: Must match existing customer_key in dim_customer where is_current=true.',

    product_key STRING NOT NULL
        COMMENT 'FK to dim_product dimension. Business: Links orders to product for category and brand analysis. Technical: Must match existing product_key in dim_product.',

    store_key STRING NOT NULL
        COMMENT 'FK to dim_store dimension. Business: Links orders to store location for geographic and channel analysis. Technical: Must match existing store_key in dim_store.',

    -- Measures
    quantity INT NOT NULL
        COMMENT 'Number of units ordered. Business: Volume metric for inventory planning and demand forecasting. Technical: Must be positive integer, validated by CHECK constraint.',

    unit_price DECIMAL(18,2) NOT NULL
        COMMENT 'Price per unit at time of sale in USD. Business: Used for average selling price analysis. Technical: Captured at transaction time, not updated retroactively.',

    discount_pct DECIMAL(5,2) NOT NULL DEFAULT 0
        COMMENT 'Discount percentage applied to this line. Business: Promotion effectiveness and margin analysis. Technical: Range 0-100, validated by CHECK constraint.',

    total_amount DECIMAL(18,2) NOT NULL
        COMMENT 'Total order amount after discounts in USD. Business: Primary revenue metric for financial reporting and dashboards. Technical: Calculated as quantity * unit_price * (1 - discount_pct/100).',

    tax_amount DECIMAL(18,2) NOT NULL DEFAULT 0
        COMMENT 'Tax amount in USD. Business: Tax liability reporting by jurisdiction. Technical: Calculated based on store location tax rate.',

    -- Audit metadata
    record_created_timestamp TIMESTAMP NOT NULL
        COMMENT 'Timestamp when this row was first created. Business: Audit trail for data lineage. Technical: Set to current_timestamp() during INSERT.',

    record_updated_timestamp TIMESTAMP NOT NULL
        COMMENT 'Timestamp when this row was last modified. Business: Audit trail for data freshness. Technical: Updated to current_timestamp() during MERGE WHEN MATCHED.',

    -- Composite primary key constraint (DM-02)
    CONSTRAINT pk_fact_orders
        PRIMARY KEY (order_id) NOT ENFORCED,

    -- CHECK constraints for business rules (DM-06)
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0),
    CONSTRAINT chk_discount_range CHECK (discount_pct BETWEEN 0 AND 100),
    CONSTRAINT chk_amount_non_negative CHECK (total_amount >= 0)
)
USING DELTA
CLUSTER BY AUTO
COMMENT 'Daily order facts at order grain with customer, product, and store dimensions. Business: Primary source for revenue reporting, conversion analysis, sales dashboards, and demand forecasting. Technical: Composite PK on order_id, incremental MERGE with deduplication, CDF enabled, CHECK constraints on measures.'
TBLPROPERTIES (
    'quality' = 'gold',
    'layer' = 'gold',
    'delta.enableChangeDataFeed' = 'true',
    'domain' = '${domain}'
);


-- *****************************************************************************
-- PART 3: FOREIGN KEY CONSTRAINTS
-- *****************************************************************************
-- IMPORTANT (DM-03): FK constraints must be applied AFTER both tables exist
-- and AFTER all PRIMARY KEY constraints are in place.
--
-- Application order:
--   Step 1: Create all tables (Parts 1 and 2 above)
--   Step 2: PKs are already declared inline above
--   Step 3: Apply FKs below (this section)
-- *****************************************************************************

/*
 * Constraint: fk_orders_customer
 * Type: Foreign Key (NOT ENFORCED - informational only)
 * Purpose: Documents relationship between fact_orders and dim_customer.
 *          Used by query optimizer for join ordering and by Metric Views
 *          for automatic join inference in Genie/AI-BI.
 */
ALTER TABLE ${catalog}.${schema}.fact_orders
ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_key)
    REFERENCES ${catalog}.${schema}.dim_customer(customer_key) NOT ENFORCED;

/*
 * Constraint: fk_orders_product
 * Type: Foreign Key (NOT ENFORCED - informational only)
 * Purpose: Documents relationship between fact_orders and dim_product.
 *          Enables product-level analytics in Metric Views and Genie.
 */
ALTER TABLE ${catalog}.${schema}.fact_orders
ADD CONSTRAINT fk_orders_product
    FOREIGN KEY (product_key)
    REFERENCES ${catalog}.${schema}.dim_product(product_key) NOT ENFORCED;

/*
 * Constraint: fk_orders_store
 * Type: Foreign Key (NOT ENFORCED - informational only)
 * Purpose: Documents relationship between fact_orders and dim_store.
 *          Enables geographic analytics and store-level reporting.
 */
ALTER TABLE ${catalog}.${schema}.fact_orders
ADD CONSTRAINT fk_orders_store
    FOREIGN KEY (store_key)
    REFERENCES ${catalog}.${schema}.dim_store(store_key) NOT ENFORCED;


-- *****************************************************************************
-- VERIFICATION QUERIES
-- *****************************************************************************

-- Verify table exists and check properties
-- DESCRIBE EXTENDED ${catalog}.${schema}.dim_customer;
-- DESCRIBE EXTENDED ${catalog}.${schema}.fact_orders;

-- Verify table properties
-- SHOW TBLPROPERTIES ${catalog}.${schema}.dim_customer;
-- SHOW TBLPROPERTIES ${catalog}.${schema}.fact_orders;

-- Verify constraints
-- SHOW CONSTRAINTS ON ${catalog}.${schema}.dim_customer;
-- SHOW CONSTRAINTS ON ${catalog}.${schema}.fact_orders;
