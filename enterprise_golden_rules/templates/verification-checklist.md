# Verification Checklist

## Golden Rules Compliance Verification

**Version:** 2.0  
**Last Updated:** February 2026  
**Usage:** Complete before each deployment and during quarterly audits

---

## Pre-Deployment Checklist

### Phase 1: Design Review

#### Rule 1: Unity Catalog Everywhere

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 1.1 | All tables created in Unity Catalog (not HMS) | ☐ |
| 1.2 | Catalog naming follows convention (`{company}_{env}`) | ☐ |
| 1.3 | Schema naming follows convention (bronze/silver/gold) | ☐ |
| 1.4 | Table naming follows convention (`{layer}_{entity}`) | ☐ |
| 1.5 | External locations (if any) registered in UC | ☐ |
| 1.6 | Service principal configured for automation | ☐ |

**Sign-off:** _________________ Date: _________

---

#### Rule 2: Medallion Architecture

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 2.1 | Bronze layer exists and is append-only | ☐ |
| 2.2 | Silver layer uses DLT streaming | ☐ |
| 2.3 | Gold layer follows star schema | ☐ |
| 2.4 | Data flows Bronze → Silver → Gold | ☐ |
| 2.5 | No direct Bronze → Gold transformations | ☐ |
| 2.6 | Layer tags applied to all tables | ☐ |

**Sign-off:** _________________ Date: _________

---

#### Rule 3: Data Quality by Design

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 3.1 | DLT expectations defined (5+ per table) | ☐ |
| 3.2 | Critical fields use `expect_or_drop` | ☐ |
| 3.3 | Business rules use `expect` (warning) | ☐ |
| 3.4 | Quarantine tables capture failures | ☐ |
| 3.5 | Quarantine includes failure reason | ☐ |
| 3.6 | Quality metrics monitored | ☐ |

**Sign-off:** _________________ Date: _________

---

### Phase 2: Table Configuration

#### Rule 4: Delta Lake Everywhere

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 4.1 | All tables use `USING DELTA` | ☐ |
| 4.2 | `CLUSTER BY AUTO` on all tables | ☐ |
| 4.3 | `delta.enableChangeDataFeed = true` | ☐ |
| 4.4 | `delta.autoOptimize.optimizeWrite = true` | ☐ |
| 4.5 | `delta.autoOptimize.autoCompact = true` | ☐ |
| 4.6 | Predictive optimization enabled at schema level | ☐ |

**Verification Query:**
```sql
-- Run for each table
SHOW TBLPROPERTIES {catalog}.{schema}.{table};
-- Verify: delta.enableChangeDataFeed = true
```

**Sign-off:** _________________ Date: _________

---

#### Rule 5: Dimensional Modeling with Constraints

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 5.1 | Surrogate keys defined for dimensions | ☐ |
| 5.2 | Business keys preserved in dimensions | ☐ |
| 5.3 | PRIMARY KEY on surrogate key (NOT ENFORCED) | ☐ |
| 5.4 | FOREIGN KEY references PK (NOT ENFORCED) | ☐ |
| 5.5 | SCD Type assigned (1 or 2) | ☐ |
| 5.6 | `is_current` column for SCD Type 2 | ☐ |
| 5.7 | Fact table has composite PK | ☐ |
| 5.8 | Fact table has FKs to all dimensions | ☐ |

**Verification Query:**
```sql
-- Check constraints
SELECT * FROM information_schema.table_constraints
WHERE table_schema = '{schema}';
```

**Sign-off:** _________________ Date: _________

---

### Phase 3: Job Configuration

#### Rule 6: Serverless-First Compute

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 6.1 | Jobs use serverless environment | ☐ |
| 6.2 | `environment_version: "4"` in YAML | ☐ |
| 6.3 | `environment_key` in every task | ☐ |
| 6.4 | DLT pipelines have `serverless: true` | ☐ |
| 6.5 | DLT pipelines have `photon: true` | ☐ |
| 6.6 | No hardcoded cluster configurations | ☐ |

**Verification:**
```yaml
# Check in resources/*.yml
environments:
  - environment_key: "default"
    spec:
      environment_version: "4"
```

**Sign-off:** _________________ Date: _________

---

