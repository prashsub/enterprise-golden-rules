# Enterprise Data Platform Golden Rules

## Documentation Hub

**Version:** 5.4.2 | **Last Updated:** February 2026 | **Owner:** Platform Team

This documentation suite provides comprehensive standards, patterns, and governance frameworks for our Databricks-based enterprise data platform, aligned with the [Databricks Well-Architected Lakehouse Framework](https://docs.databricks.com/en/lakehouse-architecture/index.html) and [official Databricks Architecture](https://docs.databricks.com/en/getting-started/concepts.html) documentation.

---

## Official Microsoft Learn References

The following official documentation has been incorporated into these golden rules:

| Topic | URL | Key Concepts |
|-------|-----|--------------|
| **Architecture Overview** | [Architecture](https://learn.microsoft.com/en-us/azure/databricks/getting-started/architecture) | Control plane, compute plane, lakehouse |
| **High-Level Architecture** | [High-Level Architecture](https://learn.microsoft.com/en-us/azure/databricks/getting-started/high-level-architecture) | Workspace architecture, serverless vs classic |
| **Medallion Architecture** | [Medallion Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion) | Bronze, Silver, Gold layers |
| **Unity Catalog** | [What is Unity Catalog?](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/) | Centralized governance, lineage, security |
| **ACID Guarantees** | [ACID on Databricks](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/acid) | Transactions, isolation, durability |
| **Single Source of Truth** | [SSOT](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/ssot) | Data unification, Delta Lake |
| **Governance Best Practices** | [Data Governance](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/data-governance/best-practices) | Lineage, quality, security |
| **Managed Tables** | [Unity Catalog Managed Tables](https://learn.microsoft.com/en-us/azure/databricks/tables/managed) | Default table type, AI optimization |
| **Liquid Clustering** | [Use Liquid Clustering](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering) | CLUSTER BY AUTO, automatic optimization |
| **Performance Efficiency** | [Performance](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/performance-efficiency/best-practices) | Serverless, optimization |
| **Cost Optimization** | [Cost](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/cost-optimization/best-practices) | Serverless pricing, efficiency |
| **Reliability** | [Reliability](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/reliability/best-practices) | HA, DR, autoscaling |
| **Well-Architected Framework** | [Service Guide](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-databricks) | All 5 pillars, security, network |
| **CI/CD Best Practices** | [CI/CD](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/ci-cd/best-practices) | Asset Bundles, testing, MLOps |
| **AI/BI Genie** | [Genie](https://learn.microsoft.com/en-us/azure/databricks/genie/) | Natural language, trusted assets |
| **Data Engineering Best Practices** | [Data Engineering](https://learn.microsoft.com/en-us/azure/databricks/data-engineering/best-practices) | Streaming, observability, optimization |
| **Delta Lake Best Practices** | [Delta Lake](https://docs.databricks.com/en/delta/best-practices.html) | Clustering, MERGE, caching |
| **Unity Catalog Best Practices** | [Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/best-practices.html) | Identities, privileges, storage |
| **Compute Configuration** | [Compute](https://docs.databricks.com/en/compute/cluster-config-best-practices.html) | Serverless, sizing, Photon |
| **Data Modeling** | [Data Modeling](https://learn.microsoft.com/en-us/azure/databricks/transform/data-modeling) | Star schema, joins, normalization |
| **Table Constraints** | [Constraints](https://learn.microsoft.com/en-us/azure/databricks/tables/constraints) | PK, FK, CHECK, NOT NULL |
| **Data Quality Monitoring** | [Data Quality](https://learn.microsoft.com/en-us/azure/databricks/data-quality-monitoring/) | Anomaly detection, profiling, drift |

---

## Documentation Structure

```
enterprise_golden_rules/
│
├── enterprise-architecture/     # 🏢 Governance, Roles, Compliance
│   ├── 01-data-governance.md
│   ├── 02-roles-responsibilities.md
│   ├── 03-implementation-workflow.md
│   ├── 04-data-modeling.md
│   ├── 05-naming-comment-standards.md
│   ├── 06-tagging-standards.md
│   ├── 07-data-quality-standards.md
│   └── 08-architecture-evolution.md  # NEW - Maturity levels, decision heuristics
│
├── platform-architecture/       # 🔧 Infrastructure, CI/CD, Standards
│   ├── 10-platform-overview.md
│   ├── 11-serverless-compute.md
│   ├── 12-unity-catalog-tables.md      # UC Tables & Delta Lake (DL-01..12)
│   ├── 13-cluster-policies.md          # Classic Compute Governance (CP-01..09)
│   ├── 14-secrets-workspace-management.md
│   ├── 15-unity-catalog-governance.md
│   ├── 16-data-access-patterns.md          # NEW - Ingest vs Federate vs Share (DI-01..07)
│   ├── 17-reliability-disaster-recovery.md  # NEW - HA, DR, recovery
│   ├── 18-network-security.md               # NEW - VNet, Private Link, CMK
│   ├── 19-asset-bundle-standards.md
│   └── 20-python-development.md
│
├── solution-architecture/       # 🏗️ Implementation Patterns
│   ├── data-pipelines/
│   │   ├── 25-bronze-layer-patterns.md
│   │   ├── 26-silver-layer-patterns.md
│   │   ├── 27-gold-layer-patterns.md
│   │   └── 28-streaming-production-patterns.md
│   ├── semantic-layer/
│   │   ├── 30-metric-view-patterns.md
│   │   ├── 31-tvf-patterns.md
│   │   ├── 32-genie-space-patterns.md
│   │   └── 33-semantic-layer-overview.md
│   ├── dashboards/
│   │   └── 35-aibi-dashboard-patterns.md
│   ├── monitoring/
│   │   └── 36-lakehouse-monitoring.md
│   ├── ml-ai/
│   │   ├── 50-mlflow-model-patterns.md
│   │   ├── 51-genai-agent-patterns.md
│   │   ├── 52-genai-standards.md
│   │   └── 53-ai-gateway-patterns.md
│   └── data-sharing/
│       └── 60-delta-sharing-patterns.md
│
├── onboarding/                  # 🎓 New Hire Quick Start
│   ├── 80-new-hire-week1.md
│   └── 81-new-hire-week2.md
│
├── training/                    # 📚 Structured Training Curriculum
│   ├── 70-training-curriculum-overview.md
│   ├── 71-module-platform-foundations.md
│   ├── 72-module-data-engineering.md
│   ├── 73-module-gold-layer-semantic.md
│   └── 74-module-operations-deployment.md
│
├── templates/                   # 📝 Reusable Templates
│   ├── architecture-review-checklist.md
│   ├── deployment-checklist.md
│   ├── exception-request-form.md
│   ├── compliance-report-template.md
│   └── verification-checklist.md
│
└── appendix/                    # 📖 Reference Materials
    ├── glossary.md
    └── quick-reference-cards.md
```

### Numbering Standard

Each domain owns a dedicated number range. Every file gets a globally unique number.

| Domain | Range | Current Files |
|--------|-------|---------------|
| **EA** (Enterprise Architecture) | 01–09 | 01–08 |
| **PA** (Platform Architecture) | 10–24 | 10–20 |
| **SA** Data Pipelines | 25–29 | 25–28 |
| **SA** Semantic Layer | 30–34 | 30–33 |
| **SA** Dashboards & Monitoring | 35–39 | 35–36 |
| **SA** ML/AI | 50–54 | 50–53 |
| **SA** Data Sharing | 60–64 | 60 |
| **Training** | 70–79 | 70–74 |
| **Onboarding** | 80–89 | 80–81 |

When adding a new file, use the next available number within the domain's range.

---

## Quick Navigation by Role

### Data Engineers
| Priority | Document | Topic |
|----------|----------|-------|
| 🔴 Must Read | [Bronze Layer](solution-architecture/data-pipelines/25-bronze-layer-patterns.md) | CDF, Faker, ingestion |
| 🔴 Must Read | [Silver Layer](solution-architecture/data-pipelines/26-silver-layer-patterns.md) | DLT, expectations, DQX |
| 🔴 Must Read | [Gold Layer](solution-architecture/data-pipelines/27-gold-layer-patterns.md) | YAML schemas, MERGE, SCD2 |
| 🔴 Must Read | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) | Clustering, MERGE, caching |
| 🔴 Must Read | [Streaming Production](solution-architecture/data-pipelines/28-streaming-production-patterns.md) | Triggers, idempotency, scheduler pools |
| 🟡 Required | [Data Access Patterns](platform-architecture/16-data-access-patterns.md) | Ingest vs federate vs share |
| 🟡 Required | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) | CI/CD, job configuration |
| 🟡 Required | [Python Standards](platform-architecture/20-python-development.md) | Parameters, imports |

### Analytics Engineers
| Priority | Document | Topic |
|----------|----------|-------|
| 🔴 Must Read | [Metric Views](solution-architecture/semantic-layer/30-metric-view-patterns.md) | v1.1 YAML, no transitive joins |
| 🔴 Must Read | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) | STRING dates, v3.0 comments |
| 🔴 Must Read | [Genie Spaces](solution-architecture/semantic-layer/32-genie-space-patterns.md) | Asset inventory, optimization |
| 🟡 Required | [Dashboards](solution-architecture/dashboards/35-aibi-dashboard-patterns.md) | fieldName, formatting |
| 🟡 Required | [Monitoring](solution-architecture/monitoring/36-lakehouse-monitoring.md) | Custom metrics |

### ML Engineers
| Priority | Document | Topic |
|----------|----------|-------|
| 🔴 Must Read | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) | Feature tables, inference |
| 🔴 Must Read | [GenAI Agents](solution-architecture/ml-ai/51-genai-agent-patterns.md) | ResponsesAgent, OBO auth |
| 🟡 Required | [GenAI Standards](solution-architecture/ml-ai/52-genai-standards.md) | Evaluation, memory |
| 🟡 Required | [AI Gateway](solution-architecture/ml-ai/53-ai-gateway-patterns.md) | Payload logging, guardrails |

### Platform Engineers
| Priority | Document | Topic |
|----------|----------|-------|
| 🔴 Must Read | [Platform Overview](platform-architecture/10-platform-overview.md) | Architecture principles |
| 🔴 Must Read | [Serverless Compute](platform-architecture/11-serverless-compute.md) | SQL Warehouses, Jobs, DLT |
| 🔴 Must Read | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) | Managed tables, Delta ops, clustering |
| 🔴 Must Read | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) | Naming conventions, SQL comments |
| 🔴 Must Read | [Tagging Standards](enterprise-architecture/06-tagging-standards.md) | Table properties, compute tags, governed tags |
| 🔴 Must Read | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) | CI/CD, hierarchical jobs |
| 🔴 Must Read | [UC Governance](platform-architecture/15-unity-catalog-governance.md) | Identities, privileges, ownership |
| 🔴 Must Read | [Network Security](platform-architecture/18-network-security.md) | VNet, Private Link, CMK |
| 🟡 Required | [Data Access Patterns](platform-architecture/16-data-access-patterns.md) | Ingest vs federate vs share |
| 🟡 Required | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) | Time travel, checkpointing, HA |
| 🟡 Required | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) | Policies, access modes, Photon, sizing |
| 🟡 Required | [Secrets & Workspaces](platform-architecture/14-secrets-workspace-management.md) | Security, organization |
| 🟡 Required | [Data Governance](enterprise-architecture/01-data-governance.md) | Classification, compliance |
| 🟡 Required | [Data Modeling](enterprise-architecture/04-data-modeling.md) | Star schema, constraints |
| 🟡 Required | [Data Quality Standards](enterprise-architecture/07-data-quality-standards.md) | DLT Expectations, DQX, Lakehouse Monitor |
| 🟡 Required | [Architecture Evolution](enterprise-architecture/08-architecture-evolution.md) | Maturity levels, decision heuristics |

### New Team Members

**Quick Start (First Week):**
| Day | Document | Focus |
|-----|----------|-------|
| Day 1-2 | [Onboarding Week 1](onboarding/80-new-hire-week1.md) | Concepts, reading, setup |
| Day 3-5 | [Onboarding Week 2](onboarding/81-new-hire-week2.md) | Hands-on labs, full pipeline |

**Structured Training (40 hours):**
| Module | Duration | Document | Topics |
|--------|----------|----------|--------|
| Overview | - | [Curriculum](training/70-training-curriculum-overview.md) | Learning path, prerequisites |
| Module 1 | 8 hrs | [Platform Foundations](training/71-module-platform-foundations.md) | Unity Catalog, governance, architecture |
| Module 2 | 12 hrs | [Data Engineering](training/72-module-data-engineering.md) | Bronze, Silver, DLT, data quality |
| Module 3 | 12 hrs | [Gold & Semantic](training/73-module-gold-layer-semantic.md) | Dimensional modeling, TVFs, Metric Views |
| Module 4 | 8 hrs | [Operations](training/74-module-operations-deployment.md) | Asset Bundles, deployment, monitoring |

---

## Golden Rules Quick Reference

### Critical Rules (🔴 Must Follow)

| ID | Rule | Domain |
|----|------|--------|
| **NC-01** | Use `snake_case` for all object names | Naming |
| **NC-02** | Use layer-appropriate prefixes for tables | Naming |
| **CM-02** | Use COMMENT ON TABLE with business + technical context | Comments |
| **CM-03** | Use COMMENT ON COLUMN with business + technical context | Comments |
| **CM-04** | Use v3.0 structured comments for TVFs | Comments |
| **TG-01** | All tables require standard TBLPROPERTIES | Tagging |
| **TG-02** | All compute resources require custom tags | Tagging |
| **TG-03** | Use Governed Tags for UC object metadata | Tagging |
| **DL-01** | All tables in Unity Catalog | Platform |
| **DL-04** | Delta Lake format required | Platform |
| **IN-01** | Asset Bundles for deployment | Platform |
| **PY-01** | `dbutils.widgets.get()` for notebook params | Platform |
| **DP-02** | CDF enabled on Bronze tables | Data Pipelines |
| **SA-01** | DLT with expectations for Silver | Data Pipelines |
| **DA-03** | Dedup before MERGE in Gold | Data Pipelines |
| **DM-01** | Dimensional modeling (star/snowflake) in Gold | Data Modeling |
| **DM-02** | PRIMARY KEY constraints on all tables | Data Modeling |
| **MV-01** | All core metrics must be in Metric Views | Semantic |
| **TF-01** | STRING type for date parameters in TVFs | Semantic |
| **MV-05** | No transitive joins in Metric Views | Semantic |
| **ML-02** | `output_schema` required for UC models | ML/AI |
| **ML-07** | Register all models in Unity Catalog with aliases | ML/AI |
| **ML-08** | Champion/Challenger pattern for model promotion | ML/AI |
| **GA-02** | OBO authentication context detection | ML/AI |
| **GA-03** | Declare Genie Space resources | ML/AI |
| **DB-03** | Dashboard fieldName matches query alias | Monitoring |
| **REL-01** | Delta Lake time travel ≥7 days retention | Reliability |
| **REL-03** | Streaming checkpoints on ZRS/GRS storage | Reliability |
| **SEC-01** | Production workspaces use VNet injection | Security |
| **SEC-02** | Azure Private Link for control plane access | Security |
| **SEC-07** | Secure cluster connectivity (no public IPs) | Security |
| **EA-10** | Treat data as a product with SLAs and ownership | Enterprise |
| **PA-01** | No production data on DBFS root | Platform |
| **PA-02** | System tables for platform observability | Platform |
| **PA-03** | Workspace isolation by environment and security boundary | Platform |
| **DL-11** | UniForm for cross-engine interoperability | Delta Lake |
| **DQ-05** | Schema-level anomaly detection for freshness and completeness | Data Quality |
| **GS-06** | Responsible AI practices for all production agents | ML/AI |

### Required Rules (🟡 Should Follow)

| ID | Rule | Domain |
|----|------|--------|
| **NC-03** | Use approved abbreviations only | Naming |
| **CM-01** | Use SQL block comments for DDL headers | Comments |
| **EA-01** | All tables must have documentation | Governance |
| **EA-02** | PII columns tagged | Governance |
| **IN-05** | Hierarchical job architecture | Platform |
| **PY-02** | Pure Python files for imports | Platform |
| **DP-04** | Gold tables from YAML schema | Data Pipelines |
| **DP-06** | PK/FK constraints in Gold | Data Pipelines |
| **TF-02** | Schema validation before writing SQL | Semantic |
| **DM-03** | FOREIGN KEY constraints for relationships | Data Modeling |
| **DM-04** | Avoid heavy normalization (3NF) in Gold | Data Modeling |
| **TF-03** | v3.0 comment format for TVFs | Semantic |
| **MO-01** | `input_columns=[":table"]` for KPIs | Monitoring |
| **DB-04** | SQL returns raw numbers (widgets format) | Monitoring |
| **ML-03** | NaN/Inf handling at feature table creation | ML/AI |
| **GA-04** | Evaluation thresholds before production | ML/AI |
| **ML-09** | Log parameters, metrics, artifacts for every run | ML/AI |
| **REL-02** | Configure job retry with exponential backoff | Reliability |
| **REL-04** | Enable cluster autoscaling for variable workloads | Reliability |
| **REL-05** | Configure auto-termination on all clusters | Reliability |
| **REL-08** | Test disaster recovery procedures quarterly | Reliability |
| **SEC-03** | Implement IP access lists | Security |
| **SEC-04** | Customer-managed keys (CMK) for encryption | Security |
| **SEC-05** | Enable diagnostic logging to Azure Monitor | Security |
| **SEC-06** | Configure network egress controls | Security |
| **DQ-06** | Data profiling with baseline tables for drift detection | Data Quality |
| **DQ-07** | Custom metrics for business KPIs in Lakehouse Monitors | Data Quality |
| **EA-11** | Data contracts for cross-domain interfaces | Enterprise |
| **EA-12** | AI readiness assessment per domain | Enterprise |
| **DM-09** | Design Gold layer for BI and AI reuse | Data Modeling |
| **GOV-08** | Lineage-driven impact analysis before schema changes | Governance |
| **GOV-09** | Governance-as-code via system tables | Governance |
| **AG-05** | AI lifecycle integrated with data lifecycle | ML/AI |

---

## Rules by Well-Architected Lakehouse Pillar

All golden rules mapped to the [Databricks Well-Architected Lakehouse Framework](https://docs.databricks.com/en/lakehouse-architecture/index.html) pillars. Each rule links to its source document for full details.

### [Governance](https://docs.databricks.com/en/lakehouse-architecture/data-governance/best-practices) (49 rules)

| ID | Rule | Document |
|----|------|----------|
| **EA-01** | All data assets must have business context documentation | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-02** | PII columns must be tagged and classified | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-03** | Every data domain must have an assigned data steward | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-04** | All compute usage must be attributed with tags | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-05** | Required custom tags: team, cost_center, environment | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-07** | All new projects require architecture review | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-09** | Use Governed Tags for UC object metadata | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-11** | Define data contracts for cross-domain interfaces | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **EA-12** | Assess and track AI readiness across data domains | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **DM-02** | Declare PRIMARY KEY constraints on all tables | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DM-03** | Declare FOREIGN KEY constraints to document relationships | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DM-07** | Handle semi-structured data with appropriate complex types | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **NC-01** | All object names use snake_case | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **NC-02** | Tables prefixed by layer or entity type | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **NC-03** | No abbreviations except approved list | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **CM-01** | SQL block comments for all DDL operations | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **CM-02** | Table COMMENT follows dual-purpose format | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **CM-03** | Column COMMENT required for all columns | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **CM-04** | TVF COMMENT follows v3.0 structured format | [Naming & Comment Standards](enterprise-architecture/05-naming-comment-standards.md) |
| **TG-01** | All workflows must have required tags | [Tagging Standards](enterprise-architecture/06-tagging-standards.md) |
| **TG-02** | Use Governed Tags for UC securables | [Tagging Standards](enterprise-architecture/06-tagging-standards.md) |
| **TG-03** | Serverless resources must use approved budget policies | [Tagging Standards](enterprise-architecture/06-tagging-standards.md) |
| **DL-01** | All data in Unity Catalog (no HMS) | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **CM-02** | Table COMMENTs mandatory | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **TG-01** | Layer tags on all tables | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **GOV-01** | Provision identities at account level via SCIM | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-02** | Define and manage groups in your identity provider | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-05** | Prefer managed tables over external tables | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-07** | Assign object ownership to groups, not individuals | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-08** | Use lineage for impact analysis before schema changes | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-09** | Implement governance-as-code via system tables | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-10** | Use row filters and column masks for fine-grained access | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-11** | Configure audit logging for all workspaces | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-12** | Use ABAC policies for scalable tag-driven access control | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-13** | Define ABAC policies at catalog level for maximum inheritance | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-16** | Grant BROWSE on catalogs for data discoverability | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **ML-01** | Feature tables in Unity Catalog with primary keys | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **ML-02** | `output_schema` required for UC models | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **ML-03** | NaN/Inf handling at feature table creation | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **ML-04** | Organize experiments by lifecycle stage | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **ML-05** | Label binarization for classifiers | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **ML-06** | Exclude label and key columns from feature set | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **GS-01** | Evaluate managed services before custom development | [GenAI Standards](solution-architecture/ml-ai/52-genai-standards.md) |
| **GS-02** | Create evaluation dataset before development | [GenAI Standards](solution-architecture/ml-ai/52-genai-standards.md) |
| **GS-03** | Pass LLM judge thresholds before production | [GenAI Standards](solution-architecture/ml-ai/52-genai-standards.md) |
| **GS-06** | Implement responsible AI practices | [GenAI Standards](solution-architecture/ml-ai/52-genai-standards.md) |
| **ML-07** | Register all models in Unity Catalog with aliases | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |
| **ML-09** | Log parameters, metrics, and artifacts for every run | [MLflow Models](solution-architecture/ml-ai/50-mlflow-model-patterns.md) |

### [Security](https://docs.databricks.com/en/lakehouse-architecture/security-compliance-and-privacy/best-practices) (18 rules)

| ID | Rule | Document |
|----|------|----------|
| **EA-06** | All serverless workloads must use assigned budget policies | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **PA-01** | No production data on DBFS root | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **PA-03** | Workspace isolation by environment and security boundary | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **GOV-03** | Assign admin roles sparingly; avoid ALL PRIVILEGES | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-04** | Use catalog-level managed storage for data isolation | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **GOV-06** | Use service principals for production jobs | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |
| **CP-07** | Use standard access mode for most workloads | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **SEC-01** | Production workspaces must use VNet/VPC injection | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-02** | Configure Private Link/PSC for control plane access | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-03** | Implement IP access lists for workspace access | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-04** | Use customer-managed keys (CMK) for encryption | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-05** | Enable diagnostic logging to cloud monitoring | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-06** | Configure network egress controls | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-07** | Use secure cluster connectivity (no public IPs) | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-08** | Enable Compliance Security Profile for regulated workloads | [Network Security](platform-architecture/18-network-security.md) |
| **SEC-09** | Security monitoring and SIEM integration | [Network Security](platform-architecture/18-network-security.md) |
| **SC-09** | Configure private package repositories for internal libraries | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **GOV-14** | Use RBAC (privilege grants) as the baseline access model | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |

### [Reliability](https://docs.databricks.com/en/lakehouse-architecture/reliability/best-practices) (27 rules)

| ID | Rule | Document |
|----|------|----------|
| **EA-08** | Rule exceptions require documented approval | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **DM-05** | Design for minimal joins in common query patterns | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DQ-01** | All DLT pipelines must have data quality expectations | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DQ-02** | Classic Spark jobs must use DQX for quality validation | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DQ-03** | Gold layer tables must have Lakehouse Monitors | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DQ-04** | Quality failures must be captured, not silently dropped | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DQ-05** | Enable schema-level anomaly detection for freshness and completeness | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DQ-06** | Configure data profiling with baseline tables for drift detection | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DQ-07** | Define custom metrics for business KPIs in Lakehouse Monitors | [Data Quality](enterprise-architecture/07-data-quality-standards.md) |
| **DP-02** | CDF enabled on Bronze tables | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **REL-01** | Time Travel retention ≥7 days | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **DL-09** | Never manually modify Delta data files | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) |
| **REL-01** | Enable Delta Lake time travel (≥7 days retention) | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-02** | Configure job retry with exponential backoff | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-03** | Use structured streaming with checkpointing | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-04** | Enable cluster autoscaling for variable workloads | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-05** | Configure auto-termination on all clusters | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-06** | Use cluster pools for faster recovery | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-07** | Implement workspace backup procedures | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-08** | Test disaster recovery procedures quarterly | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-09** | Use managed model serving for production ML | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **ST-01** | Lakeflow SDP First for streaming | [Streaming Production](solution-architecture/data-pipelines/28-streaming-production-patterns.md) |
| **ST-02** | Managed Checkpointing for DR | [Streaming Production](solution-architecture/data-pipelines/28-streaming-production-patterns.md) |
| **ST-04** | Idempotent Operations for streaming | [Streaming Production](solution-architecture/data-pipelines/28-streaming-production-patterns.md) |
| **SC-06** | Pin all custom dependencies with explicit versions | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **SC-08** | Never install PySpark on serverless compute | [Serverless Compute](platform-architecture/11-serverless-compute.md) |

### [Performance Efficiency](https://docs.databricks.com/en/lakehouse-architecture/performance-efficiency/best-practices) (25 rules)

| ID | Rule | Document |
|----|------|----------|
| **DM-01** | Use dimensional modeling (star/snowflake) for Gold layer | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DM-04** | Avoid heavily normalized models (3NF) in analytical layers | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DM-06** | Use enforced constraints (NOT NULL, CHECK) for integrity | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DM-08** | Design for single-table transactions | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DL-05** | Automatic Liquid Clustering (CLUSTER BY AUTO) | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) |
| **DP-06** | Use incremental ingestion (not full loads) | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **CP-08** | Enable Photon for complex transformations | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **DL-08** | Never use Spark caching with Delta tables | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) |
| **DL-10** | Remove legacy Delta configurations on upgrade | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) |
| **DL-12** | Run ANALYZE TABLE on performance-critical tables | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) |
| **DA-01** | Schema extracted from YAML (never generated) | [Gold Layer](solution-architecture/data-pipelines/27-gold-layer-patterns.md) |
| **SA-01** | Silver must use Lakeflow SDP with expectations | [Silver Layer](solution-architecture/data-pipelines/26-silver-layer-patterns.md) |
| **DA-02** | Surrogate keys via MD5 hash | [Gold Layer](solution-architecture/data-pipelines/27-gold-layer-patterns.md) |
| **DA-03** | Always deduplicate before MERGE | [Gold Layer](solution-architecture/data-pipelines/27-gold-layer-patterns.md) |
| **DA-04** | SCD Type 2 for historical dimensions | [Gold Layer](solution-architecture/data-pipelines/27-gold-layer-patterns.md) |
| **PY-04** | No notebook header in importable modules | [Python Development](platform-architecture/20-python-development.md) |
| **SC-05** | Use latest serverless environment version | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **GOV-15** | Keep ABAC UDFs simple, deterministic, and free of external calls | [UC Governance](platform-architecture/15-unity-catalog-governance.md) |

