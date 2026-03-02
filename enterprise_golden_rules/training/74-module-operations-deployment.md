# Module 4: Operations & Deployment

## Asset Bundles, Serverless Compute, and Monitoring

**Duration:** 8 hours  
**Prerequisites:** Modules 1-3 completed  
**Outcome:** Deploy and operate production data pipelines

---

## Learning Objectives

By the end of this module, you will be able to:

1. Create complete Databricks Asset Bundles
2. Configure serverless compute for jobs
3. Deploy pipelines to dev and production
4. Set up Lakehouse Monitoring
5. Troubleshoot common deployment issues

---

## Section 1: Asset Bundles Deep Dive (2 hours)

### Bundle Structure

```
project/
├── databricks.yml              # Main configuration
├── resources/
│   ├── schemas.yml             # Schema definitions
│   ├── bronze/
│   │   └── bronze_pipeline.yml
│   ├── silver/
│   │   └── silver_dlt_pipeline.yml
│   └── gold/
│       ├── gold_setup_job.yml
│       └── gold_merge_job.yml
└── src/
    ├── bronze/
    ├── silver/
    └── gold/
```

### Main Configuration (databricks.yml)

```yaml
bundle:
  name: enterprise_data_platform

variables:
  catalog:
    description: Unity Catalog name
    default: enterprise_catalog
  bronze_schema:
    description: Bronze layer schema
    default: bronze
  silver_schema:
    description: Silver layer schema
    default: silver
  gold_schema:
    description: Gold layer schema
    default: gold
  warehouse_id:
    description: SQL Warehouse ID
    default: "abc123def456"

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: dev_catalog
  
  staging:
    mode: development
    variables:
      catalog: staging_catalog
  
  prod:
    mode: production
    variables:
      catalog: prod_catalog

include:
  - resources/*.yml
  - resources/bronze/*.yml
  - resources/silver/*.yml
  - resources/gold/*.yml
```

### Schema Definition (resources/schemas.yml)

```yaml
resources:
  schemas:
    bronze_schema:
      name: ${var.bronze_schema}
      catalog_name: ${var.catalog}
      comment: "Bronze layer - raw data ingestion"
      properties:
        delta.autoOptimize.optimizeWrite: "true"
        delta.autoOptimize.autoCompact: "true"
        layer: bronze
    
    silver_schema:
      name: ${var.silver_schema}
      catalog_name: ${var.catalog}
      comment: "Silver layer - cleaned and validated data"
      properties:
        delta.autoOptimize.optimizeWrite: "true"
        delta.autoOptimize.autoCompact: "true"
        layer: silver
    
    gold_schema:
      name: ${var.gold_schema}
      catalog_name: ${var.catalog}
      comment: "Gold layer - business-ready data"
      properties:
        delta.autoOptimize.optimizeWrite: "true"
        delta.autoOptimize.autoCompact: "true"
        layer: gold
```

### Serverless Job Pattern

```yaml
# resources/gold/gold_merge_job.yml
resources:
  jobs:
    gold_merge_job:
      name: "[${bundle.target}] Gold Layer MERGE"
      
      # MANDATORY: Serverless environment
      environments:
        - environment_key: "default"
          spec:
            environment_version: "4"
            dependencies:
              - "pyyaml>=6.0"
      
      # Parameters
      parameters:
        - name: catalog
          default: ${var.catalog}
        - name: silver_schema
          default: ${var.silver_schema}
        - name: gold_schema
          default: ${var.gold_schema}
      
      # Tasks
      tasks:
        - task_key: merge_dimensions
          environment_key: default
          notebook_task:
            notebook_path: ../../src/gold/merge_dimensions.py
            base_parameters:
              catalog: ${var.catalog}
              silver_schema: ${var.silver_schema}
              gold_schema: ${var.gold_schema}
        
        - task_key: merge_facts
          depends_on:
            - task_key: merge_dimensions
          environment_key: default
          notebook_task:
            notebook_path: ../../src/gold/merge_facts.py
            base_parameters:
              catalog: ${var.catalog}
              silver_schema: ${var.silver_schema}
              gold_schema: ${var.gold_schema}
      
      # Schedule (PAUSED in dev)
      schedule:
        quartz_cron_expression: "0 0 2 * * ?"
        timezone_id: "America/New_York"
        pause_status: PAUSED
      
      # Notifications
      email_notifications:
        on_failure:
          - data-team@company.com
      
      # Timeout
      timeout_seconds: 7200
      
      # Tags
      tags:
        environment: ${bundle.target}
        project: enterprise_data_platform
        layer: gold
```

