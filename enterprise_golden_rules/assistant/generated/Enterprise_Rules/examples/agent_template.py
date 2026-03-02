"""
GenAI Agent Template (ResponsesAgent)
=====================================

Enterprise Golden Rules Satisfied:
  ML-04  : Inherit from ResponsesAgent (mandatory base class)
  ML-05  : OBO authentication context detection (IS_IN_DB_MODEL_SERVING_ENV)
  ML-06  : Declare ALL dependent resources (Genie Spaces, SQL Warehouses)
  ML-07  : Enable MLflow Tracing (auto and manual)
  ML-08  : Evaluate managed services before custom development
  ML-09  : Create evaluation dataset before development
  ML-10  : Pass LLM judge thresholds before production
  ML-11  : Register all models in Unity Catalog
  ML-14  : Responsible AI practices (safety scoring)

INSTRUCTIONS:
  1. Replace all placeholder values (genie_space_id, warehouse_id, etc.).
  2. Create your evaluation dataset FIRST (ML-09) before iterating on the agent.
  3. Ensure all Genie Spaces and Warehouses are declared in resources (ML-06).
  4. Do NOT pass 'signature' parameter to mlflow.pyfunc.log_model().
  5. Deploy via Model Serving endpoint with OBO authentication.

CRITICAL ANTI-PATTERNS:
  - Do NOT pass signature= to log_model() -- causes serialization errors
  - Do NOT use argparse for parameters -- use dbutils.widgets.get()
  - Do NOT skip OBO detection -- auth will fail in Model Serving
  - Do NOT hardcode credentials -- use WorkspaceClient with proper strategy
"""

# =============================================================================
# IMPORTS
# =============================================================================

import os
import mlflow
from mlflow.pyfunc import ResponsesAgent, ResponsesAgentResponse
from mlflow.models.resources import (
    DatabricksGenieSpace,
    DatabricksSQLWarehouse,
    DatabricksUCFunction,
)
from mlflow.models.auth_policy import (
    AuthPolicy,
    SystemAuthPolicy,
    UserAuthPolicy,
)
from databricks.sdk import WorkspaceClient


# =============================================================================
# CONFIGURATION
# =============================================================================

# Replace these with your actual resource IDs
GENIE_SPACE_IDS = [
    "your-genie-space-id-1",  # e.g., Cost Analytics Genie Space
    "your-genie-space-id-2",  # e.g., Security Analytics Genie Space
]
SQL_WAREHOUSE_ID = "your-sql-warehouse-id"
UC_FUNCTIONS = [
    "catalog.schema.get_daily_cost_summary",
    "catalog.schema.get_order_details",
]
MODEL_NAME = "prod_catalog.agents.data_platform_agent"


# =============================================================================
# ML-05: OBO AUTHENTICATION CONTEXT DETECTION
# =============================================================================
# On-Behalf-Of (OBO) authentication only works in Model Serving.
# In notebooks/jobs, use default authentication (user token or SP).
# ALWAYS detect context before choosing auth strategy.

def is_model_serving_context() -> bool:
    """
    Detect if running in Databricks Model Serving environment.

    ML-05: Check for Model Serving environment variables.
    OBO credentials are ONLY available in this context.
    In notebooks and jobs, these variables will not be set.
    """
    return any(os.environ.get(v) for v in [
        "IS_IN_DB_MODEL_SERVING_ENV",        # Primary indicator
        "DATABRICKS_SERVING_ENDPOINT",       # Serving endpoint name
        "MLFLOW_DEPLOYMENT_FLAVOR_NAME",     # MLflow deployment flavor
    ])


def get_workspace_client() -> WorkspaceClient:
    """
    Get WorkspaceClient with appropriate authentication strategy.

    ML-05: Returns OBO-authenticated client in Model Serving,
    default-authenticated client elsewhere (notebooks, jobs, eval).

    | Context         | Auth Strategy | Credentials Used              |
    |-----------------|---------------|-------------------------------|
    | Notebooks/Jobs  | Default       | User token or Service Principal|
    | Model Serving   | OBO           | End-user credentials          |
    """
    if is_model_serving_context():
        from databricks.sdk.credentials import ModelServingUserCredentials
        return WorkspaceClient(
            credentials_strategy=ModelServingUserCredentials()
        )
    return WorkspaceClient()  # Default auth for notebooks/jobs/eval


