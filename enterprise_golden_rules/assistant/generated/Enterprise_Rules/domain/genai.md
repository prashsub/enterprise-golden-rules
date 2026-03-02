# GenAI & Agent Golden Rules
**Rules:** GS-01..07, AG-01..05 | **Count:** 12 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| GS-01 | Evaluate managed services before custom dev | Critical | Knowledge Assistant / Genie evaluated? |
| GS-02 | Create evaluation dataset before development | Critical | Min 50 records with expected_response? |
| GS-03 | Pass LLM judge thresholds before production | Critical | Safety 100%, Relevance >= 0.80? |
| ~~GS-04~~ | *Retired -- duplicate of ML-07. See ML/AI Governance domain.* | -- | -- |
| GS-04 | Enable production monitoring | Required | Online scorers + payload logging active? |
| GS-05 | Version prompts in Unity Catalog | Required | Prompts in UC table with version column? |
| GS-06 | Implement responsible AI practices | Critical | Guardrails, PII detection, human escalation? |
| GS-07 | Integrate AI lifecycle with data lifecycle | Required | Features derived from Gold layer? |
| AG-01 | Enable payload logging on AI Gateway | Required | Payload logging active? |
| AG-02 | Configure rate limiting | Required | Rate limits set? |
| AG-03 | Enable AI Guardrails for external-facing endpoints | Critical | Guardrails enabled? |
| AG-04 | Usage tracking for cost attribution | Required | Usage tags configured? |
| AG-05 | Configure fallbacks for LLM endpoints | Required | Fallback routes defined? |

## Detailed Rules

### GS-01: Managed Services First
**Severity:** Critical | **Trigger:** When starting a new GenAI project without evaluating managed options

**Rule:** Always evaluate Databricks managed services (Knowledge Assistant, Multi Agent Supervisor, Genie Spaces) before building custom agents.
**Why:** Managed services require no custom code, include built-in governance, and reduce maintenance burden. Custom agents require full compliance with all GS-01 through GS-07 rules.

**Decision Flow:**
```
Can Knowledge Assistant or Genie Spaces solve the problem?
  YES --> Use Managed Service (no custom code needed)
  NO  --> Document justification, then build custom agent
```

| Service | Use Case |
|---------|----------|
| Knowledge Assistant | Document Q&A, RAG with UC integration |
| Multi Agent Supervisor | Complex workflows, agent orchestration |
| Genie Spaces | Natural language to SQL, semantic analytics |

**Anti-Pattern:**
```
# WRONG: Building a custom RAG agent without first testing Knowledge Assistant
# Custom code = custom maintenance, custom compliance, custom monitoring
```

---

### GS-02: Evaluation Dataset Before Development
**Severity:** Critical | **Trigger:** When developing an agent without a defined evaluation dataset

**Rule:** Create an evaluation dataset with ground truth before starting agent development; minimum 50 records for dev, 200 for staging, 500+ for production.
**Why:** Without evaluation data, you cannot measure quality, detect regressions, or validate improvements. "Vibes-based" evaluation does not scale.

**Correct:**
```python
import mlflow.genai.datasets as datasets

# Dataset schema: inputs, expectations.expected_response, expectations.expected_facts
eval_dataset = datasets.create_dataset(
    name="agent_eval_v1",
    source="catalog.schema.eval_records"
)

# Each record must include:
# - inputs: {"query": "What is our Q4 revenue?"}
# - expectations.expected_response: "$2.4M based on..."
# - expectations.expected_facts: ["$2.4M", "Q4 2025"]
```

| Environment | Minimum Records | Coverage |
|-------------|-----------------|----------|
| Development | 50 | Core use cases |
| Staging | 200 | Edge cases included |
| Production | 500+ | Full domain coverage |

**Anti-Pattern:**
```python
# WRONG: Manual testing with 3-5 ad hoc queries
response = agent.predict("Does this work?")
print(response)  # "Looks good to me" -- not a real evaluation
```

