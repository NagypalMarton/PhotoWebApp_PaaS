# OpenShift telepítés (CLI nélkül, Docker Hub image forrással)

Ez a mappa a PhotoWebApp OpenShift (PaaS) deploy erőforrásait tartalmazza.

## Áttekintés

A backend és frontend image-ek GitHub Actions-ből kerülnek Docker Hubra minden `push` után:

- `<DOCKERHUB_USERNAME>/photowebapp-backend:latest`
- `<DOCKERHUB_USERNAME>/photowebapp-frontend:latest`

OpenShift oldalon az `ImageStream` erőforrások Docker Hubról importálnak, a `DeploymentConfig` pedig ezekre image-change triggerrel frissül.

## Előfeltételek

- OpenShift projekt (namespace)
- Docker Hub repository-k létrehozva
- GitHub repository secret-ek:
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN`

## 1) GitHub secret-ek

A `DOCKERHUB_USERNAME` és `DOCKERHUB_TOKEN` értékeket **Repository secrets**-ként add meg
(nem Environment secretként), mert a workflow ezeket közvetlenül használja.

## 2) OpenShift erőforrások importálása weben

OpenShift Console: `+Add` → `Import YAML` → illeszd be az `openshift/openshift-all-generated.yaml` tartalmát.

Az import előtt cseréld ki:

- `CHANGE_ME_STRONG_*` → erős, egyedi secret értékek

Megjegyzés: a `CHANGE_ME_DOCKERHUB_USERNAME` helyettesítést a GitHub Actions automatikusan elvégzi
a `DOCKERHUB_USERNAME` Repository Secretből, és frissíti a `openshift-all-generated.yaml` fájlt.

## 3) Automatikus frissítés működése

Nincs szükség OpenShift CLI parancsokra:

- GitHub Actions minden `push` és `release` után feltolja az image-eket Docker Hubra,
- OpenShift `ImageStream` ütemezetten importálja a `latest` taget,
- `DeploymentConfig` image-change trigger automatikusan rolloutol.

## Opcionális: secret generáló script

Futtasd a scriptet, ha helyileg szeretnél generált secretekkel egy kész YAML-t:

```bash
bash scripts/generate-secrets.sh
```

Ez létrehozza a `openshift/openshift-all-generated.yaml` fájlt.

Ha ezt az utat választod, a `openshift-all-generated.yaml` fájlt ugyanúgy az OpenShift Console
`Import YAML` felületén add hozzá.

## Megjegyzések

- A DB továbbra is OpenShift-en fut (`bitnami/mysql:8.4`).
- A backend (`3000`) és frontend (`8080`) OpenShift-kompatibilis portokon fut.
- A `uploads` és DB adat PVC-n tárolódik.
- A GitHub Actions workflow fájl: `.github/workflows/dockerhub-publish.yml`.
