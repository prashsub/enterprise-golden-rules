# Reliability & Compute Golden Rules
**Rules:** PA-01..05, COST-01..03, REL-01..11, SC-01..09, CP-01..09 | **Count:** 36 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| PA-01 | No production data on DBFS root | Critical | UC volumes or managed tables only |
| PA-02 | System tables enabled for platform observability | Critical | `system.billing.usage` queryable? |
| PA-03 | Workspace isolation by environment and security boundary | Critical | Separate workspaces per env? |
| PA-04 | Use Lakehouse Federation for external data access | Required | `CREATE FOREIGN CATALOG` for external? |
| PA-05 | Use certified partner integrations | Required | Check partner connect catalog first? |
| COST-01 | Budget policies for all production workspaces | Critical | Budget policy assigned? |
| COST-02 | Quarterly cost optimization reviews via system tables | Required | `system.billing.usage` review? |
| COST-03 | Balance always-on vs triggered streaming workloads | Required | Cost/latency tradeoff documented? |
| REL-01 | Delta Lake time travel >= 7 days retention | Critical | `delta.logRetentionDuration` set? |
| REL-02 | Job retry with exponential backoff | Required | `max_retries` + `min_retry_interval_millis`? |
| REL-03 | Structured streaming with checkpointing | Critical | `checkpointLocation` on ZRS/GRS? |
| REL-04 | Autoscaling for variable workloads | Required | `autoscale` block present? |
| REL-05 | Auto-termination on all clusters | Required | `autotermination_minutes` > 0? |
| REL-06 | Cluster pools for faster recovery | Recommended | Pool configured for frequent configs? |
| REL-07 | Workspace backup procedures | Critical | Code in Git, bundles versioned? |
| REL-08 | DR testing quarterly | Required | Last DR test < 90 days ago? |
| REL-09 | Managed model serving for production ML | Required | Using Mosaic AI Model Serving? |
| REL-10 | Monitor and manage platform service limits | Recommended | Check system tables for limit proximity |
| REL-11 | Invest in capacity planning for production workloads | Recommended | Quarterly planning reviews |
| SC-01 | Serverless compute for all new workloads | Critical | Environment block, not new_cluster? |
| SC-02 | Serverless SQL Warehouses for all SQL | Critical | Warehouse type = SERVERLESS? |
| SC-03 | Serverless Jobs for notebooks and Python | Critical | No `job_clusters` in YAML? |
| SC-04 | Serverless DLT for all pipelines | Required | `serverless: true` on pipelines? |
| SC-05 | Use latest serverless environment version | Required | Latest `environment_version`? |
| SC-06 | Pin all custom dependencies with explicit versions | Critical | Pinned versions in requirements |
| SC-07 | Use workspace base environments for shared dependencies | Required | Shared base environment configured? |
| SC-08 | Never install PySpark on serverless compute | Critical | No PySpark in dependencies |
| SC-09 | Configure private package repositories for internal libs | Required | Admin-level repo configured? |
| CP-01 | Compute policies for classic clusters | Critical | Policy attached to cluster? |
| CP-02 | No unrestricted cluster creation | Critical | All users assigned policies? |
| CP-03 | Instance types limited by policy | Required | Policy restricts node types? |
| CP-04 | Auto-termination on interactive clusters | Required | Max idle <= 30 min? |
| CP-05 | Jobs compute for scheduled, All-Purpose for exploration | Critical | Correct compute type used? |
| CP-06 | Dependencies consistent between All-Purpose and Jobs | Required | Same library versions? |
| CP-07 | Standard access mode for most workloads | Required | `USER_ISOLATION` unless GPU/RDD/R? |
| CP-08 | Photon for complex transformations | Required | `runtime_engine: PHOTON`? |
| CP-09 | Right-size clusters by workload type | Required | Instance size matches workload? |

## Detailed Rules

### REL-01: Delta Lake Time Travel Retention
**Severity:** Critical | **Trigger:** When you see a Delta table without explicit retention settings

**Rule:** All Delta tables must retain at least 7 days of history for point-in-time recovery.
**Why:** Enables recovery from accidental deletes/updates without external backup systems; provides audit trail for compliance.

**Correct:**
```sql
ALTER TABLE catalog.schema.my_table
SET TBLPROPERTIES ('delta.logRetentionDuration' = '7 days');

-- Restore to previous version
RESTORE TABLE catalog.schema.my_table TO VERSION AS OF 42;
```

