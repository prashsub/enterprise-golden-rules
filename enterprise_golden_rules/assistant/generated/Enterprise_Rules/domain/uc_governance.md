# Unity Catalog & Data Governance Golden Rules
**Rules:** GOV-01..16, EA-01..12, DS-01..07 | **Count:** 35 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| GOV-01 | Provision identities at account level via SCIM | Critical | No manual user creation in workspace |
| GOV-02 | Define and manage groups in your IdP | Critical | No workspace-local groups |
| GOV-03 | Assign admin roles sparingly; avoid ALL PRIVILEGES | Required | Account admins limited to 2-3 people |
| GOV-04 | Use catalog-level managed storage for data isolation | Required | Each catalog has its own `MANAGED LOCATION` |
| GOV-05 | Prefer managed tables over external tables | Required | External tables have documented justification |
| GOV-06 | Use service principals for production jobs | Required | `run_as: service_principal_name` in prod bundles |
| GOV-07 | Assign object ownership to groups, not individuals | Required | No individual email in `SET OWNER TO` |
| GOV-08 | Use lineage for impact analysis before schema changes | Required | Query `system.access.table_lineage` before ALTER |
| GOV-09 | Implement governance-as-code via system tables | Required | Scheduled compliance check jobs exist |
| GOV-10 | Use row filters and column masks for fine-grained access | Required | No per-audience filtered views |
| GOV-11 | Configure audit logging for all workspaces | Required | `system.access.audit` queries operational |
| GOV-12 | Use ABAC policies for scalable tag-driven access control | Critical | Tag-driven row filters/column masks |
| GOV-13 | Define ABAC policies at catalog level for max inheritance | Required | Catalog-level ABAC policies |
| GOV-14 | Use RBAC (privilege grants) as baseline access model | Critical | GRANT/REVOKE privileges |
| GOV-15 | Keep ABAC UDFs simple, deterministic, no external calls | Required | Simple SQL, no is_member() |
| GOV-16 | Grant BROWSE on catalogs for discoverability | Required | BROWSE for all-account-users |
| EA-01 | All data assets must have business context documentation | Critical | Table and column COMMENTs present |
| EA-02 | PII columns must be tagged and classified | Critical | `pii = true` tag on sensitive columns |
| EA-03 | Every data domain must have an assigned data steward | Required | Steward names documented per domain |
| EA-04 | All compute usage attributed with tags | Critical | Custom tags enforced via cluster policies |
| EA-05 | Required custom tags: team, cost_center, environment | Required | Cluster policy requires these three tags |
| EA-06 | Serverless workloads use assigned budget policies | Critical | Budget policies in system.billing.usage |
| EA-07 | All new projects require architecture review | Required | Architecture checklist completed pre-build |
| EA-08 | Rule exceptions require documented approval | Required | Exception requests filed and tracked |
| EA-09 | Use Governed Tags for UC object metadata | Critical | Account-level governed tags configured |
| EA-10 | Treat data as a product with defined SLAs and ownership | Critical | Gold tables tagged as `data_product = true` |
| EA-11 | Define data contracts for cross-domain interfaces | Required | YAML contract files in Git per interface |
| EA-12 | Assess and track AI readiness across data domains | Required | `monitoring.ai_readiness_scores` populated |
| DS-01 | Unity Catalog for all shared assets | Critical | Delta Sharing via UC |
| DS-02 | Prefer Databricks-to-Databricks sharing | Critical | D2D sharing first |
| DS-03 | Never share PII without row filters or column masks | Critical | PII protection on shares |
| DS-04 | Define retention and revocation policies | Critical | Share expiration configured |
| DS-05 | Enable audit logging for all sharing | Critical | `system.access.audit` for shares |
| DS-06 | Short-lived tokens for open sharing | Required | Token rotation policy |
| DS-07 | Share views, not base tables | Required | Curated views in shares |

## Detailed Rules

### GOV-01: SCIM Identity Provisioning
**Severity:** Critical | **Trigger:** When onboarding users or groups to Databricks

