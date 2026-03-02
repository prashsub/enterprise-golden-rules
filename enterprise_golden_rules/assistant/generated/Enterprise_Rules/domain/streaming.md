# Streaming Golden Rules
**Rules:** ST-01..04 | **Count:** 4 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| ST-01 | Lakeflow SDP first for all streaming | Critical | Use `@dlt.table`, not raw Structured Streaming |
| ~~ST-02~~ | *Retired -- duplicate of DQ-01. See Data Quality domain.* | -- | -- |
| ST-02 | Use SDP managed checkpointing for DR | Required | No manual checkpoint path config in SDP |
| ~~ST-04~~ | *Retired -- duplicate of CP-05. See Compute domain.* | -- | -- |
| ST-03 | Fixed worker count for streaming | Required | `num_workers: N`, no `autoscale` block |
| ST-04 | All streaming operations must be idempotent | Required | `foreachBatch` uses MERGE, not append |

---

## Detailed Rules

### ST-01: Lakeflow SDP First
**Severity:** Critical | **Trigger:** When designing any new streaming workload

**Rule:** Use Lakeflow Spark Declarative Pipelines (SDP, formerly DLT) for all streaming workloads; raw Structured Streaming requires an approved exception from a Platform Architect.
**Why:** SDP provides managed checkpointing, automatic recovery, built-in expectations, schema evolution, and serverless execution -- eliminating an entire class of operational failures that custom Structured Streaming code must handle manually.

**Decision Tree:**
```
New Streaming Workload
  |
  +-- Can use declarative SQL/Python? --YES--> Use Lakeflow SDP
  |
  +-- NO --> Complex custom logic required?
                |
                +--YES--> Raw Structured Streaming (Exception Required)
                +--NO --> Return to Lakeflow SDP
```

**Correct:**
```python
import dlt
from pyspark.sql.functions import col, current_timestamp

@dlt.table(
    name="silver_events",
    comment="Cleaned event stream with quality validation. Source: bronze_events",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.enableRowTracking": "true"
    },
    cluster_by_auto=True
)
@dlt.expect("event_id_not_null", "event_id IS NOT NULL")
@dlt.expect_or_drop("valid_user_id", "user_id IS NOT NULL")
@dlt.expect_or_fail("valid_timestamp", "event_timestamp <= current_timestamp()")
def silver_events():
    return (
        dlt.read_stream("bronze_events")
        .select(
            col("event_id"), col("user_id"), col("event_type"),
            col("event_timestamp"),
            current_timestamp().alias("processed_at")
        )
    )
```

**Anti-Pattern:**
```python
# Raw Structured Streaming without justification
spark.readStream.table("bronze_events") \
    .writeStream \
    .option("checkpointLocation", "/checkpoints/events") \
    .toTable("silver_events")
```

**Serverless SDP Bundle Config (Recommended):**
```yaml
resources:
  pipelines:
    streaming_pipeline:
      name: "[${bundle.target}] Event Streaming Pipeline"
      catalog: ${var.catalog}
      schema: ${var.silver_schema}
      serverless: true
      photon: true
      channel: CURRENT
      continuous: true
      edition: ADVANCED
      libraries:
        - notebook:
            path: ../src/streaming/silver_events.py
      configuration:
        catalog: ${var.catalog}
        bronze_schema: ${var.bronze_schema}
        silver_schema: ${var.silver_schema}
      notifications:
        - alerts:
            - on-update-failure
            - on-flow-failure
          email_recipients:
            - data-engineering@company.com
      tags:
        environment: ${bundle.target}
        layer: silver
        pipeline_type: streaming
```

---

### ~~ST-02 (Retired)~~: Expectations for Quality
> **Retired in v5.4.0** -- this rule duplicated DQ-01. See the **Data Quality** domain for streaming expectation guidance.

---

### ST-02: Managed Checkpointing
**Severity:** Required | **Trigger:** When configuring disaster recovery for streaming

**Rule:** Use Lakeflow SDP's managed checkpointing for all streaming state; do not manually configure checkpoint locations for SDP pipelines.
**Why:** Managed checkpoints provide automatic state management, failure recovery with exactly-once semantics, and cross-region replication for DR compliance. Manual checkpoint management introduces operational risk from misconfigured paths or orphaned state.

