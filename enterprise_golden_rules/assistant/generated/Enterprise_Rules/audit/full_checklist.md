# Enterprise Golden Rules — Full Audit Checklist

**Version:** 5.4.1 | **Rules:** 162+ | **Updated:** Feb 2026

Instructions: Mark each rule as PASS, FAIL, or N/A. For FAIL items, note the cell/line and required fix.

**Scoring:** Compliance % = (PASS / (PASS + FAIL)) x 100. N/A items are excluded from scoring.

| Severity | Meaning | Action |
|----------|---------|--------|
| Critical | Must follow — blocks production deployment | Fix immediately |
| Required | Should follow — fix within current sprint | Fix before next release |

---

## Table Creation & Storage (DL, SC, PA)

- [ ] **DL-01** [Critical] All tables in Unity Catalog (no HMS)
- [ ] **DL-02** [Critical] Managed tables are the default
- [ ] **DL-03** [Required] External tables require approval
- [ ] **DL-04** [Critical] Delta Lake format for all tables
- [ ] **SC-01** [Critical] Serverless compute for all jobs
- [ ] **SC-02** [Critical] Serverless SQL Warehouses for all SQL workloads
- [ ] **SC-03** [Critical] Serverless Jobs for notebooks and Python
- [ ] **SC-04** [Critical] Serverless DLT for all pipelines
- [ ] **SC-05** [Required] Use latest serverless environment version
- [ ] **SC-06** [Critical] Pin all custom dependencies with explicit versions
- [ ] **SC-07** [Required] Use workspace base environments for shared dependencies
- [ ] **SC-08** [Critical] Never install PySpark on serverless compute
- [ ] **SC-09** [Required] Configure private package repositories for internal libraries
- [ ] **DL-05** [Critical] Automatic Liquid Clustering (CLUSTER BY AUTO) on all tables
- [ ] **DL-06** [Required] Standard TBLPROPERTIES required on all tables
- [ ] **DL-07** [Required] LLM-friendly COMMENTs required on all tables and columns
- [ ] **PY-01** [Critical] `dbutils.widgets.get()` for notebook parameters
- [ ] **PA-01** [Critical] No production data on DBFS root
- [ ] **PA-02** [Critical] System tables enabled for platform observability
- [ ] **PA-03** [Critical] Workspace isolation by environment and security boundary
- [ ] **PA-04** [Required] Use Lakehouse Federation for external data access
- [ ] **PA-05** [Required] Use certified partner integrations
- [ ] **DL-08** [Required] Never use Spark caching with Delta tables
- [ ] **DL-09** [Critical] Never manually modify Delta data files
- [ ] **DL-10** [Required] Remove legacy Delta configurations on upgrade
- [ ] **DL-11** [Critical] UniForm enabled for cross-engine interoperability
- [ ] **DL-12** [Required] Run ANALYZE TABLE on performance-critical tables

---

## Naming & Comments (NC, CM)

- [ ] **NC-01** [Critical] All object names use `snake_case`
- [ ] **NC-02** [Critical] Tables prefixed by layer or entity type
- [ ] **NC-03** [Required] No abbreviations except approved list
- [ ] **CM-01** [Required] SQL block comments for all DDL operations
- [ ] **CM-02** [Critical] Table COMMENT follows dual-purpose format (business + technical)
- [ ] **CM-03** [Critical] Column COMMENT required for all columns (business + technical)
- [ ] **CM-04** [Critical] TVF COMMENT follows v3.0 structured format

---

## Tagging (TG)

- [ ] **TG-01** [Critical] All workflows must have required tags (team, cost_center, environment)
- [ ] **TG-02** [Critical] Use Governed Tags for UC securables
- [ ] **TG-03** [Critical] Serverless resources must use approved budget policies

---

## Data Pipelines — Bronze/Silver/Gold (DP, DA)