**Rule:** All users, groups, and service principals must be provisioned at the Databricks account level via SCIM from your identity provider.
**Why:** Manual user creation leads to identity drift, orphaned accounts after offboarding, and inconsistent access control across workspaces.

**Correct:**
```
Identity Provider (Okta, Azure AD, etc.)
    |
    +-- SCIM Provisioning --> Databricks Account
                                   |
                                   +-- Automatic Sync to Workspaces
```

**Anti-Pattern:**
```
# WRONG: Manual user creation per workspace
Workspace Admin -> Settings -> Add User -> john@company.com
# Results in: no IdP sync, no automated offboarding
```

---

### GOV-03: Limit Admin Roles
**Severity:** Required | **Trigger:** When assigning permissions to any user or group

**Rule:** Assign admin roles sparingly (2-3 account admins max) and never grant `ALL PRIVILEGES` on catalogs or schemas.
**Why:** Overly broad privileges bypass row filters, column masks, and fine-grained governance, creating compliance risk and accidental data exposure.

**Correct:**
```sql
-- Specific grants following least privilege
GRANT USE CATALOG ON CATALOG prod_catalog TO `data-engineers`;
GRANT SELECT ON SCHEMA prod_catalog.gold TO `business-analysts`;
GRANT BROWSE ON CATALOG prod_catalog TO `all-account-users`;
```

**Anti-Pattern:**
```sql
-- WRONG: Overly broad, bypasses governance controls
GRANT ALL PRIVILEGES ON CATALOG prod_catalog TO `data-engineers`;
```

---

### GOV-04: Catalog-Level Managed Storage
**Severity:** Required | **Trigger:** When creating a new catalog

**Rule:** Configure dedicated managed storage at the catalog level as the primary unit of data isolation.
**Why:** Catalog-level storage ensures environment separation (dev vs prod), simplifies IAM policies, and prevents cross-environment data leakage.

**Correct:**
```sql
CREATE CATALOG production_catalog
MANAGED LOCATION 's3://prod-data/unity-catalog/';

CREATE CATALOG development_catalog
MANAGED LOCATION 's3://dev-data/unity-catalog/';
```

**Anti-Pattern:**
```sql
-- WRONG: Reusing DBFS root or shared bucket
CREATE CATALOG production_catalog
MANAGED LOCATION 'dbfs:/unity-catalog/';
```

---

### GOV-06: Service Principals for Production
**Severity:** Required | **Trigger:** When deploying production jobs via Asset Bundles

**Rule:** All production jobs must run as service principals, not individual user accounts.
**Why:** Jobs tied to individual accounts break when employees leave, create audit ambiguity, and risk accidental overwrites from personal credentials.

**Correct:**
```yaml
resources:
  jobs:
    production_etl:
      run_as:
        service_principal_name: "etl-service-principal"
```

**Anti-Pattern:**
```yaml
# WRONG: Job runs as individual user (implicit default)
resources:
  jobs:
    production_etl:
      # No run_as specified -- defaults to deploying user
```

---

### GOV-07: Group Ownership
**Severity:** Required | **Trigger:** When setting ownership of catalogs, schemas, or tables

**Rule:** Assign ownership of all UC objects to groups, never to individual user accounts.
**Why:** Individual ownership creates single points of failure; when that person leaves, ownership transfers require admin intervention and may block operations.

**Correct:**
```sql
ALTER CATALOG production SET OWNER TO `data-platform-admins`;
ALTER SCHEMA production.gold SET OWNER TO `analytics-engineers`;
```

**Anti-Pattern:**
```sql
-- WRONG: Individual ownership
ALTER TABLE prod.gold.sales SET OWNER TO `john@company.com`;
```

---

### GOV-10: Row Filters and Column Masks
**Severity:** Required | **Trigger:** When multiple teams need different access levels to the same table

**Rule:** Use UC row filters and column masks for fine-grained access control instead of creating separate filtered views per audience.
**Why:** Separate views per audience cause data duplication, governance gaps (views may not inherit tags), and maintenance overhead that grows with each new team.

