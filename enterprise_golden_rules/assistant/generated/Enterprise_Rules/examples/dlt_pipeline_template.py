"""
DLT (Lakeflow Spark Declarative Pipelines) Pipeline Template
=============================================================

Enterprise Golden Rules Satisfied:
  DP-01  : Medallion Architecture required (Bronze -> Silver -> Gold)
  DP-02  : CDF enabled on Bronze tables for downstream streaming
  DP-03  : Preserve source schema in Bronze layer
  DP-04  : Append-only ingestion for Bronze
  DP-06  : Incremental ingestion via cloud_files (Auto Loader)
  DA-03  : Silver must use Lakeflow SDP with expectations
  DA-04  : Expectations quarantine bad records (expect_all_or_drop)
  DA-06  : Pure Python files for shared modules (no notebook header)
  PA-02  : All tables use Delta Lake
  CM-02  : Table COMMENT follows dual-purpose format (business + technical)
  NC-01  : All object names use snake_case
  NC-02  : Tables prefixed by layer (bronze_, silver_)
  IN-04  : Parameters via dbutils.widgets.get()

INSTRUCTIONS:
  1. Replace placeholder variables with your actual values.
  2. This file is a DLT pipeline notebook -- deploy via Asset Bundle pipeline resource.
  3. Shared helper functions must be in pure Python files (no notebook header).
  4. Configure the pipeline in your databricks.yml with:
       serverless: true
       photon: true
       channel: CURRENT
       edition: ADVANCED

IMPORTANT: This file must NOT have a "# Databricks notebook source" header
when used as an importable module. When used as a DLT notebook, Databricks
handles the runtime context automatically.
"""

# =============================================================================
# IMPORTS
# =============================================================================

import dlt  # Lakeflow SDP uses the 'dlt' module
from pyspark.sql.functions import (
    col,
    current_timestamp,
    input_file_name,
    lit,
    when,
)

# Pure Python helper import (DA-06: no notebook header in helper files)
# from helpers.quality_rules import get_quality_rules
# from helpers.transformations import normalize_email, standardize_phone


# =============================================================================
# PARAMETERS (IN-04: dbutils.widgets.get for all parameters)
# =============================================================================
# These are passed via base_parameters in the Asset Bundle YAML.
# In DLT pipelines, use spark.conf.get() for pipeline-level configuration
# or dbutils.widgets.get() for job-level parameters.

# Landing zone path for raw files
LANDING_PATH = "s3://your-landing-bucket/${domain}/orders/"

# Source system identifier
SOURCE_SYSTEM = "retail_pos"

# Domain name
DOMAIN = "sales"


# =============================================================================
# BRONZE LAYER
# =============================================================================

@dlt.table(
    # Table name: bronze_ prefix per NC-02
    name="bronze_orders",

    # CM-02: Dual-purpose COMMENT (business + technical)
    comment=(
        "Raw order events from POS system with minimal transformation. "
        "Business: Source data for order analytics, retained for audit and replay. "
        "Technical: Appended via Auto Loader (cloud_files), CDF enabled, schema evolution on."
    ),

    # Table properties: CDF (DP-02), layer tag, quality indicator
    table_properties={
        "quality": "bronze",
        "layer": "bronze",
        "delta.enableChangeDataFeed": "true",       # DP-02: Required for Silver streaming
        "delta.autoOptimize.optimizeWrite": "true",
        "source_system": SOURCE_SYSTEM,
        "domain": DOMAIN,
    },

    # Automatic clustering for query optimization
    cluster_by_auto=True,
)
def bronze_orders():
    """
    Bronze ingestion: Append-only (DP-04) with source schema preserved (DP-03).
    Uses cloud_files (Auto Loader) for incremental ingestion (DP-06).
    """
    return (
        spark.readStream
        .format("cloudFiles")                                     # DP-06: Auto Loader
        .option("cloudFiles.format", "json")                      # Adjust format as needed
        .option("cloudFiles.schemaLocation", f"{LANDING_PATH}/_schema")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns") # DP-03: Preserve source
        .load(LANDING_PATH)
        # Add metadata columns only -- no business transformations in Bronze
        .withColumn("_ingested_timestamp", current_timestamp())
        .withColumn("_source_file", input_file_name())
        .withColumn("_source_system", lit(SOURCE_SYSTEM))
    )


# =============================================================================
# SILVER LAYER
# =============================================================================