#### Rule 7: Infrastructure as Code

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 7.1 | `databricks.yml` exists and is valid | ☐ |
| 7.2 | Schemas defined in `resources/schemas.yml` | ☐ |
| 7.3 | All jobs defined in Asset Bundle | ☐ |
| 7.4 | All pipelines defined in Asset Bundle | ☐ |
| 7.5 | Variables defined for environment-specific values | ☐ |
| 7.6 | `databricks bundle validate` passes | ☐ |
| 7.7 | No manual UI-created resources | ☐ |

**Verification:**
```bash
databricks bundle validate -t dev
# Should complete without errors
```

**Sign-off:** _________________ Date: _________

---

### Phase 4: Documentation

#### Rule 8: LLM-Friendly Documentation

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 8.1 | All tables have COMMENT (50+ chars) | ☐ |
| 8.2 | Table comments explain business purpose | ☐ |
| 8.3 | All columns have COMMENT | ☐ |
| 8.4 | Column comments explain business meaning | ☐ |
| 8.5 | TVFs use standardized comment format | ☐ |
| 8.6 | Metric Views have comprehensive comments | ☐ |
| 8.7 | PII columns are clearly marked | ☐ |

**Verification Query:**
```sql
-- Check table comments
SELECT 
    table_name,
    comment,
    LENGTH(comment) as comment_length
FROM information_schema.tables
WHERE table_schema = '{schema}'
AND (comment IS NULL OR LENGTH(comment) < 50);
-- Should return 0 rows
```

**Sign-off:** _________________ Date: _________

---

### Phase 5: Development Patterns

#### Rule 9: Schema-First Development

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 9.1 | YAML schema exists for all Gold tables | ☐ |
| 9.2 | YAML defines all columns | ☐ |
| 9.3 | YAML defines PK/FK relationships | ☐ |
| 9.4 | Code extracts schema from YAML | ☐ |
| 9.5 | No hardcoded column names in code | ☐ |
| 9.6 | Schema validation runs before deployment | ☐ |

**Verification:**
```bash
# Check YAML files exist
ls gold_layer_design/yaml/{domain}/*.yaml
```

**Sign-off:** _________________ Date: _________

---

#### Rule 10: Deduplication Before MERGE

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 10.1 | `.orderBy()` before `.dropDuplicates()` | ☐ |
| 10.2 | Order by timestamp descending | ☐ |
| 10.3 | Deduplicate key matches MERGE key | ☐ |
| 10.4 | Deduplication metrics logged | ☐ |
| 10.5 | MERGE uses correct business key | ☐ |
| 10.6 | SCD Type 2 MERGE includes `is_current = true` | ☐ |

**Verification Pattern:**
```python
# Correct pattern in code
silver_df = (
    spark.table(silver_table)
    .orderBy(col("processed_timestamp").desc())  # ✓ Order first
    .dropDuplicates([business_key])  # ✓ Then dedupe
)
```

**Sign-off:** _________________ Date: _________

---

#### Rule 11: Semantic Layer Standards

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 11.1 | Metric Views use v1.1 YAML format | ☐ |
| 11.2 | No `name` field in Metric View YAML | ☐ |
| 11.3 | No transitive joins in Metric Views | ☐ |
| 11.4 | TVFs use STRING for date parameters | ☐ |
| 11.5 | Schema validation before SQL deployment | ☐ |
| 11.6 | v3.0 comment format (PURPOSE, BEST FOR) | ☐ |
| 11.7 | Column references verified against Gold YAML | ☐ |
| 11.8 | Genie Space benchmark testing completed | ☐ |

**Verification:**
```bash
# Check Metric View YAML structure
grep -r "name:" src/semantic/metric_views/*.yaml
# Should NOT find 'name' field in view definitions
```

**Sign-off:** _________________ Date: _________

---

#### Rule 12: ML/AI Standards

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 12.1 | Experiment paths use `/Shared/` convention | ☐ |
| 12.2 | `output_schema` defined for UC models | ☐ |
| 12.3 | NaN/Inf cleaned at feature table creation | ☐ |
| 12.4 | OBO context detection implemented | ☐ |
| 12.5 | Genie Spaces in AuthPolicy resources | ☐ |
| 12.6 | SQL Warehouse in AuthPolicy resources | ☐ |
| 12.7 | MLflow tracing enabled | ☐ |

**Verification (Agent Authentication):**
```python
# Check for environment variable detection
grep -r "IS_IN_DB_MODEL_SERVING_ENV" src/agents/
# Should find context detection code
```

**Sign-off:** _________________ Date: _________

---

