# Architecture Review Checklist
## Pre-Flight Check for New Projects and Major Changes

### Document Information
- **Project Name:** ________________________________
- **Review Date:** ________________________________
- **Requestor:** ________________________________
- **Reviewer(s):** ________________________________
- **Review Type:** [ ] New Project  [ ] Major Change  [ ] Exception Request

---

## Pre-Review Requirements

Before scheduling an architecture review, ensure these artifacts are complete:

- [ ] Design document submitted (use standard template)
- [ ] Data flow diagram included
- [ ] ERD for dimensional model (if applicable)
- [ ] Sample data or schema definitions provided
- [ ] Estimated data volumes documented
- [ ] Target SLAs defined
- [ ] Cost estimates prepared

---

## Section 1: Data Architecture (DA Rules)

### DA-01: Unity Catalog

| Check | Status | Notes |
|-------|--------|-------|
| All tables use Unity Catalog (three-part naming) | [ ] Pass [ ] Fail [ ] N/A | |
| Catalog naming follows convention (`{env}_catalog`) | [ ] Pass [ ] Fail [ ] N/A | |
| Schema naming follows convention | [ ] Pass [ ] Fail [ ] N/A | |
| No Hive metastore dependencies | [ ] Pass [ ] Fail [ ] N/A | |

### DA-02: Medallion Architecture

| Check | Status | Notes |
|-------|--------|-------|
| Data flows through Bronze → Silver → Gold | [ ] Pass [ ] Fail [ ] N/A | |
| Bronze layer captures raw source data | [ ] Pass [ ] Fail [ ] N/A | |
| Silver layer applies quality rules | [ ] Pass [ ] Fail [ ] N/A | |
| Gold layer contains business-ready aggregates | [ ] Pass [ ] Fail [ ] N/A | |
| No direct Bronze → Gold processing | [ ] Pass [ ] Fail [ ] N/A | |

### DA-03: Delta Lake Configuration

| Check | Status | Notes |
|-------|--------|-------|
| All tables use Delta Lake format | [ ] Pass [ ] Fail [ ] N/A | |
| Change Data Feed enabled | [ ] Pass [ ] Fail [ ] N/A | |
| Row tracking enabled (Silver/Gold) | [ ] Pass [ ] Fail [ ] N/A | |
| Deletion vectors enabled | [ ] Pass [ ] Fail [ ] N/A | |
| Auto-optimize configured | [ ] Pass [ ] Fail [ ] N/A | |

### DA-04: Clustering

| Check | Status | Notes |
|-------|--------|-------|
| Tables use `CLUSTER BY AUTO` | [ ] Pass [ ] Fail [ ] N/A | |
| No manual clustering columns specified | [ ] Pass [ ] Fail [ ] N/A | |

### DA-02 / DA-04: Dimensional Modeling

| Check | Status | Notes |
|-------|--------|-------|
| Dimensional design process followed (process → grain → dimensions → facts) | [ ] Pass [ ] Fail [ ] N/A | |
| Fact table grain explicitly documented — no mixed grains | [ ] Pass [ ] Fail [ ] N/A | |
| Fact table type identified (transaction / periodic snapshot / accumulating snapshot) | [ ] Pass [ ] Fail [ ] N/A | |
| Fact additivity classified for every measure (additive / semi-additive / non-additive) | [ ] Pass [ ] Fail [ ] N/A | |
| No text attributes stored in fact tables (use dimensions or degenerate dimensions) | [ ] Pass [ ] Fail [ ] N/A | |
| Dimension tables have surrogate keys (`_key` suffix) — not operational keys | [ ] Pass [ ] Fail [ ] N/A | |
| Business keys have UNIQUE constraints | [ ] Pass [ ] Fail [ ] N/A | |
| Fact tables have foreign keys to dimensions | [ ] Pass [ ] Fail [ ] N/A | |
| SCD strategy defined per attribute (Type 0/1/2/3/6) | [ ] Pass [ ] Fail [ ] N/A | |
| Conformed dimensions identified and reused (DM-10) | [ ] Pass [ ] Fail [ ] N/A | |
| Enterprise Bus Matrix updated with new fact/dimension (DM-11) | [ ] Pass [ ] Fail [ ] N/A | |
| Dimensions loaded before facts in pipeline order | [ ] Pass [ ] Fail [ ] N/A | |
| Hierarchies flattened into dimensions (not normalized into separate tables) | [ ] Pass [ ] Fail [ ] N/A | |

