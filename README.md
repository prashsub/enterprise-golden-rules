# Enterprise Golden Rules for Databricks

**Version 5.4.2** | **162+ Golden Rules** | **7 WAF Pillars** | **12 Domains**

A comprehensive, opinionated standards framework for building and governing enterprise Databricks lakehouse platforms. Covers everything from table DDL and naming conventions to ML model lifecycle and network security — aligned with the [Databricks Well-Architected Lakehouse Framework](https://docs.databricks.com/en/lakehouse-architecture/index.html).

---

## What's Inside

```
enterprise_golden_rules/
├── enterprise-architecture/   Governance, roles, compliance, data modeling, naming, tagging, data quality
├── platform-architecture/     Unity Catalog, serverless compute, Delta Lake, networking, CI/CD, reliability
├── solution-architecture/     Data pipelines, semantic layer, dashboards, ML/AI, GenAI, data sharing
├── training/                  40-hour structured curriculum (4 modules)
├── onboarding/                New-hire week 1 & 2 guides
├── templates/                 Architecture review, deployment, compliance, exception request
├── appendix/                  Glossary (50+ terms), quick-reference cards (13 cheat sheets)
└── assistant/                 Databricks Assistant integration (workspace instructions, domain rules, audit)
```

| Metric | Count |
|--------|-------|
| Total documents | 40+ |
| Golden rules | 162+ |
| Rule prefixes | 32 |
| Architecture domains | 3 (Enterprise, Platform, Solution) |
| WAF pillars covered | 7 (Governance, Security, Reliability, Performance, Cost, OpEx, Interop) |
| Training hours | 40 |
| Code templates | 5 (Gold DDL, DLT, Asset Bundle, Metric View, Agent) |

## Key Highlights

- **Medallion Architecture** — Bronze/Silver/Gold patterns with DLT expectations, YAML-driven schemas, and SCD Type 2
- **Unity Catalog First** — Managed tables, liquid clustering, governed tags, ABAC/RBAC, lineage
- **Serverless by Default** — SQL Warehouses, Jobs, and DLT on serverless compute
- **Semantic Layer** — Metric Views (v1.1 YAML), Table-Valued Functions (v3.0 comments), Genie Spaces
- **Asset Bundles** — CI/CD with hierarchical jobs, environment management, and service principals
- **ML/AI & GenAI** — MLflow model patterns, GenAI agent standards, AI Gateway, responsible AI
- **Databricks Assistant Integration** — Three-layer progressive disclosure enforcing all 162+ rules via workspace instructions and agent-mode domain files

## Quick Links

| Resource | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Get up and running in 5 minutes |
| [Full Documentation Hub](enterprise_golden_rules/README.md) | Complete navigation by role, domain, and WAF pillar |
| [Changelog](CHANGELOG.md) | Version history for the framework |
| [Glossary](enterprise_golden_rules/appendix/glossary.md) | 50+ terms and acronyms |
| [Quick Reference Cards](enterprise_golden_rules/appendix/quick-reference-cards.md) | 13 one-page cheat sheets |

## Who Is This For?

| Role | Start Here |
|------|------------|
| **Data Engineers** | [Bronze](enterprise_golden_rules/solution-architecture/data-pipelines/25-bronze-layer-patterns.md), [Silver](enterprise_golden_rules/solution-architecture/data-pipelines/26-silver-layer-patterns.md), [Gold](enterprise_golden_rules/solution-architecture/data-pipelines/27-gold-layer-patterns.md) layer patterns |
| **Analytics Engineers** | [Metric Views](enterprise_golden_rules/solution-architecture/semantic-layer/30-metric-view-patterns.md), [TVFs](enterprise_golden_rules/solution-architecture/semantic-layer/31-tvf-patterns.md), [Genie Spaces](enterprise_golden_rules/solution-architecture/semantic-layer/32-genie-space-patterns.md) |
| **ML Engineers** | [MLflow Models](enterprise_golden_rules/solution-architecture/ml-ai/50-mlflow-model-patterns.md), [GenAI Agents](enterprise_golden_rules/solution-architecture/ml-ai/51-genai-agent-patterns.md), [AI Gateway](enterprise_golden_rules/solution-architecture/ml-ai/53-ai-gateway-patterns.md) |
| **Platform Engineers** | [Platform Overview](enterprise_golden_rules/platform-architecture/10-platform-overview.md), [UC Governance](enterprise_golden_rules/platform-architecture/15-unity-catalog-governance.md), [Network Security](enterprise_golden_rules/platform-architecture/18-network-security.md) |
| **New Hires** | [Onboarding Week 1](enterprise_golden_rules/onboarding/80-new-hire-week1.md), [Training Curriculum](enterprise_golden_rules/training/70-training-curriculum-overview.md) |

## Databricks Assistant Integration

The `assistant/` directory contains tooling to enforce these rules directly inside the Databricks Assistant:

1. **Workspace Instructions** — Paste into Admin Console for always-on enforcement of the top 40 critical rules
2. **Domain Rule Files** — Deploy to `/Workspace/Enterprise_Rules/` for full agent-mode coverage
3. **Audit Workflow** — Automated compliance checking against all 162+ rules

See [assistant/README.md](enterprise_golden_rules/assistant/README.md) for deployment instructions.

## Contributing

1. Follow the numbering convention — each domain owns a dedicated range (see [Documentation Hub](enterprise_golden_rules/README.md#numbering-standard))
2. Use the file naming pattern: `XX-kebab-case-name.md`
3. Include a Document Information header and Golden Rules summary table
4. Add the document to the appropriate architecture domain
5. Update the README navigation and CHANGELOG
6. Submit a PR for review

## License

Internal use. Not for external distribution without approval.
