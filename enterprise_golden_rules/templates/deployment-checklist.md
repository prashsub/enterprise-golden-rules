# Pre-Deployment Checklist

## Project Information

| Field | Value |
|-------|-------|
| **Project Name** | |
| **PR/Branch** | |
| **Developer** | |
| **Reviewer** | |
| **Date** | |

---

## Section 1: Schema Validation (CRITICAL)

### Gold Layer Tables

- [ ] All table schemas extracted from YAML (not hardcoded)
- [ ] All column names verified against `gold_layer_design/yaml/{domain}/`
- [ ] Column types match YAML definitions
- [ ] Primary keys defined in YAML
- [ ] Foreign keys reference existing tables

**YAML Verification Command:**
```bash
# List all Gold YAML schemas
ls gold_layer_design/yaml/
```

### Silver Layer Tables

- [ ] DLT tables use `cluster_by_auto=True`
- [ ] All tables have `table_properties` including layer tag
- [ ] Source table references are correct (Bronze tables exist)

### Semantic Layer

- [ ] Metric View YAML has no `name` field
- [ ] TVF parameters use STRING for dates (not DATE type)
- [ ] All column references verified against Gold YAML
- [ ] Schema mapping document created (SCHEMA_MAPPING.md)

---

## Section 2: Asset Bundle Configuration

### Job Configuration

- [ ] Job uses serverless environment
  ```yaml
  environments:
    - environment_key: "default"
      spec:
        environment_version: "4"
  ```

- [ ] Every task has `environment_key: default`
- [ ] Job name includes `[${bundle.target}]` prefix
- [ ] Parameters use `base_parameters` (not `parameters` with CLI flags)

### Hierarchical Architecture

- [ ] Notebooks appear in exactly ONE atomic job
- [ ] Composite jobs use `run_job_task` only
- [ ] Orchestrators use `run_job_task` only
- [ ] Job references use `${resources.jobs.<name>.id}`

### Path Resolution

- [ ] Notebook paths correct for YAML file location
  - From `resources/*.yml` → `../src/`
  - From `resources/<layer>/*.yml` → `../../src/`
- [ ] DLT libraries within `root_path`
- [ ] Include paths in `databricks.yml` cover all subdirectories

### Variable References

- [ ] All variables use `${var.name}` format
- [ ] No hardcoded catalog/schema values

---

## Section 3: Python Code Quality

### Parameter Handling

- [ ] Notebooks use `dbutils.widgets.get()` (NOT argparse)
  ```python
  # ✅ CORRECT
  catalog = dbutils.widgets.get("catalog")
  
  # ❌ WRONG
  import argparse
  parser.parse_args()
  ```

### Module Imports

- [ ] Shared modules are pure Python (no `# Databricks notebook source`)
- [ ] `sys.path` setup block at top of notebooks that import modules
- [ ] No notebook imports in serverless compute

### MERGE Operations

- [ ] Deduplication before MERGE
  ```python
  silver_df = silver_raw.orderBy(col("processed_timestamp").desc()).dropDuplicates([business_key])
  ```
- [ ] Deduplication key matches MERGE key

### Code Style

- [ ] All functions have docstrings
- [ ] Error handling with try/except
- [ ] Print statements for monitoring/debugging
- [ ] No hardcoded values (use parameters)

---

## Section 4: Data Quality

### DLT Expectations

- [ ] All Silver tables have expectations
- [ ] Critical rules use `expect_or_drop`
- [ ] Quarantine tables for failed records

### Gold Layer Quality

- [ ] PK constraints applied (after all tables created)
- [ ] FK constraints reference correct tables
- [ ] Table comments include business context

### Semantic Layer Quality

- [ ] TVF comments use v3.0 format (PURPOSE, BEST FOR, etc.)
- [ ] "DO NOT wrap in TABLE()" in TVF NOTE section
- [ ] Metric View comments include BEST FOR / NOT FOR

### Semantic Layer Validation

- [ ] Metric Views use v1.1 YAML (no `name` field)
- [ ] TVFs use STRING for date parameters (not DATE type)
- [ ] No transitive joins in Metric Views (only source → dim)
- [ ] All column references verified against Gold YAML
- [ ] Genie Space benchmark testing completed (if applicable)

---

## Section 5: Documentation

### Table Documentation

- [ ] All tables have COMMENT
- [ ] All columns have COMMENT
- [ ] Comments are LLM-friendly (business + technical)

### Code Documentation

- [ ] README updated (if needed)
- [ ] CHANGELOG updated
- [ ] Architecture diagrams updated (if applicable)

