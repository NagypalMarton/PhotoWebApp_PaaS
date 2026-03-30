# Locust Image Build for OpenShift - Quick Start (PowerShell)
# ==============================================================================
# This file provides a quick way to build and deploy Locust to OpenShift.
# ==============================================================================

# 1. Építsd az image-t a Dockerfile alapján
oc new-build --name=locust --strategy=docker --source-uri=https://github.com/NagypalMarton/PhotoWebApp_PaaS.git --context-dir=locust

# 2. Várj, amíg a build befejeződik
oc logs -f bc/locust

# 3. Alkalmazd a Locust konfigurációt
oc apply -f openshift/locust-openshift.yaml

# 4. Nézd meg a podokat
oc get pods -l app=locust

# 5. Nézd meg a Route-ot
oc get route locust
