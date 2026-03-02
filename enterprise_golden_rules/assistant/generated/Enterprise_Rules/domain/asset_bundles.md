# Asset Bundles & Python Development Golden Rules
**Rules:** IN-01..13, PY-01..04 | **Count:** 17 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| IN-01 | Serverless compute for all jobs | Required | No `job_clusters:` or classic compute in YAML |
| IN-02 | Environment-level dependencies (not task) | Critical | `environments:` block at job level, not `libraries:` on tasks |
| IN-03 | Use `notebook_task` (never `python_task`) | Critical | No `python_task:` keys in any YAML |
| IN-04 | Use `dbutils.widgets.get()` for parameters | Critical | No `argparse` in notebook entry points |
| IN-05 | Hierarchical job architecture (atomic/composite/orchestrator) | Required | Jobs tagged with `job_level` |
| IN-06 | Notebooks in exactly ONE atomic job | Critical | Each `.py` entry point referenced once |
| IN-07 | Use `run_job_task` for job references | Critical | Composite/orchestrator tasks use `run_job_task:` |
| IN-08 | Include `[${bundle.target}]` prefix in job names | Required | All job `name:` fields start with prefix |
| IN-09 | Use `${var.name}` for variable references | Required | No `${catalog}` without `var.` prefix |
| IN-10 | Path resolution relative to YAML file location | Required | `../src/` or `../../src/` depending on nesting |
| IN-11 | Use `mode: development` / `mode: production` on all targets | Critical | Every target has explicit `mode:` |
| IN-12 | Set `run_as` to service principal for staging/prod | Critical | No personal credentials in non-dev targets |
| IN-13 | Define top-level `permissions` on all bundles | Required | `permissions:` block at bundle level |
| PY-01 | Use dbutils.widgets.get() for parameters | Critical | No argparse in notebook entry points |
| PY-02 | Pure Python files for imports (no notebook header) | Critical | No `# Databricks notebook source` in shared modules |
| PY-03 | `sys.path` setup for Asset Bundle imports | Critical | Notebook entry points configure path before imports |
| PY-04 | No Databricks notebook source in importable modules | Critical | No notebook header in shared .py files |

## Detailed Rules

### IN-01: Serverless Compute for All Jobs
**Severity:** Required | **Trigger:** When defining job compute in `databricks.yml`

**Rule:** All workflow jobs must use serverless compute; never define `job_clusters` or classic cluster specs.
**Why:** Serverless eliminates infrastructure management, auto-scales to zero, and provides instant startup with no cluster configuration drift.

**Correct:**
```yaml
resources:
  jobs:
    my_job:
      name: "[${bundle.target}] My Job"
      environments:
        - environment_key: "default"
          spec:
            environment_version: "4"
            dependencies:
              - "pandas==2.0.3"
      tasks:
        - task_key: etl_step
          environment_key: default
          notebook_task:
            notebook_path: ../src/etl.py
```

**Anti-Pattern:**
```yaml
# WRONG: Classic compute with job clusters
resources:
  jobs:
    my_job:
      job_clusters:
        - job_cluster_key: shared
          new_cluster:
            spark_version: "14.3.x-scala2.12"
            num_workers: 4
```

---

### IN-02: Environment-Level Dependencies
**Severity:** Critical | **Trigger:** When adding Python packages to a job

**Rule:** Declare all pip dependencies in the job-level `environments:` block, never as task-level `libraries:`.
**Why:** Task-level libraries fail on serverless compute and create inconsistent dependency resolution across tasks.

**Correct:**
```yaml
environments:
  - environment_key: "default"
    spec:
      environment_version: "4"
      dependencies:
        - "pandas==2.0.3"
        - "requests>=2.28"
```

**Anti-Pattern:**
```yaml
# WRONG: Task-level libraries
tasks:
  - task_key: my_task
    libraries:
      - pypi: { package: pandas }
```

---

### IN-03: Use `notebook_task` Only
**Severity:** Critical | **Trigger:** When defining task types in YAML

**Rule:** Always use `notebook_task` for Python execution; `python_task` does not exist in the Databricks Jobs API.
**Why:** Using `python_task` causes `Invalid task type` errors at deploy time. All Python files run as notebooks via `notebook_task`.

**Correct:**
```yaml
tasks:
  - task_key: process
    notebook_task:
      notebook_path: ../src/process.py
      base_parameters:
        catalog: ${var.catalog}
```

**Anti-Pattern:**
```yaml
# WRONG: python_task is not a valid task type
tasks:
  - task_key: process
    python_task:
      python_file: ../src/process.py
```

---

