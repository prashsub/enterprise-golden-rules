# Python Development Standards

> **Document Owner:** Platform Engineering | **Status:** Approved | **Last Updated:** February 2026

## Overview

This document defines Python development standards for Databricks, including parameter handling, module imports, and the distinction between pure Python files and notebooks.

---

## Golden Rules

| ID | Rule | Severity | WAF Pillar |
|----|------|----------|------------|
| **PY-01** | Use `dbutils.widgets.get()` for parameters | Critical | [OpEx](https://docs.databricks.com/en/dev-tools/databricks-utils) |
| **PY-02** | Pure Python files for imports | Critical | Reliability |
| **PY-03** | sys.path setup for Asset Bundle imports | Critical | OpEx |
| **PY-04** | No notebook header in importable modules | Critical | Performance |

---

## Parameter Handling

### Correct Pattern

```python
def get_parameters():
    """Get job parameters from dbutils widgets."""
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")

    print(f"Parameters: catalog={catalog}, schema={schema}")
    return catalog, schema
```

### Wrong Pattern

```python
# This FAILS in notebook_task!
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--catalog", required=True)
args = parser.parse_args()  # ERROR: arguments are required
```

### Decision Table

| Context | Python Method |
|---------|---------------|
| `notebook_task` in Asset Bundles | `dbutils.widgets.get()` |
| Interactive notebook | `dbutils.widgets.get()` |
| DLT pipeline | `spark.conf.get()` |
| Local script | `argparse` |

---

## Pure Python vs Notebooks

### The Problem

Files with `# Databricks notebook source` header cannot be imported in serverless compute.

```python
# utils.py with notebook header - CANNOT import!
# Databricks notebook source  <- Breaks imports!

def helper():
    pass
```

### The Solution

Remove the notebook header from importable files:

```python
# utils.py - Pure Python (NO header)
"""Utility functions for data processing."""

def helper():
    """Helper function that can be imported."""
    pass
```

### File Organization

| File Type | Header | Can Import | Use For |
|-----------|--------|------------|---------|
| Pure Python | None | Yes | Shared modules |
| Notebook | `# Databricks notebook source` | No | Entry points |

```
src/
├── my_project/
│   ├── __init__.py        # Package init
│   ├── utils.py           # Pure Python - imports OK
│   └── transformations.py # Pure Python - imports OK
│
└── jobs/
    ├── bronze_setup.py    # Notebook - entry point
    └── gold_merge.py      # Notebook - entry point
```

---

## sys.path Setup for Imports

Add this at the top of notebooks needing imports:

```python
# Databricks notebook source

import sys
from pathlib import Path

def setup_path():
    """Set up sys.path for Asset Bundle imports."""
    try:
        notebook_path = dbutils.notebook.entry_point \
            .getDbutils().notebook().getContext() \
            .notebookPath().get()

        workspace_base = "/Workspace" + "/".join(
            notebook_path.split("/")[:-2]
        )

        if workspace_base not in sys.path:
            sys.path.insert(0, workspace_base)

        return workspace_base
    except Exception as e:
        print(f"Path setup failed: {e}")
        return None

workspace_path = setup_path()

# NOW imports work
from my_project.utils import helper
```

---

## DLT Pipeline Parameters

DLT uses `spark.conf.get()`:

```python
import dlt

catalog = spark.conf.get("catalog")
bronze_schema = spark.conf.get("bronze_schema")

@dlt.table(name="silver_customers")
def silver_customers():
    return dlt.read_stream(f"{catalog}.{bronze_schema}.bronze_customers")
```

---

## Standard Job Template

```python
# Databricks notebook source

def get_parameters():
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    return catalog, schema


def main():
    catalog, schema = get_parameters()
    spark = SparkSession.builder.appName("My Job").getOrCreate()

    try:
        # Your logic here
        process_data(spark, catalog, schema)

        print("Job completed successfully")
        dbutils.notebook.exit("SUCCESS")

    except Exception as e:
        print(f"Error: {e}")
        dbutils.notebook.exit(f"FAILED: {e}")
        raise


if __name__ == "__main__":
    main()
```

---

## Error Handling Pattern

```python
def robust_job():
    catalog, schema = get_parameters()
    spark = get_spark_session()

    tables_processed = 0
    errors = []

    for table in ["dim_customer", "fact_orders"]:
        try:
            process_table(spark, catalog, schema, table)
            tables_processed += 1
            print(f"OK: {table}")
        except Exception as e:
            errors.append(f"{table}: {e}")
            print(f"FAIL: {table}: {e}")

    print(f"\nProcessed: {tables_processed} tables")

    if errors:
        raise RuntimeError(f"{len(errors)} errors occurred")

    dbutils.notebook.exit("SUCCESS")
```

---

## Validation Checklist

### Parameters
- [ ] Uses `dbutils.widgets.get()` (not argparse)
- [ ] Parameters logged for debugging
- [ ] YAML uses `base_parameters`

### Module Organization
- [ ] Shared code in pure Python (no header)
- [ ] Entry points are notebooks
- [ ] sys.path setup where needed

### Error Handling
- [ ] try/except around main logic
- [ ] `dbutils.notebook.exit()` for signaling
- [ ] Errors logged with context

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `arguments are required` | argparse | Use widgets |
| `ModuleNotFoundError` | Notebook header | Remove header |
| `ModuleNotFoundError` | Missing path | Add sys.path setup |

---

## Related Documents

- [Asset Bundle Standards](19-asset-bundle-standards.md)
- [Serverless Compute](11-serverless-compute.md)

---

## References

- [Databricks Notebooks](https://docs.databricks.com/notebooks/)
- [Databricks Widgets](https://docs.databricks.com/notebooks/widgets.html)