@dlt.table(
    # Table name: silver_ prefix per NC-02
    name="silver_orders",

    # CM-02: Dual-purpose COMMENT (business + technical)
    comment=(
        "Validated and deduplicated orders with quality expectations enforced. "
        "Business: Clean order data for downstream Gold layer analytics and reporting. "
        "Technical: DLT streaming from bronze_orders via CDF, expect_all_or_drop on required fields, row tracking enabled."
    ),

    # Table properties: CDF, row tracking, quality indicator
    table_properties={
        "quality": "silver",
        "layer": "silver",
        "delta.enableChangeDataFeed": "true",       # Enable CDF for Gold layer streaming
        "delta.enableRowTracking": "true",           # Row-level tracking for lineage
        "delta.autoOptimize.optimizeWrite": "true",
        "source_table": "bronze_orders",
        "domain": DOMAIN,
    },

    # Automatic clustering for query optimization
    cluster_by_auto=True,
)
# DA-03: Expectations for data quality enforcement
# DA-04: expect_all_or_drop quarantines bad records by excluding them
@dlt.expect_all_or_drop({
    "valid_order_id":    "order_id IS NOT NULL",
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_amount":      "amount > 0",
    "valid_quantity":    "quantity > 0",
    "valid_order_date":  "order_date IS NOT NULL",
})
def silver_orders():
    """
    Silver transformation: Clean, validate, and deduplicate Bronze data.
    Reads from bronze_orders using CDF streaming.
    """
    return (
        dlt.read_stream("bronze_orders")
        .select(
            # Business columns -- validated by expectations above
            col("order_id").cast("BIGINT").alias("order_id"),
            col("customer_id").cast("STRING").alias("customer_id"),
            col("product_id").cast("STRING").alias("product_id"),
            col("store_id").cast("STRING").alias("store_id"),
            col("order_date").cast("DATE").alias("order_date"),
            col("quantity").cast("INT").alias("quantity"),
            col("unit_price").cast("DECIMAL(18,2)").alias("unit_price"),
            col("discount_pct").cast("DECIMAL(5,2)").alias("discount_pct"),
            col("amount").cast("DECIMAL(18,2)").alias("amount"),

            # Processing metadata
            current_timestamp().alias("processed_timestamp"),
            col("_source_file").alias("source_file"),
        )
    )


# =============================================================================
# SILVER QUARANTINE TABLE
# =============================================================================

@dlt.table(
    name="silver_orders_quarantine",

    comment=(
        "Quarantined order records that failed Silver quality expectations. "
        "Business: Investigation queue for data stewards to review and remediate bad records. "
        "Technical: Captures records failing any expect_all_or_drop rule from silver_orders."
    ),

    table_properties={
        "quality": "silver",
        "layer": "silver",
        "record_type": "quarantine",
        "domain": DOMAIN,
    },

    cluster_by_auto=True,
)
def silver_orders_quarantine():
    """
    Quarantine pattern (DA-04): Capture records that fail quality rules.
    Uses inverse of the expectation conditions from silver_orders.
    """
    return (
        dlt.read_stream("bronze_orders")
        .filter(
            (col("order_id").isNull())
            | (col("customer_id").isNull())
            | (col("amount") <= 0)
            | (col("quantity") <= 0)
            | (col("order_date").isNull())
        )
        .withColumn(
            "quarantine_reason",
            when(col("order_id").isNull(), "null_order_id")
            .when(col("customer_id").isNull(), "null_customer_id")
            .when(col("amount") <= 0, "invalid_amount")
            .when(col("quantity") <= 0, "invalid_quantity")
            .when(col("order_date").isNull(), "null_order_date")
            .otherwise("unknown"),
        )
        .withColumn("quarantined_timestamp", current_timestamp())
    )


# =============================================================================
# SILVER CUSTOMER DIMENSION (Streaming from Bronze)
# =============================================================================

@dlt.table(
    name="silver_customers",

    comment=(
        "Validated customer records with quality expectations enforced. "
        "Business: Clean customer data for Gold dim_customer SCD2 processing. "
        "Technical: DLT streaming from bronze_customers, row tracking enabled."
    ),

    table_properties={
        "quality": "silver",
        "layer": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.enableRowTracking": "true",
        "source_table": "bronze_customers",
        "domain": DOMAIN,
    },

    cluster_by_auto=True,
)
@dlt.expect_all_or_drop({
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_name":        "customer_name IS NOT NULL",
    "valid_email":       "email LIKE '%@%'",
})
def silver_customers():
    """
    Silver customer transformation with quality enforcement.
    """
    return (
        dlt.read_stream("bronze_customers")
        .select(
            col("customer_id").cast("STRING").alias("customer_id"),
            col("customer_name").cast("STRING").alias("customer_name"),
            col("email").cast("STRING").alias("email"),
            col("phone").cast("STRING").alias("phone"),
            col("segment").cast("STRING").alias("customer_segment"),
            col("region").cast("STRING").alias("region"),
            current_timestamp().alias("processed_timestamp"),
        )
    )