---

### GS-03: LLM Judge Thresholds
**Severity:** Critical | **Trigger:** When deploying an agent without passing quality gates

**Rule:** All agents must pass LLM judge thresholds before production: Safety 100%, Relevance >= 0.80, Groundedness >= 0.70, Guidelines >= 0.70.
**Why:** Safety failures expose the organization to risk; low relevance means the agent is not useful; low groundedness means it hallucinates.

| Judge | Threshold | Blocking |
|-------|-----------|----------|
| Safety | 100% | Yes |
| Relevance | >= 0.80 | Yes |
| Groundedness | >= 0.70 | Yes |
| Guidelines | >= 0.70 | Yes |

**Correct:**
```python
from mlflow.genai.scorers import scorer

# Built-in judges
# Relevance()  - Is response relevant to the query?
# Groundedness() - Is response grounded in provided context?
# Safety() - Does response contain harmful content?
# Guidelines(text) - Does response follow specified guidelines?

# Custom domain-specific judge
@scorer
def sql_accuracy(outputs, expectations):
    """Verify generated SQL returns correct results."""
    generated = outputs.get("sql_query")
    expected = expectations.get("expected_sql")
    return accuracy_score
```

**Anti-Pattern:**
```python
# WRONG: Deploying without evaluation -- no quality gate
mlflow.pyfunc.log_model(python_model=MyAgent(), ...)
# Straight to production with zero evaluation
```

---

### ~~GS-04 (Retired)~~: UC Model Registration for Agents
> **Retired in v5.4.0** -- this rule duplicated ML-07. See the **ML/AI Governance** domain for Unity Catalog model registration guidance.

---

### GS-04: Production Monitoring
**Severity:** Required | **Trigger:** When a production agent lacks online evaluation or payload logging

**Rule:** Enable payload logging and online evaluation scorers for all production agents. Safety at 100% sample rate; relevance at 10% sample rate.
**Why:** Production quality can drift over time; monitoring catches regressions before users report them.

| Metric | Sample Rate | Alert Threshold |
|--------|-------------|-----------------|
| Safety | 100% | Any failure |
| Relevance | 10% | < 0.70 avg |
| Latency | 100% | P95 > 30s |
| Error Rate | 100% | > 5% |

**Correct:**
```python
# Enable payload logging on serving endpoint
from databricks.sdk.service.serving import AutoCaptureConfigInput

auto_capture_config = AutoCaptureConfigInput(
    catalog_name=catalog,
    schema_name=schema,
    table_name_prefix=endpoint_name,
    enabled=True
)
w.serving_endpoints.update_config(
    name=endpoint_name,
    auto_capture_config=auto_capture_config
)
```

**Anti-Pattern:**
```python
# WRONG: Production endpoint with no monitoring
# No payload logging, no online evaluation, no alerts
# You find out it is broken when a VP sends a Slack message
```

---

### GS-05: Prompt Versioning in Unity Catalog
**Severity:** Required | **Trigger:** When prompts are hard-coded in source code without version tracking

**Rule:** Store all prompts in Unity Catalog tables with version tracking; log prompt versions used in each run.
**Why:** Prompt changes can dramatically alter agent behavior; versioning enables rollback, A/B testing, and audit trail.

**Correct:**
```sql
CREATE TABLE prod_catalog.prompts.agent_prompts (
    prompt_key STRING,
    prompt_text STRING,
    version INT,
    created_at TIMESTAMP,
    created_by STRING
);
```

| Change Type | Review Required |
|-------------|-----------------|
| New prompt | Tech lead approval |
| Minor edit | Peer review |
| Major rewrite | Tech lead + evaluation rerun |

**Anti-Pattern:**
```python
# WRONG: Prompt hard-coded in notebook, no version tracking
SYSTEM_PROMPT = "You are a helpful assistant..."  # Changed by who? When? Why?
```

---

### GS-06: Responsible AI Practices
**Severity:** Critical | **Trigger:** When deploying an agent to external users without safety guardrails

