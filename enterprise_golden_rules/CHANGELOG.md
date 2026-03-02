# Changelog

All notable changes to the Enterprise Golden Rules framework.

## [5.4.2] - 2026-02-18

### Changed
- **Globally unique file numbering**: Assigned unique number ranges per domain to eliminate cross-directory collisions and gaps
  - **PA** (10-20): Closed gap at 17 — shifted 18→17, 19→18, 20→19, 21→20
  - **SA Data Pipelines** (25-28): Moved from 10-14 to avoid PA collision — 10→25, 11→26, 12→27, 14→28
  - **SA Dashboards/Monitoring** (35-36): Moved from 40-41 to avoid onboarding collision — 40→35, 41→36
  - **Training** (70-74): Moved from 00-04 to avoid EA collision — 00→70, 01→71, 02→72, 03→73, 04→74
  - **Onboarding** (80-81): Moved from 40-41 to avoid dashboard collision — 40→80, 41→81
- 17 files renamed, 24 files unchanged; all cross-references updated
- Fixed pre-existing broken links in onboarding (wrong paths to `part2-development-standards/` and `part3-infrastructure/`)
- Added "Numbering Standard" section to README.md
- Updated `assistant/build_rules.py` SOURCE_DOCS paths

---

## [5.4.1] - 2026-02-17

### Added
- **New document**: `platform-architecture/16-data-access-patterns.md` — decision framework for Ingestion vs Federation vs Delta Sharing
- **DI prefix** (Data Integration): DI-01..DI-07 (7 new golden rules)
  - DI-01: Default to ingestion for production analytics (Critical)
  - DI-02: Reserve federation for ad-hoc access and migration staging (Critical)
  - DI-03: Use Delta Sharing for cross-organization exchange (Required)
  - DI-04: Prefer catalog federation over query federation (Required)
  - DI-05: Transition federation to ingestion when patterns stabilize (Required)
  - DI-06: Document data access pattern for every external source (Required)
  - DI-07: Never federate high-volume joins or aggregations (Critical)
- Data Access Pattern comparison matrix and decision tree
- Cross-references from PA-04, Bronze (DP-05), and Delta Sharing (DS-01..07)
- DI-01/DI-02 added to assistant workspace instructions Top-40

### Changed
- Framework now has **32 prefixes** (was 31) and **162+ golden rules** (was 155+)

---

## [5.4.0] - 2026-02-16

### Removed
- **3 duplicate SA documents** deleted (all rules were duplicates of PA):
  - `solution-architecture/governance/20-unity-catalog-governance.md` (BP-08/09, GOV-01..05)
  - `solution-architecture/compute/21-compute-configuration.md` (BP-04, CMP-01..04)
  - `solution-architecture/data-pipelines/13-delta-lake-best-practices.md` (BP-01/02/03/06/07/10)
- **BP prefix retired**: All 10 rules were duplicates of DL/SC/GOV rules
- **SL prefix retired**: SL-01 = MV-01+MV-04, SL-02 = MV-05; doc 33 converted to navigation hub
- **12 overlapping rules removed** from 6 SA documents:
  - SA-03 (= DQ-02), SA-04 (= PY-02) from silver layer
  - DA-01 (= DM-02+DM-03), DA-06 (= DL-07+CM-02/03) from gold layer
  - ST-02 (= DQ-01), ST-04 (= CP-05) from streaming
  - GS-04 (= ML-07) from genai standards
  - MO-05, MO-06 relocated to REL-10/11

### Changed
- **DA rules renumbered**: DA-02→DA-01, DA-03→DA-02, DA-04→DA-03, DA-05→DA-04 (4 rules)
- **ST rules renumbered**: ST-03→ST-02, ST-05→ST-03, ST-06→ST-04 (4 rules)
- **GS rules renumbered**: GS-05→GS-04, GS-06→GS-05, GS-07→GS-06, GS-08→GS-07 (7 rules)

### Added
- **REL-10**: Monitor and manage platform service limits (relocated from MO-05)
- **REL-11**: Invest in capacity planning for production workloads (relocated from MO-06)
- **Platform & Enterprise Prerequisites** sections added to all 15 SA documents
- Cross-reference callouts for all removed rules pointing to their EA/PA equivalents

### Summary
- SA documents: 18 → 15
- SA rules (removing duplicates): ~113 → 73 unique
- Framework prefixes: 33 → 31 (retired BP, SL)
- PA REL rules: 9 → 11 (added REL-10/11)
- Framework total: 155+ unique rules, 31 prefixes, zero collisions

---

## [5.3.0] - 2026-02-16

### Changed
- **Rule ID Rationalization**: Eliminated all rule ID collisions by giving every source document its own unique prefix. Zero duplicate IDs across the entire framework.
  - **11 new prefixes**: SC (Serverless Compute), CP (Cluster Policies), SM (Secrets Management), PY (Python Development), SA (Silver Architecture), TF (Table-Valued Functions), GN (Genie Spaces), GA (GenAI Agents), GS (GenAI Standards), AG (AI Gateway), DB (Dashboards unified)
  - **33 total prefixes**, 165+ rules, zero collisions