**Anti-Pattern:**
```sql
-- WRONG: Reducing retention below 7 days
ALTER TABLE catalog.schema.my_table
SET TBLPROPERTIES ('delta.logRetentionDuration' = '1 day');
```

---

### REL-02: Job Retry with Exponential Backoff
**Severity:** Required | **Trigger:** When you see a production job without retry configuration

**Rule:** Configure retry policies with exponential backoff for all production jobs; only retry transient failures.
**Why:** Automatic recovery from transient failures prevents manual intervention and avoids overwhelming downstream services.

**Correct:**
```yaml
tasks:
  - task_key: process_data
    retry_on_timeout: true
    max_retries: 3
    min_retry_interval_millis: 60000   # 1 min initial wait
    notebook_task:
      notebook_path: ../src/process.py
```

**Anti-Pattern:**
```yaml
# WRONG: No retry config; job fails permanently on transient errors
tasks:
  - task_key: process_data
    notebook_task:
      notebook_path: ../src/process.py
```

---

### REL-03: Streaming Checkpointing
**Severity:** Critical | **Trigger:** When you see a writeStream without checkpointLocation

**Rule:** All structured streaming jobs must use checkpointing with zone-redundant or geo-redundant storage.
**Why:** Enables exactly-once processing guarantees and automatic recovery from cluster failures.

**Correct:**
```python
checkpoint_path = "abfss://container@storage.dfs.core.windows.net/checkpoints/my_stream"

streaming_query = (
    spark.readStream.format("delta").table("bronze.events")
    .writeStream.format("delta")
    .option("checkpointLocation", checkpoint_path)
    .trigger(availableNow=True)
    .toTable("silver.events")
)
```

**Anti-Pattern:**
```python
# WRONG: No checkpoint - no recovery, no exactly-once guarantee
spark.readStream.format("delta").table("bronze.events") \
    .writeStream.format("delta").toTable("silver.events")
```

---

### REL-04: Cluster Autoscaling
**Severity:** Required | **Trigger:** When you see fixed-size clusters for variable workloads

**Rule:** Enable autoscaling for variable workloads; use fixed sizing only for streaming with steady load or ML training.
**Why:** Handles demand fluctuations automatically, prevents under-provisioning during peak and over-provisioning during lulls.

**Correct:**
```yaml
new_cluster:
  autoscale:
    min_workers: 2
    max_workers: 10
```

**Anti-Pattern:**
```yaml
# WRONG: Fixed size for variable batch ETL wastes resources
new_cluster:
  num_workers: 10   # Always 10, even when idle
```

---

### REL-05: Auto-Termination
**Severity:** Required | **Trigger:** When you see a cluster without autotermination_minutes

**Rule:** Configure auto-termination on all clusters (dev: 15 min, staging: 30 min, prod batch: 60 min).
**Why:** Prevents idle cluster costs (the top source of cloud waste) and forces regular security patch refresh.

---

### REL-06: Cluster Pools
**Severity:** Recommended | **Trigger:** When cluster startup time exceeds 5 minutes for frequent configs

**Rule:** Use cluster pools for frequently used configurations to reduce startup from 5-10 min to under 60 seconds.
**Why:** Ensures instance availability during capacity constraints; no DBU charges for idle pool instances.

**Correct:**
```yaml
resources:
  cluster_pools:
    data_engineering_pool:
      pool_name: "[${bundle.target}] DE Pool"
      node_type_id: "i3.xlarge"
      min_idle_instances: 2
      max_capacity: 20
      idle_instance_autotermination_minutes: 60
```

---

### REL-07: Workspace Backup
**Severity:** Critical | **Trigger:** When workspace assets are not version-controlled

**Rule:** All notebooks in Git repos, all job/cluster configs in Asset Bundles, secrets in external vault.
**Why:** Enables rapid recovery from workspace corruption and supports disaster recovery requirements.

---

### REL-08: DR Testing
**Severity:** Required | **Trigger:** When last DR test was more than 90 days ago

**Rule:** Test disaster recovery procedures quarterly with documented runbook.
**Why:** Untested DR procedures fail when needed most; regular testing validates RTO/RPO targets (Tier 1: <1h RTO, <15m RPO).

---

### REL-09: Managed Model Serving
**Severity:** Required | **Trigger:** When deploying ML models to production

