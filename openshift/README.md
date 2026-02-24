# OpenShift telepítés (Red Hat OpenShift)

Ez a mappa a PhotoWebApp OpenShift (PaaS) deploy erőforrásait tartalmazza.

## Előfeltételek

- OpenShift projekt (namespace)
- `oc` CLI bejelentkezve
- Publikus image repository a backend és frontend image-ekhez (pl. GHCR / Quay)

## 1) Image-ek build és push

A `openshift-all.yaml` fájlban az alábbi image neveket állítsd át saját repository-ra:

- `ghcr.io/your-org/photowebapp-backend:latest`
- `ghcr.io/your-org/photowebapp-frontend:latest`

Példa lokális build + push:

```bash
docker build -t ghcr.io/<ORG>/photowebapp-backend:latest .
docker push ghcr.io/<ORG>/photowebapp-backend:latest

docker build -t ghcr.io/<ORG>/photowebapp-frontend:latest ./frontend
docker push ghcr.io/<ORG>/photowebapp-frontend:latest
```

## 2) Deploy

```bash
oc apply -f openshift/openshift-all.yaml
```

## 3) Ellenőrzés

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