### IN-04: Use `dbutils.widgets.get()` for Parameters
**Severity:** Critical | **Trigger:** When reading parameters in a notebook entry point

**Rule:** Use `dbutils.widgets.get()` to receive job parameters; never use `argparse` in notebook-executed code.
**Why:** `argparse` calls `sys.argv` which is empty in `notebook_task` execution, causing `arguments are required` errors.

**Correct:**
```python
def get_parameters():
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    print(f"Parameters: catalog={catalog}, schema={schema}")
    return catalog, schema
```

**Anti-Pattern:**
```python
# WRONG: argparse fails in notebook_task
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--catalog", required=True)
args = parser.parse_args()  # ERROR: arguments are required
```

---

### IN-05: Hierarchical Job Architecture
**Severity:** Required | **Trigger:** When building multi-step workflows

**Rule:** Structure jobs in three layers: atomic (notebook refs), composite (job refs via `run_job_task`), and orchestrators (composite refs).
**Why:** Hierarchical design enables independent testing, reuse of atomic jobs across composites, and clear operational boundaries.

**Correct:**
```yaml
# Layer 1 - Atomic: references a notebook
resources:
  jobs:
    tvf_deploy:
      name: "[${bundle.target}] TVF Deploy"
      tasks:
        - task_key: deploy
          notebook_task:
            notebook_path: ../../src/deploy_tvfs.py
      tags:
        job_level: atomic

# Layer 2 - Composite: references atomic jobs
    semantic_setup:
      name: "[${bundle.target}] Semantic Setup"
      tasks:
        - task_key: deploy_tvfs
          run_job_task:
            job_id: ${resources.jobs.tvf_deploy.id}
      tags:
        job_level: composite
```

---

### IN-07: Use `run_job_task` for Job References
**Severity:** Critical | **Trigger:** When a composite or orchestrator job needs to call another job

**Rule:** Reference other jobs using `run_job_task` with `${resources.jobs.<name>.id}`; never duplicate notebook references across jobs.
**Why:** Duplicating notebook refs means a notebook appears in multiple jobs, breaking the single-ownership principle and making debugging ambiguous.

**Correct:**
```yaml
tasks:
  - task_key: run_gold_setup
    run_job_task:
      job_id: ${resources.jobs.gold_setup_job.id}
```

**Anti-Pattern:**
```yaml
# WRONG: Duplicating notebook across jobs
# Job A and Job B both reference the same notebook
tasks:
  - task_key: setup
    notebook_task:
      notebook_path: ../src/gold_setup.py  # Also in another job!
```

---

### IN-11: Deployment Modes
**Severity:** Critical | **Trigger:** When defining targets in `databricks.yml`

**Rule:** Every target must declare `mode: development` or `mode: production`. Never deploy without a mode.
**Why:** Modes control resource naming, schedule behavior, DLT pipeline state, and compute overrides. Without a mode, resources may collide across environments or run with unintended settings.

**Correct:**
```yaml
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: ${var.dev_host}

  prod:
    mode: production
    workspace:
      host: ${var.prod_host}
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
```

**Development mode automatically:**
- Prepends `[dev ${workspace.current_user.short_name}]` to resource names
- Pauses all schedules and triggers
- Sets DLT pipelines to `development: true`
- Enables concurrent runs

**Production mode automatically:**
- Validates DLT pipelines are `development: false`
- Validates Git branch matches target (if configured)
- Prevents cluster override via `--compute-id`

**Custom Presets** (for staging or non-standard environments):
```yaml
targets:
  staging:
    presets:
      name_prefix: "staging_"
      pipelines_development: false
      trigger_pause_status: PAUSED
      jobs_max_concurrent_runs: 1
      tags:
        environment: staging
```

---

### IN-12: Run Identity (`run_as`)
**Severity:** Critical | **Trigger:** When configuring staging or production targets

**Rule:** Set `run_as` to a service principal for all non-dev targets. Separate the deploy identity from the run identity.
**Why:** Personal credentials in production create single points of failure and audit gaps. Service principals provide traceable, role-based execution.

**Top-Level (default for all targets):**
```yaml
run_as:
  service_principal_name: ${var.prod_sp_id}
```

**Per-Target Override:**
```yaml
targets:
  dev:
    mode: development
    run_as:
      user_name: ${workspace.current_user.userName}

  prod:
    mode: production
    run_as:
      service_principal_name: ${var.prod_sp_id}
```

**Per-Job Override (sensitive workloads):**
```yaml
resources:
  jobs:
    sensitive_job:
      run_as:
        service_principal_name: ${var.restricted_sp_id}
```

> **Note:** `run_as` is not supported for model serving endpoints.