**Rule:** Use Databricks Model Serving (Mosaic AI) for production ML; avoid self-managed serving infrastructure.
**Why:** Auto-scaling, built-in monitoring via inference tables, HA with automatic failover, UC governance integration.

**Correct:**
```python
endpoint_config = {
    "served_entities": [{
        "entity_name": "catalog.schema.my_model",
        "entity_version": "1",
        "scale_to_zero_enabled": True,
        "workload_size": "Small"
    }]
}
```

---

### REL-10: Monitor and Manage Platform Service Limits
**Severity:** Recommended | **Trigger:** When production workloads approach platform quotas or experience throttling

**Rule:** Proactively monitor platform service limits (API rate limits, workspace object counts, cluster quotas) using system tables and alerts; request limit increases before hitting ceilings.
**Why:** Hitting undocumented or unmonitored service limits causes unexpected production failures that are difficult to diagnose under pressure.

**Correct:**
```sql
-- Monitor workspace object counts against known limits
SELECT object_type, COUNT(*) AS object_count,
       CASE
         WHEN COUNT(*) > 0.8 * limit THEN 'WARNING'
         WHEN COUNT(*) > 0.9 * limit THEN 'CRITICAL'
         ELSE 'OK'
       END AS status
FROM system.information_schema.tables
GROUP BY object_type;
```

**Anti-Pattern:**
```
# WRONG: No monitoring -- discover limits only when production breaks
# "Why did all our jobs fail at 2 AM?" -- you hit the concurrent runs limit
```

---

### REL-11: Capacity Planning for Production Workloads
**Severity:** Recommended | **Trigger:** When production workloads lack documented capacity plans

**Rule:** Conduct quarterly capacity planning reviews for all production workloads; document expected growth, resource requirements, and scaling triggers.
**Why:** Reactive scaling leads to outages during demand spikes; proactive planning ensures resources are available when needed and budgets are predictable.

**Quarterly Review Checklist:**

| Area | Review Item |
|------|-------------|
| Compute | Peak vs. average utilization, right-sizing opportunities |
| Storage | Growth rate, retention policy compliance |
| Throughput | Pipeline SLAs vs. actual processing times |
| Cost | Budget vs. actual, forecast for next quarter |

**Correct:**
```
# Document capacity plan per workload:
# 1. Current resource usage (compute, storage, throughput)
# 2. Growth forecast (data volume, user count, query load)
# 3. Scaling triggers (when to add capacity)
# 4. Budget impact and approval
```

**Anti-Pattern:**
```
# WRONG: No capacity plan -- scramble for resources during Black Friday
# "We need 10x compute by tomorrow" -- not possible without planning
```

---

### SC-01: Serverless Compute First
**Severity:** Critical | **Trigger:** When you see `new_cluster` blocks for supported workloads

**Rule:** Serverless compute is mandatory for all new workloads where supported; classic clusters require documented justification.
**Why:** Zero config overhead, automatic scaling, no idle costs, always latest optimizations.

**Correct:**
```yaml
environments:
  - environment_key: default
    spec:
      environment_version: "4"
      dependencies:
        - pandas==2.0.3
```

**Anti-Pattern:**
```yaml
# WRONG: Classic cluster for a standard notebook job
new_cluster:
  spark_version: "14.3.x-scala2.12"
  num_workers: 4
```

---

### CP-07: Standard Access Mode
**Severity:** Required | **Trigger:** When you see SINGLE_USER mode without GPU/RDD/R justification

**Rule:** Use standard (USER_ISOLATION) access mode for most workloads; dedicated only for GPU, RDD APIs, R, or container services.
**Why:** Multi-user isolation, cost-effective resource sharing, enforces Unity Catalog governance.

---

### CP-01: Compute Policies
**Severity:** Critical | **Trigger:** When classic clusters are created without a policy

**Rule:** All classic clusters must be created through approved compute policies; unrestricted creation is prohibited.
**Why:** Enforces cost/security guardrails and standardizes configurations across teams.

---

### CP-08: Photon Enabled
**Severity:** Required | **Trigger:** When you see complex joins or large aggregations without Photon

**Rule:** Enable Photon for workloads with complex joins, large aggregations, or frequent disk access.
**Why:** Native vectorized execution yields significant performance improvement; combined with AQE (default on DBR 14.3+).

**Correct:**
```yaml
new_cluster:
  spark_version: "14.3.x-photon-scala2.12"
  runtime_engine: PHOTON
```

---

