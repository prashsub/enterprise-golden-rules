# Semantic Layer Golden Rules
**Rules:** TF-01..06, GN-01..03, MV-01..08, DB-01..04, MO-01..04 | **Count:** 25 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| ~~SL-01~~ | *Retired -- duplicate of MV-01/MV-04. See Metric Views rules below.* | -- | -- |
| TF-01 | TVF date parameters must be STRING | Critical | `start_date STRING`, not `DATE` |
| TF-02 | Schema validation before writing SQL | Critical | Columns verified against Gold YAML |
| TF-03 | v3.0 comment format for Genie assets | Required | PURPOSE, BEST FOR, NOT FOR present |
| ~~SL-02~~ | *Retired -- duplicate of MV-05. See Metric Views rules below.* | -- | -- |
| GN-01 | Inventory-first Genie Space creation | Required | Question-to-asset map documented |
| TF-04 | Required parameters before optional | Critical | No DEFAULT on first params |
| TF-05 | No LIMIT with TVF parameters | Critical | Uses ROW_NUMBER + WHERE instead |
| TF-06 | Single aggregation pass per source table | Critical | Source table read only once in CTE |
| MV-01 | All core metrics must be in Metric Views | Critical | KPI used in 2+ dashboards has MV |
| MV-02 | Reference Gold layer tables only | Critical | Source uses `gold` schema path |
| MV-03 | Business context documentation required | Critical | Structured comment block present |
| MV-04 | Schema validation before MV creation | Critical | Columns exist in Gold table |
| MV-05 | No transitive joins | Critical | No dim-to-dim joins |
| MV-06 | Synonyms for all dimensions/measures | Required | 3+ synonyms per field |
| MV-07 | Display format for all measures | Required | `format:` block on each measure |
| MV-08 | Structured comment format in YAML | Required | PURPOSE/BEST FOR/NOT FOR/DIMENSIONS |
| MO-01 | Curated data for Genie (comments, no nulls) | Required | Tables have COMMENTs, keys non-null |
| GN-02 | Sample questions configured | Required | Genie Space has sample_questions |
| GN-03 | No overlapping asset coverage | Required | Each question maps to one asset |
| MO-02 | TVF NOTE includes "DO NOT wrap in TABLE()" | Required | NOTE line present in comment |
| MO-03 | PRE-AGGREGATED in RETURNS comment | Required | Prevents Genie adding GROUP BY |
| MO-04 | Implement async wait pattern for monitors | Required | `run.wait()` or polling before query |
| DB-01 | No hardcoded environment values | Critical | Uses `${catalog}` placeholders |
| DB-02 | UPDATE-or-CREATE deployment pattern | Required | `overwrite=True` in import call |
| DB-03 | fieldName must match query alias | Critical | Widget JSON matches SQL alias |
| DB-04 | SQL returns raw numbers | Required | No FORMAT_NUMBER in SQL |

---

## Detailed Rules

### ~~SL-01 (Retired)~~: Metric View v1.1 YAML -- No Name Field
> **Retired in v5.4.0** -- this rule duplicated MV-01 and MV-04. See the **Metric Views** rules (MV-01, MV-04) in this document for YAML format and schema validation guidance.

---

### TF-01: STRING for Date Parameters
**Severity:** Critical | **Trigger:** When defining TVF parameters for dates

**Rule:** All TVF date parameters must use STRING type with explicit CAST inside the function body because Genie cannot pass DATE types.
**Why:** Genie generates SQL that passes string literals; a DATE parameter type causes runtime type-mismatch errors.

**Correct:**
```sql
CREATE FUNCTION get_costs(
    start_date STRING COMMENT 'Format: YYYY-MM-DD'
)
RETURNS TABLE (...)
RETURN
  SELECT * FROM fact_usage
  WHERE usage_date >= CAST(start_date AS DATE);
```

**Anti-Pattern:**
```sql
CREATE FUNCTION get_costs(start_date DATE)  -- Genie can't pass DATE!
```

---

### ~~SL-02 (Retired)~~: No Transitive Joins in Metric Views
> **Retired in v5.4.0** -- this rule duplicated MV-05. See **MV-05: No transitive joins** in this document for join guidance.

---

### TF-04: Required Parameters Before Optional
**Severity:** Critical | **Trigger:** When defining TVF parameter lists

**Rule:** Required parameters (no DEFAULT) must appear before optional parameters (with DEFAULT) in the function signature.
**Why:** SQL function resolution fails or produces unexpected behavior when optional parameters precede required ones.

**Correct:**
```sql
CREATE FUNCTION get_workspace_costs(
    workspace_name STRING,                    -- Required (no DEFAULT)
    start_date STRING DEFAULT '2024-01-01'    -- Optional
)
```

**Anti-Pattern:**
```sql
CREATE FUNCTION get_workspace_costs(
    start_date STRING DEFAULT '2024-01-01',   -- Optional first!
    workspace_name STRING                      -- Required after!
)
```

---

### TF-05: No LIMIT with Parameters
**Severity:** Critical | **Trigger:** When implementing top-N logic in a TVF

