# Enterprise Data Platform Training Curriculum

## Onboarding Program for Data Engineers

**Duration:** 2 weeks (40 hours)  
**Format:** Self-paced with hands-on labs  
**Prerequisites:** SQL basics, Python fundamentals, cloud concepts

---

## Learning Path Overview

```
Week 1: Foundations & Core Concepts
├── Module 1: Platform Foundations (8 hours)
│   ├── Day 1: Unity Catalog & Governance
│   └── Day 2: Medallion Architecture
│
├── Module 2: Data Engineering (12 hours)
│   ├── Day 3: Bronze Layer Patterns
│   ├── Day 4: Silver Layer & DLT
│   └── Day 5: Delta Lake Deep Dive

Week 2: Advanced Patterns & Operations
├── Module 3: Gold Layer & Semantic (12 hours)
│   ├── Day 6: Dimensional Modeling
│   ├── Day 7: Semantic Layer (TVFs, Metric Views)
│   └── Day 8: Query Optimization
│
└── Module 4: Operations & Best Practices (8 hours)
    ├── Day 9: Asset Bundles & Deployment
    └── Day 10: Monitoring & Troubleshooting
```

---

## Module Breakdown

### Module 1: Platform Foundations (8 hours)

**Objective:** Understand the enterprise data platform architecture and governance framework.

| Topic | Duration | Hands-On Lab |
|-------|----------|--------------|
| Unity Catalog Overview | 1 hour | Explore catalog, schemas, tables |
| Access Control & RBAC | 1 hour | Grant/revoke permissions |
| Data Classification & Tags | 1 hour | Apply PII and domain tags |
| Lineage & Auditing | 1 hour | Trace data flow |
| Medallion Architecture | 2 hours | Design layer strategy |
| Golden Rules Introduction | 2 hours | Review all 10 rules |

**Certification:** Platform Foundations Quiz (80% pass rate)

---

### Module 2: Data Engineering Best Practices (12 hours)

**Objective:** Master Bronze and Silver layer implementation patterns.

| Topic | Duration | Hands-On Lab |
|-------|----------|--------------|
| Bronze Layer Ingestion | 2 hours | Create Bronze tables |
| Change Data Feed (CDF) | 1 hour | Enable and consume CDF |
| DLT Pipeline Design | 3 hours | Build streaming pipeline |
| Data Quality Expectations | 2 hours | Implement expect_or_drop |
| Quarantine Patterns | 2 hours | Capture failed records |
| Deduplication Strategies | 2 hours | Implement deduplication |

**Certification:** Data Engineering Practical Assessment

---

### Module 3: Gold Layer & Semantic (12 hours)

**Objective:** Build business-ready Gold layer with semantic layer components.

| Topic | Duration | Hands-On Lab |
|-------|----------|--------------|
| Dimensional Modeling | 3 hours | Design star schema |
| SCD Type 1 & Type 2 | 2 hours | Implement both patterns |
| PK/FK Constraints | 1 hour | Apply constraints |
| Delta MERGE Operations | 2 hours | Build MERGE pipelines |
| Table-Valued Functions | 2 hours | Create Genie-ready TVFs |
| Metric Views | 2 hours | Build YAML metric views |

**Certification:** Gold Layer Implementation Project

---

### Module 4: Operations & Best Practices (8 hours)

**Objective:** Deploy and operate production data pipelines.

| Topic | Duration | Hands-On Lab |
|-------|----------|--------------|
| Asset Bundles Deep Dive | 2 hours | Create complete bundle |
| Serverless Compute | 1 hour | Configure serverless jobs |
| Deployment Workflows | 2 hours | Deploy to dev/prod |
| Monitoring & Alerting | 2 hours | Set up Lakehouse Monitoring |
| Troubleshooting Guide | 1 hour | Debug common issues |

**Certification:** End-to-End Deployment Project

---

## Assessment & Certification

### Knowledge Assessments

| Assessment | Type | Passing Score |
|------------|------|---------------|
| Module 1 Quiz | Multiple choice | 80% |
| Module 2 Quiz | Multiple choice | 80% |
| Module 3 Quiz | Multiple choice | 80% |
| Module 4 Quiz | Multiple choice | 80% |

### Practical Assessments

| Project | Scope | Evaluation Criteria |
|---------|-------|---------------------|
| Bronze Pipeline | Create ingestion pipeline | Schema compliance, CDF enabled |
| Silver DLT Pipeline | Build streaming pipeline | Expectations, deduplication |
| Gold Layer | Implement star schema | Constraints, documentation |
| Full Deployment | End-to-end pipeline | Asset Bundle, production-ready |

### Certification Levels

| Level | Requirements | Badge |
|-------|--------------|-------|
| **Associate** | Pass all quizzes | Bronze Badge |
| **Professional** | Pass quizzes + 2 projects | Silver Badge |
| **Expert** | Pass all + mentor others | Gold Badge |

---

## Learning Resources

### Required Reading
1. [Golden Rules Document](../01-golden-rules-enterprise-data-platform.md)
2. Official Databricks Documentation
3. Internal coding standards

### Reference Materials
- [Process Documents](../processes/) - RACI and workflows
- [Appendices](../appendices/) - Templates and checklists
- Databricks Academy courses

### Support Channels
- Data Platform Slack channel
- Office hours (Tuesdays/Thursdays)
- Mentorship program

---

## Onboarding Schedule Template

### Week 1: Foundations

| Day | Morning (4 hours) | Afternoon (4 hours) |
|-----|-------------------|---------------------|
| Mon | Unity Catalog + Governance | Medallion Architecture |
| Tue | Bronze Layer Patterns | Bronze Lab |
| Wed | DLT Pipeline Design | Silver Lab |
| Thu | Data Quality Expectations | Quarantine Lab |
| Fri | Delta Lake Deep Dive | CDF + Deduplication Lab |

### Week 2: Advanced

| Day | Morning (4 hours) | Afternoon (4 hours) |
|-----|-------------------|---------------------|
| Mon | Dimensional Modeling | Star Schema Lab |
| Tue | SCD Types + MERGE | Gold MERGE Lab |
| Wed | TVFs + Metric Views | Semantic Layer Lab |
| Thu | Asset Bundles | Deployment Lab |
| Fri | Final Project | Certification Review |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Completion Rate | 95% | Tracking system |
| Quiz Pass Rate | 90% | Assessment scores |
| Time to First Production PR | < 3 weeks | Code review system |
| Mentor Satisfaction | 4.5/5 | Survey |
| New Hire Satisfaction | 4.5/5 | Survey |

---

**Next Steps:**
- [Module 1: Platform Foundations](./71-module-platform-foundations.md)
- [Module 2: Data Engineering](./72-module-data-engineering.md)
- [Module 3: Gold Layer & Semantic](./73-module-gold-layer-semantic.md)
- [Module 4: Operations](./74-module-operations-deployment.md)
