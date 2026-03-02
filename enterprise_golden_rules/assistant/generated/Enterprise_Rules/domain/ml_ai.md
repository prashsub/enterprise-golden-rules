# ML/AI Golden Rules
**Rules:** ML-01..09, GA-01..04 | **Count:** 13 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| ML-01 | Feature tables in UC with primary keys | Critical | `fe.create_table()` with `primary_keys`? |
| ML-02 | `output_schema` required for UC models | Critical | `output_schema` in `fe.log_model()`? |
| ML-03 | NaN/Inf handling at feature table creation | Critical | Clean before `fe.write_table()`, not in training? |
| ML-04 | Organize experiments by lifecycle stage | Required | Separate dev/eval/prod experiments? |
| ML-05 | Label binarization for classifiers (0/1) | Critical | Integer labels, not continuous floats? |
| ML-06 | Exclude label and key columns from features | Critical | `exclude_columns` set correctly? |
| ML-07 | Register all models in UC with aliases | Critical | `catalog.schema.model_name` registered? |
| ML-08 | Champion/Challenger pattern for promotion | Required | Alias-based, not version-number-based? |
| ML-09 | Log parameters, metrics, and artifacts | Required | `log_params`, `log_metrics`, `log_dict`? |
| GA-01 | Inherit from ResponsesAgent for all agents | Critical | Uses ResponsesAgent base class? |
| GA-02 | OBO auth context detection | Critical | IS_IN_DB_MODEL_SERVING_ENV check? |
| GA-03 | Declare all resources (Genie, Warehouses) | Critical | Resources list in log_model? |
| GA-04 | Enable MLflow Tracing for all agents | Required | mlflow.tracing enabled? |

## Detailed Rules

### ML-01: Feature Tables in Unity Catalog
**Severity:** Critical | **Trigger:** When you see ML features stored outside Unity Catalog or without primary keys

**Rule:** All feature tables must be created in Unity Catalog via `FeatureEngineeringClient` with defined primary keys.
**Why:** `fe.score_batch()` requires primary keys for automatic feature lookup at inference; UC provides lineage, governance, and cross-team sharing.

**Correct:**
```python
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup

fe = FeatureEngineeringClient()

fe.create_table(
    name=f"{catalog}.{schema}.customer_features",
    primary_keys=["customer_id"],
    df=feature_df,
    description="Customer features from gold.dim_customer. Updated daily."
)

# With timestamp key for point-in-time correctness
fe.create_table(
    name=f"{catalog}.{schema}.customer_features_ts",
    primary_keys=["customer_id"],
    timestamp_keys=["feature_date"],
    df=feature_df_with_dates,
    description="Time-series customer features for temporal ML training."
)
```

**Anti-Pattern:**
```python
# WRONG: No primary keys, no UC, no governance
feature_df.write.saveAsTable("default.my_features")
```

---

### ML-02: Output Schema Required
**Severity:** Critical | **Trigger:** When you see `fe.log_model()` without `output_schema`

**Rule:** All models registered in Unity Catalog must include an explicit `output_schema` defining the prediction output type.
**Why:** UC requires schema metadata for governance; `fe.score_batch()` needs it to work correctly; enables downstream consumers to understand predictions.

**Correct:**
```python
from mlflow.models.signature import ColSpec, Schema, DataType

output_schema = Schema([ColSpec(DataType.double)])   # Regression
# output_schema = Schema([ColSpec(DataType.long)])   # Classification

fe.log_model(
    model=trained_model,
    artifact_path="model",
    flavor=mlflow.sklearn,
    output_schema=output_schema,
    training_set=training_set,
    registered_model_name=f"{catalog}.{schema}.{model_name}"
)
```

**Anti-Pattern:**
```python
# WRONG: No output_schema - UC registration fails or lacks metadata
fe.log_model(
    model=trained_model,
    artifact_path="model",
    flavor=mlflow.sklearn,
    training_set=training_set,
    registered_model_name=f"{catalog}.{schema}.{model_name}"
)
```

---

### ML-03: NaN/Inf Handling at Source
**Severity:** Critical | **Trigger:** When you see NaN imputation during training preprocessing

**Rule:** Clean NaN and Inf values at feature table creation time, not during training; training preprocessing is NOT applied during `fe.score_batch()`.
**Why:** `fe.score_batch()` bypasses your training pipeline -- raw feature values go directly to the model. NaN in the table means NaN at inference, causing `Input X contains NaN` errors in production.