- **Platform Architecture restructured**:
  - Doc 10 (Platform Overview): Reduced from 21 PA rules to PA-01..05 navigation hub with cross-reference table; COST-01..03 unchanged
  - Doc 11 (Serverless): PA-03/PA-03a..h → **SC-01..09**
  - Doc 12 (UC Tables & Delta Lake): PA-01/01a/01b, PA-02/02a/02b/02c → **DL-01..07**; old DL-04..08 → **DL-08..12** (12 rules unified under DL prefix)
  - Doc 13 (Cluster Policies): PA-18/18a..e, PA-19..21 → **CP-01..09**
  - Doc 14 (Secrets & Workspace): PA-09/09a/09b, PA-11 → **SM-01..04**
  - Doc 21 (Python Development): PA-07/08/11/12 → **PY-01..04**
- **Solution Architecture restructured**:
  - Doc 50 (MLflow): ML-16..18 → **ML-07..09** (ML-01..06 unchanged)
  - Doc 51 (GenAI Agent Patterns): ML-04..07 → **GA-01..04**
  - Doc 52 (GenAI Standards): ML-08..15 → **GS-01..08**
  - Doc 53 (AI Gateway): ML-11..15 → **AG-01..05**
  - Silver Layer: DA-03..06 → **SA-01..04**
  - Gold Layer: DA-05..08 → **DA-03..06** (renumbered sequential)
  - TVF Patterns: SL-02/03/04/07/08/09 → **TF-01..06**
  - Genie Space Patterns: SL-06/04/08 → **GN-01..03**
  - Semantic Layer Overview: Reduced to **SL-01..02** with cross-refs
  - Dashboard Patterns: MO-02/03 → **DB-03..04** (unified under DB prefix)
  - Lakehouse Monitoring: MO-05..07, IN-09/10 → **MO-02..06** (unified under MO prefix)
- Updated all cross-references: README.md, architecture-evolution.md, all WAF pillar tables
- Updated all assistant files: workspace instructions, 12 domain files, audit checklist, build_rules.py

---

## [5.2.6] - 2026-02-16

### Added
- **IN-11**: Use `mode: development` / `mode: production` on all deployment targets
- **IN-12**: Set `run_as` to service principal for staging/production targets
- **IN-13**: Define top-level `permissions` block on all bundles

### Changed
- **Improved Asset Bundle Standards** (`19-asset-bundle-standards.md`):
  - Added deployment modes section (development, production, custom presets)
  - Added `run_as` identity section (top-level, per-target, per-job)
  - Added `permissions` section (top-level, resource-level, precedence)
  - Expanded `variables` section (declaration, per-target, complex types, lookups, precedence)
  - Added library dependencies section (environments, requirements.txt, wheel, PyPI)
  - Added supported resource types reference table
  - Added complete bundle template combining all patterns
  - Added 6 new reference URLs from official docs
- **Consolidated UC Tables & Delta Lake**: Merged `17-delta-lake-best-practices.md` into `12-unity-catalog-tables.md` (renamed "Unity Catalog Tables & Delta Lake")
  - Deleted `17-delta-lake-best-practices.md` — DL-01, DL-02, DL-03 were duplicates of PA-01/PA-01a and PA-02a
  - Kept unique Delta Lake rules: DL-04 (no caching), DL-05 (no manual mods), DL-06 (legacy configs), DL-07 (UniForm), DL-08 (ANALYZE TABLE)
  - Added MERGE performance tips and "Operations You Don't Need" sections
- Fixed remaining CMP→PA references in assistant files (build_rules.py, README.md, audit checklist)
- Fixed golden rules table ordering in 4 documents: `15-unity-catalog-governance.md` (GOV), `04-data-modeling.md` (DM), `25-bronze-layer-patterns.md` (DP), `10-platform-overview.md` (PA)
- Updated all cross-references (README, platform overview, reliability, architecture evolution)
- Platform Architecture docs reduced from 11 to 10; Total docs 44→43

---

## [5.2.5] - 2026-02-11

### Changed
- **Consolidated compute docs**: Merged `16-compute-configuration.md` into `13-cluster-policies.md` (renamed "Classic Compute Governance")
  - Deleted `16-compute-configuration.md` — 3 of 6 CMP rules were duplicates of PA-03, PA-18, PA-18c
  - Moved unique rules: CMP-02 → **PA-19** (standard access mode), CMP-04 → **PA-20** (Photon), CMP-05 → **PA-21** (right-sizing)
  - Retired CMP prefix from platform-architecture (CMP remains in solution-architecture `21-compute-configuration.md` with cross-reference)
- Updated `10-platform-overview.md`: Added PA-19, PA-20, PA-21 to golden rules table; updated WAF alignment and cross-references
- Updated `README.md`: Replaced CMP references with PA IDs, removed deleted doc from tree
- Updated assistant files: audit checklist, report template, domain/reliability.md — all CMP→PA
- Platform Architecture docs reduced from 12 to 11