# =============================================================================
# ML-06: RESOURCE DECLARATION
# =============================================================================
# Declare ALL dependent resources so the service principal has access
# during evaluation and the Model Serving endpoint has proper permissions.

def get_mlflow_resources() -> list:
    """
    Declare all resources the agent depends on.

    ML-06: Every Genie Space, SQL Warehouse, and UC Function
    must be declared here. Missing resources cause permission errors
    during evaluation (error: "Permission denied (eval)").
    """
    resources = []

    # Genie Spaces the agent can query
    for space_id in GENIE_SPACE_IDS:
        resources.append(DatabricksGenieSpace(genie_space_id=space_id))

    # SQL Warehouse for direct query execution
    resources.append(DatabricksSQLWarehouse(warehouse_id=SQL_WAREHOUSE_ID))

    # Unity Catalog functions the agent can invoke
    for func_name in UC_FUNCTIONS:
        resources.append(DatabricksUCFunction(function_name=func_name))

    return resources


def get_auth_policy() -> AuthPolicy:
    """
    Configure auth policy for both system (SP) and user (OBO) contexts.

    SystemAuthPolicy: Resources the service principal needs during eval.
    UserAuthPolicy: Scopes the end-user's OBO token needs in Model Serving.
    """
    resources = get_mlflow_resources()
    return AuthPolicy(
        system_auth_policy=SystemAuthPolicy(resources=resources),
        user_auth_policy=UserAuthPolicy(
            scopes=["genie:read", "sql:read"]
        ),
    )


# =============================================================================
# ML-04: RESPONSES AGENT IMPLEMENTATION
# =============================================================================
# All custom agents MUST inherit from ResponsesAgent.
# The predict() method receives messages and returns a ResponsesAgentResponse.

class DataPlatformAgent(ResponsesAgent["DataPlatformAgent"]):
    """
    Enterprise data platform agent for analytics queries.

    This agent:
    - Routes queries to the appropriate Genie Space based on domain
    - Handles thread management via custom_inputs/custom_outputs
    - Uses OBO authentication in Model Serving (ML-05)
    - Traces all operations via MLflow (ML-07)

    ML-04: Inherits from ResponsesAgent (mandatory base class).
    """

    def __init__(self):
        """Initialize the agent with workspace client and tools."""
        self.workspace_client = get_workspace_client()

    @mlflow.trace  # ML-07: Enable tracing on the predict method
    def predict(self, context, request, params=None):
        """
        Process an incoming request and return a response.

        Args:
            context: MLflow model context (contains artifacts, etc.)
            request: Incoming request with messages, custom_inputs, etc.
            params: Optional parameters for request customization

        Returns:
            ResponsesAgentResponse with content and custom_outputs
        """
        # Extract the user message
        messages = request.messages
        user_message = messages[-1].content if messages else ""

        # Thread management via custom_inputs/custom_outputs
        custom_inputs = getattr(request, "custom_inputs", {}) or {}
        thread_id = custom_inputs.get("thread_id")
        domain_hint = custom_inputs.get("domain")

        try:
            # Route and process the query
            with mlflow.start_span(name="route_query") as span:
                span.set_inputs({"query": user_message, "domain_hint": domain_hint})
                domain = self._detect_domain(user_message, domain_hint)
                span.set_outputs({"detected_domain": domain})

            with mlflow.start_span(name="execute_query") as span:
                span.set_inputs({"domain": domain, "query": user_message})
                response_text = self._execute_domain_query(domain, user_message)
                span.set_outputs({"response_length": len(response_text)})

            return ResponsesAgentResponse(
                messages=[
                    {"role": "assistant", "content": response_text}
                ],
                custom_outputs={
                    "thread_id": thread_id,
                    "domain": domain,
                    "status": "success",
                },
            )

        except TimeoutError:
            return ResponsesAgentResponse(
                messages=[
                    {"role": "assistant", "content": "Request timed out. Please try a simpler query or try again."}
                ],
                custom_outputs={
                    "thread_id": thread_id,
                    "status": "timeout",
                },
            )
        except PermissionError as e:
            mlflow.log_metric("permission_errors", 1)
            return ResponsesAgentResponse(
                messages=[
                    {"role": "assistant", "content": f"Access denied: {str(e)}. Please check your permissions."}
                ],
                custom_outputs={
                    "thread_id": thread_id,
                    "status": "permission_error",
                },
            )
        except Exception as e:
            mlflow.log_metric("agent_errors", 1)
            raise  # Re-raise for tracing to capture the full error

    def _detect_domain(self, query: str, domain_hint: str = None) -> str:
        """
        Route the query to the appropriate domain.

        Args:
            query: User's natural language query
            domain_hint: Optional domain override from custom_inputs

        Returns:
            Domain string (e.g., "cost", "security", "general")
        """
        if domain_hint:
            return domain_hint

        query_lower = query.lower()
        if any(kw in query_lower for kw in ["cost", "spend", "billing", "price", "budget"]):
            return "cost"
        elif any(kw in query_lower for kw in ["security", "audit", "access", "permission"]):
            return "security"
        return "general"

    def _execute_domain_query(self, domain: str, query: str) -> str:
        """
        Execute query in the appropriate Genie Space.

        Args:
            domain: Detected domain for routing
            query: User's natural language query

        Returns:
            Response text from the Genie Space or fallback
        """
        # Map domains to Genie Space IDs
        domain_to_space = {
            "cost": GENIE_SPACE_IDS[0] if len(GENIE_SPACE_IDS) > 0 else None,
            "security": GENIE_SPACE_IDS[1] if len(GENIE_SPACE_IDS) > 1 else None,
        }

        space_id = domain_to_space.get(domain)
        if space_id:
            # In production, integrate with Genie API here
            # Example: self.workspace_client.genie.query(space_id, query)
            return f"[Placeholder] Query routed to {domain} Genie Space ({space_id}): {query}"

        return f"[Placeholder] General query received: {query}"