**Correct:**
```sql
-- Row filter: regional access control
CREATE FUNCTION gold.region_filter(region_param STRING)
RETURNS BOOLEAN
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('global-analysts'),
          true, region_param = current_user_region());

ALTER TABLE gold.fact_sales
SET ROW FILTER gold.region_filter ON (region);

-- Column mask: PII redaction
CREATE FUNCTION gold.mask_email(email_param STRING)
RETURNS STRING
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('pii-readers'),
          email_param,
          CONCAT('***@', SPLIT(email_param, '@')[1]));

ALTER TABLE gold.dim_customer
ALTER COLUMN email SET MASK gold.mask_email;
```

**Anti-Pattern:**
```sql
-- WRONG: Separate views per audience
CREATE VIEW gold.sales_emea AS SELECT * FROM gold.fact_sales WHERE region = 'EMEA';
CREATE VIEW gold.sales_na AS SELECT * FROM gold.fact_sales WHERE region = 'NA';
```

---

### EA-02: PII Classification
**Severity:** Critical | **Trigger:** When creating or altering tables containing personal data

**Rule:** All columns containing personally identifiable information must be tagged with `pii = true` and the appropriate `pii_type`.
**Why:** Untagged PII prevents automated compliance enforcement (GDPR/CCPA/HIPAA), blocks audit reporting, and exposes the organization to regulatory fines.

**Correct:**
```sql
ALTER TABLE gold.dim_customer
ALTER COLUMN email SET TAGS ('pii' = 'true', 'pii_type' = 'email');

ALTER TABLE gold.dim_customer
ALTER COLUMN phone SET TAGS ('pii' = 'true', 'pii_type' = 'phone');

ALTER TABLE gold.dim_customer
SET TAGS ('data_classification' = 'confidential');
```

**Anti-Pattern:**
```sql
-- WRONG: No PII tags, no classification
CREATE TABLE gold.dim_customer (
    customer_id BIGINT,
    email STRING,      -- PII but untagged
    phone STRING       -- PII but untagged
);
```

---

### EA-10: Data as a Product
**Severity:** Critical | **Trigger:** When publishing Gold layer tables for consumption

**Rule:** Each Gold layer data asset must be published as a data product with defined ownership, SLAs, quality guarantees, and discoverability metadata.
**Why:** Without product discipline, consumers rely on tribal knowledge, duplicate pipelines proliferate, and nobody is accountable when data quality degrades.

**Correct:**
```sql
ALTER TABLE gold.dim_customer SET TAGS (
    'data_product' = 'true',
    'data_product_owner' = 'customer-analytics',
    'data_product_sla' = 'daily-6am-utc',
    'data_product_version' = 'v2.1'
);
```

---

### EA-11: Data Contracts
**Severity:** Required | **Trigger:** When data flows across domain boundaries

**Rule:** Cross-domain data interfaces must define explicit contracts specifying schema, quality rules, freshness guarantees, and breaking change policies.
**Why:** Without contracts, upstream schema changes silently break downstream dashboards, models, and pipelines, causing cascading failures with no accountability.

**Correct:**
```yaml
# data_contract_dim_customer.yaml
contract:
  name: dim_customer
  version: "2.1"
  owner: customer-analytics
  schema: gold
  freshness_sla: "daily by 06:00 UTC"
  breaking_change_policy: "30-day deprecation notice"
  quality_rules:
    - "customer_key IS NOT NULL"
    - "customer_id IS NOT NULL"
    - "is_current IN (true, false)"
  volume_expectation:
    min_rows: 100000
    max_rows: 50000000
```

---

### GOV-09: Governance-as-Code
**Severity:** Required | **Trigger:** When auditing compliance across tables and permissions

**Rule:** Automate governance enforcement using system tables and scheduled validation jobs rather than manual audits.
**Why:** Manual audits are point-in-time snapshots that miss violations between reviews; automated checks provide continuous compliance and proactive alerting.