---

### IN-13: Permissions
**Severity:** Required | **Trigger:** When defining any bundle

**Rule:** Define a top-level `permissions` block on all bundles to control who can view, run, and manage resources.
**Why:** Without explicit permissions, bundle resources inherit workspace defaults, which may be too open or too restrictive.

**Top-Level Permissions (recommended):**
```yaml
permissions:
  - group_name: data-engineering
    level: CAN_MANAGE
  - group_name: data-analysts
    level: CAN_VIEW
  - service_principal_name: ${var.prod_sp_id}
    level: CAN_MANAGE
```

Allowed levels: `CAN_VIEW`, `CAN_MANAGE`, `CAN_RUN`.

**Resource-Level Permissions (fine-grained):**
```yaml
resources:
  jobs:
    sensitive_job:
      permissions:
        - group_name: restricted-team
          level: CAN_MANAGE
        - group_name: data-analysts
          level: CAN_VIEW
```

**Precedence Order:**
1. Resource permissions within target
2. Target-level permissions
3. Resource permissions in bundle
4. Top-level bundle permissions

> **Note:** Permissions for a user/group/SP cannot be defined in both top-level and resource-level mappings.

---

### PY-02: Pure Python Files for Imports
**Severity:** Critical | **Trigger:** When creating shared utility modules

**Rule:** Importable Python modules must be pure Python files without the `# Databricks notebook source` header.
**Why:** Files with the notebook header cannot be imported in serverless compute, causing `ModuleNotFoundError`.

**Correct:**
```python
# utils.py - Pure Python (NO header)
"""Utility functions for data processing."""

def helper():
    """Helper function that can be imported."""
    pass
```

**Anti-Pattern:**
```python
# WRONG: Notebook header breaks imports
# Databricks notebook source

def helper():
    pass
```

---

### PY-03: sys.path Setup for Asset Bundle Imports
**Severity:** Critical | **Trigger:** When a notebook entry point needs to import from project modules

**Rule:** Add `sys.path` setup at the top of notebook entry points to resolve Asset Bundle workspace paths before importing project modules.
**Why:** Asset Bundles deploy code to workspace paths that are not on the default `sys.path`, causing `ModuleNotFoundError` without explicit path configuration.

**Correct:**
```python
# Databricks notebook source
import sys
from pathlib import Path

def setup_path():
    notebook_path = dbutils.notebook.entry_point \
        .getDbutils().notebook().getContext() \
        .notebookPath().get()
    workspace_base = "/Workspace" + "/".join(
        notebook_path.split("/")[:-2]
    )
    if workspace_base not in sys.path:
        sys.path.insert(0, workspace_base)
    return workspace_base

workspace_path = setup_path()
from my_project.utils import helper  # Now works
```

---

### IN-08: Bundle Target Prefix
**Severity:** Required | **Trigger:** When naming any job or pipeline resource

**Rule:** All resource names must start with `[${bundle.target}]` to distinguish dev/staging/prod deployments.
**Why:** Without the prefix, identically-named jobs across environments collide in the workspace, making operational triage impossible.

**Correct:**
```yaml
name: "[${bundle.target}] Silver Pipeline"
```

**Anti-Pattern:**
```yaml
name: "Silver Pipeline"  # No environment distinction
```

---

## Variables

Declare custom variables for environment-specific values. Always define defaults.

### Variable Declaration
```yaml
variables:
  catalog:
    description: Unity Catalog name
    default: dev_catalog
  schema:
    description: Target schema
    default: default
  sp_id:
    description: Service principal application ID
```

### Per-Target Values
```yaml
targets:
  dev:
    variables:
      catalog: dev_catalog
  prod:
    variables:
      catalog: prod_catalog
      sp_id: "68ed9cd5-8923-4851-x0c1-c7536c67ff99"
```

### Complex Variables
```yaml
variables:
  notification_config:
    type: complex
    default:
      on_failure:
        - team-alerts@company.com
      on_success:
        - team-reports@company.com
```

### Variable Lookups
```yaml
variables:
  warehouse_id:
    lookup:
      warehouse: "Shared SQL Warehouse"
```

### Precedence Order
1. `--var="key=value"` CLI option
2. `BUNDLE_VAR_` environment variables
3. `.databricks/bundle/<target>/variable-overrides.json`
4. Target-level `variables` mapping
5. Top-level `variables` default

---

## Library Dependencies

### Environment Block (Serverless)
```yaml
environments:
  - environment_key: "default"
    spec:
      environment_version: "4"
      dependencies:
        - "pandas==2.0.3"
        - "scikit-learn>=1.3.0"
```