- [ ] **DP-01** [Critical] Medallion Architecture required (Bronze -> Silver -> Gold)
- [ ] **DP-02** [Critical] CDF enabled on Bronze tables (`delta.enableChangeDataFeed = true`)
- [ ] **DP-03** [Critical] DLT with expectations for Silver layer / Preserve source schema
- [ ] **DP-04** [Required] Append-only ingestion for Bronze / Gold tables from YAML schema
- [ ] **DP-05** [Critical] Prefer Lakeflow Connect managed connectors / Dedup before MERGE in Gold
- [ ] **DP-06** [Required] Use incremental ingestion / PK-FK constraints in Gold
- [ ] **DA-01** [Critical] Schema extracted from YAML (never generated)
- [ ] **SA-01** [Critical] Silver must use Lakeflow SDP with expectations
- [ ] **SA-02** [Required] Expectations must quarantine bad records
- [ ] ~~**SA-03**~~ Retired → see **DQ-02** (DQX for advanced validation)
- [ ] ~~**SA-04**~~ Retired → see **PY-02** (Pure Python files for shared modules)
- [ ] **DA-02** [Required] Surrogate keys via MD5 hash
- [ ] **DA-03** [Critical] Always deduplicate before MERGE
- [ ] **DA-04** [Required] SCD Type 2 for historical dimensions

---

## Data Quality (DQ)

- [ ] **DQ-01** [Critical] All DLT pipelines must have data quality expectations
- [ ] **DQ-02** [Critical] Classic Spark jobs must use DQX for quality validation
- [ ] **DQ-03** [Critical] Gold layer tables must have Lakehouse Monitors
- [ ] **DQ-04** [Critical] Quality failures must be captured, not silently dropped
- [ ] **DQ-05** [Critical] Enable schema-level anomaly detection for freshness and completeness
- [ ] **DQ-06** [Required] Configure data profiling with baseline tables for drift detection
- [ ] **DQ-07** [Required] Define custom metrics for business KPIs in Lakehouse Monitors

---

## Data Modeling (DM)

- [ ] **DM-01** [Critical] Dimensional modeling (star/snowflake) for Gold layer
- [ ] **DM-02** [Critical] PRIMARY KEY constraints on all tables
- [ ] **DM-03** [Required] FOREIGN KEY constraints to document relationships
- [ ] **DM-04** [Required] Avoid heavily normalized models (3NF) in analytical layers
- [ ] **DM-05** [Required] Design for minimal joins in common query patterns
- [ ] **DM-06** [Required] Use enforced constraints (NOT NULL, CHECK) for integrity
- [ ] **DM-07** [Required] Handle semi-structured data with appropriate complex types
- [ ] **DM-08** [Required] Design for single-table transactions
- [ ] **DM-09** [Required] Design Gold layer for both BI and AI consumption

---

## Semantic Layer (MV, TF, GN)

> Note: SL-01 and SL-02 have been retired. Their requirements are now covered by MV-01/MV-04 and MV-05 respectively.

- [ ] **TF-01** [Critical] STRING type for date parameters in TVFs
- [ ] **TF-02** [Required] Schema validation before writing SQL
- [ ] **TF-03** [Required] v3.0 comment format for TVFs (PURPOSE, BEST FOR)
- [ ] **GN-01** [Required] Inventory-first creation for Genie Spaces
- [ ] **GN-02** [Required] v3.0 comment format for Genie Spaces
- [ ] **GN-03** [Required] Curated data for Genie (comments, no nulls)
- [ ] **TF-04** [Required] Required parameters before optional in TVFs
- [ ] **TF-05** [Required] No LIMIT with parameters in TVFs
- [ ] **TF-06** [Required] Single aggregation pass in TVFs
- [ ] **MV-01** [Critical] All core metrics MUST be in Metric Views
- [ ] **MV-02** [Critical] Reference Gold layer tables only
- [ ] **MV-03** [Required] Business context documentation required
- [ ] **MV-04** [Required] Schema validation before creation
- [ ] **MV-05** [Critical] No transitive joins
- [ ] **MV-06** [Required] Synonyms for all dimensions and measures
- [ ] **MV-07** [Required] Display format for all measures
- [ ] **MV-08** [Required] Structured comment format

