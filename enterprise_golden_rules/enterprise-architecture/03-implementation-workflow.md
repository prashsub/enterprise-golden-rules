# Implementation Workflow

> **Document Owner:** Platform Team | **Status:** Approved | **Last Updated:** February 2026

## Overview

This document provides step-by-step workflows for implementing Golden Rules in new data domains and conducting compliance audits.

---

## New Domain Implementation (8 Weeks)

### Phase 1: Planning & Design (Week 1)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 1.1 Requirements gathering | Requirements document | Data Steward |
| 1.2 Data classification | Classification matrix | Data Steward + Security |
| 1.3 Architecture design | ERD, data flow diagram | Data Engineer |
| 1.4 Schema definition | Gold layer YAML files | Data Engineer |

**Checklist:**
- [ ] Business requirements documented
- [ ] Data sources identified
- [ ] PII columns identified and classified
- [ ] Gold layer star schema designed (ERD)
- [ ] YAML schema files created

---

### Phase 2: Infrastructure Setup (Week 2)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 2.1 Unity Catalog setup | Catalog and schemas | Platform Engineer |
| 2.2 Asset Bundle creation | Bundle directory | Platform Engineer |
| 2.3 Access control | Permissions granted | Platform Admin |

**Checklist:**
- [ ] Catalog created (if new)
- [ ] Schemas created (bronze, silver, gold)
- [ ] Predictive optimization enabled
- [ ] Asset Bundle validated
- [ ] Service principal configured

---

### Phase 3: Bronze Layer (Week 3)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 3.1 Create Bronze tables | DDL with metadata | Data Engineer |
| 3.2 Build ingestion pipeline | Auto Loader config | Data Engineer |
| 3.3 Deploy Bronze job | Working ingestion | Data Engineer |

**Checklist:**
- [ ] Tables created with `USING DELTA CLUSTER BY AUTO`
- [ ] CDF enabled (`delta.enableChangeDataFeed = true`)
- [ ] Table and column COMMENTs added
- [ ] Ingestion metadata columns present
- [ ] Job running successfully

---

### Phase 4: Silver Layer (Week 4)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 4.1 Design DLT pipeline | Notebook structure | Data Engineer |
| 4.2 Implement data quality | Expectations (5+ per table) | Data Engineer |
| 4.3 Deploy DLT pipeline | Working pipeline | Data Engineer |

**Checklist:**
- [ ] DLT pipeline uses Direct Publishing Mode
- [ ] All tables have `cluster_by_auto=True`
- [ ] Critical rules use `expect_or_drop`
- [ ] Quarantine tables capture failures
- [ ] Pipeline running with serverless + Photon

---

### Phase 5: Gold Layer (Week 5)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 5.1 Create Gold tables | Tables from YAML | Data Engineer |
| 5.2 Apply constraints | PKs and FKs | Data Engineer |
| 5.3 Build MERGE pipelines | Merge scripts | Data Engineer |
| 5.4 Deploy Gold jobs | Setup + merge jobs | Data Engineer |

**Checklist:**
- [ ] Tables created from YAML schema
- [ ] All dimensions have PRIMARY KEY
- [ ] All facts have composite PRIMARY KEY
- [ ] FKs applied AFTER all PKs exist
- [ ] MERGE uses deduplication pattern
- [ ] SCD Type 2 for historical dimensions

---

### Phase 6: Semantic Layer (Week 6)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 6.1 Create TVFs | SQL functions | Analytics Engineer |
| 6.2 Create Metric Views | YAML definitions | Analytics Engineer |
| 6.3 Configure Genie Space | Trusted assets | Analytics Engineer |

**Checklist:**
- [ ] TVFs use STRING date parameters
- [ ] Metric Views use v1.1 format (no `name` field)
- [ ] Comments follow v3.0 structured format
- [ ] No transitive joins in Metric Views
- [ ] Genie Space tested with sample questions

---

### Phase 7-8: Production (Weeks 7-8)

