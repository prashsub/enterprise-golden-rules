# Enterprise Golden Rules — Shared Workspace Files

**Version:** 5.4 | **Updated:** Feb 2026

## Purpose

These files provide detailed Enterprise Golden Rules for the Databricks Assistant via progressive disclosure. The assistant's workspace instructions (20K char limit) contain the Top-40 critical rules and a navigation index that points here for full domain coverage.

## How It Works

```
Layer 0: Workspace Instructions (always active, all modes)
  → Top-40 rules inline + Navigation Index

Layer 1: These files (agent mode only, on-demand)
  → 12 domain rule files + audit checklist + code templates
  → Loaded via: open("/Workspace/Enterprise_Rules/domain/{name}.md").read()

Layer 2: Git repository (source of truth)
  → enterprise_golden_rules/ — 40 docs, 500K+ chars, 155+ rules
```

## File Structure

```
Enterprise_Rules/
├── README.md                    # This file
├── VERSION                      # Version tracking
│
├── domain/                      # 12 domain-specific rule files
│   ├── data_pipelines.md        # DP, DA, DQ, DI rules
│   ├── delta_lake.md            # DL rules + BP operational tips
│   ├── streaming.md             # ST rules
│   ├── semantic_layer.md        # MV, TF, GN, MO, DB rules
│   ├── data_modeling.md         # DM rules
│   ├── naming_tagging.md        # NC, CM, TG rules
│   ├── asset_bundles.md         # IN, PY rules
│   ├── uc_governance.md         # GOV, EA, DS rules
│   ├── security.md              # SEC, SM rules
│   ├── reliability.md           # REL, SC, CP, PA, COST rules
│   ├── ml_ai.md                 # ML-01..09, GA-01..04 rules
│   └── genai.md                 # GS-01..07, AG-01..05 rules
│
├── audit/                       # Audit-specific files
│   ├── full_checklist.md        # All 155+ rules as pass/fail
│   └── report_template.md       # Structured audit report format
│
└── examples/                    # Ready-to-use code templates
    ├── gold_table_template.sql  # Gold DDL with PK/FK, comments
    ├── dlt_pipeline_template.py # DLT with expectations
    ├── asset_bundle_template.yml# Serverless job YAML
    ├── metric_view_template.yml # v1.1 Metric View
    └── agent_template.py        # ResponsesAgent with OBO auth
```

## Deployment

Deploy to workspace:
```bash
databricks workspace import_dir ./Enterprise_Rules /Workspace/Enterprise_Rules --overwrite
```

Or via Asset Bundle sync (see `databricks.yml`).

## Usage by the Assistant

The Databricks Assistant loads these files in **agent mode** when it detects relevant trigger keywords. Example:

1. User asks: "Create a Gold table for customer orders"
2. Assistant detects keywords: "Gold", "table", "orders"
3. Assistant loads: `domain/data_pipelines.md`, `domain/data_modeling.md`, `domain/naming_tagging.md`
4. Assistant applies all rules from loaded files to generate compliant code

## Updating

1. Update source docs in `enterprise_golden_rules/` Git repo
2. Run `python assistant/build_rules.py` to regenerate these files
3. Deploy to workspace: `bash assistant/deploy.sh`
4. Bump VERSION file

## Source

Generated from `enterprise_golden_rules/` Git repository v5.4.