---

## Monitoring & Dashboards (MO, DB)

- [ ] **MO-01** [Required] Use `input_columns=[":table"]` for table-level KPIs
- [ ] **DB-03** [Critical] Dashboard fieldName must match query alias
- [ ] **DB-04** [Required] SQL returns raw numbers (widgets format)
- [ ] **MO-02** [Required] Document monitor output tables for Genie
- [ ] **MO-04** [Required] Implement async wait pattern for monitors
- [ ] **DB-01** [Required] No hardcoded environment values in dashboards
- [ ] **DB-02** [Required] UPDATE-or-CREATE deployment pattern
- [ ] **MO-03** [Critical] All related metrics must use same input_columns

---

## Streaming (ST)

- [ ] **ST-01** [Critical] Lakeflow SDP First for streaming
- [ ] **ST-02** [Critical] Managed Checkpointing for DR
- [ ] **ST-03** [Required] Fixed worker count for streaming (cost optimization)
- [ ] **ST-04** [Critical] Idempotent Operations for streaming

---

## Asset Bundles & Deployment (IN, PY)

- [ ] **PY-02** [Required] Pure Python files for imports (no notebook header)
- [ ] **PY-03** [Critical] sys.path setup for Asset Bundle imports
- [ ] **PY-04** [Critical] No `# Databricks notebook source` in importable modules
- [ ] **IN-01** [Critical] Serverless compute for all jobs in bundle config
- [ ] **IN-02** [Critical] Environment-level dependencies (not task-level)
- [ ] **IN-03** [Critical] Use notebook_task (never python_task)
- [ ] **IN-04** [Critical] Use `dbutils.widgets.get()` for parameters
- [ ] **IN-05** [Critical] Hierarchical job architecture (orchestrator + atomic)
- [ ] **IN-06** [Critical] Notebooks in exactly ONE atomic job
- [ ] **IN-07** [Required] Use run_job_task for job references
- [ ] **IN-08** [Required] Include `[${bundle.target}]` prefix in job names
- [ ] **IN-11** [Critical] Use `mode: development` / `mode: production` on all targets
- [ ] **IN-12** [Critical] Set `run_as` to service principal for staging/prod targets
- [ ] **IN-13** [Required] Define top-level `permissions` block on all bundles

---

## Governance (GOV, EA)

- [ ] **EA-01** [Required] All data assets must have business context documentation
- [ ] **EA-02** [Required] PII columns must be tagged and classified
- [ ] **EA-03** [Required] Every data domain must have an assigned data steward
- [ ] **EA-04** [Required] All compute usage must be attributed with tags
- [ ] **EA-05** [Required] Required custom tags: team, cost_center, environment
- [ ] **EA-06** [Required] All serverless workloads must use assigned budget policies
- [ ] **EA-07** [Required] All new projects require architecture review
- [ ] **EA-08** [Required] Rule exceptions require documented approval
- [ ] **EA-09** [Required] Use Governed Tags for UC object metadata
- [ ] **EA-10** [Critical] Treat data as a product with defined SLAs and ownership
- [ ] **EA-11** [Required] Define data contracts for cross-domain interfaces
- [ ] **EA-12** [Required] Assess and track AI readiness across data domains
- [ ] **GOV-01** [Critical] Provision identities at account level via SCIM
- [ ] **GOV-02** [Critical] Define and manage groups in your identity provider
- [ ] **GOV-03** [Critical] Assign admin roles sparingly; avoid ALL PRIVILEGES
- [ ] **GOV-04** [Required] Use catalog-level managed storage for data isolation
- [ ] **GOV-05** [Critical] Prefer managed tables over external tables
- [ ] **GOV-06** [Critical] Use service principals for production jobs
- [ ] **GOV-07** [Required] Assign object ownership to groups, not individuals
- [ ] **GOV-08** [Required] Use lineage for impact analysis before schema changes
- [ ] **GOV-09** [Required] Implement governance-as-code via system tables
- [ ] **GOV-10** [Required] Use row filters and column masks for fine-grained access
- [ ] **GOV-11** [Required] Configure audit logging for all workspaces
- [ ] **GOV-12** [Critical] Use ABAC policies for scalable tag-driven access control
- [ ] **GOV-13** [Required] Define ABAC policies at catalog level for maximum inheritance
- [ ] **GOV-14** [Critical] Use RBAC (privilege grants) as the baseline access model
- [ ] **GOV-15** [Required] Keep ABAC UDFs simple, deterministic, and free of external calls
- [ ] **GOV-16** [Required] Grant BROWSE on catalogs for data discoverability