### [Cost Optimization](https://docs.databricks.com/en/lakehouse-architecture/cost-optimization/best-practices) (16 rules)

| ID | Rule | Document |
|----|------|----------|
| **SC-01** | Serverless compute for all jobs | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **SC-02** | Serverless SQL Warehouses for all SQL | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **SC-03** | Serverless Jobs for notebooks and Python | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **SC-04** | Serverless DLT for all pipelines | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **COST-01** | Budget policies for all production workspaces | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **COST-02** | Quarterly cost optimization reviews via system tables | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **COST-03** | Balance always-on vs triggered streaming workloads | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **CP-01** | All classic clusters must use approved policies | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **CP-02** | No unrestricted cluster creation | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **CP-03** | Instance types limited by policy | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **CP-04** | Auto-termination required | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **CP-05** | Jobs compute for scheduled, All-Purpose for exploration | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **CP-06** | Dependencies consistent between All-Purpose and Jobs | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **CP-09** | Right-size clusters based on workload type | [Classic Compute Governance](platform-architecture/13-cluster-policies.md) |
| **ST-03** | Fixed worker count for streaming | [Streaming Production](solution-architecture/data-pipelines/28-streaming-production-patterns.md) |

### [Operational Excellence](https://docs.databricks.com/en/lakehouse-architecture/operational-excellence/best-practices) (28 rules)

