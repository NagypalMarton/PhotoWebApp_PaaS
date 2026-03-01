# OpenShift telepítés (Red Hat OpenShift)

Ez a mappa a PhotoWebApp OpenShift (PaaS) deploy erőforrásait tartalmazza.

## Előfeltételek

- OpenShift projekt (namespace)
- `oc` CLI bejelentkezve
- Publikus image repository a backend és frontend image-ekhez (pl. GHCR / Quay)

## 1) Image-ek build és push

Az `openshift-all.yaml` alapértelmezetten az alábbi image-ekre mutat:

- `ghcr.io/nagypalmarton/photowebapp-backend:latest`
- `ghcr.io/nagypalmarton/photowebapp-frontend:latest`

Ha más registry-t használsz, ezeket az értékeket írd át.

Példa lokális build + push:

```bash
docker build -t ghcr.io/nagypalmarton/photowebapp-backend:latest .
docker push ghcr.io/nagypalmarton/photowebapp-backend:latest

docker build -t ghcr.io/nagypalmarton/photowebapp-frontend:latest ./frontend
docker push ghcr.io/nagypalmarton/photowebapp-frontend:latest
```

## 2) Secret értékek beállítása

A `openshift-all.yaml` fájlban a Secret objektumokban `CHANGE_ME_*` placeholder értékek vannak.
Telepítés előtt ezeket kötelező erős, egyedi értékekre cserélni.

## 3) Deploy

```bash
oc apply -f openshift/openshift-all.yaml
```

## 4) Ellenőrzés

```bash
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