### CP-09: Right-Sizing
**Severity:** Required | **Trigger:** When cluster size does not match workload characteristics

**Rule:** Size clusters based on workload: single-node for analysis, 2-4 workers for ETL, fixed for streaming/ML training.
**Why:** Over-provisioning wastes cost; under-provisioning causes failures and slow performance.

---

### CP-04: Auto-Termination on Interactive Clusters
**Severity:** Required | **Trigger:** When interactive clusters lack autotermination_minutes

**Rule:** All interactive clusters: max 30 min idle (dev), 10 min idle (prod). Enforced via compute policies.
**Why:** Idle clusters are the number one source of cloud waste.

**Correct:**
```json
{
  "autotermination_minutes": {
    "type": "range",
    "maxValue": 30,
    "defaultValue": 10
  }
}
```

---

### SC-06: Pin All Custom Dependencies
**Severity:** Critical | **Trigger:** Adding dependencies to serverless environments

**Rule:** All custom dependencies in serverless environments must be pinned to explicit versions. No unpinned specifiers for production.
**Why:** Unpinned dependencies change between runs, causing silent failures and breaking reproducibility.

**Correct:**
```
pandas==2.0.3
pyarrow==14.0.2
scikit-learn==1.3.2
```

**Anti-Pattern:**
```
pandas          # Any version
scikit-learn>=1.0  # Range specifier
```

---

### SC-08: Never Install PySpark on Serverless
**Severity:** Critical | **Trigger:** Installing libraries on serverless compute

**Rule:** Never install PySpark or PySpark-dependent libraries on serverless. The managed runtime provides Spark.
**Why:** Installing PySpark conflicts with the managed runtime and terminates the session immediately.

**Known problematic packages:** pyspark, delta-spark, databricks-connect (standalone)
**Recovery:** Remove offending package, click Apply > Reset to defaults, restart session.

---

## Checklist

### Platform & Cost
- [ ] PA-01: No production data on DBFS root — UC volumes or managed tables only
- [ ] PA-02: System tables enabled for platform observability
- [ ] PA-03: Workspace isolation by environment and security boundary
- [ ] PA-04: Lakehouse Federation for external data access (CREATE FOREIGN CATALOG)
- [ ] PA-05: Certified partner integrations used where available
- [ ] COST-01: Budget policies assigned to all production workspaces
- [ ] COST-02: Quarterly cost optimization reviews conducted via system tables
- [ ] COST-03: Streaming workloads assessed for always-on vs triggered mode

### Reliability & DR
- [ ] REL-01: Delta time travel >= 7 days retention set
- [ ] REL-02: Job retry + backoff configured for production jobs
- [ ] REL-03: Streaming checkpoints on ZRS/GRS storage
- [ ] REL-04: Autoscaling enabled for variable workloads
- [ ] REL-05: Auto-termination on all clusters
- [ ] REL-06: Cluster pools for frequently used configs
- [ ] REL-07: All code in Git, configs in Asset Bundles
- [ ] REL-08: DR runbook tested within last 90 days
- [ ] REL-09: Managed Model Serving for production ML
- [ ] REL-10: Platform service limits monitored with alerts
- [ ] REL-11: Quarterly capacity planning reviews conducted

### Serverless Compute
- [ ] SC-01: Serverless compute for all new workloads
- [ ] SC-02: Serverless SQL Warehouses for all SQL workloads
- [ ] SC-03: Serverless Jobs for notebooks and Python
- [ ] SC-04: Serverless DLT for all pipelines
- [ ] SC-05: Latest serverless environment version used
- [ ] SC-06: All dependencies pinned with explicit versions
- [ ] SC-07: Workspace base environments for shared dependencies
- [ ] SC-08: No PySpark or PySpark-dependent libraries installed
- [ ] SC-09: Private package repositories configured at workspace level

### Cluster Policies
- [ ] CP-01: Compute policies enforced for classic clusters
- [ ] CP-02: No unrestricted cluster creation
- [ ] CP-03: Instance types limited by policy
- [ ] CP-04: Interactive clusters auto-terminate <= 30 min
- [ ] CP-05: Jobs compute for scheduled work, All-Purpose for exploration
- [ ] CP-06: Dependencies consistent between All-Purpose and Jobs compute
- [ ] CP-07: Standard access mode unless GPU/RDD/R required
- [ ] CP-08: Photon enabled for complex transformations
- [ ] CP-09: Cluster size matches workload type
