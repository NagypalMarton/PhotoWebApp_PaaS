#!/usr/bin/env bash
# generate-secrets.sh
# Generates cryptographically random values for secret placeholders in
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
DOCKERHUB_USERNAME_VALUE="${DOCKERHUB_USERNAME:-CHANGE_ME_DOCKERHUB_USERNAME}"

sed \
  -e "s/CHANGE_ME_STRONG_APP_SECRET/${SECRET_KEY}/g" \
  -e "s/CHANGE_ME_STRONG_DB_PASSWORD/${DB_PASSWORD}/g" \
  -e "s/CHANGE_ME_STRONG_ROOT_PASSWORD/${MYSQL_ROOT_PASSWORD}/g" \
  -e "s/CHANGE_ME_DOCKERHUB_USERNAME/${DOCKERHUB_USERNAME_VALUE}/g" \
  "${TEMPLATE}" > "${OUTPUT}"

echo "✅ Generated: ${OUTPUT}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Apply the configuration to OpenShift:"
echo "     oc apply -f openshift/openshift-all-generated.yaml"
echo ""
echo "  2. Import Docker Hub images into OpenShift ImageStreams:"
echo "     oc import-image photowebapp-backend:latest --confirm"
echo "     oc import-image photowebapp-frontend:latest --confirm"
echo ""
echo "  3. Verify resources:"
echo "     oc get is"
echo "     oc get pods"
echo ""
if [ "${DOCKERHUB_USERNAME_VALUE}" = "CHANGE_ME_DOCKERHUB_USERNAME" ]; then
  echo "⚠️  DOCKERHUB_USERNAME env var is not set."
  echo "    Replace CHANGE_ME_DOCKERHUB_USERNAME in openshift-all-generated.yaml before apply."
  echo ""
fi

echo "The original openshift/openshift-all.yaml template remains unchanged."
