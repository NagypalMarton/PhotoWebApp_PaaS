# OpenShift telepítés (Red Hat OpenShift)

Ez a mappa a PhotoWebApp OpenShift (PaaS) deploy erőforrásait tartalmazza.

## Előfeltételek

- OpenShift projekt (namespace)
- `oc` CLI bejelentkezve
- A klaszter elérje a GitHub repository-t

## 1) Secret értékek beállítása

A `openshift-all.yaml` fájlban a Secret objektumokban `CHANGE_ME_*` placeholder értékek vannak.
Telepítés előtt ezeket kötelező erős, egyedi értékekre cserélni.

Webhookhoz külön secret kulcsok is vannak:

- `CHANGE_ME_BACKEND_WEBHOOK_SECRET`
- `CHANGE_ME_FRONTEND_WEBHOOK_SECRET`

## 2) Erőforrások telepítése

```bash
oc apply -f openshift/openshift-all.yaml
```

Ez létrehozza többek között a következőket:

- `ImageStream` a backendhez és frontendhez,
- `BuildConfig` a GitHub forrásból történő S2I/source buildhez,
- `DeploymentConfig` image-change triggerrel,
- `Service` + `Route` + PVC + DB deployment.

Builder image-ek:

- backend: `openshift/python:3.11-ubi9`
- frontend: `openshift/nginx:1.24-ubi9`

Frontend Nginx konfiguráció útvonala a repository-ban:

- `frontend/nginx-cfg/default.conf`

## 3) Build indítása

Első telepítés után indítsd el a buildet (vagy triggereld webhookkal):

```bash
oc start-build photowebapp-backend --follow
oc start-build photowebapp-frontend --follow
```

Sikeres build után a `DeploymentConfig` automatikusan frissít és elindítja a rolloutot.

### GitHub webhook URL-ek lekérdezése

Backend:

```bash
oc describe bc photowebapp-backend | grep "Webhook GitHub"
```

PowerShell:

```powershell
oc describe bc photowebapp-backend | Select-String "Webhook GitHub"
```

Frontend:

```bash
oc describe bc photowebapp-frontend | grep "Webhook GitHub"
```

PowerShell:

```powershell
oc describe bc photowebapp-frontend | Select-String "Webhook GitHub"
```

A kapott URL-eket add meg a GitHub repository `Settings > Webhooks` felületén `application/json` payload formátummal.

## 4) Ellenőrzés

```bash
oc get builds
oc get is
oc get pods
oc get svc
oc get route
```

A route hostot így kérdezheted le:

```bash
oc get route photowebapp -o jsonpath='{.spec.host}'
```

## Megjegyzések

- A backend és frontend OpenShift-kompatibilis portokon fut (`3000`, `8080`).
- A feltöltési limit `100 MB` (frontend Nginx + backend Flask).
- A `uploads` és adatbázis tárolás PVC-n keresztül történik.
- A DB deployment `bitnami/mysql:8.4` image-et használ non-root kompatibilitás miatt.
