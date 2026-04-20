# Fényképalbum alkalmazás – Dokumentáció

Ez a projekt egy Flask alapú fényképalbum alkalmazás, amit OpenShiftre és Terraformos IaC megoldásra is fel lehet húzni. A repo célja nem csak az, hogy fusson az app, hanem az is, hogy jól bemutassa a build, deploy, skálázás és terhelésteszt részeket is.

## Rövid áttekintés

Az alkalmazás három fő részből áll:

- frontend: a webes felület és a backend API proxyzása
- backend: REST API, autentikáció, képfeltöltés és képkezelés
- MySQL: felhasználók és képek adatainak tárolása

Az OpenShiftes megoldás kétféleképpen van jelen a repo-ban:

- klasszikus YAML alapú deploy manifestekkel
- Terraform alapú IaC telepítéssel

## Választott környezet

Az alkalmazás **OpenShift PaaS** platformon fut (OKD). Az image-ek buildelése a repo workflow-jaival és az OpenShift BuildConfig megoldással is meg van támogatva.

## IaC (Terraform) telepítés OpenShiftre

A projekt tartalmaz egy teljes Terraform alapú OpenShift deploy megoldást is, amely deklaratívan kezeli a következőket:

- Namespace
- Secret
- MySQL (PVC + Deployment + Service)
- Backend és frontend (Deployment + Service)
- NetworkPolicy szabályok
- Opcionális HPA (backend + frontend)

Megjegyzés: a frontend OpenShift Route jelenleg nem Terraform erőforrásként szerepel, hanem az IaC deploy workflow külön kubectl lépésben hozza létre.

Elérési út: [infra/terraform/](infra/terraform/)

Automatikus deploy workflow:

- [iac-terraform-deploy.yml](.github/workflows/iac-terraform-deploy.yml)
- A Docker image build/push után automatikusan lefut a Terraform apply lépés.
- Manuálisan is indítható workflow_dispatch eseménnyel.

Külön Terraform leírás: [infra/terraform/README.md](infra/terraform/README.md)

A TASK4 részletes dokumentáció: [Documentations/TASK4 - IaC/terraform_openshift_iac_report.md](Documentations/TASK4%20-%20IaC/terraform_openshift_iac_report.md)

---

## Architektúra – Rétegek és kapcsolatok

```
Böngésző
    │  HTTP :80
    ▼
┌─────────────────────────────┐
│  Frontend (Flask + Gunicorn) │  :5000
│  JSON API proxy réteg         │
└─────────────┬───────────────┘
              │  HTTP REST :5001
              ▼
┌─────────────────────────────┐
│  Backend  (Flask + Gunicorn) │  :5001
│  REST API, üzleti logika     │
│  Képek tárolása az adatbázisban│
└─────────────┬───────────────┘
              │  TCP :3306 (SQLAlchemy / PyMySQL)
              ▼
┌─────────────────────────────┐
│  MySQL 8.0                   │  :3306
│  Felhasználók, kép metaadatok│
└─────────────────────────────┘
```

### Frontend réteg

- **Technológia:** Python 3.12, Flask 3.1, Gunicorn
- **Feladat:** JSON API proxy a backend felé és session/token kezelés
- **Képmegjelenítés:** proxy route-on keresztül adja vissza a képfájlt a backendből
- **Session kezelés:** A bejelentkezési token szerver oldali Flask session-ban tárolódik

### Backend réteg

- **Technológia:** Python 3.12, Flask 3.1, Gunicorn, Flask-SQLAlchemy, PyMySQL, Werkzeug, itsdangerous
- **Feladat:** REST API biztosítása a frontend számára, autentikáció, képfeltöltés kezelése
- **Autentikáció:** Token-alapú (`itsdangerous.URLSafeTimedSerializer`), 24 órás lejárattal, `Authorization: Bearer <token>` fejléccel
- **Képtárolás:** a feltöltött kép bináris tartalma és MIME típusa az adatbázisban van eltárolva, ezért a backend stateless és horizontálisan skálázható
- **Sémafrissítés:** az induláskor futó külön migrációs script gondoskodik a `photos` tábla bővítéséről

