# Golden Rules Audit Report

**Notebook/Project:** [NAME]
**Auditor:** Databricks Assistant
**Date:** [TODAY]
**Version:** Enterprise Golden Rules v5.4
**Domains Assessed:** [list applicable domains]

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Rules Assessed | X |
| PASS | X |
| FAIL | X |
| N/A | X |
| **Compliance Score** | **X%** |

### Severity Breakdown

| Severity | Pass | Fail | Total | Compliance |
|----------|------|------|-------|------------|
| Critical | X | X | X | X% |
| Required | X | X | X | X% |

### Risk Assessment

| Risk Level | Criteria |
|------------|----------|
| **GREEN** (>= 95%) | Production-ready. Minor fixes only. |
| **YELLOW** (80-94%) | Conditional deployment. Fix Critical items first. |
| **RED** (< 80%) | Blocked. Remediation required before deployment. |

**Overall Risk Level:** [GREEN / YELLOW / RED]

---

## Findings by Domain

### Table Creation & Storage (DL, SC, PA)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| DL-01 | All tables in Unity Catalog | Critical | PASS/FAIL | [details] |
| DL-04 | Delta Lake format required | Critical | PASS/FAIL | [details] |
| DL-02 | Managed tables (not external) | Critical | PASS/FAIL | [details] |
| DL-05 | CLUSTER BY AUTO on all tables | Critical | PASS/FAIL | [details] |
| SC-01 | Serverless compute for all jobs | Critical | PASS/FAIL | [details] |

### Naming & Comments (NC, CM)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| NC-01 | snake_case for all objects | Critical | PASS/FAIL | [details] |
| CM-02 | Table COMMENT with business context | Critical | PASS/FAIL | [details] |
| CM-03 | Column COMMENT for all columns | Critical | PASS/FAIL | [details] |

### Tagging (TG)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| TG-01 | Required workflow tags | Critical | PASS/FAIL | [details] |
| TG-02 | Governed Tags for UC securables | Critical | PASS/FAIL | [details] |

### Data Pipelines (DP, DA)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| DP-01 | Medallion Architecture | Critical | PASS/FAIL | [details] |
| DP-02 | CDF on Bronze tables | Critical | PASS/FAIL | [details] |
| DA-03 | Dedup before MERGE | Critical | PASS/FAIL | [details] |

### Data Quality (DQ)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| DQ-01 | DLT expectations defined | Critical | PASS/FAIL | [details] |
| DQ-03 | Gold Lakehouse Monitors | Critical | PASS/FAIL | [details] |

### Data Modeling (DM)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| DM-01 | Dimensional modeling in Gold | Critical | PASS/FAIL | [details] |
| DM-02 | PRIMARY KEY constraints | Critical | PASS/FAIL | [details] |

### Semantic Layer (MV, TF, GN)

> Note: SL prefix retired in v5.4. Requirements now covered by MV-01/MV-04 and MV-05.

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| MV-01 | All core metrics in Metric Views | Critical | PASS/FAIL | [details] |
| MV-05 | No transitive joins | Critical | PASS/FAIL | [details] |

### Streaming (ST)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| ST-01 | Lakeflow SDP First | Critical | PASS/FAIL | [details] |
| ST-02 | Managed Checkpointing | Critical | PASS/FAIL | [details] |

### Asset Bundles & Deployment (IN)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| PA-04 | Asset Bundles for deployment | Critical | PASS/FAIL | [details] |
| IN-01 | Serverless in bundle config | Critical | PASS/FAIL | [details] |

### Governance (GOV, EA)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| EA-10 | Data as a product with SLAs | Critical | PASS/FAIL | [details] |
| GOV-01 | Identities via SCIM | Critical | PASS/FAIL | [details] |

### Security (SEC)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| SEC-01 | VNet/VPC injection | Critical | PASS/FAIL | [details] |
| SEC-07 | No public IPs | Critical | PASS/FAIL | [details] |

### Reliability & Compute (REL, SC, CP)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| REL-01 | Time travel >= 7 days | Critical | PASS/FAIL | [details] |
| SC-01 | Serverless compute first | Critical | PASS/FAIL | [details] |
| CP-01 | Cluster policies enforced | Critical | PASS/FAIL | [details] |
| CP-07 | Standard access mode | Required | PASS/FAIL | [details] |
| REL-10 | Monitor platform service limits | Required | PASS/FAIL | [details] |
| REL-11 | Capacity planning for production | Required | PASS/FAIL | [details] |

### ML/AI (ML)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| ML-02 | output_schema for UC models | Critical | PASS/FAIL | [details] |
| ML-07 | Models in UC with aliases | Critical | PASS/FAIL | [details] |

### Cost Optimization (COST)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| COST-01 | Budget policies | Critical | PASS/FAIL | [details] |

### Data Sharing (DS)

| ID | Rule | Severity | Status | Notes |
|----|------|----------|--------|-------|
| DS-01 | UC for shared assets | Critical | PASS/FAIL | [details] |
| DS-03 | No PII without filters | Critical | PASS/FAIL | [details] |

---

## Critical Findings (Detail)

> Expand each FAIL item with the detail block below. List Critical items first, then Required.

### [FAIL] XX-01: Rule Name

- **Severity:** Critical
- **Domain:** [Domain Name]
- **Location:** Cell X, line Y
- **Violation:** [describe what was found]
- **Current Code:**
```sql
-- violating code here
SELECT * FROM hive_metastore.default.my_table
```
- **Required Code:**
```sql
-- corrected code here
SELECT * FROM catalog.schema.my_table
```
- **Business Impact:** [why this matters -- e.g., "Tables in HMS bypass Unity Catalog governance, lineage tracking, and fine-grained access controls"]
- **Reference:** [Link to golden rules document section]

---

### [FAIL] XX-02: Rule Name

- **Severity:** Required
- **Domain:** [Domain Name]
- **Location:** Cell X, line Y
- **Violation:** [describe what was found]
- **Current Code:**
```python
# violating code here
```
- **Required Code:**
```python
# corrected code here
```
- **Business Impact:** [why this matters]
- **Reference:** [Link to golden rules document section]

---

## Recommendations

### Priority 1 — Critical (Fix Before Deployment)

1. [Specific actionable fix with rule ID]
2. [Specific actionable fix with rule ID]

### Priority 2 — Required (Fix Within Sprint)

1. [Specific actionable fix with rule ID]
2. [Specific actionable fix with rule ID]

### Priority 3 — Improvements (Fix When Possible)

1. [Suggested improvement]
2. [Suggested improvement]

---

## Next Steps

- [ ] Fix all Critical findings (Priority 1)
- [ ] Fix all Required findings (Priority 2)
- [ ] Re-run audit to verify compliance
- [ ] Obtain sign-off from Platform Lead
- [ ] Update architecture review checklist
- [ ] Schedule follow-up audit if compliance < 95%

---

## Appendix: Audit Metadata

| Field | Value |
|-------|-------|
| Audit Tool | Databricks Assistant |
| Checklist Version | Enterprise Golden Rules v5.4 |
| Rules Engine | Full Checklist (155+ rules) |
| Scope | [notebooks / project / domain] |
| Duration | [time taken] |
| Previous Audit | [date or N/A] |
| Previous Score | [X% or N/A] |

---

*Generated by Databricks Assistant — Enterprise Golden Rules v5.4*
*Audit Date: [TODAY]*
