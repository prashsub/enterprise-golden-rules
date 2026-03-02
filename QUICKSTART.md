# Quick Start Guide

Get the Enterprise Golden Rules enforced in your Databricks workspace in under 5 minutes.

---

## Step 1: Understand the Structure (1 min)

The framework is organized into three architecture tiers:

```
Enterprise Architecture  →  WHY: Governance, compliance, roles, data modeling standards
Platform Architecture    →  HOW: Unity Catalog, compute, networking, CI/CD, reliability
Solution Architecture    →  WHAT: Data pipelines, semantic layer, ML/AI, dashboards
```

Every rule has a unique ID (e.g., `DL-01`, `IN-05`, `MV-01`) and a severity level:
- **Critical** — Must follow. Violations block deployment.
- **Required** — Should follow. Exceptions need documented approval.
- **Recommended** — Best practice. Follow when practical.

## Step 2: Read the Top 10 Rules (2 min)

These rules apply to nearly every piece of code on the platform:

| # | Rule ID | One-Liner |
|---|---------|-----------|
| 1 | **DL-01** | All tables in Unity Catalog — no Hive Metastore |
| 2 | **DL-04** | Delta Lake format required |
| 3 | **DL-05** | `CLUSTER BY AUTO` on all tables |
| 4 | **NC-01** | `snake_case` for all object names |
| 5 | **DM-02** | `PRIMARY KEY` constraint on every table |
| 6 | **CM-02** | Table COMMENT with business + technical context |
| 7 | **DP-01** | Medallion Architecture: Bronze → Silver → Gold |
| 8 | **IN-01** | Serverless compute for all jobs |
| 9 | **IN-03** | `notebook_task` only — never `python_task` |
| 10 | **GOV-06** | Service principals for production jobs |

The full top-40 critical rules are in the [workspace instructions](enterprise_golden_rules/assistant/workspace_instructions/.assistant_workspace_instructions.md).

## Step 3: Deploy the Databricks Assistant Enforcement (2 min)

### Option A: Workspace Instructions Only (fastest)

1. Open your workspace Admin Console
2. Navigate to **AI/BI Settings → Assistant Workspace Instructions**
3. Paste the contents of [`assistant/workspace_instructions/.assistant_workspace_instructions.md`](enterprise_golden_rules/assistant/workspace_instructions/.assistant_workspace_instructions.md)
4. Save

The Assistant will now enforce the top 40 critical rules in inline, chat, edit, and suggest-fix modes.

### Option B: Full Deployment (recommended)

For complete coverage of all 162+ rules in agent mode:

```bash
# Deploy domain rule files to your Databricks workspace
cd enterprise_golden_rules/assistant

# Option 1: Shell script
bash deploy.sh /Workspace/Enterprise_Rules --profile YOUR_PROFILE

# Option 2: Asset Bundle
databricks bundle deploy -t prod

# Option 3: Direct import
databricks workspace import-dir ./generated/Enterprise_Rules /Workspace/Enterprise_Rules --overwrite
```

Then paste the workspace instructions (Step 3a above).

## Step 4: Verify It Works

Open the Databricks Assistant in agent mode and try:

```
Audit this code against golden rules:

CREATE TABLE my_catalog.my_schema.MyTable (
  id INT,
  name STRING
);
```

Expected findings:
- `NC-01` violation — `MyTable` should be `snake_case`
- `DM-02` violation — missing `PRIMARY KEY` constraint
- `CM-02` violation — missing table `COMMENT`
- `DL-05` violation — missing `CLUSTER BY AUTO`
- `CM-03` violation — missing column comments

## What's Next?

| Goal | Resource |
|------|----------|
| Deep-dive into your role's rules | [Role-based navigation](enterprise_golden_rules/README.md#quick-navigation-by-role) |
| Understand all 162+ rules by WAF pillar | [WAF pillar cross-reference](enterprise_golden_rules/README.md#rules-by-well-architected-lakehouse-pillar) |
| Onboard a new team member | [Week 1 guide](enterprise_golden_rules/onboarding/80-new-hire-week1.md) |
| Run a full compliance audit | Use agent mode: `"Run a full golden rules audit on this notebook"` |
| Review code templates | [Gold DDL](enterprise_golden_rules/assistant/generated/Enterprise_Rules/examples/gold_table_template.sql), [DLT pipeline](enterprise_golden_rules/assistant/generated/Enterprise_Rules/examples/dlt_pipeline_template.py), [Asset Bundle](enterprise_golden_rules/assistant/generated/Enterprise_Rules/examples/asset_bundle_template.yml) |
| Request a rule exception | [Exception request form](enterprise_golden_rules/templates/exception-request-form.md) |
| Start the 40-hour training program | [Training curriculum](enterprise_golden_rules/training/70-training-curriculum-overview.md) |

## Common Patterns Cheat Sheet

### Gold Table DDL

```sql
CREATE TABLE IF NOT EXISTS catalog.schema.dim_customer (
    customer_key STRING NOT NULL
        COMMENT 'Surrogate key. Business: Fact joins. Technical: MD5.',
    customer_id STRING NOT NULL
        COMMENT 'Natural key. Business: Customer ID. Technical: Source system.',
    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key) NOT ENFORCED
)
CLUSTER BY AUTO
COMMENT 'Customer dimension. Business: Segmentation. Technical: SCD2 from Silver.';
```

### Asset Bundle Job

```yaml
resources:
  jobs:
    my_job:
      name: "[${bundle.target}] My Job"
      environments:
        - environment_key: "default"
          spec:
            environment_version: "4"
      tags:
        team: data-engineering
        cost_center: CC-1234
        environment: ${bundle.target}
      tasks:
        - task_key: transform
          environment_key: default
          notebook_task:
            notebook_path: ../src/transform.py
```

### DLT Pipeline

```python
@dlt.table(name="silver_orders", comment="Validated orders.", cluster_by_auto=True)
@dlt.expect_all_or_drop({
    "valid_id": "order_id IS NOT NULL",
    "valid_amount": "amount >= 0"
})
def silver_orders():
    return dlt.read_stream("bronze_orders")
```