### DL-05: Predictive Optimization (Best Practice)

| Check | Status | Notes |
|-------|--------|-------|
| Predictive Optimization enabled at schema level | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 2: Security & Access (SEC Rules)

### SEC-01: Credential Management

| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded credentials in code | [ ] Pass [ ] Fail [ ] N/A | |
| No credentials in configuration files | [ ] Pass [ ] Fail [ ] N/A | |
| Secrets stored in Databricks secret scopes | [ ] Pass [ ] Fail [ ] N/A | |
| Secret scope ACLs configured appropriately | [ ] Pass [ ] Fail [ ] N/A | |

### SEC-02: Access Control

| Check | Status | Notes |
|-------|--------|-------|
| Access grants follow least privilege | [ ] Pass [ ] Fail [ ] N/A | |
| No `ALL PRIVILEGES` grants except Platform Admin | [ ] Pass [ ] Fail [ ] N/A | |
| Access matrix documented | [ ] Pass [ ] Fail [ ] N/A | |
| Service principals used for automation | [ ] Pass [ ] Fail [ ] N/A | |

### SEC-03: Data Classification

| Check | Status | Notes |
|-------|--------|-------|
| All tables have `data_classification` property | [ ] Pass [ ] Fail [ ] N/A | |
| PII-containing tables tagged `contains_pii=true` | [ ] Pass [ ] Fail [ ] N/A | |
| PII columns identified in tags | [ ] Pass [ ] Fail [ ] N/A | |
| Appropriate access controls for classified data | [ ] Pass [ ] Fail [ ] N/A | |

### SEC-04: Authentication (for ML/AI projects)

| Check | Status | Notes |
|-------|--------|-------|
| OBO authentication implemented with context detection | [ ] Pass [ ] Fail [ ] N/A | |
| Resources declared in AuthPolicy | [ ] Pass [ ] Fail [ ] N/A | |
| API scopes appropriately limited | [ ] Pass [ ] Fail [ ] N/A | |

### SEC-05: Network Security (Production)

| Check | Status | Notes |
|-------|--------|-------|
| VNet injection configured | [ ] Pass [ ] Fail [ ] N/A | |
| Private Link enabled for control plane | [ ] Pass [ ] Fail [ ] N/A | |
| IP access lists implemented | [ ] Pass [ ] Fail [ ] N/A | |
| Secure cluster connectivity (no public IPs) | [ ] Pass [ ] Fail [ ] N/A | |
| Diagnostic logging to Azure Monitor | [ ] Pass [ ] Fail [ ] N/A | |
| Network egress controls configured | [ ] Pass [ ] Fail [ ] N/A | |
| Customer-managed keys (CMK) for encryption | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 3: Data Quality (DQ Rules)

### DQ-01: DLT Expectations

| Check | Status | Notes |
|-------|--------|-------|
| Silver tables have DLT expectations | [ ] Pass [ ] Fail [ ] N/A | |
| Critical rules use `expect_all_or_drop` | [ ] Pass [ ] Fail [ ] N/A | |
| Warning rules use `expect_all` | [ ] Pass [ ] Fail [ ] N/A | |
| Quarantine pattern implemented for failed records | [ ] Pass [ ] Fail [ ] N/A | |

### DQ-02: Config-Driven Rules