**Correct:**
```sql
-- Automated check: All Gold tables have PRIMARY KEY constraints
SELECT t.table_catalog, t.table_schema, t.table_name,
    CASE WHEN tc.constraint_name IS NOT NULL
         THEN 'PASS' ELSE 'FAIL' END AS pk_check
FROM information_schema.tables t
LEFT JOIN information_schema.table_constraints tc
    ON t.table_catalog = tc.table_catalog
    AND t.table_schema = tc.table_schema
    AND t.table_name = tc.table_name
    AND tc.constraint_type = 'PRIMARY KEY'
WHERE t.table_schema = 'gold';

-- Automated check: No ALL PRIVILEGES grants exist
SELECT grantee, privilege_type, table_catalog
FROM information_schema.table_privileges
WHERE privilege_type = 'ALL PRIVILEGES';
```

---

### GOV-12: Use ABAC for Scalable Tag-Driven Access Control
**Severity:** Critical | **Trigger:** Fine-grained access control needed across many tables

**Rule:** Use Attribute-Based Access Control (ABAC) policies with governed tags for centralized, scalable fine-grained access. Prefer ABAC over per-table row filters/column masks.
**Why:** ABAC policies defined at catalog/schema level inherit to all children — no per-table config. Governed tags drive dynamic enforcement.

**Correct:**
```sql
CREATE POLICY mask_pii ON CATALOG prod_catalog
COLUMN MASK governance.mask_ssn
TO `all_users` EXCEPT `compliance_team`
FOR TABLES
MATCH COLUMNS hasTagValue('pii', 'ssn') AS ssn
ON COLUMN ssn;
```

**Anti-Pattern:** Creating individual row filters on each table instead of using ABAC policies

---

### GOV-13: Define ABAC Policies at Catalog Level
**Severity:** Required | **Trigger:** Creating ABAC policies

**Rule:** Define ABAC policies at the highest applicable level (catalog preferred) for maximum inheritance.
**Why:** Catalog-level policies govern all child schemas and tables automatically. New tagged tables inherit policies without additional configuration.

**Anti-Pattern:** Creating identical ABAC policies on individual tables instead of once at catalog level

---

### GOV-14: Use RBAC as Baseline Access Model
**Severity:** Critical | **Trigger:** Setting up access control

**Rule:** Use RBAC (GRANT/REVOKE) as the foundation. Layer ABAC on top for data-level controls.
**Why:** RBAC controls WHO can access WHAT objects. ABAC controls WHAT DATA they see within those objects.

**Correct:**
```sql
-- Step 1: RBAC baseline
GRANT USE CATALOG ON CATALOG prod_catalog TO `data-engineers`;
GRANT SELECT ON SCHEMA prod_catalog.gold TO `business-analysts`;
-- Step 2: ABAC layer (data-level filtering/masking)
```

**Anti-Pattern:** Granting ALL PRIVILEGES, or granting to individual users instead of groups

---

### GOV-15: Keep ABAC UDFs Simple and Deterministic
**Severity:** Required | **Trigger:** Writing UDFs for ABAC policies

**Rule:** ABAC UDFs must be simple SQL functions: deterministic, no external calls, no is_member() inside UDFs.
**Why:** UDFs run on EVERY query for EVERY row. Inefficient UDFs become governance bottlenecks.

**Correct:**
```sql
CREATE FUNCTION governance.mask_email(email STRING)
RETURNS STRING DETERMINISTIC
RETURN CONCAT('***@', SPLIT(email, '@')[1]);
```

**Anti-Pattern:** Using is_account_group_member() inside UDFs, external API calls, complex subqueries

---

### GOV-16: Grant BROWSE on Catalogs for Discoverability
**Severity:** Required | **Trigger:** Setting up catalog permissions

**Rule:** Grant BROWSE on all catalogs to all-account-users for metadata discovery without data access.
**Why:** Enables self-service data discovery and access request workflows.

**Correct:**
```sql
GRANT BROWSE ON CATALOG prod_catalog TO `all-account-users`;
```

---