### Requirements File
```yaml
tasks:
  - task_key: my_task
    libraries:
      - requirements: ./requirements.txt
```

### Python Wheel Files
```yaml
tasks:
  - task_key: my_task
    libraries:
      - whl: ./dist/my_package-0.1.0-py3-none-any.whl
      - whl: /Volumes/main/default/libs/shared-0.2.0.whl
```

### PyPI Packages (Classic Compute)
```yaml
tasks:
  - task_key: my_task
    libraries:
      - pypi:
          package: numpy==1.25.2
```

---

## Supported Resource Types

| Resource | Description |
|----------|-------------|
| `jobs` | Jobs and tasks |
| `pipelines` | Lakeflow Spark Declarative Pipelines (DLT) |
| `schemas` | Unity Catalog schemas |
| `volumes` | Unity Catalog volumes |
| `clusters` | Compute clusters |
| `catalogs` | Unity Catalog catalogs |
| `dashboards` | AI/BI dashboards (Lakeview) |
| `registered_models` | Unity Catalog registered models |
| `model_serving_endpoints` | Model serving endpoints |
| `experiments` | MLflow experiments |
| `apps` | Databricks Apps |
| `sql_warehouses` | SQL warehouses |
| `secret_scopes` | Secret scopes |
| `quality_monitors` | Data quality monitors |

Reference: `${resources.<type>.<name>.<field>}`

---

## Complete Bundle Template

```yaml
bundle:
  name: my_data_pipeline

variables:
  catalog:
    description: Unity Catalog name
    default: dev_catalog
  schema:
    description: Target schema
    default: default

permissions:
  - group_name: data-engineering
    level: CAN_MANAGE
  - group_name: data-analysts
    level: CAN_VIEW

run_as:
  service_principal_name: ${var.sp_id}

targets:
  dev:
    mode: development
    default: true
    run_as:
      user_name: ${workspace.current_user.userName}
    variables:
      catalog: dev_catalog

  prod:
    mode: production
    workspace:
      root_path: /Shared/.bundle/${bundle.name}/${bundle.target}
    variables:
      catalog: prod_catalog

resources:
  jobs:
    transform_job:
      name: "[${bundle.target}] Transform Pipeline"

      environments:
        - environment_key: "default"
          spec:
            environment_version: "4"
            dependencies:
              - "pandas==2.0.3"

      tags:
        team: data-engineering
        cost_center: CC-1234
        environment: ${bundle.target}

      tasks:
        - task_key: transform
          environment_key: default
          notebook_task:
            notebook_path: ../src/transform.py
            base_parameters:
              catalog: ${var.catalog}
              schema: ${var.schema}
```

---

## Checklist

### Deployment & Identity
- [ ] IN-11: `mode: development` on dev target
- [ ] IN-11: `mode: production` on prod target
- [ ] IN-12: `run_as` set to service principal for staging/prod
- [ ] IN-13: Top-level `permissions` block defined
- [ ] Variables declared with defaults

### Job Configuration
- [ ] IN-01: No `job_clusters` or classic compute specs in YAML
- [ ] IN-02: Dependencies in `environments:` block, not task `libraries:`
- [ ] IN-03: All tasks use `notebook_task`, zero `python_task` references
- [ ] IN-04: Entry points use `dbutils.widgets.get()`, not `argparse`
- [ ] IN-05: Jobs tagged with `job_level`: atomic / composite / orchestrator
- [ ] IN-06: Each notebook `.py` file appears in exactly one atomic job
- [ ] IN-07: Composite and orchestrator jobs use only `run_job_task`
- [ ] IN-08: All job names start with `[${bundle.target}]`
- [ ] IN-09: Variable references use `${var.name}` (not `${name}`)
- [ ] IN-10: Paths resolve relative to YAML file location

### Python Development
- [ ] PY-01: Notebook entry points use dbutils.widgets.get() (not argparse)
- [ ] PY-02: Shared modules have no `# Databricks notebook source` header
- [ ] PY-03: Notebook entry points include `sys.path` setup before imports
- [ ] PY-04: No # Databricks notebook source header in importable modules

### Tags
- [ ] `team`, `cost_center`, `environment` tags on all jobs

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `arguments are required` | argparse | Use `dbutils.widgets.get()` |
| `Invalid task type` | python_task | Use `notebook_task` |
| `Variable not found` | Missing prefix | Use `${var.name}` |
| `run_as not supported` | model_serving_endpoint | Remove `run_as` from that resource |
| `Permission overlap` | Same identity in top-level + resource | Use one or the other, not both |
| `Git branch mismatch` | Production mode branch check | Deploy from correct branch or use `--force` |
