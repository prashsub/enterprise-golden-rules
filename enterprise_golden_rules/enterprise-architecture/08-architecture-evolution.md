# Architecture Evolution & Decision Heuristics

> **Document Owner:** Platform Architecture Team | **Status:** Approved | **Last Updated:** February 2026

## Overview

This document provides architecture maturity guidance and decision heuristics for evolving from a foundational data platform to an AI-native enterprise. It helps architects make principled decisions about when to apply or deviate from standard patterns.

---

## Architecture Maturity Levels

### Level 1: Foundational Enterprise

**Characteristics:** Centralized team, batch workloads, basic governance.

| Aspect | State |
|--------|-------|
| **Governance** | Unity Catalog enabled, basic permissions |
| **Data Architecture** | Medallion architecture (Bronze/Silver/Gold) |
| **Compute** | Mix of classic and serverless |
| **CI/CD** | Manual or basic Asset Bundle deployments |
| **AI/ML** | Ad-hoc notebooks, no model registry |
| **Observability** | Job alerts only |

**Priority Actions:**
1. Migrate all tables to Unity Catalog managed tables
2. Establish naming and tagging standards
3. Enable predictive optimization and CLUSTER BY AUTO
4. Implement basic Asset Bundle CI/CD

---

### Level 2: Scaled Data Platform

**Characteristics:** Multiple domains, self-service teams, data products emerging.

| Aspect | State |
|--------|-------|
| **Governance** | Federated with central standards, governed tags, SCIM |
| **Data Architecture** | Domain-aligned Gold layers, data contracts |
| **Compute** | Serverless-first, budget policies enforced |
| **CI/CD** | Automated multi-environment deployments |
| **AI/ML** | Feature tables in UC, MLflow tracking, model registry |
| **Observability** | System tables dashboards, Lakehouse Monitoring |

**Priority Actions:**
1. Define data products with SLAs and ownership (EA-10)
2. Implement data contracts for cross-domain interfaces (EA-11)
3. Automate governance checks via system tables (GOV-09)
4. Deploy Lakehouse Monitoring with custom metrics
5. Establish feature tables derived from Gold layer (DM-09)

---

### Level 3: AI-Native Enterprise

**Characteristics:** AI embedded in products, agents in production, data and AI lifecycle unified.

| Aspect | State |
|--------|-------|
| **Governance** | Lineage-driven, policy-as-code, automated compliance |
| **Data Architecture** | Data products serving both BI and AI, feature stores |
| **Compute** | Fully serverless, cost-optimized with budget policies |
| **CI/CD** | MLOps integrated, model + data pipeline promotion together |
| **AI/ML** | Production agents, evaluation pipelines, responsible AI |
| **Observability** | End-to-end lineage, AI monitoring, cost optimization |

**Priority Actions:**
1. Unify data and AI lifecycle (GS-07)
2. Deploy production agents with responsible AI practices (GS-06)
3. Implement AI Gateway with guardrails for all serving endpoints
4. Enable continuous model evaluation and monitoring
5. Assess AI readiness across all domains (EA-12)

---

## Architecture Decision Heuristics

### When NOT to Use Medallion Layers

The Medallion architecture (Bronze/Silver/Gold) is the default pattern, but not every workload needs all three layers.

| Scenario | Recommendation |
|----------|----------------|
| **Simple reference data** (country codes, currencies) | Load directly to Gold — no transformation needed |
| **Pre-cleaned SaaS data** (Lakeflow Connect with governed source) | Bronze + Gold — Silver adds no value if source is clean |
| **Real-time feature serving** | Bronze → Feature table — skip Gold if latency matters |
| **Exploratory/sandbox data** | Bronze only — no need for downstream layers |
| **Complex multi-hop transformations** | Full medallion — progressive refinement is valuable |

**Principle:** Use as many layers as add value. The medallion pattern is a guide, not a mandate. Each layer should have a clear purpose.

---

### When to Split Workspaces

| Split When | Don't Split When |
|-----------|-----------------|
| Different security/network requirements (VNet isolation) | Cost attribution is the only driver (use budget policies) |
| Regulatory isolation required (HIPAA, PCI-DSS) | Teams want "their own workspace" for preference |
| Production vs non-production environment segregation | Schema-level access control is sufficient (use UC grants) |
| Independent admin control needed (acquired company) | Different compute needs (use cluster policies instead) |
| Cloud region requirements differ | Team size alone (UC handles multi-team governance) |

**Principle:** Workspaces are a security and operations boundary, not an organizational boundary. Unity Catalog provides cross-workspace governance.

---

### When to Centralize vs Federate Governance

| Centralize | Federate |
|-----------|----------|
| Security baselines (VNet, Private Link, SCIM) | Data quality rules (domain teams know their data) |
| Naming and tagging standards | Access decisions for domain data |
| Compute policies and budget policies | Data modeling choices within the domain |
| Identity management (IdP, SCIM) | Data product SLAs and freshness targets |
| Network security and encryption | Domain-specific business logic |
| Compliance and audit requirements | Schema evolution within data contracts |