**Correct:**
```python
from pyspark.sql import functions as F

def clean_numeric_features(df, numeric_columns):
    """Clean NaN/Inf at source - critical for fe.score_batch()."""
    for col_name in numeric_columns:
        df = df.withColumn(
            col_name,
            F.when(F.col(col_name).isNull() | F.isnan(F.col(col_name)), F.lit(0.0))
             .when(F.col(col_name) == float('inf'), F.lit(0.0))
             .when(F.col(col_name) == float('-inf'), F.lit(0.0))
             .otherwise(F.col(col_name))
        )
    return df

# Apply BEFORE writing to feature table
clean_df = clean_numeric_features(feature_df, numeric_cols)
fe.write_table(name=f"{catalog}.{schema}.customer_features", df=clean_df, mode="merge")
```

**Anti-Pattern:**
```python
# WRONG: Imputer only works during training, NOT during fe.score_batch()
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy="median")
X_train = imputer.fit_transform(X_train)  # Fills NaN for training only!
```

---

### ML-04: Experiment Organization
**Severity:** Required | **Trigger:** When you see all runs in a single experiment

**Rule:** Organize MLflow experiments by lifecycle stage: development, evaluation, and production.
**Why:** Prevents dev noise from polluting production history; enables team members to find relevant runs; supports audit trail for promotion decisions.

**Correct:**
```python
# Development: rapid iteration
mlflow.set_experiment("/Shared/customer360_ml_churn_development")

# Evaluation: formal model comparison (retention: 1 year)
mlflow.set_experiment("/Shared/customer360_ml_churn_evaluation")

# Production: production training runs only (retention: permanent)
mlflow.set_experiment("/Shared/customer360_ml_churn_production")
```

**Anti-Pattern:**
```python
# WRONG: Everything in one experiment - dev noise hides production runs
mlflow.set_experiment("/Shared/churn_model")
```

---

### ML-05: Label Binarization
**Severity:** Critical | **Trigger:** When you see continuous float values used as classification labels

**Rule:** Classification labels must be integer-encoded (0/1 for binary, 0..N for multi-class); never pass continuous floats.
**Why:** Tree classifiers (XGBoost, LightGBM) expect integer labels; continuous labels cause `base_score must be in (0,1)` errors; evaluation metrics require discrete labels.

**Correct:**
```python
from pyspark.sql import functions as F

labeled_df = df.withColumn(
    "label",
    F.when(F.col("churn_rate") > 0.10, 1).otherwise(0).cast("integer")
)

# Verify label distribution
label_counts = labeled_df.groupBy("label").count().collect()
minority_ratio = min(r["count"] for r in label_counts) / sum(r["count"] for r in label_counts)
if minority_ratio < 0.05:
    print(f"WARNING: Severe imbalance ({minority_ratio:.1%}). Consider scale_pos_weight.")
```

**Anti-Pattern:**
```python
# WRONG: Continuous float as label - XGBoost will error
labeled_df = df.withColumn("label", F.col("churn_rate"))  # 0.0 to 1.0 float!
```

---

### ML-06: Exclude Label and Keys from Features
**Severity:** Critical | **Trigger:** When you see label or primary key columns in the feature set

**Rule:** Always exclude label columns, primary keys, and timestamp columns from features using an explicit exclusion list.
**Why:** Including the label causes data leakage (model memorizes the answer); including keys teaches the model to memorize IDs instead of learning patterns.

**Correct:**
```python
EXCLUDE = ["label", "customer_id", "product_id", "feature_date", "processed_at"]
feature_cols = [c for c in training_df.columns if c not in EXCLUDE]

assert "label" not in feature_cols, "Label column in features!"
assert all(k not in feature_cols for k in ["customer_id", "product_id"])

X_train = training_df[feature_cols].values
y_train = training_df["label"].values
```

**Anti-Pattern:**
```python
# WRONG: Training on all columns including label and keys
X_train = training_df.drop("label").values  # customer_id still included!
```

---

### ML-07: Model Registration in Unity Catalog
**Severity:** Critical | **Trigger:** When you see models stored outside UC or without three-level namespace

**Rule:** All models must be registered in Unity Catalog as `catalog.schema.model_name` with description and tags.
**Why:** Centralized access control (GRANT/REVOKE), version history with full lineage, required for model serving endpoints.