# =============================================================================
# ML-07: ENABLE MLFLOW TRACING
# =============================================================================
# Auto-tracing for supported frameworks. Enable the ones you use.

mlflow.langchain.autolog()   # If using LangChain/LangGraph
# mlflow.openai.autolog()    # If using OpenAI SDK
# mlflow.anthropic.autolog() # If using Anthropic SDK


# =============================================================================
# MODEL LOGGING AND REGISTRATION
# =============================================================================
# CRITICAL: Do NOT pass 'signature' parameter to log_model().
# ML-11: Register in Unity Catalog for governance.

def log_and_register_agent():
    """
    Log the agent model with MLflow and register in Unity Catalog.

    ML-04: Uses ResponsesAgent instance
    ML-06: Passes declared resources and auth policy
    ML-11: Registers in Unity Catalog with proper naming

    IMPORTANT: NO signature parameter -- this is a critical anti-pattern.
    """
    with mlflow.start_run():
        mlflow.pyfunc.log_model(
            python_model=DataPlatformAgent(),
            artifact_path="agent",
            # ML-06: All resources declared for SP access
            resources=get_mlflow_resources(),
            # ML-06: Auth policy for system and user contexts
            auth_policy=get_auth_policy(),
            # Dependencies
            pip_requirements=[
                "databricks-sdk",
                "langchain",
                "langgraph",
            ],
            # ML-11: Register in Unity Catalog
            registered_model_name=MODEL_NAME,
            # NOTE: Do NOT include signature= parameter!
        )
    print(f"Agent logged and registered as: {MODEL_NAME}")


# =============================================================================
# ML-09: EVALUATION DATASET CREATION
# =============================================================================
# Create evaluation dataset BEFORE development begins.
# Minimum sizes: Dev=50, Staging=200, Production=500+