| ID | Rule | Document |
|----|------|----------|
| **SC-07** | Use workspace base environments for shared dependencies | [Serverless Compute](platform-architecture/11-serverless-compute.md) |
| **EA-10** | Treat data as a product with defined SLAs and ownership | [Data Governance](enterprise-architecture/01-data-governance.md) |
| **DP-05** | Prefer Lakeflow Connect for ingestion | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **PA-02** | Use system tables for platform observability | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **IN-01** | Serverless compute for all jobs | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-02** | Environment-level dependencies (not task) | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-03** | Use notebook_task (never python_task) | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-04** | Use dbutils.widgets.get() for parameters | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-05** | Hierarchical job architecture | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-06** | Notebooks in exactly ONE atomic job | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-07** | Use run_job_task for job references | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-08** | Include [${bundle.target}] prefix | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **DP-01** | Medallion Architecture required | [Bronze Layer](solution-architecture/data-pipelines/25-bronze-layer-patterns.md) |
| **DP-03** | Preserve source schema | [Bronze Layer](solution-architecture/data-pipelines/25-bronze-layer-patterns.md) |
| **DP-04** | Append-only ingestion | [Bronze Layer](solution-architecture/data-pipelines/25-bronze-layer-patterns.md) |
| **DP-05** | Prefer Lakeflow Connect managed connectors | [Bronze Layer](solution-architecture/data-pipelines/25-bronze-layer-patterns.md) |
| **DP-06** | Use incremental ingestion (not full loads) | [Bronze Layer](solution-architecture/data-pipelines/25-bronze-layer-patterns.md) |
| **MO-01** | Use input_columns=[":table"] for table-level KPIs | [Lakehouse Monitoring](solution-architecture/monitoring/36-lakehouse-monitoring.md) |
| **DB-03** | fieldName must match query alias | [Dashboards](solution-architecture/dashboards/35-aibi-dashboard-patterns.md) |
| **DB-04** | SQL returns raw numbers | [Dashboards](solution-architecture/dashboards/35-aibi-dashboard-patterns.md) |
| **MO-02** | Document monitor output tables for Genie | [Lakehouse Monitoring](solution-architecture/monitoring/36-lakehouse-monitoring.md) |
| **MO-04** | Implement async wait pattern | [Lakehouse Monitoring](solution-architecture/monitoring/36-lakehouse-monitoring.md) |
| **REL-10** | Monitor and manage platform service limits | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **REL-11** | Invest in capacity planning for production workloads | [Reliability & DR](platform-architecture/17-reliability-disaster-recovery.md) |
| **IN-11** | Use `mode: development` / `mode: production` on all targets | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-12** | Set `run_as` to service principal for staging/prod | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |
| **IN-13** | Define top-level `permissions` on all bundles | [Asset Bundles](platform-architecture/19-asset-bundle-standards.md) |