### Adatbázis réteg

- **Technológia:** MySQL 8.0 (`registry.access.redhat.com/rhscl/mysql-80-rhel7`)
- **Táblák:**
  - `users`: `id`, `username` (max 80 kar., egyedi), `password_hash`
  - `photos`: `id`, `name` (max 40 kar.), `filename`, `content_type`, `image_data`, `uploaded_at`, `owner_id` (FK → users)
- **Perzisztencia:** az adatok a MySQL adatbázisban maradnak meg

---

## REST API végpontok

| Metódus | Végpont | Auth | Leírás |
|---|---|---|---|
| GET | `/api/health` | – | Állapot ellenőrzés |
| POST | `/api/register` | – | Regisztráció |
| POST | `/api/login` | – | Bejelentkezés, tokent ad vissza |
| GET | `/api/photos?sort=date\|name&order=asc\|desc` | – | Fotók listázása |
| POST | `/api/photos` | ✅ | Fotó feltöltése |
| GET | `/api/photos/<id>` | – | Fotó metaadatai |
| DELETE | `/api/photos` | ✅ | Tömeges törlés szűrőkkel |
| DELETE | `/api/photos/<id>` | ✅ | Fotó törlése (csak saját) |
| GET | `/api/photos/<id>/image` | – | Képfájl visszaadása |

A tömeges törlésnél ezek a szűrők használhatók:

- `name_prefix`
- `uploaded_before`
- `uploaded_after`

Az időpontok ISO 8601 formátumúak.

---

## Megvalósított funkciók

- Felhasználókezelés: regisztráció, belépés, kilépés
- Fényképfeltöltés (csak bejelentkezett felhasználónak)
- Fényképtörlés (csak bejelentkezett felhasználónak, csak saját kép)
- Tömeges képtörlés szűréssel az API-n keresztül
- Minden képhez: név (max. 40 karakter), feltöltési dátum (`ÉÉÉÉ-HH-NN ÓÓ:PP`) és feltöltő felhasználónév
- Lista név vagy dátum szerinti rendezéssel, emelkedő vagy csökkenő sorrendben
- Listaelemre kattintva a kép részletes megjelenítése (a feltöltő nevével)

---

## Környezeti változók

A projekt több helyen is használ környezeti változókat. A legfontosabbak:

- `DATABASE_URL`: backend adatbázis kapcsolat
- `SECRET_KEY`: backend token-aláírás
- `FLASK_SECRET_KEY`: frontend session kulcs
- `BACKEND_URL`: frontend által használt backend cím
- `UPLOAD_FOLDER`: feltöltések helye, alapból `/data/uploads`
- `MAX_PHOTO_SIZE`: maximális fájlméret bájtban

Példaértékek itt vannak: [.env.example](.env.example)

OpenShift/Terraform oldalról ezek a secret és var beállítások számítanak:

- `OPENSHIFT_SERVER`
- `OPENSHIFT_TOKEN`
- `OPENSHIFT_CA_CERT`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `TF_API_TOKEN`
- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `BACKEND_SECRET_KEY`
- `FRONTEND_SECRET_KEY`
- `OPENSHIFT_NAMESPACE`
- `ENABLE_HPA`
- `DEPLOY_ROLLOUT_TIMEOUT`

---

## Könyvtárstruktúra