| Check | Status | Notes |
|-------|--------|-------|
| Quality rules stored in Delta table | [ ] Pass [ ] Fail [ ] N/A | |
| Rules loaded dynamically at runtime | [ ] Pass [ ] Fail [ ] N/A | |
| Rule versioning and audit trail in place | [ ] Pass [ ] Fail [ ] N/A | |

### DQ-03: Schema Validation

| Check | Status | Notes |
|-------|--------|-------|
| Pre-merge schema validation implemented | [ ] Pass [ ] Fail [ ] N/A | |
| Column names extracted from YAML (not hardcoded) | [ ] Pass [ ] Fail [ ] N/A | |
| Type mismatches detected before merge | [ ] Pass [ ] Fail [ ] N/A | |

### DQ-04: Fact Table Validation

| Check | Status | Notes |
|-------|--------|-------|
| Fact grain matches DDL PRIMARY KEY | [ ] Pass [ ] Fail [ ] N/A | |
| Duplicate detection at grain level | [ ] Pass [ ] Fail [ ] N/A | |
| Aggregation logic documented and validated | [ ] Pass [ ] Fail [ ] N/A | |

### DQ-05: Documentation

| Check | Status | Notes |
|-------|--------|-------|
| All tables have comprehensive COMMENT | [ ] Pass [ ] Fail [ ] N/A | |
| Comments include Business + Technical sections | [ ] Pass [ ] Fail [ ] N/A | |
| All columns have descriptive comments | [ ] Pass [ ] Fail [ ] N/A | |
| Documentation suitable for Genie/LLM consumption | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 4: Performance (PERF Rules)

### PERF-01: Compute Configuration

| Check | Status | Notes |
|-------|--------|-------|
| Jobs use serverless compute | [ ] Pass [ ] Fail [ ] N/A | |
| Justification provided if classic compute required | [ ] Pass [ ] Fail [ ] N/A | |
| Environment version is "4" (serverless) | [ ] Pass [ ] Fail [ ] N/A | |

### PERF-02: SQL Warehouse

| Check | Status | Notes |
|-------|--------|-------|
| SQL Warehouse uses serverless | [ ] Pass [ ] Fail [ ] N/A | |
| Auto-stop configured (≤10 min dev, ≤30 min prod) | [ ] Pass [ ] Fail [ ] N/A | |
| Appropriate sizing for workload | [ ] Pass [ ] Fail [ ] N/A | |

### PERF-03: DLT Configuration

| Check | Status | Notes |
|-------|--------|-------|
| Photon enabled | [ ] Pass [ ] Fail [ ] N/A | |
| Serverless enabled | [ ] Pass [ ] Fail [ ] N/A | |
| ADVANCED edition for expectations | [ ] Pass [ ] Fail [ ] N/A | |

### PERF-04: ML Data Preparation

| Check | Status | Notes |
|-------|--------|-------|
| Feature tables have NaN/Inf values cleaned | [ ] Pass [ ] Fail [ ] N/A | |
| Cleaning happens at table creation, not training | [ ] Pass [ ] Fail [ ] N/A | |
| All numeric columns validated | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 5: Development Standards (DEV Rules)

### DEV-01: Asset Bundles

| Check | Status | Notes |
|-------|--------|-------|
| All resources defined in Asset Bundle YAML | [ ] Pass [ ] Fail [ ] N/A | |
| No manual UI-created resources | [ ] Pass [ ] Fail [ ] N/A | |
| `databricks bundle validate` passes | [ ] Pass [ ] Fail [ ] N/A | |
| Proper target configuration (dev/prod) | [ ] Pass [ ] Fail [ ] N/A | |

### DEV-02: Parameter Handling

| Check | Status | Notes |
|-------|--------|-------|
| Notebooks use `dbutils.widgets.get()` | [ ] Pass [ ] Fail [ ] N/A | |
| No argparse in notebook code | [ ] Pass [ ] Fail [ ] N/A | |
| Parameters logged for debugging | [ ] Pass [ ] Fail [ ] N/A | |

