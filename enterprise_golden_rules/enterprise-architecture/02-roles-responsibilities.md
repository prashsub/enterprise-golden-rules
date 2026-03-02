# Roles & Responsibilities

> **Document Owner:** Platform Architecture Team | **Status:** Approved | **Last Updated:** February 2026

## Overview

This document defines roles, responsibilities, and accountability for implementing and maintaining the Golden Rules across the data platform.

---

## Role Definitions

### Platform Team

| Role | Primary Responsibilities |
|------|--------------------------|
| **Platform Architect** | Architecture decisions, standards enforcement, exception approvals |
| **Platform Engineer** | Infrastructure, CI/CD, Asset Bundles, compute policies |
| **Platform Admin** | Access control, workspace management, cost monitoring |

### Solution Teams

| Role | Primary Responsibilities |
|------|--------------------------|
| **Data Engineer** | Pipeline development (Bronze→Silver→Gold), data quality |
| **Analytics Engineer** | Semantic layer (TVFs, Metric Views), dashboards |
| **ML Engineer** | Model development, feature engineering, serving |
| **GenAI Engineer** | Agent development, prompt engineering, evaluation |

### Governance & Oversight

| Role | Primary Responsibilities |
|------|--------------------------|
| **Domain Product Owner** | Data product strategy, SLA definition, consumer engagement, AI readiness |
| **Data Steward** | Domain governance, quality standards, access approvals |
| **Security Analyst** | Security reviews, compliance audits, incident response |

---

## RACI Matrix

**Legend:** R=Responsible, A=Accountable, C=Consulted, I=Informed

### Enterprise Architecture Rules

| Rule | Platform Architect | Platform Admin | Data Steward | Security |
|------|-------------------|----------------|--------------|----------|
| EA-01: Documentation | C | I | **A/R** | I |
| EA-02: PII classification | C | I | R | **A** |
| EA-03: Steward assignment | **A** | I | R | I |
| EA-04: Usage attribution | **A** | R | C | I |
| EA-05: Custom tags | **A** | R | C | I |
| EA-06: Budget policies | **A** | **A/R** | C | I |
| EA-07: Architecture review | **A/R** | I | C | C |
| EA-08: Exception approval | **A** | I | C | C |
| EA-09: Governed tags | **A** | R | **A/R** | C |

### Data Product & AI Rules

| Rule | Domain Product Owner | Platform Architect | Data Steward | ML Engineer |
|------|---------------------|--------------------|--------------|-------------|
| EA-10: Data as a Product | **A/R** | C | R | I |
| EA-11: Data Contracts | **A** | C | R | I |
| EA-12: AI Readiness | **A/R** | C | C | R |

### Platform Architecture Rules

| Rule | Platform Architect | Platform Engineer | Data Engineer |
|------|-------------------|-------------------|---------------|
| Unity Catalog only | **A** | R | R |
| Delta Lake format | **A** | R | R |
| Serverless compute | **A** | R | R |
| Asset Bundles | **A** | R | R |
| Hierarchical jobs | C | **A/R** | R |
| Secrets management | C | R | R |

### Data Pipeline Rules

| Rule | Platform Engineer | Data Engineer | Data Steward |
|------|-------------------|---------------|--------------|
| Medallion architecture | C | R | **A** |
| CDF on Bronze | C | R | I |
| DLT with expectations | C | R | **A** |
| Gold from YAML | **A** | R | C |
| Dedup before MERGE | C | R | I |
| PK/FK constraints | **A** | R | C |

---

## Escalation Matrix

| Issue Type | Level 1 | Level 2 | Level 3 | SLA |
|------------|---------|---------|---------|-----|
| Data Quality | Data Engineer | Data Steward | Platform Architect | 4 hours |
| Pipeline Failure | Data Engineer | Platform Engineer | Platform Architect | 2 hours |
| Security Incident | Security Analyst | Security Lead | CISO | 1 hour |
| Access Request | Platform Admin | Data Steward | Platform Architect | 24 hours |

---

## Verification Procedures

### Automated Checks

| Check | Frequency | Tool |
|-------|-----------|------|
| Schema validation | Per PR | Pre-commit hook |
| YAML compliance | Per PR | Bundle validate |
| UC compliance | Daily | System tables scan |
| Documentation coverage | Weekly | Table COMMENTs audit |

### Manual Reviews

| Review | Frequency | Participants |
|--------|-----------|--------------|
| Architecture Review | Per project | Architects, Leads, Security |
| Code Review | Per PR | 2 Engineers minimum |
| Compliance Review | Quarterly | Compliance, Stewards |

---

## Metrics & Reporting

| Metric | Target | Owner |
|--------|--------|-------|
| Rule compliance rate | >95% | Platform Architect |
| Review turnaround | <24h | All |
| Exception rate | <5% | Platform Architect |
| Training completion | 100% | Managers |

---

## Communication Channels

| Purpose | Channel | Response SLA |
|---------|---------|--------------|
| General questions | #data-platform-help | 4 hours |
| Urgent issues | #data-platform-oncall | 30 min |
| Architecture discussions | #data-platform-architecture | 24 hours |
| Security incidents | security@company.com | 1 hour |

---

## Related Documents

- [Data Governance](01-data-governance.md)
- [Implementation Workflow](03-implementation-workflow.md)
- [Data Modeling](04-data-modeling.md)
- [Naming & Comment Standards](05-naming-comment-standards.md)
- [Tagging Standards](06-tagging-standards.md)
- [Data Quality Standards](07-data-quality-standards.md)
- [Exception Request Form](../templates/exception-request-form.md)
