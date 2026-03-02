# New Hire Onboarding - Week 1

## Welcome to the Data Platform Team! 🎉

**Duration:** Week 1 (Days 1-5)  
**Goal:** Understand our platform, standards, and complete environment setup

---

## Day 1: Platform Overview & Access

### Morning: Welcome & Introduction (2 hours)

**Objective:** Understand our mission and team structure.

1. **Meet Your Mentor** - Schedule intro call
2. **Team Overview** - Review [Roles & Responsibilities](../part4-process-governance/31-roles-responsibilities-raci.md)
3. **Platform Vision** - Read [Platform Architecture](../part1-platform-foundations/01-platform-architecture.md)

### Afternoon: Access Setup (3 hours)

**Objective:** Get access to all required systems.

| System | Request Via | Expected Time |
|--------|-------------|---------------|
| Databricks Workspace | IT Ticket | Same day |
| Unity Catalog Access | Data Steward | 1-2 days |
| Git Repository | Team Lead | Same day |
| Confluence | IT Ticket | Same day |
| Slack Channels | Self-service | Immediate |

**Join These Slack Channels:**
- `#data-platform-general` - Announcements
- `#data-platform-help` - Questions
- `#data-engineering` - Technical discussions
- `#ml-engineering` - ML-specific topics
- `#data-quality` - Quality alerts

### Day 1 Checklist
- [ ] Completed welcome meeting with mentor
- [ ] Requested all system access
- [ ] Read Platform Architecture document
- [ ] Joined Slack channels

---

## Day 2: Core Concepts

### Morning: Architecture Deep Dive (3 hours)

**Objective:** Understand our technical architecture.

**Reading Assignment:**

1. **Medallion Architecture** - [03-medallion-architecture.md](../part1-platform-foundations/03-medallion-architecture.md)
   - Bronze: Raw data ingestion
   - Silver: Validated, cleaned data
   - Gold: Business-ready entities

2. **Unity Catalog Governance** - [02-unity-catalog-governance.md](../part1-platform-foundations/02-unity-catalog-governance.md)
   - Catalog/Schema organization
   - Access control model
   - Tagging standards

### Afternoon: Golden Rules Overview (2 hours)

**Objective:** Understand our non-negotiable standards.

**Reading Assignment:**

Review the [README](../README.md) and understand:
- Rule categories (Platform, Data Architecture, Semantic, ML, Monitoring, Infrastructure)
- Severity levels (🔴 Critical, 🟡 Required, 🟢 Recommended)
- How to navigate documentation

### Knowledge Check - Day 2

**Answer these questions (discuss with mentor):**

1. What are the three layers in our Medallion Architecture?
2. Why do we require Delta Lake for all tables?
3. What does "CLUSTER BY AUTO" mean and why do we use it?
4. What is Unity Catalog and why is it important?

### Day 2 Checklist
- [ ] Read Medallion Architecture
- [ ] Read Unity Catalog Governance
- [ ] Completed Knowledge Check with mentor
- [ ] Databricks workspace access confirmed

---

## Day 3: Development Standards - Part 1

### Morning: Data Pipeline Standards (3 hours)

**Objective:** Understand how we build data pipelines.

**Reading Assignment:**

1. **Bronze Layer** - [25-bronze-layer-patterns.md](../solution-architecture/data-pipelines/25-bronze-layer-patterns.md)
   - CDF (Change Data Feed) requirements
   - Table properties
   - Faker data generation for testing

2. **Silver Layer** - [26-silver-layer-patterns.md](../solution-architecture/data-pipelines/26-silver-layer-patterns.md)
   - DLT (Delta Live Tables) patterns
   - Expectations and quality rules
   - DQX framework basics

### Afternoon: Gold Layer Standards (2 hours)

**Reading Assignment:**

3. **Gold Layer** - [27-gold-layer-patterns.md](../solution-architecture/data-pipelines/27-gold-layer-patterns.md)
   - YAML-driven schema management (critical!)
   - MERGE deduplication pattern
   - PK/FK constraints

### Key Concepts to Understand

**YAML-Driven Development:**
```
Schema Source of Truth:
gold_layer_design/yaml/{domain}/{table}.yaml

NOT:
- Hardcoded in Python
- Generated from memory
- Assumed from Silver
```

**Deduplication Before MERGE:**
```python
# ALWAYS deduplicate before MERGE
silver_df = (
    silver_raw
    .orderBy(col("processed_timestamp").desc())
    .dropDuplicates([business_key])  # Key must match MERGE key
)
```

### Knowledge Check - Day 3

1. What file should you check before writing Gold layer SQL?
2. Why do we deduplicate before MERGE?
3. What is a DLT expectation?
4. Why is CDF (Change Data Feed) important for Bronze?

### Day 3 Checklist
- [ ] Read Bronze, Silver, Gold layer standards
- [ ] Understand YAML-driven development
- [ ] Understand deduplication pattern
- [ ] Completed Knowledge Check

---

## Day 4: Infrastructure Standards

### Morning: Asset Bundles (3 hours)