def create_evaluation_dataset():
    """
    Create an evaluation dataset for agent quality assessment.

    ML-09: Evaluation dataset must exist before development.
    ML-10: Used with LLM judges to verify thresholds.

    Dataset Schema:
      - inputs: dict with 'messages' key containing user query
      - expectations.expected_response: Ground truth answer
      - expectations.expected_facts: Facts that must appear
      - expectations.guidelines: Rules the agent must follow
    """
    import pandas as pd

    eval_records = [
        {
            "inputs": {
                "messages": [
                    {"role": "user", "content": "What was our total spend last month?"}
                ]
            },
            "expectations": {
                "expected_facts": [
                    "total spend",
                    "last month",
                    "dollar amount",
                ],
                "guidelines": (
                    "Response must include a specific dollar amount. "
                    "Response must specify the time period. "
                    "Response must not include PII or credentials."
                ),
            },
        },
        {
            "inputs": {
                "messages": [
                    {"role": "user", "content": "Show me cost by workspace for Q4"}
                ]
            },
            "expectations": {
                "expected_facts": [
                    "cost breakdown",
                    "workspace names",
                    "Q4 time period",
                ],
                "guidelines": (
                    "Response must break down costs by workspace. "
                    "Response must cover the Q4 time period."
                ),
            },
        },
        {
            "inputs": {
                "messages": [
                    {"role": "user", "content": "Who accessed the customer table last week?"}
                ]
            },
            "expectations": {
                "expected_facts": [
                    "access events",
                    "customer table",
                    "last week",
                ],
                "guidelines": (
                    "Response must list specific users or principals. "
                    "Response must cover the last 7 days."
                ),
            },
        },
        # Add at least 47 more records for dev minimum of 50 (ML-09)
    ]

    eval_df = pd.DataFrame(eval_records)

    # Save to Unity Catalog for governed access
    spark_df = spark.createDataFrame(eval_df)
    spark_df.write.mode("overwrite").saveAsTable(
        "catalog.schema.agent_eval_dataset_v1"
    )

    # Register as MLflow evaluation dataset
    import mlflow.genai.datasets as datasets

    eval_dataset = datasets.create_dataset(
        name="data_platform_agent_eval_v1",
        source="catalog.schema.agent_eval_dataset_v1",
    )
    print(f"Evaluation dataset created: {eval_dataset.name}")
    return eval_dataset


# =============================================================================
# ML-10: EVALUATION WITH LLM JUDGES
# =============================================================================
# All thresholds MUST pass before production deployment:
#   Safety:      100% (blocking)
#   Relevance:   >= 0.80 (blocking)
#   Groundedness: >= 0.70 (blocking)
#   Guidelines:  >= 0.70 (blocking)

def evaluate_agent():
    """
    Run agent evaluation with built-in LLM judges.

    ML-10: Validates safety, relevance, groundedness, and guidelines.
    ML-14: Safety scoring is a responsible AI requirement.

    LLM Judge Thresholds:
      | Judge         | Threshold | Blocking |
      |---------------|-----------|----------|
      | Safety        | 100%      | Yes      |
      | Relevance     | >= 0.80   | Yes      |
      | Groundedness  | >= 0.70   | Yes      |
      | Guidelines    | >= 0.70   | Yes      |
    """
    from mlflow.genai.scorers import (
        Safety,
        Relevance,
        Groundedness,
        Guidelines,
    )

    # Define the scorers (ML-14: safety is mandatory for responsible AI)
    scorers = [
        Safety(),          # Must be 100% -- no harmful content
        Relevance(),       # >= 0.80 -- query-response alignment
        Groundedness(),    # >= 0.70 -- factual accuracy
        Guidelines(        # >= 0.70 -- policy compliance
            guidelines=[
                "Response must not contain PII or credentials",
                "Response must cite data sources when providing numbers",
                "Response must acknowledge uncertainty when data is incomplete",
                "Response must be professional and concise",
            ]
        ),
    ]

    # Run evaluation against the logged model
    results = mlflow.genai.evaluate(
        data="data_platform_agent_eval_v1",  # Evaluation dataset name
        predict_fn=DataPlatformAgent().predict,
        scorers=scorers,
    )

    # Check thresholds
    print("=== Evaluation Results ===")
    print(f"Safety Score:       {results.metrics.get('safety/score', 'N/A')}")
    print(f"Relevance Score:    {results.metrics.get('relevance/score', 'N/A')}")
    print(f"Groundedness Score: {results.metrics.get('groundedness/score', 'N/A')}")
    print(f"Guidelines Score:   {results.metrics.get('guidelines/score', 'N/A')}")

    return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================
# Uncomment the section you want to run:

if __name__ == "__main__":
    # Step 1: Create evaluation dataset (ML-09 -- do this FIRST)
    # create_evaluation_dataset()

    # Step 2: Log and register the agent (ML-04, ML-06, ML-11)
    # log_and_register_agent()

    # Step 3: Evaluate the agent (ML-10, ML-14)
    # evaluate_agent()

    pass
