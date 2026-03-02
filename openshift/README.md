# OpenShift telepítés (Red Hat OpenShift)

Ez a mappa a PhotoWebApp OpenShift (PaaS) deploy erőforrásait tartalmazza.

## Előfeltételek

- OpenShift projekt (namespace)
- `oc` CLI bejelentkezve
- A klaszter elérje a GitHub repository-t

## 1) Secret értékek beállítása

**Fontos:** Ez a projekt **NEM használ GitHub Secrets-et** (GitHub → Settings → Secrets and variables → Actions).
Nincs `.github/workflows` könyvtár, és nincsenek GitHub Actions workflow-k.

Minden secret **OpenShift/Kubernetes Secret objektum**, amelyek az `openshift/openshift-all.yaml` fájlban vannak definiálva:

| Secret neve | Tartalom |
|---|---|
| `photowebapp-backend-secret` | `SECRET_KEY` (Flask titkos kulcs) |
| `photowebapp-db-secret` | `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD` (adatbázis jelszavak) |
| `photowebapp-backend-webhook` | `WebHookSecretKey` (GitHub webhook secret a backend BuildConfig-hoz) |
| `photowebapp-frontend-webhook` | `WebHookSecretKey` (GitHub webhook secret a frontend BuildConfig-hoz) |

A fájlban szereplő `CHANGE_ME_*` placeholder értékeket kötelező erős, egyedi értékekre cserélni
**`oc apply` futtatása előtt**. Ha a placeholderek cseréletlenül maradnak, a webhook-ok 403-as hibával fognak visszatérni.

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

### Webhook 403-as hiba elhárítása

Ha a GitHub webhook `403 Forbidden` hibával tér vissza, a leggyakoribb ok az, hogy a
`CHANGE_ME_BACKEND_WEBHOOK_SECRET` / `CHANGE_ME_FRONTEND_WEBHOOK_SECRET` értékek nem lettek kicserélve
valódi értékekre `oc apply` előtt.

**Fontos:** Az OpenShift a webhook secret-et az URL-be ágyazza be (pl. `…/webhooks/<secret>/github`).
A GitHub Settings → Webhooks felületén a **„Secret"** mezőt **hagyd üresen** — OpenShift nem a
GitHub által küldött `X-Hub-Signature` fejlécet ellenőrzi, hanem az URL-ben szereplő titkot.

**Lépések a javításhoz:**

1. Az `openshift/openshift-all.yaml` fájlban cseréld ki a `CHANGE_ME_*` placeholder értékeket
   erős, egyedi stringekre.
2. Alkalmazd újra a konfigurációt:
   ```bash
   oc apply -f openshift/openshift-all.yaml
   ```
3. Kérd le a helyes webhook URL-eket:
   ```bash
   oc describe bc photowebapp-backend | grep "Webhook GitHub"
   oc describe bc photowebapp-frontend | grep "Webhook GitHub"
   ```
4. A GitHub repository `Settings → Webhooks` felületén:
   - **Payload URL**: az előző lépésben kapott URL
   - **Content type**: `application/json`
   - **Secret**: hagyd üresen
5. A webhook kézbesítések állapotát a GitHub `Settings → Webhooks → (webhook) → Recent Deliveries`
   alatt ellenőrizheted hibakeresés céljából.

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