### DLT Pipeline Pattern

```yaml
# resources/silver/silver_dlt_pipeline.yml
resources:
  pipelines:
    silver_dlt_pipeline:
      name: "[${bundle.target}] Silver Layer DLT"
      
      # Unity Catalog
      catalog: ${var.catalog}
      schema: ${var.silver_schema}
      
      # Root path for pipeline
      root_path: ../../src/silver
      
      # Libraries
      libraries:
        - notebook:
            path: ../../src/silver/silver_customers.py
        - notebook:
            path: ../../src/silver/silver_orders.py
      
      # Configuration
      configuration:
        catalog: ${var.catalog}
        bronze_schema: ${var.bronze_schema}
        silver_schema: ${var.silver_schema}
      
      # Compute
      serverless: true
      photon: true
      channel: CURRENT
      continuous: false
      development: true
      edition: ADVANCED
      
      # Notifications
      notifications:
        - alerts:
            - on-update-failure
            - on-flow-failure
          email_recipients:
            - data-team@company.com
```

### Hands-On Lab 4.1: Create Asset Bundle

```bash
# 1. Initialize bundle structure
mkdir -p my_project/resources/{bronze,silver,gold}
mkdir -p my_project/src/{bronze,silver,gold}

# 2. Create databricks.yml
cat > my_project/databricks.yml << 'EOF'
bundle:
  name: my_data_platform

variables:
  catalog:
    default: my_catalog
  bronze_schema:
    default: bronze
  silver_schema:
    default: silver
  gold_schema:
    default: gold

targets:
  dev:
    mode: development
    default: true
  prod:
    mode: production

include:
  - resources/*.yml
  - resources/bronze/*.yml
  - resources/silver/*.yml
  - resources/gold/*.yml
EOF

# 3. Validate bundle
cd my_project
databricks bundle validate
```

---

## Section 2: Serverless Compute Configuration (1 hour)

### Environment Specification

```yaml
# Shared environment for all tasks
environments:
  - environment_key: "default"
    spec:
      environment_version: "4"
      dependencies:
        - "pyyaml>=6.0"
        - "pandas>=2.0"
        - "requests>=2.28"
```

### Task Reference Pattern

```yaml
tasks:
  - task_key: task_1
    environment_key: default  # Reference shared environment
    notebook_task:
      notebook_path: ../src/script1.py
      base_parameters:
        param1: value1
  
  - task_key: task_2
    environment_key: default  # Same environment
    depends_on:
      - task_key: task_1
    notebook_task:
      notebook_path: ../src/script2.py
```

### Parameter Passing (Critical)

**ALWAYS use `dbutils.widgets.get()` in notebooks:**

```python
# Databricks notebook source

def get_parameters():
    """Get parameters from job configuration."""
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    
    print(f"Catalog: {catalog}")
    print(f"Schema: {schema}")
    
    return catalog, schema

def main():
    catalog, schema = get_parameters()
    
    # Your logic here
    spark = SparkSession.builder.getOrCreate()
    # ...

if __name__ == "__main__":
    main()
```

**Never use `argparse` in Databricks notebooks!**

---

## Section 3: Deployment Workflows (2 hours)

### Development Workflow

```bash
# 1. Validate configuration
databricks bundle validate -t dev

# 2. Deploy to dev
databricks bundle deploy -t dev

# 3. Run a specific job
databricks bundle run -t dev gold_merge_job

# 4. Check job status
databricks jobs list --output JSON | jq '.jobs[] | select(.name | contains("[dev]"))'
```

### Production Deployment