---

## Security (SEC, SM)

- [ ] **SM-01** [Critical] All secrets in Databricks Secret Scopes
- [ ] **SM-02** [Critical] Never hardcode credentials
- [ ] **SM-03** [Critical] Use dbutils.secrets.get() only
- [ ] **SM-04** [Required] Workspace follows naming conventions
- [ ] **SEC-01** [Critical] Production workspaces must use VNet/VPC injection
- [ ] **SEC-02** [Critical] Configure Private Link/PSC for control plane access
- [ ] **SEC-03** [Required] Implement IP access lists for workspace access
- [ ] **SEC-04** [Required] Use customer-managed keys (CMK) for encryption
- [ ] **SEC-05** [Required] Enable diagnostic logging to cloud monitoring
- [ ] **SEC-06** [Required] Configure network egress controls
- [ ] **SEC-07** [Critical] Use secure cluster connectivity (no public IPs)
- [ ] **SEC-08** [Required] Enable Compliance Security Profile for regulated workloads
- [ ] **SEC-09** [Required] Security monitoring and SIEM integration

---

## Reliability & Compute (REL, CP)

- [ ] **REL-01** [Critical] Delta Lake time travel >= 7 days retention
- [ ] **REL-02** [Required] Configure job retry with exponential backoff
- [ ] **REL-03** [Critical] Streaming checkpoints on ZRS/GRS storage
- [ ] **REL-04** [Required] Enable cluster autoscaling for variable workloads
- [ ] **REL-05** [Required] Configure auto-termination on all clusters
- [ ] **REL-06** [Required] Use cluster pools for faster recovery
- [ ] **REL-07** [Required] Implement workspace backup procedures
- [ ] **REL-08** [Required] Test disaster recovery procedures quarterly
- [ ] **REL-09** [Required] Use managed model serving for production ML
- [ ] **CP-07** [Required] Use standard access mode for most workloads
- [ ] **CP-08** [Required] Enable Photon for complex transformations
- [ ] **CP-09** [Required] Right-size clusters based on workload type
- [ ] **REL-10** [Required] Monitor and manage platform service limits
- [ ] **REL-11** [Required] Invest in capacity planning for production workloads

---

## ML/AI (ML, GS, GA, AG)

- [ ] **ML-01** [Critical] Feature tables in Unity Catalog with primary keys
- [ ] **ML-02** [Critical] `output_schema` required for UC models
- [ ] **ML-03** [Required] NaN/Inf handling at feature table creation
- [ ] **ML-04** [Required] Organize experiments by lifecycle stage
- [ ] **ML-05** [Critical] Label binarization for classifiers
- [ ] **ML-06** [Critical] Exclude label+key columns from features
- [ ] **GS-01** [Required] Evaluate managed services before custom development
- [ ] **GS-02** [Required] Create evaluation dataset before development
- [ ] **GS-03** [Required] Pass LLM judge thresholds before production
- [ ] **GS-04** [Required] Enable production monitoring for GenAI
- [ ] **GS-05** [Required] Version prompts in Unity Catalog
- [ ] **GS-06** [Critical] Implement responsible AI practices for all production agents
- [ ] **GS-07** [Required] AI lifecycle integrated with data lifecycle
- [ ] **GA-01** [Critical] Inherit from ResponsesAgent for agent development
- [ ] **GA-02** [Critical] OBO auth context detection
- [ ] **GA-03** [Critical] Declare all resources (Genie Spaces, Warehouses)
- [ ] **GA-04** [Critical] Enable MLflow Tracing for all agents
- [ ] **AG-01** [Critical] Enable payload logging on AI Gateway
- [ ] **AG-02** [Critical] Configure rate limiting on AI Gateway
- [ ] **AG-03** [Critical] Enable AI Guardrails for external-facing endpoints
- [ ] **AG-04** [Required] Usage tracking for cost on AI Gateway
- [ ] **AG-05** [Required] Configure fallbacks for LLM endpoints
- [ ] **ML-07** [Critical] Register all models in Unity Catalog with aliases
- [ ] **ML-08** [Critical] Champion/Challenger pattern for model promotion
- [ ] **ML-09** [Required] Log parameters, metrics, and artifacts for every run

