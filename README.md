# Fényképalbum alkalmazás – Dokumentáció

## Választott környezet

Az alkalmazás **OpenShift PaaS** platformon fut (OKD). Az image-eket az OpenShift maga buildeli közvetlenül a GitHub repóból (OpenShift BuildConfig).

---

## Architektúra – Rétegek és kapcsolatok

```
Böngésző
    │  HTTP :80
    ▼
┌─────────────────────────────┐
│  Frontend (Flask + Gunicorn) │  :5000
│  Jinja2 sablonok, Bootstrap  │
└─────────────┬───────────────┘
              │  HTTP REST :5001
              ▼
┌─────────────────────────────┐
│  Backend  (Flask + Gunicorn) │  :5001
│  REST API, üzleti logika     │
│  Fájl tárolás (/data/uploads)│
└─────────────┬───────────────┘
              │  TCP :3306 (SQLAlchemy / PyMySQL)
              ▼
┌─────────────────────────────┐
│  MySQL 8.0                   │  :3306
│  Felhasználók, kép metaadatok│
└─────────────────────────────┘
```

### Frontend réteg

- **Technológia:** Python 3.12, Flask 3.1, Gunicorn, Jinja2, Bootstrap 5.3
- **Feladat:** Szerver-oldali HTML renderelés, HTTP sablonvezérelt UI
- **Képmegjelenítés:** Proxy route-on keresztül (`/photo/<id>/image`) kéri le a képfájlt a backendtől, így a böngészőnek nem kell közvetlenül a backend service-t elérnie
- **Session kezelés:** A bejelentkezési token szerver oldali Flask session-ban tárolódik

### Backend réteg

- **Technológia:** Python 3.12, Flask 3.1, Gunicorn, Flask-SQLAlchemy, PyMySQL, Werkzeug, itsdangerous
- **Feladat:** REST API biztosítása a frontend számára, autentikáció, fájl feltöltés kezelése
- **Autentikáció:** Token-alapú (`itsdangerous.URLSafeTimedSerializer`), 24 órás lejárattal, `Authorization: Bearer <token>` fejléccel
- **Fájl tárolás:** `/data/uploads` könyvtár (OpenShift-kompatibilis: `chgrp -R 0 / chmod -R g+rwx`)

### Adatbázis réteg

- **Technológia:** MySQL 8.0 (`registry.access.redhat.com/rhscl/mysql-80-rhel7`)
- **Táblák:**
  - `users`: `id`, `username` (max 80 kar., egyedi), `password_hash`
  - `photos`: `id`, `name` (max 40 kar.), `filename`, `uploaded_at`, `owner_id` (FK → users)
- **Perzisztencia:** PersistentVolumeClaim (5Gi) biztosítja az adatok megőrzését

---

## REST API végpontok

| Metódus | Végpont | Auth | Leírás |
|---|---|---|---|
| GET | `/api/health` | – | Állapot ellenőrzés |
| POST | `/api/register` | – | Regisztráció |
| POST | `/api/login` | – | Bejelentkezés, tokent ad vissza |
| GET | `/api/photos?sort=date\|name` | – | Fotók listázása |
| POST | `/api/photos` | ✅ | Fotó feltöltése |
| GET | `/api/photos/<id>` | – | Fotó metaadatai |
| DELETE | `/api/photos/<id>` | ✅ | Fotó törlése (csak saját) |
| GET | `/api/photos/<id>/image` | – | Képfájl visszaadása |

---

## Megvalósított funkciók

- Felhasználókezelés: regisztráció, belépés, kilépés
- Fényképfeltöltés (csak bejelentkezett felhasználónak)
- Fényképtörlés (csak bejelentkezett felhasználónak, csak saját kép)
- Minden képhez: név (max. 40 karakter), feltöltési dátum (`ÉÉÉÉ-HH-NN ÓÓ:PP`) és feltöltő felhasználónév
- Lista név vagy dátum szerinti rendezéssel
- Listaelemre kattintva a kép részletes megjelenítése (a feltöltő nevével)

---

## Könyvtárstruktúra

```
PhotoWebApp_PaaS/
├── backend/
│   ├── app.py                             # Flask REST API
│   ├── backend.yaml                       # OpenShift ImageStream-alapú Deployment + PVC + Service
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py                             # Flask UI
│   ├── frontend.yaml                      # OpenShift ImageStream-alapú Deployment + Service + Route
│   ├── Dockerfile
│   ├── requirements.txt
│   └── templates/                         # Jinja2 sablonok
├── locust/
│   ├── locustfile.py                      # Terhelésteszt – minden API funkciót lefed
│   ├── requirements.txt
│   ├── Dockerfile
│   └── locust-openshift.yaml             # Locust telepítése OpenShift-be (felhőből való futtatás)
├── mysql/
│   ├── mysql.yaml                         # Secret, PVC, Deployment, Service
│   └── Dockerfile                         # UBI9-alapú egyedi MySQL image
├── openshift/
│   ├── openshift-all.yaml                 # Teljes stack: app + HPA + Locust
│   ├── photowebapp-build.yaml             # Backend + frontend ImageStream-ek és BuildConfig-ok
│   ├── locust-image.yaml                  # Locust ImageStream + BuildConfig
│   ├── locust-openshift.yaml              # Locust runtime (master/worker, Service, Route)
│   └── hpa.yaml                           # HorizontalPodAutoscaler – frontend és backend
└── k8s/
    └── photowebapp.yaml                   # Lokális Kubernetes manifest (fejlesztéshez)
```

---

## Telepítés és üzemeltetés (UI alapú)