### DEV-03: Code Organization

| Check | Status | Notes |
|-------|--------|-------|
| Shared modules are pure Python (no notebook headers) | [ ] Pass [ ] Fail [ ] N/A | |
| sys.path setup for Asset Bundle imports | [ ] Pass [ ] Fail [ ] N/A | |
| Imports work without errors | [ ] Pass [ ] Fail [ ] N/A | |

### DEV-04: Job Architecture

| Check | Status | Notes |
|-------|--------|-------|
| Jobs follow atomic → composite → orchestrator pattern | [ ] Pass [ ] Fail [ ] N/A | |
| Each notebook in exactly one atomic job | [ ] Pass [ ] Fail [ ] N/A | |
| Orchestrators use `run_job_task` (not `notebook_task`) | [ ] Pass [ ] Fail [ ] N/A | |
| `job_level` tag on all jobs | [ ] Pass [ ] Fail [ ] N/A | |

### DEV-05: Schema Management

| Check | Status | Notes |
|-------|--------|-------|
| Schemas extracted from YAML (not generated) | [ ] Pass [ ] Fail [ ] N/A | |
| No hardcoded table/column names | [ ] Pass [ ] Fail [ ] N/A | |
| YAML files are source of truth | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 6: Operations (OPS Rules)

### OPS-01: Lakehouse Monitoring

| Check | Status | Notes |
|-------|--------|-------|
| Critical Gold tables have monitors | [ ] Pass [ ] Fail [ ] N/A | |
| Custom business KPIs defined | [ ] Pass [ ] Fail [ ] N/A | |
| `input_columns=[":table"]` for table-level metrics | [ ] Pass [ ] Fail [ ] N/A | |
| Monitor output tables documented | [ ] Pass [ ] Fail [ ] N/A | |

### OPS-02: Alerting

| Check | Status | Notes |
|-------|--------|-------|
| SQL Alerts for critical thresholds | [ ] Pass [ ] Fail [ ] N/A | |
| Alert rules in Delta table (config-driven) | [ ] Pass [ ] Fail [ ] N/A | |
| Notification destinations configured | [ ] Pass [ ] Fail [ ] N/A | |
| Alert testing documented | [ ] Pass [ ] Fail [ ] N/A | |

### OPS-03: Tracing (for ML/AI)

| Check | Status | Notes |
|-------|--------|-------|
| MLflow tracing enabled | [ ] Pass [ ] Fail [ ] N/A | |
| Production scorers registered | [ ] Pass [ ] Fail [ ] N/A | |
| Trace archival configured | [ ] Pass [ ] Fail [ ] N/A | |

### OPS-04: Deployment Automation

| Check | Status | Notes |
|-------|--------|-------|
| Deployment triggered automatically | [ ] Pass [ ] Fail [ ] N/A | |
| Quality thresholds defined | [ ] Pass [ ] Fail [ ] N/A | |
| Rollback procedure documented | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 7: Semantic Layer (SL Rules)

### MV-01: Metric Views

| Check | Status | Notes |
|-------|--------|-------|
| Metric Views use v1.1 YAML (no `name` field) | [ ] Pass [ ] Fail [ ] N/A | |
| No transitive joins (only direct source → dim) | [ ] Pass [ ] Fail [ ] N/A | |
| All column references verified against Gold YAML | [ ] Pass [ ] Fail [ ] N/A | |
| v3.0 comment format (PURPOSE, BEST FOR, NOT FOR) | [ ] Pass [ ] Fail [ ] N/A | |

### TF: Table-Valued Functions

| Check | Status | Notes |
|-------|--------|-------|
| TVFs use STRING for date parameters (not DATE) | [ ] Pass [ ] Fail [ ] N/A | |
| Schema validation before SQL deployment | [ ] Pass [ ] Fail [ ] N/A | |
| v3.0 comment format with "DO NOT wrap in TABLE()" | [ ] Pass [ ] Fail [ ] N/A | |
| Parameter validation included in function body | [ ] Pass [ ] Fail [ ] N/A | |

