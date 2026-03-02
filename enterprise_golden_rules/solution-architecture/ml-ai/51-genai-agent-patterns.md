# GenAI Agent Implementation Patterns

> **Document Owner:** ML Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

**Implementation patterns** for building GenAI agents on Databricks. This document covers the HOW - code patterns, authentication, tracing, and deployment.

For governance requirements and lifecycle standards, see [52-genai-standards.md](52-genai-standards.md).

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **GA-01** | Inherit from ResponsesAgent | Critical | [Governance](https://docs.databricks.com/en/generative-ai/agent-framework/build-genai-apps) |
| **GA-02** | OBO auth context detection | Critical | [Governance](https://docs.databricks.com/en/generative-ai/agent-framework/build-genai-apps) |
| **GA-03** | Declare all resources (Genie Spaces, Warehouses) | Critical | [Governance](https://docs.databricks.com/en/generative-ai/agent-framework/build-genai-apps) |
| **GA-04** | Enable MLflow Tracing | Critical | [Governance](https://docs.databricks.com/en/mlflow/tracing) |

---

## Platform & Enterprise Prerequisites

> This document defines **solution patterns**. The following EA/PA rules are prerequisites.

| Prerequisite | Rule IDs | Document |
|-------------|----------|----------|
| Models in Unity Catalog | ML-07 | [50-mlflow-model-patterns](50-mlflow-model-patterns.md) |
| UC governance for AI assets | GOV-06 | [15-unity-catalog-governance](../../platform-architecture/15-unity-catalog-governance.md) |

---

## ResponsesAgent Pattern

**All custom agents MUST inherit from ResponsesAgent.**

```python
from mlflow.pyfunc import ResponsesAgent, ResponsesAgentResponse

class DataPlatformAgent(ResponsesAgent["DataPlatformAgent"]):
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def predict(self, context, request, params=None):
        user_message = request.messages[-1].content
        result = self.graph.invoke({"query": user_message})
        return ResponsesAgentResponse(
            messages=[{"role": "assistant", "content": result["response"]}]
        )
    
    def _build_graph(self):
        # LangGraph implementation
        pass
```

**Critical:** Do NOT pass `signature` parameter to `log_model()`.

---

## OBO Authentication Pattern

**On-Behalf-Of (OBO) only works in Model Serving. Always detect context first.**

```python
import os
from databricks.sdk import WorkspaceClient

def is_model_serving() -> bool:
    """Detect if running in Model Serving environment."""
    return any(os.environ.get(v) for v in [
        "IS_IN_DB_MODEL_SERVING_ENV",
        "DATABRICKS_SERVING_ENDPOINT",
        "MLFLOW_DEPLOYMENT_FLAVOR_NAME"
    ])

def get_workspace_client() -> WorkspaceClient:
    """Get appropriately authenticated WorkspaceClient."""
    if is_model_serving():
        from databricks.sdk.credentials import ModelServingUserCredentials
        return WorkspaceClient(credentials_strategy=ModelServingUserCredentials())
    return WorkspaceClient()  # Default auth for notebooks/jobs
```

| Context | Auth Strategy | Credentials Used |
|---------|---------------|------------------|
| Notebooks/Jobs/Eval | Default | User token or Service Principal |
| Model Serving | OBO | End-user credentials |

---

## Resource Declaration Pattern

**Declare ALL dependent resources for service principal access during evaluation.**

```python
from mlflow.models.resources import (
    DatabricksGenieSpace,
    DatabricksSQLWarehouse,
    DatabricksUCFunction
)
from mlflow.models.auth_policy import AuthPolicy, SystemAuthPolicy, UserAuthPolicy

def get_mlflow_resources():
    """Declare all resources agent depends on."""
    resources = []
    
    # Genie Spaces
    for space_id in ["space-cost-01", "space-security-02"]:
        resources.append(DatabricksGenieSpace(genie_space_id=space_id))
    
    # SQL Warehouse for query execution
    resources.append(DatabricksSQLWarehouse(warehouse_id="abc123"))
    
    # Unity Catalog functions
    resources.append(DatabricksUCFunction(function_name="catalog.schema.my_func"))
    
    return resources

def get_auth_policy():
    """Configure auth policy for both contexts."""
    resources = get_mlflow_resources()
    return AuthPolicy(
        system_auth_policy=SystemAuthPolicy(resources=resources),
        user_auth_policy=UserAuthPolicy(scopes=["genie:read", "sql:read"])
    )
```

---

## MLflow Tracing Patterns

### Auto-Tracing (Preferred)

```python
import mlflow

# Enable for supported frameworks
mlflow.langchain.autolog()   # LangChain/LangGraph
mlflow.openai.autolog()      # OpenAI SDK
mlflow.anthropic.autolog()   # Anthropic SDK
```

### Manual Tracing

```python
@mlflow.trace
def process_query(query: str) -> str:
    """Trace entire function execution."""
    return execute_pipeline(query)

def complex_workflow(query: str) -> str:
    """Use spans for granular tracing."""
    with mlflow.start_span(name="retrieval") as span:
        span.set_inputs({"query": query})
        docs = retriever.get_documents(query)
        span.set_outputs({"doc_count": len(docs)})
    
    with mlflow.start_span(name="generation") as span:
        span.set_inputs({"context": docs})
        response = llm.generate(docs, query)
        span.set_outputs({"response_length": len(response)})
    
    return response
```

### Trace Attributes

```python
with mlflow.start_span(name="tool_call") as span:
    span.set_attribute("tool.name", "genie_query")
    span.set_attribute("tool.domain", "cost")
    span.set_attribute("user.id", user_id)
```

---

## Model Logging Pattern

```python
import mlflow

with mlflow.start_run():
    # Log the agent
    mlflow.pyfunc.log_model(
        python_model=DataPlatformAgent(),
        artifact_path="agent",
        resources=get_mlflow_resources(),
        auth_policy=get_auth_policy(),
        pip_requirements=["langchain", "langgraph", "databricks-sdk"],
        registered_model_name="prod_catalog.agents.data_platform_agent"
    )
```

---

## Multi-Agent Pattern (LangGraph)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    query: str
    domain: str
    response: str

def router(state: AgentState) -> Literal["cost", "security", "general"]:
    """Route to specialist agent based on query."""
    query = state["query"].lower()
    if "cost" in query or "spend" in query:
        return "cost"
    elif "security" in query or "audit" in query:
        return "security"
    return "general"

def build_multi_agent_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("router", router)
    graph.add_node("cost_agent", cost_specialist)
    graph.add_node("security_agent", security_specialist)
    graph.add_node("general_agent", general_handler)
    
    graph.add_conditional_edges("router", router, {
        "cost": "cost_agent",
        "security": "security_agent",
        "general": "general_agent"
    })
    
    graph.set_entry_point("router")
    return graph.compile()
```

---

## Error Handling Pattern

```python
class DataPlatformAgent(ResponsesAgent["DataPlatformAgent"]):
    
    def predict(self, context, request, params=None):
        try:
            result = self.graph.invoke({"query": request.messages[-1].content})
            return ResponsesAgentResponse(
                messages=[{"role": "assistant", "content": result["response"]}]
            )
        except TimeoutError:
            return ResponsesAgentResponse(
                messages=[{"role": "assistant", "content": "Request timed out. Please try again."}]
            )
        except PermissionError as e:
            mlflow.log_metric("permission_errors", 1)
            return ResponsesAgentResponse(
                messages=[{"role": "assistant", "content": f"Access denied: {str(e)}"}]
            )
        except Exception as e:
            mlflow.log_metric("agent_errors", 1)
            raise  # Re-raise for tracing to capture
```

---

## Validation Checklist

- [ ] Agent inherits from `ResponsesAgent`
- [ ] No `signature` parameter in `log_model()`
- [ ] OBO context detection implemented
- [ ] All Genie Spaces declared in resources
- [ ] SQL Warehouse declared in resources
- [ ] MLflow Tracing enabled (auto or manual)
- [ ] Error handling with appropriate responses
- [ ] Model registered in Unity Catalog

---

## References

- [ResponsesAgent API](https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html)
- [MLflow Tracing](https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/)
- [Agent Authentication](https://docs.databricks.com/generative-ai/agent-framework/agent-authentication)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
