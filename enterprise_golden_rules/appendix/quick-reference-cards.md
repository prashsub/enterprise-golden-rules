# Quick Reference Cards

## One-Page Cheat Sheets for Daily Development

---

## Card 1: YAML-Driven Development

### The Principle
```
Source of Truth: gold_layer_design/yaml/{domain}/{table}.yaml
NOT: Hardcoded in Python | Generated from memory | Assumed from Silver
```

### Extract Schema Pattern
```python
import yaml
from pathlib import Path

def get_gold_schema(domain: str, table_name: str) -> dict:
    yaml_file = Path(f"gold_layer_design/yaml/{domain}/{table_name}.yaml")
    with open(yaml_file) as f:
        return yaml.safe_load(f)

# ALWAYS extract, NEVER generate
schema = get_gold_schema("billing", "fact_usage")
columns = [col['name'] for col in schema['columns']]
```

### Before Writing ANY SQL
1. ✅ Find the YAML file
2. ✅ List available columns
3. ✅ Verify column types
4. ❌ Don't assume column names
5. ❌ Don't generate from memory

---

## Card 2: Delta MERGE Deduplication

### The Rule
```
ALWAYS deduplicate BEFORE MERGE
Deduplication key MUST match MERGE key
```

### The Pattern
```python
from pyspark.sql.functions import col
from delta.tables import DeltaTable

# STEP 1: Read Silver
silver_raw = spark.table(silver_table)

# STEP 2: Deduplicate (CRITICAL!)
silver_df = (
    silver_raw
    .orderBy(col("processed_timestamp").desc())  # Latest first
    .dropDuplicates([business_key])  # Keep only latest
)

# STEP 3: MERGE
delta_gold = DeltaTable.forName(spark, gold_table)
delta_gold.alias("target").merge(
    silver_df.alias("source"),
    f"target.{business_key} = source.{business_key}"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

### If You See This Error
```
[DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE]
```
**Fix:** Add `orderBy().dropDuplicates()` before MERGE

---

## Card 3: Asset Bundle Jobs

### Serverless Template
```yaml
resources:
  jobs:
    my_job:
      name: "[${bundle.target}] My Job"
      
      # MANDATORY: Environment block
      environments:
        - environment_key: "default"
          spec:
            environment_version: "4"
      
      tasks:
        - task_key: my_task
          environment_key: default  # MANDATORY: Reference
          notebook_task:            # NOT python_task!
            notebook_path: ../src/my_script.py
            base_parameters:        # NOT parameters!
              catalog: ${var.catalog}
```

### Parameter Handling
```python
# ❌ WRONG: argparse
import argparse
args = parser.parse_args()  # FAILS!