**Rule:** Never use a parameter variable in a LIMIT clause; use ROW_NUMBER() OVER + WHERE instead.
**Why:** `LIMIT param` causes `INVALID_LIMIT_LIKE_EXPRESSION` compilation error.

**Correct:**
```sql
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY cost DESC) AS rn
    FROM results
)
SELECT * FROM ranked WHERE rn <= CAST(limit_rows AS INT);
```

**Anti-Pattern:**
```sql
SELECT * FROM results LIMIT limit_rows;  -- Compilation error!
```

---

### TF-06: Single Aggregation Pass
**Severity:** Critical | **Trigger:** When aggregating multiple measures from the same source table

**Rule:** Aggregate all measures in a single SELECT from each source table; never read the same table in multiple CTEs.
**Why:** Multiple reads of the same fact table cause Cartesian products, inflating results 100x or more.

**Correct:**
```sql
WITH metrics AS (
    SELECT workspace_id, SUM(cost) AS total_cost, SUM(dbus) AS total_dbus
    FROM fact_usage
    GROUP BY workspace_id
)
SELECT * FROM metrics;
```

**Anti-Pattern:**
```sql
WITH costs AS (SELECT workspace_id, SUM(cost) FROM fact_usage GROUP BY 1),
     dbus  AS (SELECT workspace_id, SUM(dbus) FROM fact_usage GROUP BY 1)
SELECT * FROM costs c JOIN dbus d ON c.workspace_id = d.workspace_id;
```

---

### DB-03: fieldName Must Match Query Alias
**Severity:** Critical | **Trigger:** When wiring dashboard widgets to dataset queries

**Rule:** The widget `fieldName` in dashboard JSON must exactly match the SQL column alias (case-sensitive).
**Why:** A mismatch causes the widget to render with no data and no error message.

**Correct:**
```json
{
  "fieldName": "total_cost",
  "displayName": "Total Cost"
}
```
```sql
SELECT SUM(list_cost) AS total_cost FROM fact_usage
```

**Anti-Pattern:**
```json
{ "fieldName": "totalCost" }
{ "fieldName": "Total Cost" }
```

---

### DB-04: SQL Returns Raw Numbers
**Severity:** Required | **Trigger:** When writing SQL for dashboard datasets

**Rule:** Dashboard SQL must return raw numeric values; formatting is handled by widget `numberFormat` configuration.
**Why:** Pre-formatted strings break sorting, aggregation, conditional formatting, and currency localization.

**Correct:**
```sql
SELECT SUM(cost) AS total_cost FROM fact_usage  -- returns number
```
```json
{ "fieldName": "total_cost", "numberFormat": {"type": "currency", "currency": "USD"} }
```

**Anti-Pattern:**
```sql
SELECT CONCAT('$', FORMAT_NUMBER(SUM(cost), 2)) AS total_cost  -- returns string!
```

---

### DB-01: No Hardcoded Environment Values
**Severity:** Critical | **Trigger:** When writing dashboard or TVF SQL with catalog/schema references

**Rule:** Use `${catalog}` and `${gold_schema}` variable placeholders instead of hardcoded catalog or schema names.
**Why:** Hardcoded values break promotion across dev/staging/prod environments.

**Correct:**
```sql
SELECT * FROM ${catalog}.${gold_schema}.fact_usage WHERE ...
```

**Anti-Pattern:**
```sql
SELECT * FROM company_prod.gold.fact_usage WHERE ...  -- breaks in dev!
```

---

## Checklist
- [ ] ~~SL-01~~: Retired -- see MV-01/MV-04 (Metric Views)
- [ ] ~~SL-02~~: Retired -- see MV-05 (No transitive joins)
- [ ] TF-01: All TVF date parameters use STRING type with CAST
- [ ] TF-02: Every column reference verified against Gold YAML schema
- [ ] TF-03: All Genie-facing assets have v3.0 structured comment
- [ ] TF-04: Required TVF parameters listed before optional parameters
- [ ] TF-05: Top-N uses ROW_NUMBER + WHERE, not LIMIT with parameter
- [ ] TF-06: Each source table is read only once per aggregation pass
- [ ] GN-01: Genie Space has documented question-to-asset inventory
- [ ] GN-02: Sample questions configured for Genie Space
- [ ] GN-03: No overlapping asset coverage (each question maps to one asset)
- [ ] MV-06: Every dimension and measure has 3+ synonyms
- [ ] MV-07: Every measure has a display format block
- [ ] MO-01: Curated data for Genie (comments, no nulls)
- [ ] MO-02: TVF NOTE includes "DO NOT wrap in TABLE()"
- [ ] MO-03: PRE-AGGREGATED in RETURNS comment
- [ ] MO-04: Implement async wait pattern (`run.wait()`) before querying monitor results
- [ ] DB-01: No hardcoded catalog/schema names; uses ${variable} placeholders
- [ ] DB-02: Dashboard deployment uses UPDATE-or-CREATE (overwrite=True)
- [ ] DB-03: Widget fieldName matches SQL alias exactly (case-sensitive)
- [ ] DB-04: SQL returns raw numbers; formatting is in widget JSON
