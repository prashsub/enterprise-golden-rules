# Glossary of Terms

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | APP-GLOSS-001 |
| **Version** | 2.0 |
| **Last Updated** | January 2026 |
| **Owner** | Platform Team |
| **Status** | Approved |

---

## A

### Accumulating Snapshot
Fact table type where a single row tracks a business process (e.g., an order) through multiple milestones. Rows are updated as the process progresses. Milestone date columns start as NULL and are filled as events occur. See [Data Modeling](../enterprise-architecture/04-data-modeling.md) DM-01.

### AGGREGATE Metric
A Lakehouse Monitoring custom metric type that performs aggregations (SUM, AVG, COUNT) on source data. Stored in `_profile_metrics` table under the `input_columns` value.

### Asset Bundle
See **Databricks Asset Bundle**.

### Auto Loader
Databricks feature for incrementally processing new data files as they arrive in cloud storage. Uses `cloudFiles` format in Spark structured streaming.

---

## B

### Bronze Layer
First layer in Medallion Architecture. Contains raw, unvalidated data as ingested from source systems. Key property: CDF enabled for downstream streaming.

### Bus Matrix
Enterprise governance artifact that maps business processes (rows) to conformed dimensions (columns). A check mark at an intersection means the process uses that dimension. Maintained by the Platform Architecture team. See [Data Modeling](../enterprise-architecture/04-data-modeling.md) DM-11.

### Business Key
Natural identifier from source system (e.g., `customer_id`, `order_id`). Contrasts with surrogate keys which are generated.

---

## C

### CDF (Change Data Feed)
Delta Lake feature that records row-level changes. Enables incremental streaming from Bronze to Silver layer without full table scans.

### Checkpoint
Stored state for streaming queries or LangGraph workflows. Enables resume from failure and conversation continuity.

### CLUSTER BY AUTO
Delta Lake feature that automatically selects optimal clustering columns based on query patterns. Replaces manual Z-ORDER.

### Conformed Dimension
A dimension table shared identically across multiple fact tables so that queries can drill across business processes. Must have the same keys, attribute names, and domain values everywhere it is used. See [Data Modeling](../enterprise-architecture/04-data-modeling.md) DM-10.

### Conformed Fact
A numeric measure with the same business definition, calculation, and units across multiple fact tables, enabling valid cross-process comparisons.

### Constraint (PK/FK)
Unity Catalog supports informational PRIMARY KEY and FOREIGN KEY constraints with `NOT ENFORCED`. Used for query optimization and documentation, not data validation.

---

## D

### Degenerate Dimension
A dimension attribute (e.g., order number, invoice number) stored directly on the fact table because it has no additional descriptive attributes worth placing in a separate dimension table.

### Databricks Asset Bundle (DAB)
Infrastructure-as-code approach for defining Databricks resources (jobs, pipelines, schemas) in YAML. Deployed via `databricks bundle` CLI.

### Delta Lake
Open-source storage layer providing ACID transactions, time travel, and schema enforcement on data lakes. Required format for all tables.

### Delta Live Tables (DLT)
Declarative framework for building ETL pipelines with automatic dependency management and data quality expectations.

### DERIVED Metric
Lakehouse Monitoring metric type calculated from other metrics. Can only reference metrics in the same `column_name` row.

### DLT Expectation
Data quality rule in Delta Live Tables. Types: `expect` (warn), `expect_or_drop` (drop invalid), `expect_or_fail` (stop pipeline).

### DQX
Databricks Labs Data Quality framework. Provides detailed failure diagnostics beyond basic DLT expectations.

---

## E

### Enriched View
Pre-joined view combining fact and dimension data to work around Metric View transitive join limitations.

---

## F

### Fact Table
Gold layer table containing measurable events/transactions. Has grain (what each row represents) and foreign keys to dimensions. Three types: transaction, periodic snapshot, and accumulating snapshot.

### Factless Fact Table
A fact table with no numeric measures. Records events (e.g., student attendance) or coverage (e.g., which promotions apply to which products). Queried with `COUNT(*)`.

### Feature Table
Unity Catalog table containing ML features with defined primary keys for point-in-time lookups during training and inference.

---

## G

### Genie Space
Natural language interface to data. Uses Metric Views, TVFs, and tables as trusted assets for query generation.

### Gold Layer
Third layer in Medallion Architecture. Contains business-level entities (dimensions, facts) with constraints, documentation, and semantic clarity.

### Grain
The declared level of detail in a fact table — what a single row represents (e.g., one row per transaction, one row per account per month). The most critical decision in dimensional modeling. Mixed grains in a single fact table are prohibited.

---

## I

### input_columns
Lakehouse Monitoring parameter that determines where custom metrics are stored. Use `[":table"]` for table-level KPIs.

### is_current
Boolean column in SCD Type 2 dimensions indicating the current version of a record. Always filter on `is_current = true` for current state.

---

## J

### Junk Dimension
A dimension table that combines multiple low-cardinality flags and indicators (e.g., `is_gift_wrapped`, `payment_method`, `order_channel`) into a single table to keep the fact table lean. Named with `junk_` or `profile_` prefix.

---

## L

### Lakebase
Databricks memory system for GenAI agents. Provides CheckpointSaver (short-term) and DatabricksStore (long-term) storage.

### Lakehouse Monitoring
Automated data quality monitoring with drift detection, profiling, and custom metrics. Creates `_profile_metrics` and `_drift_metrics` tables.

### LangGraph
Framework for building stateful, multi-actor LLM applications with graph-based workflows.