# ✅ CORRECT: dbutils.widgets
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
```

### Path Resolution
| YAML Location | Path to src/ |
|---------------|--------------|
| `resources/*.yml` | `../src/` |
| `resources/layer/*.yml` | `../../src/` |

---

## Card 4: TVF Development

### Parameter Rules
```sql
-- Rule 1: STRING for dates (Genie can't do DATE)
start_date STRING COMMENT 'Start date (YYYY-MM-DD)'

-- Rule 2: Required params BEFORE optional
CREATE FUNCTION my_func(
    workspace STRING,                    -- Required (no DEFAULT)
    start_date STRING DEFAULT '2024-01-01'  -- Optional (has DEFAULT)
)

-- Rule 3: No LIMIT with parameter
-- ❌ WRONG: LIMIT limit_rows
-- ✅ CORRECT: WHERE rn <= CAST(limit_rows AS INT)
```

### Comment Format (v3.0)
```sql
COMMENT '
• PURPOSE: Get cost summary by workspace.
• BEST FOR: Total spend | Cost by workspace | Cost trends
• NOT FOR: Real-time alerts (use get_alerts TVF)
• RETURNS: PRE-AGGREGATED rows (workspace, total_cost, dbus)
• PARAMS: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
• SYNTAX: SELECT * FROM get_cost_summary(''2024-01-01'')
• NOTE: DO NOT wrap in TABLE(). DO NOT add GROUP BY.
'
```

---

## Card 5: Metric Views

### v1.1 YAML Structure
```yaml
version: "1.1"
# ❌ NO name field - name comes from filename!
comment: >
  PURPOSE: Cost analytics...
  BEST FOR: Total spend | Cost by SKU
  
source: ${catalog}.${gold_schema}.fact_usage

joins:
  - name: dim_workspace
    source: ${catalog}.${gold_schema}.dim_workspace
    'on': source.workspace_id = dim_workspace.workspace_id
    # Note: 'on' must be quoted

dimensions:
  - name: usage_date
    expr: source.usage_date
    comment: Date of usage
    
measures:
  - name: total_cost
    expr: SUM(source.list_cost)
    format:
      type: currency
```

### Unsupported Fields
| Field | Error | Action |
|-------|-------|--------|
| `name` | Unrecognized field | ❌ Don't include |
| `time_dimension` | Unrecognized field | ❌ Remove |
| `window_measures` | Unrecognized field | ❌ Remove |

### No Transitive Joins!
```yaml
# ❌ WRONG: dim1 → dim2
'on': dim_property.destination_id = dim_destination.destination_id

# ✅ CORRECT: source → dim only
'on': source.workspace_id = dim_workspace.workspace_id
```

---

## Card 6: Agent Development

### ResponsesAgent Pattern
```python
from mlflow.pyfunc import ResponsesAgent

class MyAgent(ResponsesAgent["MyAgent"]):
    def predict(self, context, model_input, params=None):
        messages = model_input.get("messages", [])
        thread_id = model_input.get("custom_inputs", {}).get("thread_id")
        
        response = self._process(messages)
        
        return {
            "content": response,
            "custom_outputs": {"thread_id": thread_id}
        }

# Log model - NO signature parameter!
mlflow.pyfunc.log_model(
    artifact_path="agent",
    python_model=MyAgent(),
    resources=get_mlflow_resources(),
    auth_policy=get_auth_policy()
)
```

### OBO Context Detection
```python
import os

def is_model_serving_context() -> bool:
    return any(os.environ.get(v) for v in [
        "IS_IN_DB_MODEL_SERVING_ENV",
        "DATABRICKS_SERVING_ENDPOINT"
    ])

def get_workspace_client():
    if is_model_serving_context():
        from databricks.sdk.credentials import ModelServingUserCredentials
        return WorkspaceClient(credentials_strategy=ModelServingUserCredentials())
    return WorkspaceClient()
```

### Resource Declaration
```python
from mlflow.models.resources import DatabricksGenieSpace, DatabricksSQLWarehouse

resources = [
    DatabricksGenieSpace(genie_space_id="..."),
    DatabricksSQLWarehouse(warehouse_id="...")
]
```

---

## Card 7: DLT Patterns

### Standard Table
```python
@dlt.table(
    name="silver_customers",
    comment="Silver layer with validation",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.enableRowTracking": "true",
        "layer": "silver"
    },
    cluster_by_auto=True
)
@dlt.expect_all_or_drop({
    "valid_id": "id IS NOT NULL",
    "valid_status": "status IN ('active', 'inactive')"
})
def silver_customers():
    return dlt.read_stream("bronze_customers")
```

### Expectation Types
| Type | Behavior |
|------|----------|
| `expect` | Log, keep record |
| `expect_or_drop` | Drop bad records |
| `expect_or_fail` | Fail pipeline |

### Pure Python Imports
```python
# ❌ File with notebook header - CAN'T IMPORT
# Databricks notebook source
def helper(): pass

# ✅ Pure Python file - CAN IMPORT
"""My module"""
def helper(): pass
```

---

## Card 8: Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Column 'X' not found` | Hardcoded column | Extract from YAML |
| `MERGE duplicate error` | No deduplication | Add `dropDuplicates()` |
| `argparse error` | Wrong param method | Use `dbutils.widgets.get()` |
| `python_task invalid` | Wrong task type | Use `notebook_task` |
| `Variable not found` | Missing `var.` | Use `${var.name}` |
| `Unrecognized field "name"` | YAML has name | Remove from YAML |
| `Permission denied (eval)` | Missing resources | Add to SystemAuthPolicy |
| `NOT_A_SCALAR_FUNCTION` | TABLE() wrapper | Call TVF directly |
| `ModuleNotFoundError` | Notebook header | Remove `# Databricks notebook source` |

---

## Card 9: Validation Commands

### Pre-Deployment
```bash
# Validate bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy -t dev

# Run job
databricks bundle run -t dev my_job
```

### Schema Validation Script
```bash
./scripts/validate_bundle.sh
```

### Quick Checks
```sql
-- Verify table exists
DESCRIBE EXTENDED catalog.schema.table_name

-- Check table properties
SHOW TBLPROPERTIES catalog.schema.table_name

-- Verify metric view type
DESCRIBE EXTENDED catalog.schema.metric_view_name
-- Should show: Type: METRIC_VIEW

-- Test TVF
SELECT * FROM catalog.schema.my_tvf('param') LIMIT 5
```

---

## Card 10: Reliability & DR

### Time Travel Recovery
```sql
-- Restore to version
RESTORE TABLE catalog.schema.my_table TO VERSION AS OF 42;

-- Restore to timestamp
RESTORE TABLE catalog.schema.my_table 
TO TIMESTAMP AS OF '2025-02-01 00:00:00';

-- Check history
DESCRIBE HISTORY catalog.schema.my_table;
```

### Job Retry Configuration
```yaml
tasks:
  - task_key: my_task
    retry_on_timeout: true
    max_retries: 3
    min_retry_interval_millis: 60000  # 1 min
```

### Streaming Checkpoints
```python
# Always use checkpointing
(spark.readStream
    .format("delta")
    .table("source")
    .writeStream
    .option("checkpointLocation", "s3://bucket/checkpoints/")
    .toTable("target"))
```

### DR Essentials
| Action | Command/Setting |
|--------|-----------------|
| Min retention | 7 days (`delta.logRetentionDuration`) |
| Auto-terminate | 15-60 min by environment |
| Cluster pools | Pre-warmed for fast recovery |

---

## Card 11: Network Security

### Quick Checks
```bash
# Check VNet config
az databricks workspace show --name myworkspace \
  --query "{vnet:parameters.customVirtualNetworkId}"

# Verify private endpoint
nslookup myworkspace.azuredatabricks.net
# Should resolve to 10.x.x.x (private IP)
```

### Security Essentials
| Control | Setting |
|---------|---------|
| VNet injection | Required for prod |
| Private Link | Control plane access |
| IP access lists | Known networks only |
| CMK | Customer-managed keys |
| Secure connectivity | No public IPs on clusters |

### Required Diagnostic Logs
| Category | Purpose |
|----------|---------|
| `accounts` | User/group changes |
| `clusters` | Cluster lifecycle |
| `jobs` | Job execution |
| `unityCatalog` | Data governance |
| `workspace` | Workspace events |

---

## Card 12: Naming & Comment Standards

### Naming Conventions
```
snake_case          → ✅ fact_daily_sales, dim_customer
camelCase           → ❌ factDailySales
PascalCase          → ❌ FactDailySales
kebab-case          → ❌ fact-daily-sales

Prefixes:
bronze_*, silver_*, gold_*  → Layer prefixes
dim_*, fact_*               → Entity type prefixes
```

### Table COMMENT Pattern
```sql
COMMENT ON TABLE gold.fact_orders IS
'Daily order facts at customer-product-day grain.
Business: Primary source for revenue reporting.
Technical: Composite PK, incremental merge, CDF enabled.';
```

### Column COMMENT Pattern
```sql
COMMENT ON COLUMN gold.dim_customer.customer_key IS
'Surrogate key for SCD Type 2 versioning.
Business: Used for fact table joins.
Technical: MD5 hash of customer_id + effective_from.';
```

### TVF COMMENT Pattern (v3.0)
```sql
COMMENT '
• PURPOSE: Get daily cost summary by workspace.
• BEST FOR: Spend by workspace | Cost by SKU | Trends
• NOT FOR: Real-time alerts (use get_cost_alerts)
• RETURNS: PRE-AGGREGATED rows (one per workspace-day)
• PARAMS: start_date (YYYY-MM-DD), end_date (optional)
• SYNTAX: SELECT * FROM get_daily_cost_summary(...)
• NOTE: DO NOT wrap in TABLE(). DO NOT GROUP BY.
'
```

---

## Card 13: Tagging Standards

### Workflow Tags (Jobs & Pipelines)
```yaml
tags:
  team: data-engineering        # Required
  cost_center: CC-1234          # Required
  environment: ${bundle.target} # Required
  project: customer-360         # Recommended
  layer: gold                   # Recommended
```

### Governed Tags (UC Securables)
| Level | Required Tags |
|-------|---------------|
| Catalog | `cost_center`, `business_unit` |
| Schema | `data_owner` |
| Table | `data_classification` (if confidential) |
| Column | `pii`, `pii_type` (if PII) |

```sql
ALTER CATALOG my_catalog SET TAGS ('cost_center' = 'CC-1234');
ALTER SCHEMA gold SET TAGS ('data_owner' = 'team@company.com');
ALTER TABLE gold.dim_customer 
ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');
```

### Serverless Budget Policies
- Navigate to **Settings** → **Compute** → **Serverless budget policies**
- Create policy with required tags: `team`, `cost_center`, `environment`
- Assign User/Manager permission to groups

### Query Tag Costs
```sql
SELECT custom_tags:team, custom_tags:cost_center, SUM(list_cost)
FROM system.billing.usage GROUP BY 1, 2;
```

---

## Card 14: Data Quality Standards

### DLT Expectations (Pipelines)
```python
@dlt.table(name="silver_orders")
@dlt.expect("valid_id", "order_id IS NOT NULL")        # Log warning
@dlt.expect_or_drop("valid_amt", "amount >= 0")        # Drop invalid
@dlt.expect_or_fail("valid_cust", "customer_id IS NOT NULL")  # Fail
def silver_orders():
    return dlt.read_stream("bronze_orders")
```

### DQX (Classic Spark Jobs)
```python
from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx.col_functions import is_not_null, is_not_less_than

dq_engine = DQEngine(spark)
checks = [is_not_null("order_id"), is_not_less_than("amount", limit=0)]
valid_df, invalid_df = dq_engine.apply_checks_by_metadata_and_split(df, checks)
```

### Lakehouse Monitor (Trends)
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
w.quality_monitors.create(
    table_name="catalog.gold.fact_sales",
    time_series=MonitorTimeSeries(timestamp_col="sales_date", granularities=["1 day"])
)
```

### Decision Tree
```
DLT Pipeline? → Use @dlt.expect decorators
Classic Job?  → Use DQX library
Gold Table?   → Add Lakehouse Monitor
```

---

## Card 15: Contact Quick Reference

| Need | Contact |
|------|---------|
| Quick questions | Slack: #data-platform-help |
| Architecture decisions | Platform Lead |
| Access requests | IT Ticket + Data Steward |
| Security issues | Security Team |
| Production incidents | On-Call (PagerDuty) |
| Rule exceptions | Data Steward → Platform Architect |