## Delta Sharing (DS)

### DS-01: Unity Catalog for All Shared Assets
**Severity:** Critical | **Trigger:** When sharing data across organizations or platforms

**Rule:** All data sharing must be done through Unity Catalog using Delta Sharing protocol.
**Why:** UC-based sharing inherits all governance controls, audit logging, and lineage tracking. Sharing outside UC creates unaudited data copies.

**Correct:**
```sql
-- Create share
CREATE SHARE customer_data_share;
ALTER SHARE customer_data_share ADD TABLE gold.dim_customer;

-- Create recipient
CREATE RECIPIENT partner_org USING ID 'partner-sharing-id';
GRANT SELECT ON SHARE customer_data_share TO RECIPIENT partner_org;
```

---

### DS-03: Never Share PII Without Filters
**Severity:** Critical | **Trigger:** When shares contain tables with PII columns

**Rule:** Apply row filters or column masks to shared tables containing PII before adding to shares.
**Why:** Sharing PII without protection violates GDPR/CCPA and exposes the organization to regulatory fines.

**Correct:**
```sql
-- Share a view with PII masked
CREATE VIEW gold.dim_customer_shared AS
SELECT customer_id, customer_segment,
       CONCAT('***@', SPLIT(email, '@')[1]) AS email_masked
FROM gold.dim_customer;

ALTER SHARE customer_share ADD TABLE gold.dim_customer_shared;
```

---

### DS-07: Share Views, Not Base Tables
**Severity:** Required | **Trigger:** When adding assets to a Delta Share

**Rule:** Share curated views rather than base tables to control schema exposure and enable column-level filtering.
**Why:** Sharing base tables exposes all columns including internal metadata; views allow you to curate exactly what recipients see.

---

## Checklist
- [ ] GOV-01: SCIM provisioning at account level (not workspace)
- [ ] GOV-02: All groups originate from IdP, no workspace-local groups
- [ ] GOV-03: Account admins limited to 2-3; no ALL PRIVILEGES grants
- [ ] GOV-04: Each catalog has dedicated managed storage location
- [ ] GOV-05: External tables have documented justification
- [ ] GOV-06: Production jobs use `run_as: service_principal_name`
- [ ] GOV-07: All UC object ownership assigned to groups
- [ ] GOV-08: Lineage queried before any schema ALTER/DROP
- [ ] GOV-09: Automated compliance checks run on a schedule
- [ ] GOV-10: Row filters/column masks used instead of per-audience views
- [ ] GOV-11: `system.access.audit` queries in monitoring dashboard
- [ ] GOV-12: ABAC policies used for fine-grained access control
- [ ] GOV-13: ABAC policies defined at catalog level
- [ ] GOV-14: RBAC privileges established as baseline
- [ ] GOV-15: ABAC UDFs are simple, deterministic SQL
- [ ] GOV-16: BROWSE granted on all catalogs
- [ ] EA-01: Table and column COMMENTs present on all assets
- [ ] EA-02: PII columns tagged with `pii = true` and `pii_type`
- [ ] EA-03: Data steward assigned per domain
- [ ] EA-05: Cluster policies enforce team, cost_center, environment tags
- [ ] EA-06: Budget policies assigned to all serverless workloads
- [ ] EA-07: Architecture review completed before new projects
- [ ] EA-09: Governed tags configured at account level
- [ ] EA-10: Gold tables tagged as data products with SLAs
- [ ] EA-11: Data contracts in Git for cross-domain interfaces
- [ ] EA-12: AI readiness scores tracked per domain
- [ ] DS-01: All sharing done through Unity Catalog (Delta Sharing)
- [ ] DS-02: Databricks-to-Databricks sharing preferred
- [ ] DS-03: PII protected with row filters/column masks before sharing
- [ ] DS-04: Retention and revocation policies defined for all shares
- [ ] DS-05: Audit logging enabled for all sharing activities
- [ ] DS-06: Short-lived tokens used for open sharing recipients
- [ ] DS-07: Shares use curated views, not base tables