**Correct:**
```python
from mlflow import MlflowClient
client = MlflowClient()

# Register during logging
fe.log_model(
    model=trained_model, artifact_path="model", flavor=mlflow.sklearn,
    output_schema=output_schema, training_set=training_set,
    registered_model_name=f"{catalog}.ml.customer_churn_model"
)

# Set metadata
client.update_registered_model(
    name=f"{catalog}.ml.customer_churn_model",
    description="Predicts churn probability. Binary classification. Refreshed weekly."
)
client.set_registered_model_tag(
    name=f"{catalog}.ml.customer_churn_model",
    key="team", value="ml-engineering"
)
```

**Anti-Pattern:**
```python
# WRONG: Local model registry, no UC governance
mlflow.register_model(f"runs:/{run_id}/model", "my_model")
```

---

### ML-08: Champion/Challenger Promotion
**Severity:** Required | **Trigger:** When you see model versions referenced by number in production code

**Rule:** Use MLflow model aliases (`Champion`, `Challenger`) for promotion; never reference version numbers in production. Define and validate metric thresholds before any promotion.
**Why:** Decouples deployment from versions; enables safe rollback by reassigning alias; production code references `@Champion` and never needs updating. Prevents regression in production.

**Evaluation Gates:**

| Gate | Criteria | Blocking |
|------|----------|----------|
| Metric improvement | AUC/F1 >= Champion | Yes |
| Data quality | No NaN/Inf in predictions | Yes |
| Latency | P95 inference < threshold | Yes (serving) |
| Bias check | Fairness within tolerance | Required |

**Correct:**
```python
client = MlflowClient()
model_name = f"{catalog}.ml.customer_churn_model"

# Set Challenger for validation
client.set_registered_model_alias(name=model_name, alias="Challenger", version=new_version)

# Compare against Champion
champion_metrics = evaluate_model(f"models:/{model_name}@Champion", test_df)
challenger_metrics = evaluate_model(f"models:/{model_name}@Challenger", test_df)

# Promote if improved
if challenger_metrics["auc_roc"] > champion_metrics["auc_roc"]:
    client.set_registered_model_alias(name=model_name, alias="Champion", version=new_version)
```

**Anti-Pattern:**
```python
# WRONG: Hard-coded version number breaks on every retrain
model_uri = f"models:/{model_name}/3"  # What happens when version 4 is trained?
```

---

### ML-09: Log Parameters, Metrics, and Artifacts
**Severity:** Required | **Trigger:** When you see training runs without logged parameters or metrics

**Rule:** Every training run must log parameters, metrics, and artifacts using consistent metric names across experiments.
**Why:** Enables reproducibility, supports model comparison and selection, creates audit trail for regulatory compliance.

**Correct:**
```python
with mlflow.start_run(run_name="churn_xgb_v4") as run:
    mlflow.log_params({"model_type": "xgboost", "max_depth": 8, "learning_rate": 0.1})
    mlflow.set_tags({"dataset_version": "v3", "triggered_by": "scheduled_retrain"})

    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)

    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "auc_roc": roc_auc_score(y_test, y_proba),
        "train_rows": len(X_train), "feature_count": len(feature_cols)
    })
    mlflow.log_dict(dict(zip(feature_cols, model.feature_importances_)), "feature_importance.json")
```

**Anti-Pattern:**
```python
# WRONG: No tracking - impossible to reproduce or compare
model = xgb.XGBClassifier(max_depth=8)
model.fit(X_train, y_train)
# Which parameters? Which data? Which metrics? Nobody knows.
```

---

## Checklist
- [ ] ML-01: Feature tables created via `fe.create_table()` with primary keys
- [ ] ML-02: `output_schema` defined in every `fe.log_model()` call
- [ ] ML-03: NaN/Inf cleaned at feature table creation, not during training
- [ ] ML-04: Experiments separated into dev/eval/prod paths
- [ ] ML-05: Labels are integer-encoded (0/1 for binary)
- [ ] ML-06: Label, key, and timestamp columns excluded from feature set
- [ ] ML-07: Model registered in UC as `catalog.schema.model_name`
- [ ] ML-08: Champion/Challenger aliases used (no hard-coded version numbers)
- [ ] ML-09: Parameters, metrics, and artifacts logged for every run
- [ ] GA-01: Agent inherits from ResponsesAgent
- [ ] GA-02: OBO auth context detected in serving environment
- [ ] GA-03: All dependent resources declared in log_model
- [ ] GA-04: MLflow tracing enabled for observability