```
PhotoWebApp_PaaS/
├── backend/
│   ├── app.py                             # Flask REST API
│   ├── migrate_photo_schema.py            # Külön futtatható séma-migráció
│   ├── backend.yaml                       # OpenShift ImageStream-alapú Deployment + Service
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py                             # Flask JSON API proxy
│   ├── frontend.yaml                      # OpenShift ImageStream-alapú Deployment + Service + Route
│   ├── Dockerfile
│   └── requirements.txt
├── locust/
│   ├── locustfile.py                      # Terhelésteszt – minden API funkciót lefed
│   ├── requirements.txt
│   ├── Dockerfile
│   └── locust-openshift.yaml             # Locust telepítése OpenShift-be (felhőből való futtatás)
├── mysql/
│   ├── mysql.yaml                         # Secret, PVC, Deployment, Service
│   └── Dockerfile                         # UBI9-alapú egyedi MySQL image
├── openshift/
│   ├── photowebapp-build.yaml             # Backend + frontend ImageStream-ek és BuildConfig-ok
│   ├── locust-image.yaml                  # Locust ImageStream + BuildConfig
│   ├── locust-openshift.yaml              # Locust runtime (master/worker, Service, Route)
│   └── hpa.yaml                           # HorizontalPodAutoscaler – frontend és backend
└── k8s/
    └── photowebapp.yaml                   # Lokális Kubernetes manifest (fejlesztéshez)
```

---

## Futtatás fejlesztői környezetben

A repo alapján a legegyszerűbb helyi indítási logika ez:

1. indítsd el a MySQL-t
2. állítsd be a backendhez a `DATABASE_URL` és `SECRET_KEY` változókat
3. állítsd be a frontendhez a `BACKEND_URL` és `FLASK_SECRET_KEY` változókat
4. indítsd a backend és frontend Flask appokat külön processzben

Ha a projektben a lokális teszteléshez a Kubernetes manifestet használod, akkor a [k8s/photowebapp.yaml](k8s/photowebapp.yaml) a jó kiindulópont.

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

Megjegyzés: a build manifest a repo GitHub címéről húzza a forrást, és a built image-eket OpenShift ImageStreambe teszi.

### 3) Adatbázis és alkalmazás deploy

1. **+Add → Import YAML** alatt importáld a [mysql/mysql.yaml](mysql/mysql.yaml) tartalmát.
2. A létrejött `photowebapp-secrets` Secretben cseréld a `CHANGE_THIS_*` értékeket.
3. Importáld a [backend/backend.yaml](backend/backend.yaml) tartalmát.
4. Importáld a [frontend/frontend.yaml](frontend/frontend.yaml) tartalmát.
5. **Workloads → Pods** alatt ellenőrizd, hogy `mysql`, `backend`, `frontend` podok `Running` állapotban vannak.
6. **Networking → Routes** alatt nyisd meg a `frontend` route-ot.

Itt érdemes figyelni arra, hogy a backend induláskor lefuttatja a sémafrissítést is, tehát nem csak sima deploymentről van szó.

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
    - Host: `http://backend:5001`
    - Megjegyzés: a Locust a backend `/api/*` végpontokat terheli.
6. Kattints **Start swarming**.

### 6) GitHub workflow-k

A repo-ban három fontos GitHub Actions workflow van:

- [dockerhub-publish.yml](.github/workflows/dockerhub-publish.yml): backend és frontend image-ek buildelése és pusholása Docker Hubra
- [openshift-manifest-render.yml](.github/workflows/openshift-manifest-render.yml): OpenShift manifest generálás workflow_dispatch indítással
- [iac-terraform-deploy.yml](.github/workflows/iac-terraform-deploy.yml): Terraform alapú OpenShift deploy a build után

### 7) GitHub webhook beállítás UI-ból

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

### 8) Skálázódás ellenőrzése UI-ban

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
- Újra-bejelentkezés terhelés közben

Így a teszt nem csak egy API végpontot terhel, hanem a teljes felhasználói működést modellezi.

---

## Fontos megjegyzések

- A képek bináris tartalma a `photos` táblában marad meg.
- A MySQL adatok az adatbázisban maradnak meg.
- A backend már stateless, ezért a backend HPA több replikára skálázható.
- A backend sémafrissítés (pl. `content_type`, `image_data`) külön scriptben fut: `backend/migrate_photo_schema.py`.
- A backend oldali bulk delete külön API végpont, és a lista rendezése az `order` paraméterrel is működik.
- A `CHANGE_THIS_*` értékeket minden környezetben cserélni kell.
