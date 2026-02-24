# PhotoWebApp_PaaS

Felhőalapú elosztott rendszerek laboratórium (2026) projekt: fényképalbum alkalmazás publikus PaaS környezetre.

Kapcsolódó követelményspecifikáció: [GalleryAppSRS.md](GalleryAppSRS.md)

## 1) Projektcél és beadási kontextus

A feladat célja egy PaaS-on futó fényképalbum alkalmazás elkészítése, az alábbi kulcskövetelményekkel:

- kép feltöltés és törlés,
- képek neve (max. 40 karakter) és feltöltési dátuma,
- listázás és rendezés név/dátum szerint,
- listaelemből képmegjelenítés,
- felhasználókezelés (regisztráció, belépés, kilépés),
- feltöltés/törlés csak bejelentkezett felhasználónak,
- GitHub push-ra automatikus build.

## 2) Jelenlegi implementáció (repo állapot)

Az aktuális verzió 3 konténeres felépítésben fut Docker Compose környezetben:

- MySQL adatbázis konténer (`db`),
- Python + Flask backend konténer (`backend`),
- Nginx alapú frontend konténer (`frontend`, Bootstrap v5.3 UI, reverse proxy `/api` és `/uploads` útvonalakra),
- lokális fájltárolás `uploads/` mappában.

Megvalósított funkciók:

- felhasználó regisztráció,
- bejelentkezés és kijelentkezés,
- kép feltöltése (név + fájl),
- képek listázása névvel és dátummal,
- rendezés név és dátum szerint,
- képmegtekintés listaelemből,
- kép törlése (csak tulajdonos/bejelentkezett felhasználó),
- 40 karakternél hosszabb név elutasítása.

## 3) Követelmény-megfelelés (gyors áttekintés)

| Követelmény | Állapot | Megjegyzés |
| --- | --- | --- |
| Kép feltöltés/törlés | Kész | Auth-hoz kötött |
| Név (max 40) + dátum | Kész | Validáció és tárolás működik |
| Listázás + rendezés (név/dátum) | Kész | API query paraméterekkel |
| Listaelemből képmegjelenítés | Kész | `image_url` alapján |
| Felhasználókezelés | Kész | Regisztráció, login, logout |
| Build automatikus indítás GitHub-ról | Nincs kész | CI workflow szükséges |
| Végleges külön DB szerver | Nincs kész | 2. beadási követelmény |

## 4) Technikai felépítés

- **Backend:** Flask API ([app.py](app.py))
- **DB kapcsolat:** PyMySQL kapcsolatkezelés ([app.py](app.py))
- **Séma:** `users` és `photos` táblák ([db/init.sql](db/init.sql))
- **Backend konténer:** [Dockerfile](Dockerfile)
- **Frontend konténer:** [frontend/Dockerfile](frontend/Dockerfile), [frontend/nginx.conf](frontend/nginx.conf), [frontend/index.html](frontend/index.html)
- **Konténeres orchestration:** [docker-compose.yml](docker-compose.yml)

## 5) Lokális futtatás (Docker Compose)

### Előfeltételek

- Docker Desktop (Compose támogatással)

### Indítás

```bash
docker compose up --build
```

Elérés:

- alkalmazás (frontend): <http://localhost:8080>
- health endpoint (frontend proxyn keresztül): <http://localhost:8080/api/health>

### Leállítás

```bash
docker compose down
```

### Adatbázis teljes újrainicializálása (minden adat törlődik)

```bash
docker compose down -v
docker compose up --build
```

## 6) API összefoglaló

### Egészségellenőrzés

- `GET /api/health`

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Képek listázása

- `GET /api/photos?sort=name|date&order=asc|desc`

### Kép feltöltése

- `POST /api/photos` (multipart/form-data)
  - mezők: `name`, `photo`
  - fájlméret limit: max. 100 MB

### Kép törlése

- `DELETE /api/photos/:id`

## 7) OpenShift célkörnyezet (2. beadás irány)

Tervezett éles környezet:

- PaaS: OpenShift,
- külön adatbázis-szerver (kötelező),
- backend több példányban futtatható,
- HTTPS publikus route,
- GitHub-ból automatikus build/deploy pipeline.

OpenShift erőforrásfájlok elkészítve:

- [openshift/openshift-all.yaml](openshift/openshift-all.yaml)
- [openshift/README.md](openshift/README.md)

Telepítés röviden:

```bash
oc apply -f openshift/openshift-all.yaml
```

Szükséges OpenShift erőforrások (a YAML-ben):

- app Deployment,
- db Deployment/StatefulSet (vagy menedzselt DB szolgáltatás),
- Service + Route,
- Secret (DB jelszó),
- ConfigMap (DB host/port/name),
- PVC a fájlokhoz vagy objektumtár (S3-kompatibilis) a képekhez.

## 8) Teendők a teljes követelményszinthez

Kötelezően hátralévő elemek:

1. CI pipeline létrehozása GitHub push eseményre (automatikus build).
2. OpenShift telepítés és publikus URL-es bemutatás.
3. Végleges változat: külön adatbázis-szerveres, skálázható, többrétegű üzemeltetés.

## 9) Benyújtandó elemek (2. beadás)

1. Rövid dokumentáció a végleges megoldásról:
   - választott PaaS környezet,
   - alkalmazásrétegek,
   - rétegek közötti kapcsolatok.
2. A megoldás forrásfájljai GitHub-on (repository linkkel).
3. Működő alkalmazás bemutatása PaaS környezetben.
4. Ha a végleges változat már korábban bemutatásra került, a dokumentáció újbóli feltöltése elegendő.