| Step | Deliverable | Owner |
|------|-------------|-------|
| 7.1 Setup Lakehouse Monitoring | Monitors configured | Data Engineer |
| 7.2 Create alerts | Alert rules | Data Engineer |
| 7.3 Production deployment | Production jobs | Platform Engineer |
| 7.4 Documentation | Runbook | Data Engineer |

**Checklist:**
- [ ] Monitors created for Gold tables
- [ ] Custom metrics documented
- [ ] Freshness alerts configured
- [ ] Quality threshold alerts configured
- [ ] Production schedules enabled
- [ ] Runbook completed

---

## Compliance Audit Workflow

### Step 1: Inventory

```sql
-- List all tables by layer
SELECT 
    table_catalog,
    table_schema,
    table_name,
    CASE 
        WHEN table_schema LIKE '%bronze%' THEN 'Bronze'
        WHEN table_schema LIKE '%silver%' THEN 'Silver'
        WHEN table_schema LIKE '%gold%' THEN 'Gold'
    END as layer
FROM information_schema.tables
WHERE table_catalog = 'my_catalog';
```

### Step 2: Rule Assessment

**Check CDF Enabled (Bronze/Silver):**
```sql
SELECT 
    table_schema, table_name,
    CASE WHEN option_value = 'true' THEN '✅' ELSE '❌' END as cdf_enabled
FROM information_schema.tables t
LEFT JOIN information_schema.table_options o 
    ON t.table_name = o.table_name
    AND o.option_name = 'delta.enableChangeDataFeed'
WHERE t.table_schema IN ('bronze', 'silver');
```

**Check PK Coverage (Gold):**
```sql
SELECT 
    table_name,
    CASE WHEN COUNT(constraint_name) > 0 THEN '✅' ELSE '❌' END as has_pk
FROM information_schema.table_constraints
WHERE constraint_type = 'PRIMARY KEY' AND table_schema = 'gold'
GROUP BY table_name;
```

**Check Documentation (All):**
```sql
SELECT 
    table_name,
    CASE WHEN comment IS NOT NULL AND LENGTH(comment) > 50 THEN '✅' ELSE '❌' END as documented
FROM information_schema.tables
WHERE table_schema IN ('bronze', 'silver', 'gold');
```

### Step 3: Findings Report

| Severity | Action |
|----------|--------|
| Critical | Immediate remediation required |
| High | Remediation within 1 sprint |
| Medium | Add to backlog |
| Low | Track for next audit |

---

## Exception Request Process

### Step 1: Submit Request

Complete the [Exception Request Form](../templates/exception-request-form.md) with:
- Rule being bypassed
- Business justification
- Risk assessment
- Remediation timeline

### Step 2: Review

| Risk Level | Approver |
|------------|----------|
| Low/Medium | Platform Architect |
| High | Architecture Review Board |

### Step 3: Document & Track

- Approved exceptions logged in governance system
- Review date scheduled
- Conditions documented

---

## Timeline Summary

| Phase | Duration | Key Milestone |
|-------|----------|---------------|
| Planning | 1 week | YAML schemas complete |
| Infrastructure | 1 week | Asset Bundle deployed |
| Bronze | 1 week | Ingestion running |
| Silver | 1 week | DLT pipeline running |
| Gold | 1 week | MERGE jobs running |
| Semantic | 1 week | Metric Views deployed |
| Production | 2 weeks | Monitoring active |

**Total: 8 weeks for complete domain implementation**

---

## Related Documents

- [Data Governance](01-data-governance.md)
- [Roles & Responsibilities](02-roles-responsibilities.md)
- [Data Modeling](04-data-modeling.md)
- [Naming & Comment Standards](05-naming-comment-standards.md)
- [Tagging Standards](06-tagging-standards.md)
- [Data Quality Standards](07-data-quality-standards.md)
- [Architecture Review Checklist](../templates/architecture-review-checklist.md)