### [Interoperability & Usability](https://docs.databricks.com/en/lakehouse-architecture/interoperability-and-usability/best-practices) (28 rules)

| ID | Rule | Document |
|----|------|----------|
| **DM-09** | Design Gold layer for both BI and AI consumption | [Data Modeling](enterprise-architecture/04-data-modeling.md) |
| **DL-04** | All tables use Delta Lake | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **PA-04** | Use Lakehouse Federation for external data access | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **PA-05** | Use certified partner integrations | [Platform Overview](platform-architecture/10-platform-overview.md) |
| **DL-11** | Enable UniForm for cross-engine interoperability | [UC Tables & Delta Lake](platform-architecture/12-unity-catalog-tables.md) |
| **MV-01** | All core metrics must be in Metric Views | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **TF-01** | STRING for date parameters in TVFs | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) |
| **TF-02** | Schema validation before SQL | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) |
| **TF-03** | v3.0 comment format for Genie | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) |
| **MV-05** | No transitive joins in Metric Views | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **GN-01** | Inventory-first creation for Genie Spaces | [Genie Space Patterns](solution-architecture/semantic-layer/32-genie-space-patterns.md) |
| **TF-04** | Required parameters before optional | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) |
| **TF-05** | No LIMIT with parameters in TVFs | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) |
| **TF-06** | Single aggregation pass | [TVF Patterns](solution-architecture/semantic-layer/31-tvf-patterns.md) |
| **MV-01** | All core metrics MUST be in Metric Views | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-02** | Reference Gold layer tables only | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-03** | Business context documentation required | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-04** | Schema validation before creation | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-05** | No transitive joins | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-06** | Synonyms for all dimensions/measures | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-07** | Display format for all measures | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **MV-08** | Structured comment format | [Metric View Patterns](solution-architecture/semantic-layer/30-metric-view-patterns.md) |
| **DS-01** | Unity Catalog for all shared assets | [Delta Sharing](solution-architecture/data-sharing/60-delta-sharing-patterns.md) |
| **DS-02** | Prefer Databricks-to-Databricks sharing | [Delta Sharing](solution-architecture/data-sharing/60-delta-sharing-patterns.md) |
| **DS-03** | Never share PII without filters | [Delta Sharing](solution-architecture/data-sharing/60-delta-sharing-patterns.md) |
| **DS-04** | Define retention/revocation policies | [Delta Sharing](solution-architecture/data-sharing/60-delta-sharing-patterns.md) |
| **DS-05** | Enable audit logging for sharing | [Delta Sharing](solution-architecture/data-sharing/60-delta-sharing-patterns.md) |
| **DB-01** | No hardcoded environment values in dashboards | [Dashboards](solution-architecture/dashboards/35-aibi-dashboard-patterns.md) |