---

## Cost Optimization (COST, CP)

- [ ] **COST-01** [Critical] Budget policies for all production workspaces
- [ ] **COST-02** [Required] Quarterly cost optimization reviews via system tables
- [ ] **COST-03** [Required] Balance always-on vs triggered streaming workloads
- [ ] **CP-01** [Critical] All classic clusters must use approved cluster policies
- [ ] **CP-02** [Critical] No unrestricted cluster creation
- [ ] **CP-03** [Required] Instance types limited by policy
- [ ] **CP-04** [Required] Auto-termination required on all clusters
- [ ] **CP-05** [Critical] Jobs compute for scheduled, All-Purpose for exploration
- [ ] **CP-06** [Required] Dependencies consistent between All-Purpose and Jobs

---

## Data Access Patterns (DI)

- [ ] **DI-01** [Critical] Default to ingestion for production analytics — data in Delta Lake
- [ ] **DI-02** [Critical] Federation reserved for ad-hoc access, migration staging only
- [ ] **DI-03** [Required] Delta Sharing for cross-organization data exchange
- [ ] **DI-04** [Required] Catalog federation preferred over query federation
- [ ] **DI-05** [Required] Transition federation to ingestion when patterns stabilize
- [ ] **DI-06** [Required] Data access pattern documented per external source
- [ ] **DI-07** [Critical] No high-volume joins or aggregations on federated sources

---

## Data Sharing (DS)

- [ ] **DS-01** [Critical] Unity Catalog for all shared assets
- [ ] **DS-02** [Required] Prefer Databricks-to-Databricks sharing
- [ ] **DS-03** [Critical] Never share PII without row filters or column masks
- [ ] **DS-04** [Required] Define retention and revocation policies
- [ ] **DS-05** [Required] Enable audit logging for all sharing
- [ ] **DS-06** [Required] Use Delta Sharing for cross-platform data access
- [ ] **DS-07** [Required] Monitor sharing usage via system tables

---

## Audit Summary

| Domain | Total Rules | PASS | FAIL | N/A |
|--------|-------------|------|------|-----|
| Table Creation & Storage | 27 | | | |
| Naming & Comments | 7 | | | |
| Tagging | 3 | | | |
| Data Pipelines | 14 | | | |
| Data Quality | 7 | | | |
| Data Modeling | 9 | | | |
| Semantic Layer | 17 | | | |
| Monitoring & Dashboards | 8 | | | |
| Streaming | 4 | | | |
| Asset Bundles & Deployment | 14 | | | |
| Governance | 28 | | | |
| Security | 13 | | | |
| Reliability & Compute | 14 | | | |
| ML/AI | 25 | | | |
| Cost Optimization | 9 | | | |
| Data Access Patterns | 7 | | | |
| Data Sharing | 7 | | | |
| **TOTAL** | **213** | | | |

> Note: Some rules appear in multiple audit sections (cross-cutting concerns). The unique formal rule count is 162+. BP rules have been retired in v5.4 (absorbed into existing DL/SC/GOV prefixes).

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Auditor | | | |
| Platform Lead | | | |
| Data Steward | | | |
| Security Lead | | | |

---

*Enterprise Golden Rules v5.4.1 — Full Audit Checklist*
*Generated: Feb 2026*