#### Rule 13: AI Gateway Configuration

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 13.1 | Payload logging enabled for endpoints | ☐ |
| 13.2 | Rate limiting configured | ☐ |
| 13.3 | AI Guardrails enabled (external-facing) | ☐ |
| 13.4 | Usage tracking active | ☐ |
| 13.5 | Fallbacks for critical LLM endpoints | ☐ |

**Verification:**
```python
# Check endpoint configuration
databricks serving-endpoints get my-endpoint --output JSON | jq '.config'
```

**Sign-off:** _________________ Date: _________

---

#### Rule 14: Network Security (Production)

| Check | Requirement | Pass/Fail |
|-------|-------------|-----------|
| 14.1 | VNet injection configured | ☐ |
| 14.2 | Private Link enabled | ☐ |
| 14.3 | IP access lists implemented | ☐ |
| 14.4 | CMK encryption configured | ☐ |
| 14.5 | Diagnostic logging enabled | ☐ |
| 14.6 | Network egress controls in place | ☐ |
| 14.7 | Secure cluster connectivity (no public IPs) | ☐ |

**Verification:**
```bash
# Check workspace network configuration
az databricks workspace show --name myworkspace -g mygroup \
  --query "{vnet:parameters.customVirtualNetworkId.value, privateLink:privateEndpointConnections}"
```

**Sign-off:** _________________ Date: _________

---

## Production Deployment Checklist

### Pre-Deployment

| # | Check | Required By | Status |
|---|-------|-------------|--------|
| 1 | All design review checklists passed | Platform Lead | ☐ |
| 2 | Code review completed and approved | Peer + Lead | ☐ |
| 3 | `databricks bundle validate` passes | Automated | ☐ |
| 4 | Unit tests pass (if applicable) | Data Engineer | ☐ |
| 5 | Integration tests pass in dev | Data Engineer | ☐ |
| 6 | Security review completed (if PII) | Security Team | ☐ |
| 7 | Data Steward approval | Data Steward | ☐ |

### Deployment

| # | Step | Owner | Status |
|---|------|-------|--------|
| 1 | Deploy to production | Platform Admin | ☐ |
| 2 | Verify tables created | Data Engineer | ☐ |
| 3 | Verify constraints applied | Data Engineer | ☐ |
| 4 | Run initial pipeline | Data Engineer | ☐ |
| 5 | Verify data quality | Data Steward | ☐ |
| 6 | Enable monitoring | Platform Admin | ☐ |
| 7 | Enable schedules | Platform Admin | ☐ |

### Post-Deployment

| # | Check | Owner | Status |
|---|-------|-------|--------|
| 1 | First scheduled run successful | Data Engineer | ☐ |
| 2 | Data freshness SLA met | Data Steward | ☐ |
| 3 | No quality alerts triggered | Data Steward | ☐ |
| 4 | Stakeholders notified | Data Engineer | ☐ |
| 5 | Runbook documented | Data Engineer | ☐ |

---

## Quarterly Audit Checklist

### Scope Definition

| Domain | Tables | Last Audit | Auditor |
|--------|--------|------------|---------|
| [Domain 1] | [Count] | [Date] | [Name] |
| [Domain 2] | [Count] | [Date] | [Name] |

### Audit Results Summary