**Rule:** All production agents must implement safety filtering, PII protection, bias monitoring, transparency disclosure, and human escalation paths.
**Why:** External-facing agents without guardrails expose the organization to regulatory, reputational, and legal risk.

**Correct:**
```python
from databricks.sdk.service.serving import (
    AiGatewayGuardrails, AiGatewayGuardrailsInput,
    AiGatewaySafetyConfig, AiGatewayPiiConfig
)

guardrails = AiGatewayGuardrails(
    input=AiGatewayGuardrailsInput(
        safety=AiGatewaySafetyConfig(enabled=True),
        pii=AiGatewayPiiConfig(behavior="BLOCK", categories=["CREDIT_CARD", "SSN"])
    )
)
```

| Practice | Requirement |
|----------|-------------|
| Safety filtering | AI Gateway guardrails or Llama Guard |
| PII protection | Block SSN, credit cards; mask email, phone |
| Transparency | "I am an AI assistant" in system prompt |
| Human escalation | Required for customer-facing agents |
| Content attribution | Cite sources for RAG agents |

**Anti-Pattern:**
```python
# WRONG: No guardrails on external-facing endpoint
# Agent can generate PII, harmful content, or unattributed claims
```

---

### GS-07: AI Lifecycle Integration with Data Lifecycle
**Severity:** Required | **Trigger:** When ML features are built from scratch instead of reusing Gold layer assets

**Rule:** Derive ML feature tables from Gold layer dimensions and facts; write predictions back to Gold for BI consumption; trace lineage through UC.
**Why:** Prevents duplicate pipelines for ML vs BI; ensures models train on the same governed data that powers dashboards; reduces time-to-model.

**Correct:**
```python
from databricks.feature_engineering import FeatureEngineeringClient
fe = FeatureEngineeringClient()

# Derive features from existing Gold dimension
feature_df = spark.sql("""
    SELECT customer_key, lifetime_value, order_count,
           avg_order_value, days_since_last_order
    FROM gold.dim_customer WHERE is_current = true
""")

fe.create_table(
    name="catalog.features.customer_features",
    primary_keys=["customer_key"],
    df=feature_df,
    description="Customer features derived from gold.dim_customer"
)
```

**Data-to-AI Pipeline:**
```
Bronze --> Silver --> Gold (Dimensions & Facts)
                       |
                       +-- Semantic Layer --> BI / Genie
                       |
                       +-- Feature Tables (UC) --> ML Training --> Model Serving
```

**Anti-Pattern:**
```python
# WRONG: Separate pipeline reading directly from Bronze/Silver for ML
# Duplicated logic, no governance, inconsistent with BI metrics
feature_df = spark.table("bronze.raw_events").groupBy("customer_id").agg(...)
```

---

## Checklist
- [ ] GS-01: Knowledge Assistant, Genie Spaces, Multi Agent Supervisor evaluated before custom build
- [ ] GS-02: Evaluation dataset created with min 50 records (dev), 200 (staging), 500+ (prod)
- [ ] GS-03: LLM judges passing -- Safety 100%, Relevance >= 0.80, Groundedness >= 0.70
- [ ] ~~GS-04 (old)~~: Retired -- see ML-07 in ML/AI Governance domain
- [ ] GS-04: Payload logging enabled, online evaluation scorers active
- [ ] GS-05: Prompts stored in UC table with version tracking
- [ ] GS-06: AI Gateway guardrails, PII detection, human escalation, transparency disclosure
- [ ] GS-07: Features derived from Gold layer; predictions written back to Gold
- [ ] AG-01: Payload logging enabled on all AI Gateway endpoints
- [ ] AG-02: Rate limiting configured per endpoint
- [ ] AG-03: AI Guardrails enabled for external-facing endpoints
- [ ] AG-04: Usage tags configured for cost attribution
- [ ] AG-05: Fallback routes defined for LLM endpoints
