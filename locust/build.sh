#!/bin/bash

# Locust Image Build Script for OpenShift
# ==============================================================================
# This script builds the Locust image and pushes it to OpenShift Image Registry.
# ==============================================================================

set -e

# Bejelentkezés OpenShift-be (ha még nem jelentkeztél be)
# oc login <your-openshift-cluster-url>

# Projekt kiválasztása
PROJECT="nagypalmarton-dev"
oc project "$PROJECT"

# Locust image építése
echo "Building Locust image..."
oc start-build locust-build --from-dir=. --wait

# Ellenőrzés
echo "Checking image..."
oc get is locust

echo "Locust image build completed!"
echo "You can now apply the locust-openshift.yaml configuration."
