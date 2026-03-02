# Databricks Assistant — Progressive Disclosure Enforcement

**Version:** 5.4 | **Updated:** Feb 2026

Tooling and generated files to enforce 155+ Enterprise Golden Rules via the Databricks Assistant using a three-layer progressive disclosure architecture.

## Architecture

```
Layer 0 (Always Active) ── Workspace Instructions ── 15K / 20K chars
    Top-40 critical rules inline + Navigation Index + Agent Mode Protocol
    Works in: inline, chat, edit, suggest-fix, agent

Layer 1 (Agent Mode, On-Demand) ── /Workspace/Enterprise_Rules/ ── Shared
    12 domain rule files + audit checklist + code examples
    Loaded by: open("/Workspace/Enterprise_Rules/domain/{name}.md").read()

Layer 2 (Source of Truth) ── Git Repository
    40 documents, 500K+ chars, 155+ rules
```

## Directory Structure

```
assistant/
├── README.md                              # This file
├── build_rules.py                         # Parse source docs → generate workspace files
├── deploy.sh                              # Deploy to Databricks workspace
├── databricks.yml                         # Asset Bundle config (dev/prod)
│
├── workspace_instructions/
│   └── .assistant_workspace_instructions.md   # 15K chars — paste into Admin Console
│
├── per_user_skill/
│   └── SKILL.md                           # Optional thin wrapper for auto-trigger
│
└── generated/
    └── Enterprise_Rules/                  # Deploy this directory to /Workspace/
        ├── README.md
        ├── VERSION
        ├── domain/                        # 12 domain-specific rule files
        │   ├── data_pipelines.md          # DP, DA, DQ, DI rules
        │   ├── delta_lake.md              # DL rules + BP operational tips
        │   ├── streaming.md               # ST rules
        │   ├── semantic_layer.md          # MV, TF, GN, MO, DB rules
        │   ├── data_modeling.md           # DM rules
        │   ├── naming_tagging.md          # NC, CM, TG rules
        │   ├── asset_bundles.md           # IN, PY rules
        │   ├── uc_governance.md           # GOV, EA, DS rules
        │   ├── security.md                # SEC, SM rules
        │   ├── reliability.md             # REL, SC, CP, PA, COST rules
        │   ├── ml_ai.md                   # ML-01..09, GA-01..04
        │   └── genai.md                   # GS-01..07, AG-01..05
        ├── audit/
        │   ├── full_checklist.md          # All 155+ rules as pass/fail
        │   └── report_template.md         # Structured audit report format
        └── examples/
            ├── gold_table_template.sql    # Gold DDL with PK/FK, comments
            ├── dlt_pipeline_template.py   # DLT with expectations
            ├── asset_bundle_template.yml  # Serverless job YAML
            ├── metric_view_template.yml   # v1.1 Metric View
            └── agent_template.py          # ResponsesAgent with OBO auth
```

## Deployment

### Step 1: Set Workspace Instructions

Paste the contents of `workspace_instructions/.assistant_workspace_instructions.md` into:
**Admin Console > AI/BI Settings > Assistant Workspace Instructions**

### Step 2: Deploy Shared Files

Option A — Shell script:
```bash
bash deploy.sh [WORKSPACE_PATH] [--profile PROFILE]
```

Option B — Asset Bundle:
```bash
databricks bundle deploy -t prod
```

Option C — Direct import:
```bash
databricks workspace import-dir ./generated/Enterprise_Rules /Workspace/Enterprise_Rules --overwrite
```

### Step 3 (Optional): Deploy Per-User Skill

Copy `per_user_skill/SKILL.md` to `/Users/{user}/.assistant/skills/` for auto-triggering on "audit" and "review" keywords.

## Updating Rules

1. Update source docs in the parent `enterprise_golden_rules/` directories
2. Regenerate: `python build_rules.py`
3. Deploy: `bash deploy.sh`
4. Update workspace instructions if Top-40 changed

## How It Works

| Mode | What Happens | Coverage |
|------|-------------|----------|
| Inline/Chat/Edit | Workspace instructions only | ~40 critical rules (~70%) |
| Agent mode | Instructions + reads domain files on demand | Full domain coverage |
| Agent mode (audit) | Reads full checklist + all domain files | All 155+ rules |
