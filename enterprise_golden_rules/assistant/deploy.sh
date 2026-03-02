#!/bin/bash
# Deploy Enterprise Golden Rules to Databricks workspace
#
# Usage:
#   ./deploy.sh [WORKSPACE_PATH] [--profile PROFILE]
#
# Prerequisites:
#   - Databricks CLI configured (databricks auth login)
#   - Write access to target workspace path
#
# This script deploys the generated Enterprise_Rules directory
# to /Workspace/Enterprise_Rules/ (or a custom path).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATED_DIR="${SCRIPT_DIR}/generated/Enterprise_Rules"
DEFAULT_WORKSPACE_PATH="/Workspace/Enterprise_Rules"
WORKSPACE_PATH="${1:-$DEFAULT_WORKSPACE_PATH}"
PROFILE_FLAG=""

# Parse optional --profile argument
shift 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE_FLAG="--profile $2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "=== Enterprise Golden Rules Deployment ==="
echo "Source:    ${GENERATED_DIR}"
echo "Target:   ${WORKSPACE_PATH}"
echo "Profile:  ${PROFILE_FLAG:-default}"
echo ""

# Validate source directory
if [[ ! -d "${GENERATED_DIR}" ]]; then
    echo "ERROR: Generated files not found at ${GENERATED_DIR}"
    echo "Run 'python build_rules.py' first to generate files."
    exit 1
fi

# Validate Databricks CLI
if ! command -v databricks &> /dev/null; then
    echo "ERROR: Databricks CLI not found. Install: pip install databricks-cli"
    exit 1
fi

# Show what will be deployed
echo "Files to deploy:"
find "${GENERATED_DIR}" -name "*.md" -o -name "*.sql" -o -name "*.py" -o -name "*.yml" -o -name "VERSION" | sort | while read -r f; do
    echo "  $(basename "$f") ($(wc -c < "$f" | tr -d ' ') bytes)"
done
echo ""

# Confirm
read -p "Deploy to ${WORKSPACE_PATH}? [y/N] " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Deploy using workspace import
echo ""
echo "Deploying..."

# Import directory (overwrites existing)
databricks workspace import-dir \
    "${GENERATED_DIR}" \
    "${WORKSPACE_PATH}" \
    --overwrite \
    ${PROFILE_FLAG}

echo ""
echo "Deployment complete!"
echo ""
echo "Verify with:"
echo "  databricks workspace ls ${WORKSPACE_PATH} ${PROFILE_FLAG}"
echo "  databricks workspace ls ${WORKSPACE_PATH}/domain ${PROFILE_FLAG}"
echo ""
echo "Test assistant access (in agent mode notebook):"
echo "  content = open('${WORKSPACE_PATH}/domain/data_pipelines.md').read()"
echo "  print(len(content))  # Should print file size"
