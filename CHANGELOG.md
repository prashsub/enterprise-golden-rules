# Changelog

All notable changes to the Enterprise Golden Rules framework are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

For detailed per-version diffs (rule ID changes, file renames, cross-reference updates),
see [enterprise_golden_rules/CHANGELOG.md](enterprise_golden_rules/CHANGELOG.md).

---

## [5.4.2] - 2026-02-18

### Changed
- Globally unique file numbering — each domain now owns a dedicated number range to eliminate collisions
- 17 files renamed, all cross-references updated
- Fixed broken links in onboarding docs

## [5.4.1] - 2026-02-17

### Added
- New document: **Data Access Patterns** (`16-data-access-patterns.md`) — decision framework for Ingestion vs Federation vs Delta Sharing
- **DI prefix** with 7 new rules (DI-01 through DI-07)
- Framework total: 32 prefixes, 162+ rules

## [5.4.0] - 2026-02-16

### Removed
- 3 duplicate SA documents deleted (rules were duplicates of Platform Architecture)
- **BP** and **SL** prefixes retired
- 12 overlapping rules removed from 6 SA documents

### Changed
- DA, ST, GS rules renumbered for sequential consistency
- Prerequisites sections added to all 15 SA documents
- Framework total: 31 prefixes, 155+ rules, zero collisions

## [5.3.0] - 2026-02-16

### Changed
- **Rule ID Rationalization** — eliminated all rule ID collisions with unique prefixes per document
- 11 new prefixes: SC, CP, SM, PY, SA, TF, GN, GA, GS, AG, DB
- Total: 33 prefixes, 165+ rules before deduplication

## [5.2.6] - 2026-02-16

### Added
- IN-11: Deployment modes (`mode: development` / `mode: production`)
- IN-12: `run_as` service principal for staging/prod
- IN-13: Top-level `permissions` block on all bundles
- Expanded Asset Bundle Standards with deployment modes, variables, library dependencies

### Changed
- Consolidated UC Tables & Delta Lake into a single document

## [5.2.5] - 2026-02-11

### Changed
- Consolidated compute docs — merged `16-compute-configuration.md` into `13-cluster-policies.md`
- Retired CMP prefix from platform-architecture

## [5.2.4] - 2026-02-11

### Added
- PA-18/PA-18a-e: Cluster policies rules with consistent parent/sub-rule pattern

## [5.2.3] - 2026-02-11

### Added
- Serverless environment management rules (PA-03d through PA-03h)
- ABAC/RBAC governance rules (GOV-12 through GOV-16)

## [5.2.2] - 2026-02-10

### Added
- PA-01b, PA-02b: External table approval and standard TBLPROPERTIES
- DQ-05 through DQ-07: Schema-level anomaly detection, data profiling, custom metrics
- Detailed PA-01 through PA-12 sections in platform overview

## [5.2.1] - 2026-02-09

### Added
- Databricks Assistant progressive disclosure architecture (`assistant/` directory)
  - 12 consolidated domain rule files
  - Audit checklist and report template
  - 5 code example templates
  - Workspace instructions (20K char limit)
  - Build script and deployment tooling

### Fixed
- WAF link audit: 43 edits across 20 documents

## [5.2.0] - 2026-02-08

### Changed
- Aligned all golden rules to Databricks Well-Architected Lakehouse Framework
- Standardized golden rules table format: ID, Rule, Severity, WAF Pillar

## [5.1.0] - 2026-02-06

### Added
- WAF Pillar column with hyperlinks on all 34 golden rules tables
- PA-16 (Lakehouse Federation), COST-01/02, GOV-10, SEC-08
- Cloud-agnostic network security (AWS/GCP equivalents)

## [5.0.0] - 2026-02-04

### Added
- Data as a Product (EA-10), Data Contracts (EA-11), AI Readiness (EA-12)
- DBFS root prohibition (PA-13), System Tables (PA-14), Workspace Isolation (PA-15)
- Lineage-driven governance (GOV-08), Governance-as-code (GOV-09)
- Responsible AI (ML-14), AI-Data lifecycle (ML-15), Delta UniForm (DL-07)
- New document: `08-architecture-evolution.md` (maturity model, decision heuristics)
- 15 new golden rules, 1 new document

## [4.6.0] - 2026-02-02

### Added
- Data Quality Standards document (`07-data-quality-standards.md`)
- DLT Expectations, DQX Library, and Lakehouse Monitoring patterns
- 4 new rules (DQ-01 through DQ-04)

## [4.5.0] - 2026-02-01

### Added
- Naming & Comment Standards (`05-naming-comment-standards.md`)
- Tagging Standards (`06-tagging-standards.md`)
- 10 new rules (NC-01 through NC-03, CM-01 through CM-04, TG-01 through TG-03)

## [4.4.0] - 2026-01-30

### Changed
- Reorganized for Confluence — simplified headers, golden rules summary tables, validation checklists
- Added AI Gateway Patterns and Delta Sharing Patterns documents

## [4.3.0] - 2026-01-28

### Added
- Reliability & Disaster Recovery (`17-reliability-disaster-recovery.md`)
- Network Security (`18-network-security.md`)
- 15 new rules (REL-01 through REL-08, SEC-01 through SEC-07)

## [4.2.0] - 2026-01-26

### Changed
- Split best practices into 4 focused documents for discoverability
- 6 new governance rules (GOV-01 through GOV-05, CMP-01 through CMP-04)

## [4.1.0] - 2026-01-24

### Added
- Comprehensive best practices from official Databricks docs
- 10 new rules (BP-01 through BP-10)

## [4.0.0] - 2026-01-22

### Changed
- Integrated 10+ official Microsoft Learn documentation pages
- Updated 8 core documents with control plane, medallion, UC, ACID, SSOT content

## [3.0.0] - 2026-01

### Changed
- Reorganized into 3-tier architecture (Enterprise, Platform, Solution)

## [2.0.0] - 2026-01

### Added
- Major expansion to 50+ rules

## [1.0.0] - 2026-01

### Added
- Initial golden rules documentation
