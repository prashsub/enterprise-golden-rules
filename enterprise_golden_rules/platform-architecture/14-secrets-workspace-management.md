# Secrets & Workspace Management

> **Document Owner:** Platform Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

This document covers secrets management and workspace organization patterns. Secrets must be stored securely and accessed through approved methods.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **SM-01** | All secrets in Databricks Secret Scopes | Critical | [Security](https://docs.databricks.com/en/security/secrets/) |
| **SM-02** | Never hardcode credentials | Critical | [Security](https://docs.databricks.com/en/security/secrets/) |
| **SM-03** | Use dbutils.secrets.get() only | Critical | [Security](https://docs.databricks.com/en/security/secrets/) |
| **SM-04** | Workspace follows naming conventions | Required | OpEx |

---

## Secrets Management

### Correct Pattern

```python
# CORRECT: Use dbutils.secrets.get()
password = dbutils.secrets.get(scope="data-platform", key="database-password")

# Use in connection (value redacted in logs)
jdbc_url = f"jdbc:postgresql://host/db?password={password}"
```

### Never Do This

```python
# Hardcoded password
password = "super_secret_123"

# Environment variable
password = os.environ.get("DB_PASSWORD")

# Config file in repo
with open("secrets.json") as f:
    password = json.load(f)["password"]
```

---

## Secret Scopes

### Creating Scopes

```bash
# Databricks-backed scope
databricks secrets create-scope data-platform

# Azure Key Vault-backed scope
databricks secrets create-scope --scope kv-backed \
  --scope-backend-type AZURE_KEYVAULT \
  --resource-id /subscriptions/.../vaults/my-vault
```

### Managing Secrets

```bash
# Add secret
databricks secrets put-secret data-platform database-password

# List secrets (values never shown)
databricks secrets list-secrets data-platform
```

### Access Control

```bash
# Grant READ to group
databricks secrets put-acl data-platform data_engineers READ

# Grant MANAGE (can add secrets)
databricks secrets put-acl data-platform platform_admins MANAGE
```

| Permission | List | Read | Write | Manage ACL |
|------------|------|------|-------|------------|
| READ | Yes | Yes | No | No |
| WRITE | Yes | Yes | Yes | No |
| MANAGE | Yes | Yes | Yes | Yes |

---

## Workspace Organization

```
/Workspace
├── /Shared                    # Team-shared content
│   ├── /data-platform         # Platform team
│   ├── /ml-team               # ML team
│   └── /analytics             # Analytics team
├── /Users                     # Personal workspaces
│   └── /user@company.com
└── /Repos                     # Git-connected repos
    └── /user@company.com
        └── /project-name
```

### Folder Permissions

| Level | Description |
|-------|-------------|
| CAN_READ | View folders and files |
| CAN_RUN | Execute notebooks |
| CAN_EDIT | Modify notebooks |
| CAN_MANAGE | Full control |

---

## Service Principals

### When to Use

| Scenario | Authentication |
|----------|----------------|
| Interactive notebooks | User OAuth |
| Scheduled jobs | Service principal |
| CI/CD pipelines | Service principal |
| External integrations | Service principal |

### In Asset Bundles

```yaml
resources:
  jobs:
    production_pipeline:
      name: "[prod] Production Pipeline"
      run_as:
        service_principal_name: "data-pipeline-sp"
```

---

## Environment Isolation

```yaml
# databricks.yml
targets:
  dev:
    mode: development
    variables:
      catalog: company_dev
      secret_scope: dev-secrets

  prod:
    mode: production
    variables:
      catalog: company_prod
      secret_scope: prod-secrets
    run_as:
      service_principal_name: production-sp
```

### Environment-Aware Secret Access

```python
def get_secret(key: str) -> str:
    scope = spark.conf.get("secret_scope", "dev-secrets")
    return dbutils.secrets.get(scope=scope, key=key)
```

---

## Audit Queries

### Secret Access

```sql
SELECT
    event_time,
    user_identity.email,
    request_params.scope,
    request_params.key
FROM system.access.audit
WHERE action_name = 'getSecret'
    AND event_date >= CURRENT_DATE - 7;
```

### Workspace Activity

```sql
SELECT
    event_time,
    user_identity.email,
    action_name,
    request_params.path
FROM system.access.audit
WHERE service_name = 'workspace'
    AND event_date >= CURRENT_DATE - 7;
```

---

## Validation Checklist

### Secrets
- [ ] All secrets in Secret Scopes
- [ ] No hardcoded credentials
- [ ] ACLs set appropriately
- [ ] Different scopes per environment

### Workspace
- [ ] Follows folder naming conventions
- [ ] Team folders under /Shared
- [ ] Production runs as service principal

### Service Principals
- [ ] Created for automated workloads
- [ ] Assigned to appropriate groups
- [ ] Token rotation policy in place

---

## Related Documents

- [Platform Overview](10-platform-overview.md)
- [Roles & Responsibilities](../enterprise-architecture/02-roles-responsibilities.md)

---

## References

- [Secret Scopes](https://docs.databricks.com/security/secrets/)
- [Workspace Organization](https://docs.databricks.com/workspace/)
- [Service Principals](https://docs.databricks.com/admin/service-principals/)
