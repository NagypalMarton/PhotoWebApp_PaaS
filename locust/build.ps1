# Locust Image Build Script for OpenShift (PowerShell)
# ==============================================================================
# This script builds the Locust image and pushes it to OpenShift Image Registry.
# ==============================================================================

# Bejelentkezés OpenShift-be (ha még nem jelentkeztél be)
# oc login <your-openshift-cluster-url>

# Projekt kiválasztása
$PROJECT = "nagypalmarton-dev"
oc project $PROJECT

# Locust image építése
Write-Host "Building Locust image..." -ForegroundColor Green
oc start-build locust-build --from-dir=. --wait

# Ellenőrzés
Write-Host "Checking image..." -ForegroundColor Green
oc get is locust

Write-Host "Locust image build completed!" -ForegroundColor Green
Write-Host "You can now apply the locust-openshift.yaml configuration." -ForegroundColor Green