### Liquid Clustering
Delta Lake feature for automatic data organization. Enabled via `CLUSTER BY AUTO`.

---

## M

### Medallion Architecture
Data organization pattern with three layers: Bronze (raw), Silver (validated), Gold (business). Standard for lakehouse implementations.

### Metric View
Semantic layer object defining dimensions and measures in YAML. Enables business-friendly querying via Genie and AI/BI.

### MLflow
Open-source platform for ML lifecycle management. Used for experiment tracking, model registry, and serving.

---

## O

### OBO (On-Behalf-Of)
Authentication pattern where Model Serving uses end-user credentials to access resources. Only works in Model Serving context.

### output_schema
Required MLflow parameter for Unity Catalog models defining the model's output structure.

---

## P

### Periodic Snapshot
Fact table type containing one row per entity per time period (e.g., monthly account balances). Measures are often semi-additive — valid to sum across non-time dimensions but require AVG or latest-value across time.

### Photon
Databricks vectorized query engine providing significant performance improvements for SQL and DataFrame operations.

### Predictive Optimization
Delta Lake feature that automatically optimizes tables based on query patterns. Enabled at catalog or schema level.

### Profile Metrics
Lakehouse Monitoring output table containing data profiling results and custom metrics. Named `{table}_profile_metrics`.

---

## Q

### Quarantine Table
DLT table capturing records that failed data quality expectations. Pattern: `expect_or_drop` + separate quarantine capture.

---

## R

### ResponsesAgent
MLflow base class for building conversational AI agents. Required for production agent deployment.

### RACI Matrix
Framework defining roles: Responsible (does work), Accountable (approves), Consulted (provides input), Informed (notified).

### Role-Playing Dimension
A single physical dimension table joined to a fact table multiple times under different semantic roles. Example: `dim_date` joined as `order_date`, `ship_date`, and `delivery_date` in `fact_order_fulfillment`.

### ROW_NUMBER
SQL window function used in TVFs to implement parameterized limit (since `LIMIT ${param}` is not allowed).

---

## S

### SCD (Slowly Changing Dimension)
A dimension management strategy for handling attribute changes over time. Types: Type 0 (retain original), Type 1 (overwrite), Type 2 (add row with history), Type 3 (add previous-value column), Type 6 (hybrid 1+2+3). See [Data Modeling](../enterprise-architecture/04-data-modeling.md) DM-02.

### SCD Type 2
Slowly Changing Dimension pattern preserving history. Uses `effective_from`, `effective_to`, and `is_current` columns.

### Serverless
Compute type where Databricks manages infrastructure. Required for all new jobs and warehouses.

### Silver Layer
Second layer in Medallion Architecture. Contains validated, deduplicated, and quality-checked data processed by DLT.

### Surrogate Key
System-generated unique identifier (often MD5 hash). Contrasts with business keys from source systems.

---

## T

### TBLPROPERTIES
Delta Lake table metadata. Includes optimization settings (`delta.enableChangeDataFeed`) and governance tags (`layer`, `domain`).

### Transaction Fact Table
The most common fact table type. Contains one row per individual business event (e.g., one row per sale, one row per click). All measures are at the atomic grain of the event.

### TVF (Table-Valued Function)
SQL function returning a table. Used for parameterized queries in Genie Spaces. Must use STRING for date parameters.

---

## U

### Unity Catalog
Databricks unified governance solution for data and AI assets. Provides catalogs, schemas, access control, and lineage.

---

## V

### v1.1 (Metric View)
Current Metric View specification version. Does NOT support `name`, `time_dimension`, or `window_measures` fields.

### v3.0 (Comment Format)
Standardized comment format for TVFs and Metric Views. Uses bullet points: PURPOSE, BEST FOR, NOT FOR, RETURNS, PARAMS, SYNTAX, NOTE.

---

## W

### Widget
Databricks notebook parameter mechanism. Access via `dbutils.widgets.get()` in notebooks running via `notebook_task`.

### Workspace Client
Databricks SDK class for interacting with workspace APIs. Context-aware creation is required for proper authentication.

---

## Y

### YAML-Driven Schema
Pattern where Gold layer table schemas are defined in YAML files (`gold_layer_design/yaml/`) and tables are created dynamically from these definitions.

---

## Acronym Reference

| Acronym | Meaning |
|---------|---------|
| **CDF** | Change Data Feed |
| **DAB** | Databricks Asset Bundle |
| **DLT** | Delta Live Tables |
| **DQX** | Data Quality (Databricks Labs) |
| **FK** | Foreign Key |
| **KPI** | Key Performance Indicator |
| **LLM** | Large Language Model |
| **ML** | Machine Learning |
| **OBO** | On-Behalf-Of |
| **PII** | Personally Identifiable Information |
| **PK** | Primary Key |
| **RACI** | Responsible, Accountable, Consulted, Informed |
| **SCD** | Slowly Changing Dimension |
| **TVF** | Table-Valued Function |
| **UC** | Unity Catalog |

---

## Rule ID Prefixes

| Prefix | Domain |
|--------|--------|
| **EA** | Enterprise Architecture |
| **PA** | Platform Architecture |
| **DP** | Data Pipelines |
| **SL** | Semantic Layer |
| **ML** | Machine Learning |
| **MO** | Monitoring |
| **DB** | Dashboards |

---

## Related Documents

- [Golden Rules Index](../README.md)
- [Quick Reference Cards](quick-reference-cards.md)
- [All Standards Documents](../)
