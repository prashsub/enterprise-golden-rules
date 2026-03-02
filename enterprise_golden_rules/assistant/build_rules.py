#!/usr/bin/env python3
"""
Build Enterprise Golden Rules workspace files from source documents.

This script:
1. Parses source markdown documents for golden rules tables
2. Groups rules by domain mapping
3. Generates consolidated domain files for the Databricks Assistant
4. Generates the full audit checklist
5. Validates character counts

Usage:
    python build_rules.py [--source-dir PATH] [--output-dir PATH] [--validate-only]
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Domain mapping: rule prefix -> domain file
DOMAIN_MAP = {
    "DP": "data_pipelines",
    "DA": "data_pipelines",
    "DQ": "data_pipelines",
    "DI": "data_pipelines",  # Data Integration — ingest/federate/share decisions
    "DL": "delta_lake",
    # BP retired in v5.4.0 — operational tips only, not formal golden rules
    "ST": "streaming",
    # SL retired in v5.4.0 — duplicates of MV rules
    "MV": "semantic_layer",
    "MO": "semantic_layer",
    "DB": "semantic_layer",
    "DM": "data_modeling",
    "NC": "naming_tagging",
    "CM": "naming_tagging",
    "TG": "naming_tagging",
    "IN": "asset_bundles",
    "GOV": "uc_governance",
    "EA": "uc_governance",
    "DS": "uc_governance",   # Delta Sharing
    "SEC": "security",
    "SM": "security",        # Secrets Management
    "REL": "reliability",
    "SC": "reliability",     # Serverless Compute
    "CP": "reliability",     # Cluster Policies
    "PA": "reliability",     # Platform Architecture
    "COST": "reliability",   # Cost Optimization
    "ML": "ml_ai",           # ML-01..09 (MLflow patterns)
    "PY": "asset_bundles",   # Python Development
    "SA": "data_pipelines",  # Silver Architecture
    "TF": "semantic_layer",  # Table-Valued Functions
    "GN": "semantic_layer",  # Genie Spaces
    "GA": "ml_ai",           # GenAI Agents
    "GS": "genai",           # GenAI Standards
    "AG": "genai",           # AI Gateway
}

# ML rules that belong to genai domain
GENAI_ML_RULES = set()  # No longer needed — GS/AG have their own prefixes

# Source document paths relative to enterprise_golden_rules/
SOURCE_DOCS = {
    "data_pipelines": [
        "solution-architecture/data-pipelines/25-bronze-layer-patterns.md",
        "solution-architecture/data-pipelines/26-silver-layer-patterns.md",
        "solution-architecture/data-pipelines/27-gold-layer-patterns.md",
        "enterprise-architecture/07-data-quality-standards.md",
        "platform-architecture/16-data-access-patterns.md",
    ],
    "delta_lake": [
        "platform-architecture/12-unity-catalog-tables.md",
    ],
    "streaming": [
        "solution-architecture/data-pipelines/28-streaming-production-patterns.md",
    ],
    "semantic_layer": [
        "solution-architecture/semantic-layer/30-metric-view-patterns.md",
        "solution-architecture/semantic-layer/31-tvf-patterns.md",
        "solution-architecture/semantic-layer/32-genie-space-patterns.md",
        "solution-architecture/semantic-layer/33-semantic-layer-overview.md",
        "solution-architecture/dashboards/35-aibi-dashboard-patterns.md",
        "solution-architecture/monitoring/36-lakehouse-monitoring.md",
    ],
    "data_modeling": [
        "enterprise-architecture/04-data-modeling.md",
    ],
    "naming_tagging": [
        "enterprise-architecture/05-naming-comment-standards.md",
        "enterprise-architecture/06-tagging-standards.md",
    ],
    "asset_bundles": [
        "platform-architecture/19-asset-bundle-standards.md",
        "platform-architecture/20-python-development.md",
    ],
    "uc_governance": [
        "enterprise-architecture/01-data-governance.md",
        "platform-architecture/15-unity-catalog-governance.md",
        "solution-architecture/data-sharing/60-delta-sharing-patterns.md",
    ],
    "security": [
        "platform-architecture/18-network-security.md",
    ],
    "reliability": [
        "platform-architecture/10-platform-overview.md",
        "platform-architecture/11-serverless-compute.md",
        "platform-architecture/13-cluster-policies.md",
        "platform-architecture/17-reliability-disaster-recovery.md",
    ],
    "ml_ai": [
        "solution-architecture/ml-ai/50-mlflow-model-patterns.md",
    ],
    "genai": [
        "solution-architecture/ml-ai/51-genai-agent-patterns.md",
        "solution-architecture/ml-ai/52-genai-standards.md",
        "solution-architecture/ml-ai/53-ai-gateway-patterns.md",
    ],
}

# Character limits
MAX_DOMAIN_FILE_CHARS = 10000
MAX_WORKSPACE_INSTRUCTIONS_CHARS = 20000


def parse_golden_rules_table(content: str) -> list[dict]:
    """Extract golden rules from markdown table in a source document."""
    rules = []
    # Match golden rules table rows: | **XX-01** | description | severity | pillar |
    pattern = r"\|\s*\*\*(\w+-\d+)\*\*\s*\|\s*(.+?)\s*\|\s*(\w+)\s*\|\s*(.+?)\s*\|"
    for match in re.finditer(pattern, content):
        rule_id = match.group(1)
        description = match.group(2).strip()
        severity = match.group(3).strip()
        waf_pillar = match.group(4).strip()
        # Clean markdown links from pillar
        waf_pillar = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", waf_pillar)
        rules.append({
            "id": rule_id,
            "description": description,
            "severity": severity,
            "waf_pillar": waf_pillar,
        })
    return rules


def get_domain_for_rule(rule_id: str) -> str:
    """Map a rule ID to its domain file name."""
    if rule_id in GENAI_ML_RULES:
        return "genai"
    prefix = re.match(r"([A-Z]+)", rule_id)
    if prefix:
        return DOMAIN_MAP.get(prefix.group(1), "uc_governance")
    return "uc_governance"


def extract_code_blocks(content: str) -> list[str]:
    """Extract fenced code blocks from markdown."""
    blocks = []
    pattern = r"```(\w*)\n(.*?)```"
    for match in re.finditer(pattern, content, re.DOTALL):
        blocks.append({"language": match.group(1), "code": match.group(2).strip()})
    return blocks


def collect_all_rules(source_dir: Path) -> dict[str, list[dict]]:
    """Parse all source documents and group rules by domain."""
    domain_rules = defaultdict(list)
    seen_rules = set()

    for domain, doc_paths in SOURCE_DOCS.items():
        for doc_path in doc_paths:
            full_path = source_dir / doc_path
            if not full_path.exists():
                print(f"  WARNING: {doc_path} not found, skipping")
                continue

            content = full_path.read_text(encoding="utf-8")
            rules = parse_golden_rules_table(content)

            for rule in rules:
                actual_domain = get_domain_for_rule(rule["id"])
                if rule["id"] not in seen_rules:
                    domain_rules[actual_domain].append(rule)
                    seen_rules.add(rule["id"])

    return dict(domain_rules)


def generate_domain_file(domain: str, rules: list[dict]) -> str:
    """Generate a consolidated domain rule file."""
    domain_names = {
        "data_pipelines": "Data Pipelines",
        "delta_lake": "Delta Lake Best Practices",
        "streaming": "Streaming Production",
        "semantic_layer": "Semantic Layer",
        "data_modeling": "Data Modeling",
        "naming_tagging": "Naming, Comments & Tagging",
        "asset_bundles": "Asset Bundles & Deployment",
        "uc_governance": "Unity Catalog Governance",
        "security": "Network Security",
        "reliability": "Reliability & Compute",
        "ml_ai": "ML/AI Patterns",
        "genai": "GenAI Agent Standards",
    }

    # Sort rules by ID
    rules.sort(key=lambda r: r["id"])

    id_range = f"{rules[0]['id']}..{rules[-1]['id']}" if rules else "N/A"
    name = domain_names.get(domain, domain)

    lines = [
        f"# {name} Golden Rules",
        f"**Rules:** {id_range} | **Count:** {len(rules)} | **Version:** 5.4",
        "",
        "## Rules Summary",
        "",
        "| ID | Rule | Severity | WAF Pillar |",
        "|----|------|----------|------------|",
    ]

    for rule in rules:
        lines.append(
            f"| **{rule['id']}** | {rule['description']} "
            f"| {rule['severity']} | {rule['waf_pillar']} |"
        )

    lines.extend([
        "",
        "## Detailed Rules",
        "",
    ])

    for rule in rules:
        lines.extend([
            f"### {rule['id']}: {rule['description']}",
            f"**Severity:** {rule['severity']}",
            "",
            f"**Rule:** {rule['description']}",
            "",
            "---",
            "",
        ])

    lines.extend([
        "## Checklist",
        "",
    ])
    for rule in rules:
        lines.append(f"- [ ] **{rule['id']}** [{rule['severity']}] {rule['description']}")

    return "\n".join(lines)


def generate_audit_checklist(all_rules: dict[str, list[dict]]) -> str:
    """Generate the full audit checklist from all domain rules."""
    lines = [
        "# Enterprise Golden Rules — Full Audit Checklist",
        "**Version:** 5.4 | **Updated:** Feb 2026",
        "",
        "Instructions: Mark each rule as PASS, FAIL, or N/A. "
        "For FAIL items, note the cell/line and required fix.",
        "",
    ]

    domain_order = [
        "data_pipelines", "delta_lake", "streaming", "semantic_layer",
        "data_modeling", "naming_tagging", "asset_bundles", "uc_governance",
        "security", "reliability", "ml_ai", "genai",
    ]

    domain_headers = {
        "data_pipelines": "Data Pipelines (DP, DA, DQ)",
        "delta_lake": "Delta Lake (DL)",
        "streaming": "Streaming (ST)",
        "semantic_layer": "Semantic Layer (MV, TF, GN, MO, DB)",
        "data_modeling": "Data Modeling (DM)",
        "naming_tagging": "Naming, Comments & Tagging (NC, CM, TG)",
        "asset_bundles": "Asset Bundles & Deployment (IN, PY)",
        "uc_governance": "Governance (GOV, EA, DS)",
        "security": "Security (SEC, SM)",
        "reliability": "Reliability & Compute (REL, CP, SC, COST)",
        "ml_ai": "ML/AI (ML-01..09, GA-01..04)",
        "genai": "GenAI Standards & AI Gateway (GS-01..07, AG-01..05)",
    }

    total_rules = 0
    for domain in domain_order:
        rules = all_rules.get(domain, [])
        if not rules:
            continue
        rules.sort(key=lambda r: r["id"])
        total_rules += len(rules)

        lines.extend([
            f"## {domain_headers.get(domain, domain)}",
            "",
        ])
        for rule in rules:
            lines.append(
                f"- [ ] **{rule['id']}** [{rule['severity']}] {rule['description']}"
            )
        lines.append("")

    lines.insert(4, f"**Total Rules:** {total_rules}")
    lines.insert(5, "")
    return "\n".join(lines)


def validate_files(output_dir: Path) -> bool:
    """Validate generated files meet size constraints."""
    ok = True
    domain_dir = output_dir / "domain"
    if domain_dir.exists():
        for f in sorted(domain_dir.glob("*.md")):
            size = len(f.read_text(encoding="utf-8"))
            status = "OK" if size <= MAX_DOMAIN_FILE_CHARS else "OVER LIMIT"
            if size > MAX_DOMAIN_FILE_CHARS:
                ok = False
            print(f"  {f.name}: {size:,} chars [{status}]")

    ws_file = output_dir.parent.parent / "workspace_instructions" / ".assistant_workspace_instructions.md"
    if ws_file.exists():
        size = len(ws_file.read_text(encoding="utf-8"))
        status = "OK" if size <= MAX_WORKSPACE_INSTRUCTIONS_CHARS else "OVER LIMIT"
        if size > MAX_WORKSPACE_INSTRUCTIONS_CHARS:
            ok = False
        print(f"  workspace_instructions: {size:,} chars [{status}]")

    return ok


def main():
    parser = argparse.ArgumentParser(description="Build Enterprise Golden Rules workspace files")
    parser.add_argument("--source-dir", type=Path, default=Path("."),
                        help="Path to enterprise_golden_rules/ root")
    parser.add_argument("--output-dir", type=Path, default=Path("assistant/generated/Enterprise_Rules"),
                        help="Output directory for generated files")
    parser.add_argument("--validate-only", action="store_true",
                        help="Only validate existing files, don't regenerate")
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    output_dir = (source_dir / args.output_dir).resolve()

    if args.validate_only:
        print("Validating generated files...")
        ok = validate_files(output_dir)
        sys.exit(0 if ok else 1)

    print(f"Source: {source_dir}")
    print(f"Output: {output_dir}")

    # Step 1: Collect all rules
    print("\n1. Parsing source documents...")
    all_rules = collect_all_rules(source_dir)
    total = sum(len(r) for r in all_rules.values())
    print(f"   Found {total} rules across {len(all_rules)} domains")

    # Step 2: Generate domain files
    print("\n2. Generating domain files...")
    domain_dir = output_dir / "domain"
    domain_dir.mkdir(parents=True, exist_ok=True)

    for domain, rules in sorted(all_rules.items()):
        content = generate_domain_file(domain, rules)
        out_file = domain_dir / f"{domain}.md"
        out_file.write_text(content, encoding="utf-8")
        print(f"   {domain}.md: {len(rules)} rules, {len(content):,} chars")

    # Step 3: Generate audit checklist
    print("\n3. Generating audit checklist...")
    audit_dir = output_dir / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    checklist = generate_audit_checklist(all_rules)
    (audit_dir / "full_checklist.md").write_text(checklist, encoding="utf-8")
    print(f"   full_checklist.md: {len(checklist):,} chars")

    # Step 4: Update VERSION
    version = f"5.4.{datetime.now().strftime('%Y-%m-%d')}"
    (output_dir / "VERSION").write_text(version + "\n", encoding="utf-8")
    print(f"\n4. VERSION: {version}")

    # Step 5: Validate
    print("\n5. Validation:")
    ok = validate_files(output_dir)

    if ok:
        print("\nAll files generated successfully.")
    else:
        print("\nWARNING: Some files exceed size limits. Review and trim.")
        sys.exit(1)


if __name__ == "__main__":
    main()