**Principle:** Centralize what must be consistent across the organization. Federate what requires domain expertise to define correctly.

---

### When to Use DLT/SDP vs Raw Structured Streaming

| Use Lakeflow SDP (Default) | Use Raw Structured Streaming (Exception) |
|---------------------------|----------------------------------------|
| Standard ingestion and transformation | Custom stateful processing (custom state stores) |
| Declarative quality expectations | Non-Delta sinks (JDBC, external systems) |
| Managed checkpointing and recovery | Advanced watermark/windowing logic |
| Teams with mixed SQL/Python skills | Legacy streaming code in migration |

**Principle:** Lakeflow SDP is the default. Raw Structured Streaming requires documented justification and Platform Architect approval.

---

### When to Build Custom AI vs Use Managed Services

| Use Managed Service First | Build Custom Agent |
|--------------------------|-------------------|
| Document Q&A → Knowledge Assistant | Complex multi-step workflows with external tool calls |
| Data analytics → Genie Spaces | Custom state management or memory requirements |
| Agent orchestration → Multi Agent Supervisor | Proprietary model fine-tuning requirements |
| Quick prototyping → AI Playground | Integration with non-Databricks systems |

**Principle:** Evaluate managed services first (GS-01). Document justification for custom development including which managed services were evaluated and why they don't meet requirements.

---

### Batch vs Streaming Decision

| Use Batch | Use Streaming |
|-----------|---------------|
| Data freshness SLA > 1 hour | Data freshness SLA < 15 minutes |
| Source provides periodic exports | Source provides change events (CDC, Kafka) |
| Workload is aggregation-heavy | Workload is append/update-heavy |
| Cost sensitivity is high | Latency sensitivity is high |

**Principle:** Default to triggered batch (availableNow=True) unless the business requires sub-hour freshness. Streaming costs more and adds operational complexity.

---

## Reference Architecture Alignment

Map golden rules to architecture layers:

| Architecture Layer | Key Golden Rules | Documents |
|-------------------|-----------------|-----------|
| **Enterprise Architecture** | EA-01..12, DM-01..09, NC, CM, TG, DQ | [Data Governance](01-data-governance.md), [Data Modeling](04-data-modeling.md) |
| **Platform Architecture** | PA-01..05, SC-01..09, DL-01..12, CP-01..09, GOV-01..16, SEC-01..09, REL-01..09 | [Platform Overview](../platform-architecture/10-platform-overview.md), [UC Governance](../platform-architecture/15-unity-catalog-governance.md) |
| **Solution Architecture** | DP-01..06, SA-01..04, DA-01..06, ST-01..06, MV-01..08, TF-01..06, GN, DB, MO | [Data Pipelines](../solution-architecture/data-pipelines/), [Semantic Layer](../solution-architecture/semantic-layer/) |
| **Data & AI Architecture** | ML-01..09, GA-01..04, GS-01..08, AG-01..05, DS-01..07 | [ML/AI](../solution-architecture/ml-ai/), [Delta Sharing](../solution-architecture/data-sharing/) |

---

## Anti-Patterns Across All Layers

| Anti-Pattern | Why It's Wrong | Better Approach |
|-------------|---------------|-----------------|
| **Platform sprawl** — separate tools for ETL, BI, ML, governance | Increases cost, reduces governance, fragments lineage | Unify on Lakehouse with Unity Catalog |
| **Governance as afterthought** — add security after building | Retrofit is expensive, gaps are inevitable | Governance-first design (UC from day one) |
| **Over-engineering medallion** — 5+ layers for simple data | Adds latency and maintenance without value | Use only layers that add quality/value |
| **Manual operations** — hand-running OPTIMIZE, VACUUM, partition management | Error-prone, doesn't scale, wastes engineer time | Predictive optimization + CLUSTER BY AUTO |
| **Individual ownership** — one person owns critical assets | Bus factor of 1, blocks on vacation/departure | Group ownership for all UC objects |
| **Static tokens for CI/CD** — long-lived PATs in GitHub secrets | Security risk, no rotation, no audit | Workload identity federation (OIDC) |
| **Custom everything** — building agents/pipelines from scratch | High maintenance, lower reliability | Evaluate managed services first |

---

## Related Documents

- [Data Governance](01-data-governance.md)
- [Platform Overview](../platform-architecture/10-platform-overview.md)
- [Unity Catalog Governance](../platform-architecture/15-unity-catalog-governance.md)
- [GenAI Standards](../solution-architecture/ml-ai/52-genai-standards.md)
- [Streaming Patterns](../solution-architecture/data-pipelines/28-streaming-production-patterns.md)

---

## References

- [Databricks Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-databricks)
- [Data Mesh Principles](https://www.datamesh-architecture.com/)
- [Medallion Architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion)
- [Unity Catalog Best Practices](https://docs.databricks.com/en/data-governance/unity-catalog/best-practices.html)