```bash
# 1. Create PR with changes
git checkout -b feature/new-pipeline
git add .
git commit -m "Add new pipeline"
git push origin feature/new-pipeline

# 2. After PR approval, deploy to prod
databricks bundle deploy -t prod

# 3. Enable scheduled jobs
databricks jobs update --job-id <JOB_ID> --json '{"schedule": {"pause_status": "UNPAUSED"}}'
```

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy Data Platform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Databricks CLI
        uses: databricks/setup-cli@main
      
      - name: Validate Bundle
        run: databricks bundle validate -t dev
  
  deploy-dev:
    needs: validate
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Dev
        run: databricks bundle deploy -t dev
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
  
  deploy-prod:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Prod
        run: databricks bundle deploy -t prod
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
```

### Hands-On Lab 4.3: Deploy Pipeline

```bash
# Complete deployment workflow

# 1. Authenticate
databricks auth login --host https://your-workspace.cloud.databricks.com --profile dev

# 2. Validate
databricks bundle validate -t dev

# 3. Deploy
databricks bundle deploy -t dev

# 4. List deployed jobs
databricks bundle summary -t dev

# 5. Run setup job
databricks bundle run -t dev gold_setup_job

# 6. Check results
databricks jobs get-run --run-id <RUN_ID>

# 7. Cleanup (optional)
databricks bundle destroy -t dev
```

---

## Section 4: Monitoring & Alerting (2 hours)

### Lakehouse Monitoring Setup

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import MonitorTimeSeries

def create_table_monitor(
    table_name: str,
    timestamp_col: str,
    granularities: list = ["1 day"]
):
    """Create Lakehouse Monitor for a table."""
    
    w = WorkspaceClient()
    
    monitor = w.quality_monitors.create(
        table_name=table_name,
        assets_dir=f"/Shared/lakehouse_monitoring/{table_name}",
        output_schema_name=f"{table_name}_monitoring",
        time_series=MonitorTimeSeries(
            timestamp_col=timestamp_col,
            granularities=granularities
        ),
        schedule=MonitorCronSchedule(
            quartz_cron_expression="0 0 6 * * ?",
            timezone_id="UTC"
        )
    )
    
    print(f"✓ Created monitor for {table_name}")
    return monitor
```

### Custom Metrics

```python
from databricks.sdk.service.catalog import MonitorMetric, MonitorMetricType

custom_metrics = [
    MonitorMetric(
        type=MonitorMetricType.AGGREGATE,
        name="total_revenue",
        definition="SUM(net_revenue)",
        input_columns=["net_revenue"],
        output_data_type="DOUBLE"
    ),
    MonitorMetric(
        type=MonitorMetricType.AGGREGATE,
        name="order_count",
        definition="COUNT(*)",
        input_columns=[":table"],
        output_data_type="BIGINT"
    ),
    MonitorMetric(
        type=MonitorMetricType.DERIVED,
        name="avg_order_value",
        definition="total_revenue / NULLIF(order_count, 0)",
        input_columns=[":table"],
        output_data_type="DOUBLE"
    )
]
```

### SQL Alerts

```sql
-- Alert for data freshness
CREATE OR REPLACE ALERT gold_freshness_alert
USING (
    SELECT 
        'Gold layer data is stale' as alert_message,
        MAX(record_updated_timestamp) as last_update
    FROM gold.fact_sales
    WHERE MAX(record_updated_timestamp) < current_timestamp() - INTERVAL 2 HOURS
)
WHEN COUNT(*) > 0
THEN NOTIFY 'data-alerts@company.com';

-- Alert for data quality
CREATE OR REPLACE ALERT null_revenue_alert
USING (
    SELECT COUNT(*) as null_count
    FROM gold.fact_sales
    WHERE net_revenue IS NULL
    AND record_created_timestamp >= current_date
)
WHEN null_count > 0
THEN NOTIFY 'data-quality@company.com';
```

### Hands-On Lab 4.4: Set Up Monitoring

```python
# Create comprehensive monitoring setup

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# 1. Create monitor for fact table
monitor = w.quality_monitors.create(
    table_name="gold.fact_sales",
    assets_dir="/Shared/monitoring/fact_sales",
    output_schema_name="gold_monitoring",
    time_series=MonitorTimeSeries(
        timestamp_col="transaction_date",
        granularities=["1 day", "1 week"]
    ),
    slicing_exprs=["category", "region"],
    custom_metrics=[
        MonitorMetric(
            type=MonitorMetricType.AGGREGATE,
            name="total_revenue",
            definition="SUM(net_revenue)",
            input_columns=["net_revenue"],
            output_data_type="DOUBLE"
        )
    ]
)

# 2. Run initial refresh
w.quality_monitors.run_refresh(table_name="gold.fact_sales")

# 3. Check monitor status
status = w.quality_monitors.get(table_name="gold.fact_sales")
print(f"Monitor status: {status.status}")
```

