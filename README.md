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
- **Platform:** OpenShift BuildConfig + DeploymentConfig + Route ([openshift/openshift-all.yaml](openshift/openshift-all.yaml))

## Projektstruktúra

- [app.py](app.py) – Flask API és auth/session logika
- [db/init.sql](db/init.sql) – `users` és `photos` táblák
- [frontend/](frontend/) – kliensoldali felület és Nginx konfiguráció
- [openshift/](openshift/) – teljes OpenShift manifestek és deployment dokumentáció
- [devfile.yaml](devfile.yaml) – OpenShift Dev Spaces / Import from Git leírás
- [scripts/generate-secrets.sh](scripts/generate-secrets.sh) – `CHANGE_ME_*` értékek biztonságos generálása

## Környezeti változók (backend)

| Változó | Kötelező | Alapérték | Leírás |
|---|---|---|---|
| `PORT` | nem | `3000` | Flask/Gunicorn port |
| `SECRET_KEY` | igen | – | Session titkos kulcs |
| `DB_HOST` | nem | `db` | MySQL host |
| `DB_PORT` | nem | `3306` | MySQL port |
| `DB_NAME` | igen | – | Adatbázis neve |
| `DB_USER` | igen | – | Adatbázis felhasználó |
| `DB_PASSWORD` | igen | – | Adatbázis jelszó |

Referenciaértékek: [.env.example](.env.example)

## OpenShift telepítés (ajánlott)

1. Generáld le a valódi secret értékeket:

	```bash
	bash scripts/generate-secrets.sh
	```

2. Alkalmazd a generált manifestet:

	```bash
	oc apply -f openshift/openshift-all-generated.yaml
	```

3. Indítsd el az első buildet:

	```bash
	oc start-build photowebapp-backend --follow
	oc start-build photowebapp-frontend --follow
	```

4. Ellenőrizd az erőforrásokat:

	```bash
	oc get pods
	oc get svc
	oc get route
	```

Részletes OpenShift leírás: [openshift/README.md](openshift/README.md)

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