**Objective:** Understand how we deploy code.

**Reading Assignment:**

1. **Asset Bundle Standards** - [19-asset-bundle-standards.md](../platform-architecture/19-asset-bundle-standards.md)
   - Serverless environment configuration
   - notebook_task vs python_task (CRITICAL!)
   - Parameter passing (dbutils.widgets.get)
   - Hierarchical job architecture

### Critical Pattern: Parameter Passing

```python
# ❌ WRONG: argparse fails in DABs
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--catalog")
args = parser.parse_args()  # ERROR!

# ✅ CORRECT: dbutils.widgets.get
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
```

### Afternoon: Python Development (2 hours)

**Reading Assignment:**

2. **Python Development Standards** - [20-python-development.md](../platform-architecture/20-python-development.md)
   - Pure Python files vs notebooks
   - sys.path setup for imports
   - Module organization

### Knowledge Check - Day 4

1. Why do we use `notebook_task` instead of `python_task`?
2. How do you pass parameters in Asset Bundle jobs?
3. What is the hierarchical job architecture?
4. When should you use a pure Python file vs a notebook?

### Day 4 Checklist
- [ ] Read Asset Bundle standards
- [ ] Read Python Development standards
- [ ] Understand parameter passing pattern
- [ ] Cloned team Git repository

---

## Day 5: Hands-On Setup

### Morning: Local Environment Setup (3 hours)

**Objective:** Set up your development environment.

**Step 1: Install Tools**

```bash
# Install Databricks CLI
brew install databricks-cli  # macOS
# or
pip install databricks-cli

# Verify installation
databricks --version
```

**Step 2: Configure Authentication**

```bash
# Login to Databricks
databricks auth login --host https://your-workspace.databricks.com

# Verify
databricks auth profiles
```

**Step 3: Clone Repository**

```bash
# Clone project repository
git clone https://github.com/your-org/your-project.git
cd your-project

# Install Python dependencies
pip install -r requirements.txt
```

**Step 4: Validate Bundle**

```bash
# Validate Asset Bundle configuration
databricks bundle validate

# Expected output: "Validation successful"
```

### Afternoon: First Deployment (2 hours)

**Objective:** Deploy your first job.

**Step 1: Review Configuration**

```bash
# Look at databricks.yml
cat databricks.yml

# Look at job definitions
ls resources/
```

**Step 2: Deploy to Dev**

```bash
# Deploy to dev environment
databricks bundle deploy -t dev

# Expected: Resources deployed successfully
```

**Step 3: Run a Test Job**

```bash
# Run a simple job
databricks bundle run -t dev <job_name>

# Check job status in UI
```

### Day 5 Checklist
- [ ] Databricks CLI installed and configured
- [ ] Repository cloned
- [ ] Bundle validation successful
- [ ] First deployment completed
- [ ] First job run successful

---

## Week 1 Summary

### What You Learned

| Day | Topic | Key Takeaway |
|-----|-------|--------------|
| 1 | Platform Overview | Our architecture and team structure |
| 2 | Core Concepts | Medallion Architecture + Unity Catalog |
| 3 | Data Standards | YAML-driven development, MERGE patterns |
| 4 | Infrastructure | Asset Bundles, parameter passing |
| 5 | Hands-On | Local setup and first deployment |

### Critical Rules to Remember

1. **All data in Unity Catalog** - No HMS, no external tables
2. **All tables use Delta Lake** - No Parquet, CSV, JSON
3. **YAML is source of truth** - Never hardcode schemas
4. **Always deduplicate before MERGE** - Prevents duplicate errors
5. **Use dbutils.widgets.get()** - Never argparse in notebooks
6. **Use notebook_task** - Never python_task in DABs

### Week 1 Completion Checklist

- [ ] All Day 1-5 checklists completed
- [ ] All knowledge checks passed (discuss with mentor)
- [ ] Local environment fully configured
- [ ] First deployment successful
- [ ] Scheduled Week 2 kickoff with mentor

---

## Resources for Self-Study

### Documentation
- [Databricks Documentation](https://docs.databricks.com/)
- [Delta Lake Guide](https://docs.delta.io/)
- [MLflow Documentation](https://mlflow.org/docs/latest/)

### Internal Resources
- [Enterprise Golden Rules](../README.md)
- [Project README](../../README.md)
- [QUICKSTART Guide](../../QUICKSTART.md)

### Databricks Academy Courses
- Unity Catalog Fundamentals
- Delta Live Tables Essentials
- Building Data Pipelines with Delta Lake

---

## Getting Help

| Type of Help | Where to Go |
|--------------|-------------|
| Quick questions | Slack: #data-platform-help |
| Detailed guidance | Your assigned mentor |
| Access issues | IT Support ticket |
| Architecture decisions | Platform Lead |
| Code review | Team Lead |

---

## Next Week Preview

**Week 2** will focus on hands-on practice:
- Build your first Bronze → Silver → Gold pipeline
- Create your first DLT table with expectations
- Deploy a complete workflow
- Submit your first PR

See: [New Hire Week 2](81-new-hire-week2.md)