---

## Templates

| Template | Purpose | When to Use |
|----------|---------|-------------|
| [Architecture Review](templates/architecture-review-checklist.md) | Pre-implementation review | Before starting new project |
| [Deployment Checklist](templates/deployment-checklist.md) | Pre-deployment validation | Before every deployment |
| [Verification Checklist](templates/verification-checklist.md) | Golden rules compliance | Pre-deployment & audits |
| [Exception Request](templates/exception-request-form.md) | Rule exception approval | When deviating from standards |
| [Compliance Report](templates/compliance-report-template.md) | Periodic compliance review | Monthly/Quarterly audits |

---

## Reference Materials

| Document | Content |
|----------|---------|
| [Glossary](appendix/glossary.md) | 50+ terms, acronyms, rule IDs |
| [Quick Reference Cards](appendix/quick-reference-cards.md) | 13 one-page cheat sheets |

---

## Document Statistics

| Metric | Count |
|--------|-------|
| Total Documents | 40 |
| Architecture Domains | 3 |
| Enterprise Architecture Docs | 8 |
| Platform Architecture Docs | 10 |
| Solution Architecture Docs | 15 |
| Training Modules | 5 |
| Golden Rules | 155+ |
| Templates | 5 |
| Total Training Hours | 40 |

---

## Contributing

