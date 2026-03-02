# Classic Compute Governance

> **Document Owner:** Platform Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

Serverless is mandatory first choice (see [SC-01](11-serverless-compute.md)). This document governs **classic compute** for remaining use cases: GPU, 24/7 streaming, and workloads requiring specific Spark configurations. It covers access modes, cluster policies, Photon, and workload-based sizing.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **CP-01** | All classic clusters must use approved policies | Critical | [Cost](https://docs.databricks.com/en/admin/clusters/policies) |
| **CP-02** | No unrestricted cluster creation | Critical | [Cost](https://docs.databricks.com/en/admin/clusters/policies) |
| **CP-03** | Instance types limited by policy | Required | [Cost](https://docs.databricks.com/en/admin/clusters/policy-definition) |
| **CP-04** | Auto-termination required | Required | [Cost](https://docs.databricks.com/en/lakehouse-architecture/cost-optimization/best-practices#use-auto-termination) |
| **CP-05** | Jobs compute for scheduled, All-Purpose for exploration | Critical | [Cost](https://docs.databricks.com/en/lakehouse-architecture/cost-optimization/best-practices#use-job-compute) |
| **CP-06** | Dependencies consistent between All-Purpose and Jobs | Required | [Cost](https://docs.databricks.com/en/lakehouse-architecture/cost-optimization/best-practices) |
| **CP-07** | Use standard access mode for most workloads | Required | [Security](https://docs.databricks.com/en/lakehouse-architecture/security-compliance-and-privacy/best-practices#1-manage-identity-and-access-using-least-privilege) |
| **CP-08** | Enable Photon for complex transformations | Required | [Performance](https://docs.databricks.com/en/compute/photon) |
| **CP-09** | Right-size clusters based on workload type | Required | [Cost](https://docs.databricks.com/en/lakehouse-architecture/cost-optimization/best-practices#choose-the-most-efficient-compute-size) |

> **Note:** Serverless is mandatory first choice — see [SC-01](11-serverless-compute.md). This document covers the classic compute exception path only.

---

## CP-01: All Classic Clusters Must Use Approved Policies

### Rule
Every classic cluster (Jobs or All-Purpose) must be created under an approved cluster policy. No unrestricted cluster creation is permitted.

### Why It Matters
- Policies enforce cost controls, instance limits, and auto-termination
- Prevents runaway compute costs from oversized or forgotten clusters
- Ensures consistent tagging for cost attribution

### Standard Policies

**1. Jobs - Data Engineering (CP-03)**

```json
{
  "name": "Jobs - Data Engineering",
  "definition": {
    "spark_version": {
      "type": "allowlist",
      "values": ["14.3.x-scala2.12", "15.4.x-scala2.12"]
    },
    "node_type_id": {
      "type": "allowlist",
      "values": ["i3.xlarge", "i3.2xlarge"]
    },
    "num_workers": { "type": "range", "minValue": 1, "maxValue": 10 },
    "autotermination_minutes": { "type": "fixed", "value": 10 },
    "cluster_type": { "type": "fixed", "value": "job" },
    "custom_tags.team": { "type": "required" },
    "custom_tags.cost_center": { "type": "required" }
  },
  "libraries": [/* standard libraries */]
}
```

**2. Jobs - ML Training GPU (CP-03)**

```json
{
  "name": "Jobs - ML Training GPU",
  "definition": {
    "spark_version": {
      "type": "allowlist",
      "values": ["14.3.x-gpu-ml-scala2.12"]
    },
    "node_type_id": {
      "type": "allowlist",
      "values": ["g4dn.xlarge", "g4dn.2xlarge"]
    },
    "num_workers": { "type": "range", "minValue": 1, "maxValue": 4 },
    "autotermination_minutes": { "type": "fixed", "value": 30 }
  },
  "libraries": [/* standard + ML libraries */]
}
```

**3. All-Purpose - Development (CP-03)**

```json
{
  "name": "All-Purpose - Development",
  "definition": {
    "spark_version": {
      "type": "allowlist",
      "values": ["14.3.x-scala2.12", "15.4.x-scala2.12"]
    },
    "node_type_id": {
      "type": "allowlist",
      "values": ["i3.xlarge"]
    },
    "num_workers": { "type": "range", "minValue": 0, "maxValue": 2 },
    "autotermination_minutes": { "type": "fixed", "value": 15 },
    "cluster_type": { "type": "fixed", "value": "all-purpose" }
  },
  "libraries": [/* same as Jobs policy */],
  "max_clusters_per_user": 1
}
```

### Policy Enforcement

When policies are updated, existing clusters may be out of compliance:

1. View compliance: **Compute** > **Policies** > **Compliance** column
2. Fix compliance: Click **Fix all** to update all resources
3. Monitor: Check `system.compute.clusters` for policy assignments

---

## CP-02: No Unrestricted Cluster Creation

### Rule
Remove the `Unrestricted` cluster creation permission from all users and groups. All clusters must be created under an approved policy.

### Why It Matters
- Unrestricted access allows users to create oversized, untagged clusters
- Bypasses all cost controls and instance type limits
- A single unrestricted cluster can consume an entire budget

### Implementation
1. Navigate to **Admin Console** > **Workspace Settings** > **Cluster creation**
2. Set to **Policy-restricted** (remove Allow Unrestricted)
3. Assign appropriate policies to groups

---

## CP-03: Instance Types Limited by Policy

### Rule
Cluster policies must restrict instance types to an allowlist appropriate for the workload type.

### Why It Matters
- Prevents selection of oversized or GPU instances for simple workloads
- Standardizes instance families for better reserved instance utilization
- Reduces the risk of accidental cost spikes

---

## CP-04: Auto-Termination Required

### Rule
All clusters must have auto-termination configured. No indefinitely running clusters except approved always-on streaming workloads.

### Auto-Termination Settings

| Environment | Setting |
|-------------|---------|
| Development | 15 minutes |
| Staging | 30 minutes |
| Production (batch) | 60 minutes |
| Production (streaming) | Disabled (0) — requires approval |

### Required Tags

All clusters must include required tags for cost attribution (see EA-05, TG-01):

```json
{
  "custom_tags.team": { "type": "required" },
  "custom_tags.cost_center": { "type": "required" },
  "custom_tags.environment": {
    "type": "allowlist",
    "values": ["dev", "staging", "prod"]
  }
}
```

---

## CP-05: Jobs Compute for Scheduled, All-Purpose for Exploration

### Rule
Use Jobs compute for all scheduled/automated workloads. All-Purpose compute is restricted to interactive exploration and debugging only.

### Comparison

| Aspect | Jobs Compute | All-Purpose |
|--------|--------------|-------------|
| **Purpose** | Scheduled/automated | Interactive exploration |
| **Lifecycle** | Created per run | Long-running |
| **Use For** | ETL, ML training, reports | Debugging, prototyping |
| **Not For** | Interactive work | Production workloads |

### Anti-Patterns
- Running production ETL on All-Purpose clusters (higher cost, no auto-scaling)
- Using Jobs compute for interactive debugging (poor developer experience)

---

## CP-06: Dependency Consistency Between All-Purpose and Jobs

### Rule
Code developed in All-Purpose must work identically in Jobs compute. Both environments must use the same library versions, enforced via cluster policies.

### Why It Matters
- "Works on my cluster" failures are the #1 cause of deployment issues
- Library version mismatches cause silent data quality bugs
- Policy-enforced libraries ensure a single source of truth

### Policy-Based Libraries

```json
{
  "libraries": [
    { "pypi": { "package": "pandas==2.0.3" } },
    { "pypi": { "package": "pyarrow>=14.0.0" } },
    { "pypi": { "package": "scikit-learn==1.3.2" } },
    { "pypi": { "package": "mlflow>=2.17.0" } }
  ]
}
```

**Effect:** Users cannot install/uninstall libraries on compute using this policy.

---

## CP-07: Use Standard Access Mode for Most Workloads

### Rule
Use standard (shared) access mode for most classic compute workloads. Dedicated access mode is only for GPU, RDD APIs, R, or container services.

### Why It Matters
- Multi-user with full user isolation — more cost-effective through resource sharing
- Enforces Unity Catalog governance automatically
- Reduces cluster sprawl (one shared cluster vs. many single-user clusters)

### Decision Guide

```
Need GPU, RDD, R, or Container Service?
├── YES → Dedicated Access Mode (SINGLE_USER)
└── NO → Standard Access Mode (USER_ISOLATION)
```

### Access Mode Comparison

| Feature | Standard (Shared) | Dedicated (Single-User) |
|---------|-------------------|------------------------|
| **Multi-user** | Yes | No |
| **User isolation** | Yes | N/A |
| **Unity Catalog** | Required | Required |
| **RDD APIs** | No | Yes |
| **GPU support** | Limited | Full |
| **R language** | No | Yes |

### Implementation
```yaml
# Standard access mode (default)
new_cluster:
  data_security_mode: USER_ISOLATION

# Dedicated (only when required)
new_cluster:
  data_security_mode: SINGLE_USER
```

---

## CP-08: Enable Photon for Complex Transformations

### Rule
Enable Photon for workloads with complex joins, large aggregations, or frequent disk access. Photon is built into serverless compute; for classic clusters, it must be explicitly enabled.

### Why It Matters
- Significant performance improvement for complex SQL and DataFrame operations
- Native vectorized query execution
- Optimized for wide transformations

> **Note:** Adaptive Query Execution (AQE) is enabled by default on Databricks Runtime 14.3+. Combined with Photon, AQE delivers significant performance gains without manual tuning.

### When Photon Helps Most

| Workload | Benefit |
|----------|---------|
| Complex joins | High |
| Large aggregations | High |
| Large table scans | High |
| Simple ETL (<2 sec queries) | Low |

### Implementation
```yaml
new_cluster:
  spark_version: "14.3.x-photon-scala2.12"
  runtime_engine: PHOTON

# Or for DLT
pipelines:
  gold:
    photon: true
```

---

## CP-09: Right-Size Clusters Based on Workload Type

### Rule
Size clusters based on workload characteristics. Use fewer larger workers for shuffle-heavy jobs; use single-node for interactive analysis.

### Why It Matters
- Over-provisioning wastes cost; under-provisioning causes failures and timeouts
- Instance type selection impacts shuffle performance, memory pressure, and cost
- Right-sizing is the most impactful cost optimization for classic compute

### Sizing Guide

| Workload | Workers | Instance Size | Photon |
|----------|---------|---------------|--------|
| Data Analysis | 0 (single node) | Large | Optional |
| Basic ETL | 2-4 | Small/Medium | No |
| Complex ETL | 2-4 | Large | Yes |
| ML Training | 0-2 | Large | No |
| Streaming | 4-8 (fixed) | Medium | Optional |

### Auto-Scaling Guidelines

| Workload | Auto-Scaling |
|----------|--------------|
| Interactive notebooks | Yes |
| Variable batch ETL | Yes |
| Streaming | No (fixed size) |
| ML Training | No (fixed size) |

---

## Validation Checklist

### Serverless-First
- [ ] Serverless evaluated first for ALL workloads
- [ ] Classic compute only when serverless not supported
- [ ] Exception documented if using classic

### Compute Type Separation
- [ ] Jobs compute for scheduled workloads
- [ ] All-Purpose only for interactive exploration
- [ ] No production on All-Purpose

### Dependency Consistency
- [ ] Same library versions in Jobs and All-Purpose
- [ ] Libraries defined in policies
- [ ] Single source of truth (requirements.txt)

### Policy Design
- [ ] Instance types appropriate for workload
- [ ] Auto-termination configured
- [ ] Required tags defined
- [ ] max_clusters_per_user set for All-Purpose

### Access Mode & Configuration
- [ ] Standard access mode unless GPU/RDD/R/Container required (CP-07)
- [ ] Photon enabled for complex transformations (CP-08)
- [ ] Cluster size matches workload type (CP-09)
- [ ] Auto-scaling enabled for variable workloads, disabled for streaming/ML

---

## Related Documents

- [Serverless Compute](11-serverless-compute.md)
- [Platform Overview](10-platform-overview.md)

---

## References

- [Compute Policies](https://learn.microsoft.com/en-us/azure/databricks/admin/clusters/policies)
- [Add Libraries to Policy](https://learn.microsoft.com/en-us/azure/databricks/admin/clusters/policies#add-libraries-to-a-policy)
- [Compute Configuration Recommendations](https://docs.databricks.com/en/compute/cluster-config-best-practices.html)
- [Photon](https://docs.databricks.com/en/compute/photon.html)
- [Access Modes](https://docs.databricks.com/en/compute/configure#access-mode)