### GN: Genie Spaces

| Check | Status | Notes |
|-------|--------|-------|
| Tables and Metric Views properly registered | [ ] Pass [ ] Fail [ ] N/A | |
| Sample questions aligned with asset capabilities | [ ] Pass [ ] Fail [ ] N/A | |
| Instructions provide routing guidance | [ ] Pass [ ] Fail [ ] N/A | |
| Benchmark testing completed (accuracy/repeatability) | [ ] Pass [ ] Fail [ ] N/A | |

---

## Section 8: ML/AI Extended (ML Rules)

### ML-01: MLflow Model Patterns

| Check | Status | Notes |
|-------|--------|-------|
| Experiment paths use `/Shared/` convention | [ ] Pass [ ] Fail [ ] N/A | |
| `output_schema` defined for Unity Catalog models | [ ] Pass [ ] Fail [ ] N/A | |
| NaN/Inf cleaned at feature table creation | [ ] Pass [ ] Fail [ ] N/A | |
| Label binarization for classification models | [ ] Pass [ ] Fail [ ] N/A | |

### ML-02: GenAI Agent Patterns

| Check | Status | Notes |
|-------|--------|-------|
| OBO context detection implemented | [ ] Pass [ ] Fail [ ] N/A | |
| Genie Spaces declared as `DatabricksGenieSpace` resources | [ ] Pass [ ] Fail [ ] N/A | |
| SQL Warehouse declared as `DatabricksSQLWarehouse` resource | [ ] Pass [ ] Fail [ ] N/A | |
| MLflow tracing enabled | [ ] Pass [ ] Fail [ ] N/A | |

### ML-03: AI Gateway

| Check | Status | Notes |
|-------|--------|-------|
| Payload logging enabled | [ ] Pass [ ] Fail [ ] N/A | |
| Rate limiting configured | [ ] Pass [ ] Fail [ ] N/A | |
| AI Guardrails enabled (external-facing endpoints) | [ ] Pass [ ] Fail [ ] N/A | |
| Usage tracking active for cost management | [ ] Pass [ ] Fail [ ] N/A | |
| Fallbacks configured for critical LLM endpoints | [ ] Pass [ ] Fail [ ] N/A | |

---

## Review Summary

### Overall Assessment

| Category | Pass | Fail | N/A | Compliance % |
|----------|------|------|-----|--------------|
| Data Architecture (DA) | | | | |
| Security (SEC) | | | | |
| Data Quality (DQ) | | | | |
| Performance (PERF) | | | | |
| Development (DEV) | | | | |
| Operations (OPS) | | | | |
| Semantic Layer (SL) | | | | |
| ML/AI Extended (ML) | | | | |
| **TOTAL** | | | | |

### Decision

- [ ] **APPROVED** - Proceed to development
- [ ] **APPROVED WITH CONDITIONS** - See required changes below
- [ ] **NOT APPROVED** - Major revisions required

### Required Changes (if applicable)

| Item | Rule | Required Change | Owner | Due Date |
|------|------|-----------------|-------|----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### Recommendations (optional improvements)

1. 
2. 
3. 

---

## Signatures

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Reviewer | | | |
| Requestor | | | |
| Data Steward (if required) | | | |
| Security (if required) | | | |

---

## Follow-Up

- [ ] Design document updated with review feedback
- [ ] Required changes implemented
- [ ] Re-review scheduled (if needed)
- [ ] Architecture approval recorded in tracking system

---

*Checklist Version 2.0 - Based on Enterprise Golden Rules (February 2026)*
*Added: Network Security (SEC-05), Semantic Layer (MV-01 to MV-05, TF, GN), ML/AI Extended (ML-01 to ML-03)*