1. Follow naming convention: `XX-kebab-case-name.md`
2. Include Document Information header
3. Add to appropriate architecture domain
4. Update this README navigation
5. Submit PR for review

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 5.4 | Feb 2026 | **v5.4.0 Solution Architecture Rationalization**: Eliminated 40 duplicate/overlapping rules from SA. Deleted 3 pure-duplicate documents. Retired BP and SL prefixes. Renumbered DA (6→4), ST (6→4), GS (8→7). Relocated MO-05/06 to REL-10/11. Added Prerequisites sections to all 15 SA docs. Framework: 31 prefixes, 155+ rules. |
| 5.3 | Feb 2026 | **v5.3.0 Rule ID Rationalization**: Comprehensive renumbering of all golden rule IDs across 43 documents for consistency and clarity. Key prefix changes: PA-01/02 → DL-01/DL-04, PA-03/03a-h → SC-01..09, PA-18..21 → CP-01..09, PA-13..17 → PA-01..05 (renumbered), old DL-01..03 retired (merged into new DL numbering), DL-04..08 → DL-08..12, DA-03..06 (silver) → SA-01..04, DA-05..08 (gold) → DA-03..06, SL-02..09 → TF-01..06/GN-01..03/SL-02, MO-02..03 → DB-03..04, MO-05..07 → MO-02..04, IN-09..10 → MO-05..06, ML-16..18 → ML-07..09, ML-04..07 (doc 51) → GA-01..04, ML-08..15 (doc 52/53) → GS-01..08/AG-01..05. New prefixes introduced: SC (Serverless Compute), CP (Classic Compute Policies), SA (Silver Architecture), TF (TVF), GN (Genie), GA (GenAI Agents), GS (GenAI Standards), AG (AI Gateway), PY (Python Development). Total: 165+ golden rules. |
| 5.2 | Feb 2026 | **WAF Link Validation & Gap Closure**: Replaced all generic pillar-level WAF URLs with specific, verifiable references using a three-tier strategy: T1 (WAF anchor with deep-linkable section), T2 (specific Databricks docs page), T3 (authoritative blog/learn). Fixed URL paths (`security-compliance-privacy` → `security-compliance-and-privacy`, `interoperability` → `interoperability-and-usability`). Dropped `.html` extensions. **Gap Closure**: Added 9 new rules to cover previously unmapped WAF best practices: GOV-11 (audit logging), SEC-09 (SIEM integration), REL-09 (managed model serving), DL-08 (ANALYZE TABLE), CMP-06 (auto-termination), COST-03 (streaming cost balance), PA-17 (partner integrations), IN-09 (service limits), IN-10 (capacity planning). Updated README cross-reference with all new rules and corrected pillar counts. Total: 142+ golden rules. |
| 5.1 | Feb 2026 | **Well-Architected Lakehouse Alignment**: Added WAF Pillar column with hyperlinks to all 34 golden rules tables. Regrouped multi-pillar documents by WAF pillar. Added "Rules by WAF Pillar" cross-reference section to README (pillar-first navigation). **Gap Closure**: Added PA-16 (Lakehouse Federation), COST-01 (Budget Policies), COST-02 (Quarterly Cost Reviews), GOV-10 (Row Filters and Column Masks), SEC-08 (Compliance Security Profile). Elevated CMP-04 (Photon) from Recommended to Required. **Cloud-Agnostic**: Updated network security document with AWS/GCP equivalents (VNet→VPC, Azure Private Link→AWS PrivateLink/GCP PSC, Azure Key Vault→AWS KMS/GCP Cloud KMS). Updated Well-Architected reference URLs to cloud-agnostic docs.databricks.com. Total: 5 new rules, 1 elevation, 133+ golden rules. |
| 5.0 | Feb 2026 | **Enterprise Architecture Enhancement**: Added Data as a Product (EA-10), Data Contracts (EA-11), AI Readiness Assessment (EA-12) to governance framework. Strengthened federated governance model. Added Domain Product Owner role. **Platform Architecture Enhancement**: Added DBFS root prohibition (PA-13), System Tables observability (PA-14), Workspace Isolation Strategy (PA-15). Added Well-Architected Lakehouse pillar alignment. Added Delta UniForm for interoperability (DL-07). **Governance Enhancement**: Added Lineage-driven governance (GOV-08), Governance-as-code (GOV-09) with automated compliance checks. **AI/GenAI Enhancement**: Added Responsible AI practices (ML-14), AI-Data lifecycle integration (ML-15). Strengthened agent governance with safety, PII, and bias monitoring. **Data Modeling Enhancement**: Added BI+AI dual-use design (DM-09) for Gold layer. **New Document**: Created `08-architecture-evolution.md` covering L1→L2→L3 maturity model, 7 decision heuristics (when NOT to use medallion, workspace splitting, centralize vs federate, DLT vs streaming, custom vs managed AI, batch vs streaming), anti-patterns reference. Total: 15 new golden rules, 1 new document. |
| 4.6 | Feb 2026 | **Data Quality Standards**: Created `07-data-quality-standards.md` covering DLT Expectations (pipeline validation), DQX Library (classic Spark jobs), and Lakehouse Monitoring (time-series trends, drift detection). Added 4 new golden rules (DQ-01 to DQ-04). Updated tagging standards to focus on UC governed tags, workflow tags, and serverless budget policies. |
| 4.5 | Feb 2026 | **Naming, Comments & Tagging Standards**: Created `05-naming-comment-standards.md` (naming conventions, SQL block comments, COMMENT patterns, TVF v3.0 format) and `06-tagging-standards.md` (workflow tags, UC governed tags, serverless budget policies). Added 10 new golden rules (NC-01 to NC-03, CM-01 to CM-04, TG-01 to TG-03). |
| 4.4 | Feb 2026 | **Reorganized for Confluence**: Moved platform-level concerns (`15-unity-catalog-governance.md`, `17-delta-lake-best-practices.md`) from solution-architecture to platform-architecture. Rewrote all 40 documents to Confluence-friendly format with simplified headers, golden rules summary tables, concise sections, and validation checklists. Added `53-ai-gateway-patterns.md` and `60-delta-sharing-patterns.md`. Removed empty governance/ and compute/ folders from solution-architecture. |
| 4.3 | Feb 2026 | **Added Reliability, Security & CI/CD best practices**: Created `17-reliability-disaster-recovery.md` (HA, DR, time travel, checkpointing), `18-network-security.md` (VNet, Private Link, CMK, IP access lists). Enhanced `19-asset-bundle-standards.md` with CI/CD workflows, branching strategy, and MLOps patterns. Added 15 new golden rules (REL-01 to REL-08, SEC-01 to SEC-07). Based on Microsoft Learn Well-Architected Framework, CI/CD best practices, and notebook engineering documentation. |
| 4.2 | Feb 2026 | **Reorganized best practices into categories**: Split comprehensive best practices into 4 focused documents for better discoverability: `13-delta-lake-best-practices.md` (data-pipelines), `28-streaming-production-patterns.md` (data-pipelines), `20-unity-catalog-governance.md` (new governance folder), `21-compute-configuration.md` (new compute folder). Added 6 additional governance rules (GOV-01 to GOV-05, CMP-01 to CMP-04). |
| 4.1 | Feb 2026 | **New document**: Added comprehensive best practices from official Databricks documentation covering Delta Lake, Structured Streaming production, Unity Catalog governance, and compute configuration. 10 new golden rules (BP-01 through BP-10). |
| 4.0 | Feb 2026 | **Major enhancement** - Integrated official Microsoft Learn documentation (10+ pages) covering: High-level architecture (control plane vs compute plane), Medallion architecture best practices, Unity Catalog governance, ACID guarantees, Single Source of Truth, Performance/Cost/Reliability best practices. Updated 8 core documents. |
| 3.0 | Jan 2026 | Reorganized into 3-tier architecture |
| 2.1 | Jan 2026 | Added Enterprise/Platform/Solution structure |
| 2.0 | Jan 2026 | Major expansion with 50+ rules |
| 1.0 | Jan 2026 | Initial golden rules documentation |