| Rule | WAF Pillar | Total Items | Compliant | Non-Compliant | % |
|------|------------|-------------|-----------|---------------|---|
| Rule 1: Unity Catalog | [Governance](https://docs.databricks.com/en/lakehouse-architecture/data-governance/best-practices#manage-metadata-for-all-data-and-ai-assets-in-one-place) | | | | |
| Rule 2: Medallion | [OpEx](https://docs.databricks.com/en/lakehouse/medallion) | | | | |
| Rule 3: Data Quality | [Reliability](https://docs.databricks.com/en/lakehouse-architecture/reliability/best-practices#use-constraints-and-data-expectations) | | | | |
| Rule 4: Delta Lake | [Performance](https://docs.databricks.com/en/lakehouse-architecture/performance-efficiency/best-practices#use-predictive-optimization) | | | | |
| Rule 5: Constraints | [Governance](https://docs.databricks.com/en/tables/constraints) | | | | |
| Rule 6: Serverless | [Cost](https://docs.databricks.com/en/lakehouse-architecture/cost-optimization/best-practices#use-serverless-services-for-your-workloads) | | | | |
| Rule 7: IaC | [OpEx](https://docs.databricks.com/en/dev-tools/bundles) | | | | |
| Rule 8: Documentation | [Governance](https://docs.databricks.com/en/lakehouse-architecture/data-governance/best-practices#add-consistent-descriptions-to-your-metadata) | | | | |
| Rule 9: Schema-First | [Reliability](https://docs.databricks.com/en/tables/schema-enforcement) | | | | |
| Rule 10: Deduplication | [Performance](https://docs.databricks.com/en/delta/merge) | | | | |
| Rule 11: Semantic Layer | [Interop](https://docs.databricks.com/en/genie/) | | | | |
| Rule 12: ML/AI Standards | [Governance](https://docs.databricks.com/en/lakehouse-architecture/data-governance/best-practices#govern-ai-assets-together-with-data) | | | | |
| Rule 13: AI Gateway | [Governance](https://docs.databricks.com/en/ai-gateway/) | | | | |
| Rule 14: Network Security | [Security](https://docs.databricks.com/en/lakehouse-architecture/security-compliance-and-privacy/best-practices#3-secure-your-network-and-protect-endpoints) | | | | |
| **Overall** | | | | | |

### Remediation Plan

| Finding | Severity | Owner | Due Date | Status |
|---------|----------|-------|----------|--------|
| | | | | |

---

## Quick Reference: Common Violations

### High Severity (Must Fix Before Production)

| Violation | Impact | Fix |
|-----------|--------|-----|
| Missing PK constraint | BI tools can't auto-discover relationships | Add `PRIMARY KEY ... NOT ENFORCED` |
| No CDF enabled | Can't use incremental processing | Add `delta.enableChangeDataFeed = true` |
| Missing deduplication | MERGE failures in production | Add `orderBy().dropDuplicates()` |
| Hardcoded cluster | Cost overruns, maintenance burden | Use serverless environment |

### Medium Severity (Fix Within Sprint)

| Violation | Impact | Fix |
|-----------|--------|-----|
| Missing table comment | Genie/AI can't understand data | Add COMMENT with business context |
| Missing column comments | Self-service analytics impaired | Add COMMENT to all columns |
| No schema YAML | Schema drift risk | Create YAML definition |
| Few DLT expectations | Quality issues not detected | Add 5+ expectations per table |

### Low Severity (Fix When Possible)

| Violation | Impact | Fix |
|-----------|--------|-----|
| Short comments (<50 chars) | Limited AI understanding | Expand with business context |
| Missing domain tag | Catalog browsing harder | Add `domain` TBLPROPERTY |
| No quarantine table | Failed records lost | Add quarantine pattern |

### Semantic Layer & ML/AI Violations

| Violation | Severity | Impact | Fix |
|-----------|----------|--------|-----|
| `name` field in Metric View YAML | High | Deployment fails | Remove `name` field (v1.1) |
| Transitive joins in Metric View | High | Query errors | Use direct joins only |
| DATE type in TVF parameters | High | Parameter conversion fails | Use STRING for dates |
| Missing OBO context detection | High | Agent evaluation fails | Add environment variable check |
| Missing Genie Space resources | High | Permission denied errors | Declare in AuthPolicy |
| No AI Guardrails (external) | Medium | Safety risks | Enable for external endpoints |
| Missing rate limiting | Medium | Cost overruns | Configure limits per endpoint |

---

## Sign-Off Sheet

### Design Review

| Reviewer | Role | Date | Signature |
|----------|------|------|-----------|
| | Platform Lead | | |
| | Data Steward | | |
| | Security (if PII) | | |

### Production Approval

| Approver | Role | Date | Signature |
|----------|------|------|-----------|
| | Platform Lead | | |
| | Executive Sponsor (major) | | |

---

## Related Documents

- [Golden Rules](../README.md)
- [Roles and Responsibilities](../enterprise-architecture/02-roles-responsibilities.md)
- [Implementation Workflow](../enterprise-architecture/03-implementation-workflow.md)
- [Semantic Layer Overview](../solution-architecture/semantic-layer/33-semantic-layer-overview.md)
- [GenAI Agent Patterns](../solution-architecture/ml-ai/51-genai-agent-patterns.md)
- [AI Gateway Patterns](../solution-architecture/ml-ai/53-ai-gateway-patterns.md)
- [Network Security](../platform-architecture/18-network-security.md)

---

*Verification Checklist Version 2.0 - Based on Enterprise Golden Rules (February 2026)*
*Added: Rule 11 (Semantic Layer), Rule 12 (ML/AI), Rule 13 (AI Gateway), Rule 14 (Network Security)*
