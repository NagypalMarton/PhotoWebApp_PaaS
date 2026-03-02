#!/usr/bin/env bash
# generate-secrets.sh
# Generates cryptographically random values for all CHANGE_ME_* placeholders in
# openshift/openshift-all.yaml and writes the result to
# openshift/openshift-all-generated.yaml (which is git-ignored).
#
# Usage: bash scripts/generate-secrets.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE="${REPO_ROOT}/openshift/openshift-all.yaml"
OUTPUT="${REPO_ROOT}/openshift/openshift-all-generated.yaml"

if ! command -v openssl >/dev/null 2>&1; then
  echo "Error: 'openssl' is required but not found. Please install it and try again." >&2
  exit 1
fi

if [ ! -f "${TEMPLATE}" ]; then
  echo "Error: Template file not found: ${TEMPLATE}" >&2
  exit 1
fi

echo "Generating secrets for OpenShift deployment..."
echo ""

SECRET_KEY=$(openssl rand -hex 20)
DB_PASSWORD=$(openssl rand -hex 20)
MYSQL_ROOT_PASSWORD=$(openssl rand -hex 20)
BACKEND_WEBHOOK_SECRET=$(openssl rand -hex 20)
FRONTEND_WEBHOOK_SECRET=$(openssl rand -hex 20)

sed \
  -e "s/CHANGE_ME_STRONG_APP_SECRET/${SECRET_KEY}/g" \
  -e "s/CHANGE_ME_STRONG_DB_PASSWORD/${DB_PASSWORD}/g" \
  -e "s/CHANGE_ME_STRONG_ROOT_PASSWORD/${MYSQL_ROOT_PASSWORD}/g" \
  -e "s/CHANGE_ME_BACKEND_WEBHOOK_SECRET/${BACKEND_WEBHOOK_SECRET}/g" \
  -e "s/CHANGE_ME_FRONTEND_WEBHOOK_SECRET/${FRONTEND_WEBHOOK_SECRET}/g" \
  "${TEMPLATE}" > "${OUTPUT}"

echo "✅ Generated: ${OUTPUT}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Apply the configuration to OpenShift:"
echo "     oc apply -f openshift/openshift-all-generated.yaml"
echo ""
echo "  2. Retrieve the webhook URLs after applying:"
echo "     oc describe bc photowebapp-backend | grep 'Webhook GitHub'"
echo "     oc describe bc photowebapp-frontend | grep 'Webhook GitHub'"
echo ""
echo "  3. In GitHub → Settings → Webhooks:"
echo "     - Payload URL:  <the URL from step 2>"
echo "     - Content type: application/json"
echo "     - Secret:       ⚠️  leave EMPTY (the secret is embedded in the URL)"
echo ""
echo "The original openshift/openshift-all.yaml template remains unchanged."
