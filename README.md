# PhotoWebApp_PaaS

Felhőalapú elosztott rendszerek laboratórium (2026) projekt: OpenShift-re tervezett fotóalbum alkalmazás Flask backenddel, MySQL adattárolással és Nginx alapú frontenddel.

## Fő funkciók

- Regisztráció, bejelentkezés, kijelentkezés
- Képfeltöltés (max. 100 MB) és törlés jogosultságellenőrzéssel
- Képek listázása és rendezése név vagy dátum szerint
- Kép megjelenítése a kiválasztott listaelemből

## Technológiai stack

- **Backend:** Flask + Gunicorn ([app.py](app.py))
- **Adatbázis:** MySQL 8.4 ([db/init.sql](db/init.sql))
- **Frontend:** statikus HTML + Bootstrap + Nginx reverse proxy ([frontend/index.html](frontend/index.html), [frontend/nginx-cfg/default.conf](frontend/nginx-cfg/default.conf))
- **Platform:** Docker Hub + OpenShift ImageStream import + DeploymentConfig + Route ([openshift/openshift-all.yaml](openshift/openshift-all.yaml))

## Projektstruktúra

- [app.py](app.py) – Flask API és auth/session logika
- [db/init.sql](db/init.sql) – `users` és `photos` táblák
- [frontend/](frontend/) – kliensoldali felület és Nginx konfiguráció
- [openshift/](openshift/) – teljes OpenShift manifestek és deployment dokumentáció
- [devfile.yaml](devfile.yaml) – OpenShift Dev Spaces / Import from Git leírás
- [scripts/generate-secrets.sh](scripts/generate-secrets.sh) – `CHANGE_ME_*` értékek biztonságos generálása

## Környezeti változók (backend)

| Változó | Kötelező | Alapérték | Leírás |
| --- | --- | --- | --- |
| `PORT` | nem | `3000` | Flask/Gunicorn port |
| `SECRET_KEY` | igen | – | Session titkos kulcs |
| `DB_HOST` | nem | `db` | MySQL host |
| `DB_PORT` | nem | `3306` | MySQL port |
| `DB_NAME` | igen | – | Adatbázis neve |
| `DB_USER` | igen | – | Adatbázis felhasználó |
| `DB_PASSWORD` | igen | – | Adatbázis jelszó |

Referenciaértékek: [.env.example](.env.example)

<<<<<<< HEAD
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

Az `openshift/openshift-all-generated.yaml` fájlt a GitHub Actions automatikusan előállítja/frissíti a `DOCKERHUB_USERNAME` secretből.

## OpenShift telepítés (CLI nélkül, automatikus frissítéssel)

1. OpenShift Console-ban (`+Add` → `Import YAML`) importáld az [openshift/openshift-all-generated.yaml](openshift/openshift-all-generated.yaml) tartalmát.

2. Ugyanitt cseréld le a `CHANGE_ME_STRONG_*` secret placeholdereket erős, egyedi értékekre.

3. Kész.

Az automatikus működés ezután:

- minden commit/release után a GitHub Actions feltolja az új image-et Docker Hubra,
- OpenShift `ImageStream` időzítetten importálja a `latest` taget,
- a `DeploymentConfig` image-change trigger automatikusan rolloutol.

Ha ragaszkodsz a scriptes secret-generáláshoz, opcionálisan használható helyileg:

   ```bash
   bash scripts/generate-secrets.sh
   ```

Részletes OpenShift leírás: [openshift/README.md](openshift/README.md)

=======
>>>>>>> a016d36beb99bbddd94541f3aa85c9bedad90e97
## Devfile import (OpenShift Console)

A [devfile.yaml](devfile.yaml) alapértelmezetten a `build + deploy-openshift-stack` kompozit parancsot futtatja (`deploy`), így a teljes OpenShift stack kerül alkalmazásra.

- A csak mintacélú k8s deploy továbbra is elérhető a `deploy-k8s-devfile-only` paranccsal ([openshift/devfile-k8s-deploy.yaml](openshift/devfile-k8s-deploy.yaml)).
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

## Fontos működési megjegyzések

- Feltöltött fájlméret limit: `100 MB` (backend + Nginx oldalon is)
- Törölni csak a kép tulajdonosa tud
- A feltöltött képek a `uploads` kötetben tárolódnak
- A repository OpenShift célkörnyezetre van optimalizálva
