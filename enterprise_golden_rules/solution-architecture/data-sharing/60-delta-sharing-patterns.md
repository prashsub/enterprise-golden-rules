# Delta Sharing Patterns

> **Document Owner:** Data Platform | **Status:** Approved | **Last Updated:** February 2026

## Overview

Delta Sharing is the open protocol for secure data sharing with external partners.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **DS-01** | Unity Catalog for all shared assets | Critical | [Interop](https://docs.databricks.com/en/delta-sharing/) |
| **DS-02** | Prefer Databricks-to-Databricks | Critical | [Interop](https://docs.databricks.com/en/delta-sharing/) |
| **DS-03** | Never share PII without filters | Critical | [Interop](https://docs.databricks.com/en/delta-sharing/) |
| **DS-04** | Define retention/revocation policies | Critical | [Interop](https://docs.databricks.com/en/delta-sharing/) |
| **DS-05** | Enable audit logging | Critical | [Interop](https://docs.databricks.com/en/delta-sharing/) |
| **DS-06** | Short-lived tokens (open sharing) | Required | [Interop](https://docs.databricks.com/en/delta-sharing/) |
| **DS-07** | Share views, not base tables | Required | [Interop](https://docs.databricks.com/en/delta-sharing/) |

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| UC governance | GOV-01..07 | [15-unity-catalog-governance](../../platform-architecture/15-unity-catalog-governance.md) |
| Security standards | SEC-01..09 | [14-security-hardening](../../platform-architecture/14-security-hardening.md) |
| Data access pattern decisions | DI-03, DI-06 | [16-data-access-patterns](../../platform-architecture/16-data-access-patterns.md) |

---

## Sharing Protocols

| Protocol | Recipients | Assets |
|----------|-----------|--------|
| **Databricks-to-Databricks** | UC workspaces | Tables, Views, Volumes, Models |
| **Open Sharing** | Any platform | Tables only |

**Prefer D2D** - no token management, full audit on both sides.

---

## Quick Reference

```sql
-- Create share
CREATE SHARE my_share COMMENT 'Description';
ALTER SHARE my_share ADD TABLE catalog.schema.table;

-- Create D2D recipient
CREATE RECIPIENT partner USING ID 'aws:region:workspace:metastore';

-- Create open sharing recipient
CREATE RECIPIENT external COMMENT 'External partner';

-- Grant/revoke
GRANT SELECT ON SHARE my_share TO RECIPIENT partner;
REVOKE SELECT ON SHARE my_share FROM RECIPIENT partner;

-- Token rotation
ALTER RECIPIENT external ROTATE TOKEN;
```

---

## PII Protection Pattern

```sql
-- Share view with masked PII, not base table
CREATE VIEW safe_customer AS
SELECT 
    customer_id,
    CONCAT('***@', SPLIT(email, '@')[1]) AS email_masked,
    region, segment, total_orders
FROM customer_master;

ALTER SHARE partner_share ADD VIEW safe_customer;
```

---

## Audit Queries

```sql
-- Monitor recipient access
SELECT request_params.recipient_name, COUNT(*) AS access_count
FROM system.access.audit
WHERE service_name = 'deltasharing' AND action_name = 'getTableData'
GROUP BY 1;
```

---

## Token Management

- **Lifetime**: Max 90 days for sensitive data
- **Rotation**: Quarterly or on personnel change
- **Prefer OIDC** over bearer tokens when possible

---

## Validation Checklist

### Before Sharing
- [ ] Data in Unity Catalog managed tables
- [ ] No raw PII (use filtered views)
- [ ] Share has descriptive comment

### Before Adding Recipients
- [ ] D2D vs Open protocol determined
- [ ] Agreement signed
- [ ] Token lifetime set (open sharing)

### Ongoing
- [ ] Audit monitoring active
- [ ] Quarterly token rotation
- [ ] Monthly access review

---

## References

- [Delta Sharing](https://learn.microsoft.com/en-us/azure/databricks/delta-sharing/)
- [Create Recipients](https://learn.microsoft.com/en-us/azure/databricks/delta-sharing/create-recipient)