---

## Section 6: Pre-Deployment Validation

### Run Validation Script

```bash
# Run automated validation
./scripts/validate_bundle.sh
```

- [ ] No duplicate YAML files
- [ ] No `python_task` usage
- [ ] No CLI-style parameters
- [ ] No missing `var.` prefix
- [ ] Bundle validation passes

### Manual Verification

```bash
# Authenticate
databricks auth login --host https://your-workspace.databricks.com

# Validate bundle
databricks bundle validate

# Deploy to dev (dry run)
databricks bundle deploy -t dev
```

- [ ] Authentication successful
- [ ] Bundle validation passes
- [ ] Deployment to dev succeeds

---

## Section 7: Testing

### Local Testing

- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)

### Dev Environment Testing

- [ ] Job runs successfully
- [ ] Output data verified
- [ ] Logs reviewed for errors/warnings

### Query Testing

- [ ] TVFs callable via `SELECT * FROM function(...)`
- [ ] Metric Views return expected data
- [ ] Dashboard queries execute successfully

---

## Section 8: ML/AI Deployment (if applicable)

### MLflow Models

- [ ] Experiment paths use `/Shared/` convention
- [ ] `output_schema` defined for Unity Catalog models
- [ ] NaN/Inf values cleaned at feature table creation
- [ ] Label binarization correct for classification models
- [ ] Single-class detection and graceful handling

### GenAI Agents

- [ ] OBO context detection implemented (environment variable check)
- [ ] Genie Spaces declared as `DatabricksGenieSpace` resources
- [ ] SQL Warehouse declared as `DatabricksSQLWarehouse` resource
- [ ] MLflow tracing enabled
- [ ] Agent evaluation passes without permission errors

### AI Gateway

- [ ] Payload logging enabled for endpoints
- [ ] Rate limiting configured (see standard limits)
- [ ] AI Guardrails enabled for external-facing endpoints
- [ ] Usage tracking active for cost management
- [ ] Fallbacks configured for critical LLM endpoints

---

## Section 9: Network Security (Production)

### Pre-Deployment Network Checks

- [ ] VNet injection configured (required for production)
- [ ] Private Link enabled for control plane access
- [ ] IP access lists implemented (corporate VPN + known IPs)
- [ ] Secure cluster connectivity enabled (no public IPs)
- [ ] Network egress controls configured

### Encryption & Monitoring

- [ ] Customer-managed keys (CMK) configured
- [ ] Key rotation policy in place
- [ ] Diagnostic logging to Azure Monitor enabled
- [ ] SIEM integration configured (if required)

---

## Section 10: Final Approval

### Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| Code Reviewer | | | |
| Data Steward | | | |

### Deployment Notes

<!-- Any special instructions for deployment -->

---

## Quick Reference: Common Blockers

| Issue | Check | Fix |
|-------|-------|-----|
| `Column not found` | Schema validation | Verify against YAML |
| `argparse error` | Parameter handling | Use `dbutils.widgets.get()` |
| `python_task invalid` | Job config | Use `notebook_task` |
| `Variable not found` | Variable reference | Use `${var.name}` |
| `Duplicate resource` | YAML files | Remove duplicates |
| `MERGE duplicate error` | Deduplication | Add `dropDuplicates()` |
| `FK constraint failed` | Constraint order | Apply PKs first |
| `Unrecognized field "name"` | Metric View YAML | Remove `name` field (v1.1) |
| `Transitive join error` | Metric View joins | Use direct joins only |
| `DATE parameter error` | TVF parameters | Use STRING for dates |
| `Permission denied (OBO)` | Agent auth | Check context detection |
| `Genie resource not found` | Agent resources | Declare in AuthPolicy |

---

## Related Documents

- [Asset Bundle Standards](../platform-architecture/19-asset-bundle-standards.md)
- [Gold Layer Standards](../solution-architecture/data-pipelines/27-gold-layer-patterns.md)
- [Semantic Layer Overview](../solution-architecture/semantic-layer/33-semantic-layer-overview.md)
- [GenAI Agent Patterns](../solution-architecture/ml-ai/51-genai-agent-patterns.md)
- [AI Gateway Patterns](../solution-architecture/ml-ai/53-ai-gateway-patterns.md)
- [Network Security](../platform-architecture/18-network-security.md)

---

*Pre-Deployment Checklist Version 2.0 - Based on Enterprise Golden Rules (February 2026)*
*Added: Semantic Layer Validation, ML/AI Deployment, Network Security sections*