**Managed Checkpointing Provides:**

| Feature | Description |
|---------|-------------|
| Automatic State Management | Checkpoints stored in managed location |
| Failure Recovery | Automatic restart from last checkpoint |
| Exactly-Once Semantics | Guaranteed message processing |
| Cross-Region DR | Checkpoints replicated with DR config |

**Correct:** SDP manages checkpoints automatically -- no manual configuration needed.

**Anti-Pattern (only valid for exception-approved raw Structured Streaming):**
```python
# Manual checkpoint management is error-prone
stream.writeStream \
    .option("checkpointLocation", "/mnt/checkpoints/my_stream") \
    .start()
```

---

### ~~ST-04 (Retired)~~: Jobs Compute Only
> **Retired in v5.4.0** -- this rule duplicated CP-05. See the **Compute** domain for production compute guidance.

---

### ST-03: Fixed Worker Count
**Severity:** Required | **Trigger:** When configuring compute for any streaming workload

**Rule:** Disable auto-scaling for streaming clusters; use a fixed number of workers.
**Why:** Auto-scaling causes Spark state redistribution when workers are added or removed, leading to reprocessing delays, potential data loss, and unpredictable latency spikes in streaming workloads.

**Correct:**
```yaml
# Fixed workers in SDP classic compute
clusters:
  - label: default
    num_workers: 4

# Fixed workers in raw Structured Streaming jobs
job_clusters:
  - job_cluster_key: streaming
    new_cluster:
      num_workers: 4
      spark_conf:
        spark.streaming.stopGracefullyOnShutdown: "true"
```

**Anti-Pattern:**
```yaml
# Auto-scaling causes state redistribution
new_cluster:
  autoscale:
    min_workers: 2
    max_workers: 8
```

---

### ST-04: Idempotent Operations
**Severity:** Required | **Trigger:** When using `foreachBatch` in raw Structured Streaming (exception cases)

**Rule:** All streaming write operations must be idempotent; use MERGE (not append) in `foreachBatch` to handle reprocessing after failures.
**Why:** Streaming failures trigger reprocessing from the last checkpoint. Non-idempotent operations like append create duplicate records on retry, corrupting downstream analytics.

**Correct:**
```python
def idempotent_foreach_batch(batch_df, batch_id):
    """Use MERGE for idempotent writes."""
    batch_df.createOrReplaceTempView("updates")
    spark.sql("""
        MERGE INTO silver.events AS target
        USING updates AS source
        ON target.event_id = source.event_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

(spark.readStream
    .table("bronze.events")
    .writeStream
    .foreachBatch(idempotent_foreach_batch)
    .option("checkpointLocation", "/checkpoints/events")
    .trigger(processingTime="10 seconds")
    .start())
```

**Anti-Pattern:**
```python
def non_idempotent_batch(batch_df, batch_id):
    # Append creates duplicates on retry
    batch_df.write.mode("append").saveAsTable("silver.events")
```

---

## Monitoring

Query SDP pipeline health and data quality via system tables:

```sql
-- Pipeline execution history
SELECT pipeline_name, state, start_time,
       TIMESTAMPDIFF(MINUTE, start_time, end_time) AS duration_minutes
FROM system.lakeflow.pipeline_events
WHERE pipeline_name = 'Event Streaming Pipeline'
ORDER BY start_time DESC LIMIT 10;

-- Data quality pass rates
SELECT expectation_name, dataset_name,
       passed_records, failed_records,
       ROUND(100.0 * passed_records / (passed_records + failed_records), 2) AS pass_rate
FROM system.lakeflow.flow_progress
WHERE pipeline_name = 'Event Streaming Pipeline'
ORDER BY timestamp DESC;
```

---

## Checklist
- [ ] ST-01: Using Lakeflow SDP (not raw Structured Streaming) unless exception approved
- [ ] ~~ST-02 (old)~~: Retired -- see DQ-01 in Data Quality domain
- [ ] ST-02: SDP managed checkpointing used (no manual checkpoint paths in SDP)
- [ ] ~~ST-04 (old)~~: Retired -- see CP-05 in Compute domain
- [ ] ST-03: Cluster uses fixed `num_workers` (no `autoscale` block)
- [ ] ST-04: All `foreachBatch` operations use MERGE for idempotent writes