---

## [5.2.4] - 2026-02-11

### Added
- **PA-18/PA-18a-e**: Cluster policies rules (renamed from CP-01..07, originally PA-10/PA-10a-f)
  - Follows consistent PA prefix and parent/sub-rule pattern (PA-18 parent, PA-18a-e sub-rules)
  - Dropped "Serverless first" rule (duplicated PA-03)

### Changed
- Established consistent document ownership model:
  - **Overview (10-platform-overview.md)**: Parent rules only (PA-01, PA-02, PA-03, ... PA-18) — no sub-rules in table
  - **Detail docs**: All rules including sub-rules for their topic
  - Cross-references in overview point to detail docs for sub-rules
- Removed PA-01b and PA-02b from overview table (sub-rules belong in UC tables doc only)
- Fixed ordering in `12-unity-catalog-tables.md` (PA-02c was before PA-02)
- Renamed CP-01..07 to PA-18/PA-18a-e for prefix consistency

---

## [5.2.3] - 2026-02-11

### Added
- ~~CP-01 through CP-07~~: (superseded by PA-18/PA-18a-e in v5.2.4)
- **PA-03d**: Use latest serverless environment version (Required, Performance)
- **PA-03e**: Pin all custom dependencies with explicit versions (Critical, Reliability)
- **PA-03f**: Use workspace base environments for shared dependencies (Required, OpEx)
- **PA-03g**: Never install PySpark on serverless compute (Critical, Reliability)
- **PA-03h**: Configure private package repositories for internal libraries (Required, Security)
- **GOV-12**: Use ABAC policies for scalable tag-driven access control (Critical, Governance)
- **GOV-13**: Define ABAC policies at catalog level for maximum inheritance (Required, Governance)
- **GOV-14**: Use RBAC (privilege grants) as the baseline access model (Critical, Security)
- **GOV-15**: Keep ABAC UDFs simple, deterministic, and free of external calls (Required, Performance)
- **GOV-16**: Grant BROWSE on catalogs for data discoverability (Required, Governance)

### Changed
- `13-cluster-policies.md`: Renamed PA-10/PA-10a-f to CP-01 through CP-07
- `10-platform-overview.md`: Replaced duplicate PA-01/PA-02 detail sections with cross-reference to `12-unity-catalog-tables.md`
- `11-serverless-compute.md`: Added serverless environment management rules (PA-03d through PA-03h) with detailed sections
- `15-unity-catalog-governance.md`: Added ABAC, RBAC, and discoverability rules (GOV-12 through GOV-16) with detailed sections
- `README.md`: Updated WAF pillar counts and added all new rules to appropriate sections

---

## [5.2.2] - 2026-02-10

### Added
- **PA-01b**: External tables require approval (Required, Governance)
- **PA-02b**: Standard TBLPROPERTIES required (Required, OpEx)
- **DQ-05**: Enable schema-level anomaly detection for freshness and completeness (Critical, Reliability)
- **DQ-06**: Configure data profiling with baseline tables for drift detection (Required, Reliability)
- **DQ-07**: Define custom metrics for business KPIs in Lakehouse Monitors (Required, Reliability)
- PA-01 through PA-12 detailed sections added to `10-platform-overview.md`

### Changed
- `10-platform-overview.md`: Reordered golden rules table from WAF-pillar grouping to sequential PA-01 through PA-17
- `13-cluster-policies.md`: Added Golden Rule IDs (PA-10, PA-10a-f) to all detail section headers
- `README.md`: Updated rule counts, added new rules to WAF pillar sections

### Fixed
- EA-11 WAF link changed from Reliability (constraints) to Governance (governance processes)
- EA-12 was missing from golden rules summary table — reordered table sequentially EA-01 through EA-12
- Verified all 19 WAF reference links in `10-platform-overview.md` for relevance

---

## [5.2.1] - 2026-02-09

### Added
- Assistant progressive disclosure architecture (`assistant/` directory)
  - 12 consolidated domain rule files
  - Audit checklist and report template
  - 5 code example templates
  - Workspace instructions file (20K char limit)
  - Build script and deployment tooling

### Fixed
- WAF link audit: 43 edits across 20 source documents to ensure all WAF pillar links point to relevant Databricks documentation sections

---

## [5.2.0] - 2026-02-08

### Changed
- Upgraded from v5.1 to v5.2
- Aligned all golden rules to Databricks Well-Architected Lakehouse Framework
- Standardized golden rules table format: ID, Rule, Severity, WAF Pillar
- All WAF pillar links now use `docs.databricks.com/en/lakehouse-architecture/{pillar}/best-practices`

---

## [5.1.0] - 2026-02-06

### Added
- Initial commit: 133+ golden rules across 37 documents
- Three architecture domains: Enterprise, Platform, Solution
- Seven WAF pillars: Governance, Security, Reliability, Performance, Cost, OpEx, Interop
