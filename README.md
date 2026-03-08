# PhotoWebApp_PaaS

Felhőalapú elosztott rendszerek laboratórium (2026) projekt: OpenShift-re tervezett fotóalbum alkalmazás Flask backenddel, MySQL adattárolással és Nginx alapú frontenddel.

## Fő funkciók

- Regisztráció, bejelentkezés, kijelentkezés
- Képfeltöltés (max. 100 MB) és törlés jogosultságellenőrzéssel
- Képek listázása és rendezése név vagy dátum szerint
- Kép megjelenítése a kiválasztott listaelemből
- Szigorúbb bemeneti validáció (felhasználónév és jelszó szabályok)
- Robusztusabb upload/delete folyamat (fájl + adatbázis konzisztencia)

## Technológiai stack

- **Backend:** Flask + Gunicorn ([app.py](app.py))
- **Adatbázis:** MySQL 8.4 ([db/init.sql](db/init.sql))
- **Frontend:** statikus HTML + Bootstrap + Nginx reverse proxy ([frontend/index.html](frontend/index.html), [frontend/nginx-cfg/default.conf](frontend/nginx-cfg/default.conf))
- **Platform:** Docker Hub + OpenShift Deployment + Service + Route ([openshift/openshift-all.yaml](openshift/openshift-all.yaml))

## Projektstruktúra

- [app.py](app.py) – Flask belépési pont (`create_app()`)
- [photowebapp/](photowebapp/) – backend modulok (route-ok, DB, app factory)
- [db/init.sql](db/init.sql) – `users` és `photos` táblák
- [frontend/](frontend/) – kliensoldali felület és Nginx konfiguráció
- [openshift/](openshift/) – teljes OpenShift manifestek és deployment dokumentáció
- [kubernetes/](kubernetes/) – vanilla Kubernetes manifestek (multi-tier, skálázható)
- [devfile.yaml](devfile.yaml) – OpenShift Dev Spaces / Import from Git leírás
- [scripts/generate-secrets.sh](scripts/generate-secrets.sh) – `CHANGE_ME_*` értékek biztonságos generálása

## Környezeti változók (backend)

| Változó | Kötelező | Alapérték | Leírás |
| --- | --- | --- | --- |
| `PORT` | nem | `3000` | Flask/Gunicorn port |
| `SECRET_KEY` | igen | – | Session titkos kulcs |
| `DB_HOST` | igen | – | MySQL host |
| `DB_PORT` | igen | – | MySQL port |
| `DB_NAME` | igen | – | Adatbázis neve |
| `DB_USER` | igen | – | Adatbázis felhasználó |
| `DB_PASSWORD` | igen | – | Adatbázis jelszó |

Referenciaértékek: [.env.example](.env.example)

## Docker Hub CI (minden commit után)

A repository tartalmaz egy GitHub Actions workflow-t: [.github/workflows/dockerhub-publish.yml](.github/workflows/dockerhub-publish.yml).

- Trigger: minden `push` (commit után)
- Eredmény: a backend és frontend image felpusholása Docker Hubra
  - `<DOCKERHUB_USERNAME>/photowebapp-backend:latest`
  - `<DOCKERHUB_USERNAME>/photowebapp-frontend:latest`

Szükséges GitHub repository secret-ek:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (Docker Hub access token)

> Ezeket **Repository secrets**-ként add meg (nem Environment secretként), mert a workflow közvetlenül innen olvassa.
> A `DOCKERHUB_TOKEN` tokenen legalább **Read + Write** jog kell, különben `401 insufficient scopes` hibát kapsz.

Az `openshift/openshift-all-generated.yaml` fájlt a GitHub Actions automatikusan előállítja/frissíti a `DOCKERHUB_USERNAME` Repository Secret alapján.

## OpenShift telepítés (CLI nélkül, automatikus frissítéssel)

1. OpenShift Console-ban (`+Add` → `Import YAML`) importáld az [openshift/openshift-all-generated.yaml](openshift/openshift-all-generated.yaml) tartalmát.

2. Ugyanitt cseréld le a `CHANGE_ME_STRONG_*` secret placeholdereket erős, egyedi értékekre.

3. Kész.

Az automatikus működés ezután:

- minden commit/release után a GitHub Actions feltolja az új image-et Docker Hubra,
- OpenShift deploy esetén a backend/frontend közvetlenül ezeket a Docker Hub image-eket használja.

Ha ragaszkodsz a scriptes secret-generáláshoz, opcionálisan használható helyileg:

   ```bash
   bash scripts/generate-secrets.sh
   ```

Részletes OpenShift leírás: [openshift/README.md](openshift/README.md)

## Kubernetes telepítés (multi-tier, skálázható)

A Kubernetes csomag a [kubernetes/photowebapp-paas.yaml](kubernetes/photowebapp-paas.yaml) fájlban található.

Felépítés:

- `frontend` réteg (Deployment + Service)
- `backend` réteg (Deployment + Service)
- `mysql` réteg (StatefulSet + Service)
- `Ingress` publikus belépési ponttal
- `HPA` backend és frontend autoscalinghez
- `PDB` a gördülékeny karbantartáshoz

Telepítés:

```bash
kubectl apply -f kubernetes/photowebapp-paas.yaml
```

Gyors ellenőrzés:

```bash
kubectl get all -n photowebapp-paas
kubectl get ingress -n photowebapp-paas
kubectl get hpa -n photowebapp-paas
```

Részletes Kubernetes leírás: [kubernetes/README.md](kubernetes/README.md)

## Devfile import (OpenShift Console)

A [devfile.yaml](devfile.yaml) alapértelmezetten a `build + deploy-k8s-sample` kompozit parancsot futtatja (`deploy`), mert az OpenShift Import from Git ehhez tud megbízhatóan `Deployment` definíciót felismerni.

- A teljes OpenShift stack deploy külön paranccsal elérhető: `deploy-openshift-stack`.
- A k8s minta deploy elérhető `deploy-k8s-devfile-only` néven is ([openshift/devfile-k8s-deploy.yaml](openshift/devfile-k8s-deploy.yaml)).
- A devfile endpoint explicit `targetPort: 8080` beállítással rendelkezik.

## API összefoglaló

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/photos?sort=name|date&order=asc|desc`
- `POST /api/photos` (`multipart/form-data`: `name`, `photo`)
- `DELETE /api/photos/:id`

### Bemeneti szabályok

- `POST /api/auth/register`
  - `username`: 3-50 karakter, engedélyezett karakterek: betűk, számok, `.`, `_`, `-`
  - `password`: minimum 8 karakter, és tartalmazzon legalább 1 betűt + 1 számot
- `POST /api/photos`
  - `name`: kötelező, legfeljebb 40 karakter
  - `photo`: kötelező, támogatott kiterjesztések: `jpg`, `jpeg`, `png`, `gif`, `webp`

## Fontos működési megjegyzések

- Feltöltött fájlméret limit: `100 MB` (backend + Nginx oldalon is)
- Törölni csak a kép tulajdonosa tud
- A feltöltött képek a `uploads` kötetben tárolódnak
- A feltöltés ideiglenes fájlba történik, majd csak sikeres DB művelet után kerül végleges névre
- Feltöltési hiba esetén a backend kompenzáló takarítást végez (fájl/rekord maradványok minimalizálása)
- A repository OpenShift célkörnyezetre van optimalizálva
