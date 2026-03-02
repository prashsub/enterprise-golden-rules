---
name: Enterprise Golden Rules Audit
description: >
  Performs code review and compliance auditing against 155+ Enterprise
  Golden Rules for Databricks. Activates for: code review, audit,
  compliance check, golden rules enforcement, standards review.
---

## Instructions

You are performing a Golden Rules compliance audit. Follow these steps:

### Step 1: Load Rules
Read the workspace instructions for Top-40 critical rules (always available).
Then load detailed rules for relevant domains:
```python
base = "/Workspace/Enterprise_Rules"
content = open(f"{base}/domain/{domain_name}.md").read()
```

### Step 2: Identify Domains
Scan the code for trigger keywords:
- bronze/silver/gold/MERGE/dedup → `data_pipelines.md`
- delta/CLUSTER BY/vacuum → `delta_lake.md`
- metric view/TVF/genie/dashboard → `semantic_layer.md`
- bundle/job/deploy → `asset_bundles.md`
- model/MLflow/feature/agent → `ml_ai.md` or `genai.md`
- naming/comment/tags → `naming_tagging.md`
- PK/FK/constraint/star schema → `data_modeling.md`

### Step 3: Analyze Code
Apply each rule from loaded files. Mark PASS / FAIL / N/A.

### Step 4: Report
Generate audit report per:
```python
template = open(f"{base}/audit/report_template.md").read()
```
Include: Rule ID, violation, current code, corrected code, business impact.