Ez a szakasz egységesen OpenShift és GitHub UI lépésekkel írja le a teljes folyamatot. CLI parancsok helyett minden művelet elvégezhető a webes felületeken.

### 1) Projekt létrehozása

1. OpenShift Console-ban válts **Administrator** nézetre.
2. Nyisd meg: **Home → Projects → Create Project**.
3. Projekt neve: `photowebapp`.

### 2) Build infrastruktúra (backend + frontend)

1. Nyisd meg: **+Add → Import YAML**.
2. Másold be a [openshift/photowebapp-build.yaml](openshift/photowebapp-build.yaml) teljes tartalmát.
3. Kattints **Create**.
4. Nyisd meg: **Builds → BuildConfigs** és ellenőrizd, hogy a backend/frontend build elindult.
5. Nyisd meg: **Builds → Builds** és várd meg a sikeres build státuszt.

### 3) Adatbázis és alkalmazás deploy

1. **+Add → Import YAML** alatt importáld a [mysql/mysql.yaml](mysql/mysql.yaml) tartalmát.
2. A létrejött `photowebapp-secrets` Secretben cseréld a `CHANGE_THIS_*` értékeket.
3. Importáld a [backend/backend.yaml](backend/backend.yaml) tartalmát.
4. Importáld a [frontend/frontend.yaml](frontend/frontend.yaml) tartalmát.
5. **Workloads → Pods** alatt ellenőrizd, hogy `mysql`, `backend`, `frontend` podok `Running` állapotban vannak.
6. **Networking → Routes** alatt nyisd meg a `frontend` route-ot.

### 4) HPA (automatikus skálázás) bekapcsolása

1. Nyisd meg: **+Add → Import YAML**.
2. Importáld a [openshift/hpa.yaml](openshift/hpa.yaml) tartalmát.
3. Nyisd meg: **Observe → Horizontal Pod Autoscalers**.
4. Ellenőrizd a két HPA objektumot:
  - `frontend-hpa` (min 1, max 5)
  - `backend-hpa` (min 1, max 5)

### 5) Locust integráció külön appként (UI)

1. **+Add → Import YAML** alatt importáld a [openshift/locust-image.yaml](openshift/locust-image.yaml) tartalmát.
2. **Builds → BuildConfigs** alatt nyisd meg a `locust-build` objektumot és ellenőrizd a build futását.
3. **+Add → Import YAML** alatt importáld a [openshift/locust-openshift.yaml](openshift/locust-openshift.yaml) tartalmát.
4. **Networking → Routes** alatt nyisd meg a `locust` route-ot.
5. A Locust UI-ban állítsd be:
  - Number of users: `30-60`
  - Spawn rate: `5-10`
  - Host: `http://frontend:80`
6. Kattints **Start swarming**.

### 6) GitHub webhook beállítás UI-ból

#### OpenShift oldalon

1. **Builds → BuildConfigs** alatt nyisd meg sorban:
  - `photowebapp-backend-build`
  - `photowebapp-frontend-build`
  - `locust-build`
2. Mindháromnál a **Configuration → Webhooks** résznél másold ki a GitHub webhook URL-t (**Copy URL with Secret**).

#### GitHub oldalon

1. Repo: **Settings → Webhooks → Add webhook**.
2. `Payload URL`: az OpenShiftből másolt URL.
3. `Content type`: `application/json`.
4. Esemény: `Just the push event`.
5. Mentés után ellenőrizd a zöld státuszt.

### 7) Skálázódás ellenőrzése UI-ban

1. Locust terhelés alatt nyisd meg: **Observe → Horizontal Pod Autoscalers**.
2. Közben nyisd meg: **Workloads → Deployments**.
3. Ellenőrizd, hogy a frontend/backend replika szám nő (`1 -> n`) terhelés alatt.
4. Terhelés leállítása után ellenőrizd, hogy visszaskáláz (`n -> 1`).
5. A bizonyításhoz készíts képernyőképeket:
  - HPA nézet (terhelés alatt)
  - Deployment replika változás
  - Locust statisztika oldal

---

## Terhelésteszt lefedettség

A [locust/locustfile.py](locust/locustfile.py) az alkalmazás fő funkcióit terheli:

- Regisztráció / bejelentkezés
- Fotólista (dátum és név szerinti rendezés)
- Fotó feltöltés
- Fotó megtekintés
- Fotó törlés

Így a teszt nem csak egy API végpontot terhel, hanem a teljes felhasználói működést modellezi.

---

## Fontos megjegyzések

- A képfájlok `uploads-pvc` volume-on maradnak meg.
- A MySQL adatok `mysql-pvc` volume-on maradnak meg.
- Backend oldalon `ReadWriteOnce` esetén a fájlmegosztás több replika között korlátozott lehet.
- A `CHANGE_THIS_*` értékeket minden környezetben cserélni kell.

---

## További dokumentáció

Részletes Task 2 anyagok az `openshift` mappában:

- [openshift/TASK2_SCALING_CONFIG.md](openshift/TASK2_SCALING_CONFIG.md)
- [openshift/TASK2_LOAD_TEST_REPORT.md](openshift/TASK2_LOAD_TEST_REPORT.md)
- [openshift/TASK2_LESSONS_LEARNED.md](openshift/TASK2_LESSONS_LEARNED.md)
- [openshift/README_TASK2.md](openshift/README_TASK2.md)
- [openshift/task2-load-test-guide.md](openshift/task2-load-test-guide.md)
- [openshift/task2-proof-template.md](openshift/task2-proof-template.md)