---

## Section 5: Troubleshooting Guide (1 hour)

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `DELTA_MULTIPLE_SOURCE_ROW` | Duplicate keys in MERGE | Add deduplication before MERGE |
| `InputWidgetNotDefined` | Wrong parameter name | Match YAML and notebook parameter names |
| `ModuleNotFoundError` | Import in serverless | Inline functions or use pure Python |
| `Table does not have PK` | FK before PK | Apply constraints in correct order |
| `Invalid access token` | Token expired | Re-authenticate with `databricks auth login` |

### Debug Workflow

```bash
# 1. Check job run logs
databricks jobs get-run --run-id <RUN_ID>

# 2. Get detailed task output
databricks jobs get-run-output --run-id <RUN_ID>

# 3. View cluster logs
databricks clusters get-events --cluster-id <CLUSTER_ID>

# 4. Check DLT pipeline events
databricks pipelines get-update --pipeline-id <PIPELINE_ID> --update-id <UPDATE_ID>
```

### Pre-Deployment Validation Script

```bash
#!/bin/bash
# scripts/validate_bundle.sh

echo "🔍 Pre-Deployment Validation"
echo "========================================"

# 1. Check for duplicate YAML files
echo "1. Checking for duplicates..."
duplicates=$(find resources -name "*.yml" | awk -F/ '{print $NF}' | sort | uniq -d)
if [ -n "$duplicates" ]; then
    echo "❌ ERROR: Duplicate files found: $duplicates"
    exit 1
fi
echo "✅ No duplicates"

# 2. Check for python_task (should be notebook_task)
echo "2. Checking task types..."
if grep -r "python_task:" resources/ > /dev/null 2>&1; then
    echo "❌ ERROR: Found python_task (use notebook_task)"
    exit 1
fi
echo "✅ Task types correct"

# 3. Validate bundle
echo "3. Validating bundle..."
if ! databricks bundle validate; then
    echo "❌ ERROR: Bundle validation failed"
    exit 1
fi
echo "✅ Bundle valid"

echo ""
echo "========================================"
echo "✅ All checks passed!"
```

---

## Module 4 Assessment

### Quiz (20 questions, 80% to pass)

1. Which field specifies serverless compute in Asset Bundles?
   - a) `compute: serverless`
   - b) `environments` with `environment_version: "4"` ✓
   - c) `serverless: true`

2. What must EVERY notebook_task have?
   - a) `run_name`
   - b) `environment_key` ✓
   - c) `timeout_seconds`

3. How should parameters be read in Databricks notebooks?
   - a) `argparse.ArgumentParser()`
   - b) `dbutils.widgets.get()` ✓
   - c) `sys.argv[]`

### Final Capstone Project

**Deploy End-to-End Data Platform:**

1. Create complete Asset Bundle structure
2. Deploy Bronze, Silver, Gold layers
3. Configure DLT pipeline with expectations
4. Set up Lakehouse Monitoring
5. Implement alerting for data quality
6. Document deployment runbook

**Deliverables:**
- Complete bundle code
- Deployment documentation
- Monitoring dashboard screenshot
- Runbook for operations

---

## Certification Completion

**Congratulations!** You have completed the Enterprise Data Platform Training.

### What You've Learned

| Module | Key Skills |
|--------|------------|
| **1: Foundations** | Unity Catalog, governance, medallion architecture |
| **2: Data Engineering** | Bronze/Silver patterns, DLT, data quality |
| **3: Gold & Semantic** | Dimensional modeling, TVFs, Metric Views |
| **4: Operations** | Asset Bundles, deployment, monitoring |

### Next Steps

1. Complete certification assessment
2. Join the Data Platform community
3. Start your first production project
4. Mentor new team members

---

**Training Complete!**

For questions or support, contact the Data Platform team.
