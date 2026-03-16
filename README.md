# Fényképalbum alkalmazás – Dokumentáció

## Választott környezet

Az alkalmazás **OpenShift PaaS** platformon fut (OKD). Két telepítési megközelítés támogatott:

- **A) Docker Hub + GitHub Actions** – a CI/CD pipeline buildeli és tolja fel a képeket Docker Hubra, az OpenShift ezekből húzza le az image-eket.
- **B) OpenShift BuildConfig** – az OpenShift maga buildeli az image-eket közvetlenül a GitHub repóból.

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
- Minden képhez: név (max. 40 karakter) és feltöltési dátum (`ÉÉÉÉ-HH-NN ÓÓ:PP`)
- Lista névvagy dátum szerinti rendezéssel
- Listaelemre kattintva a kép részletes megjelenítése

---

## Skálázhatóság

Mindhárom réteg önállóan skálázható az OpenShift-ben:

```bash
oc scale deployment frontend --replicas=3
oc scale deployment backend  --replicas=3
```

A MySQL egy példányban fut PVC-vel, a frontend és backend állapotmentes – tetszőleges számú példányban futtatható.

---

## Könyvtárstruktúra

```
PhotoWebApp_PaaS/
├── .github/
│   └── workflows/
│       ├── dockerhub-publish.yml          # CI: build + push Docker Hub-ra (A megközelítés)
│       └── openshift-manifest-render.yml  # CI: OpenShift manifest generálás (A megközelítés)
├── backend/
│   ├── app.py                             # Flask REST API
│   ├── backend.yaml                       # OpenShift ImageStream-alapú Deployment + PVC + Service (B megközelítés)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py                             # Flask UI
│   ├── frontend.yaml                      # OpenShift ImageStream-alapú Deployment + Service + Route (B megközelítés)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── templates/                         # Jinja2 sablonok
├── mysql/
│   ├── mysql.yaml                         # Secret, PVC, Deployment, Service
│   └── Dockerfile                         # UBI9-alapú egyedi MySQL image
├── openshift/
│   ├── photowebapp-build.yaml             # ImageStream-ek + BuildConfig-ok (B megközelítés)
│   ├── openshift-all.yaml                 # Teljes stack template (A megközelítés – CHANGE_ME placeholder)
│   ├── openshift-all-generated.yaml       # Generált manifest valódi Docker Hub névtérrel (CI hozza létre)
│   ├── redeploy-app-only.yaml             # Backend + Frontend Deployment template (A megközelítés)
│   └── redeploy-app-only-generated.yaml   # Generált redeploy manifest (CI hozza létre)
└── k8s/
    └── photowebapp.yaml                   # Lokális Kubernetes manifest (fejlesztéshez)
```

---

## Telepítés – A megközelítés: Docker Hub + GitHub Actions

Ebben a megközelítésben a GitHub Actions buildeli és tolja fel az image-eket a Docker Hubra. Az OpenShift ezeket húzza le közvetlenül.

### Előfeltételek

A GitHub repóban be kell állítani a következő **Repository Secrets**-eket:

| Secret neve | Leírás |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub felhasználónév / szervezet neve |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

### GitHub Actions workflow-ok

#### `dockerhub-publish.yml` – Image build és push

Minden `push` eseményre (és release publikálásra) lefut:
1. Buildeli a `backend/Dockerfile`-t → `<DOCKERHUB_USERNAME>/photowebapp-backend:latest`
2. Buildeli a `frontend/Dockerfile`-t → `<DOCKERHUB_USERNAME>/photowebapp-frontend:latest`
3. Mindkét image-et feltölti Docker Hubra

#### `openshift-manifest-render.yml` – Manifest generálás

Minden `push` eseményre lefut:
1. A `openshift/openshift-all.yaml` template-ben a `CHANGE_ME_DOCKERHUB_USERNAME` helyőrzőt kicseréli a `DOCKERHUB_USERNAME` secret értékére → `openshift/openshift-all-generated.yaml`
2. Ugyanezt elvégzi a `openshift/redeploy-app-only.yaml`-on → `openshift/redeploy-app-only-generated.yaml`
3. A generált fájlokat automatikusan commitálja a repóba

### OpenShift telepítési lépések

#### 1) Projekt létrehozás

1. OpenShift Console → **Administrator** nézet
2. **Home → Projects → Create Project**: név legyen `photowebapp`

#### 2) MySQL deploy

1. **+Add → Import YAML**
2. Illeszd be a [`mysql/mysql.yaml`](mysql/mysql.yaml) tartalmát
3. **Fontos:** a `photowebapp-secrets` Secret-ben cseréld le az összes `CHANGE_THIS_*` értéket erős jelszavakra, és a `DATABASE_URL`-t tartsd szinkronban a `MYSQL_PASSWORD`-del
4. Kattints **Create**
5. **Workloads → Pods** – ellenőrizd, hogy a `mysql` pod **Running** állapotú

#### 3) Teljes alkalmazás deploy (első telepítés)

1. Várd meg, amíg a CI lefut és létrejön az `openshift/openshift-all-generated.yaml`
2. **+Add → Import YAML**
3. Illeszd be az [`openshift/openshift-all-generated.yaml`](openshift/openshift-all-generated.yaml) tartalmát
4. Kattints **Create**
5. **Networking → Routes** – a `frontend` route-on érhető el az alkalmazás (HTTPS)

#### 4) Csak az alkalmazás újratelepítése (frissítés)

Ha csak a backend és/vagy frontend képet frissítetted:

1. **+Add → Import YAML**
2. Illeszd be az [`openshift/redeploy-app-only-generated.yaml`](openshift/redeploy-app-only-generated.yaml) tartalmát
3. Kattints **Create** (az `oc apply` szemantikájával frissíti a meglévő Deployment-eket)

---

## Telepítés – B megközelítés: OpenShift BuildConfig

Ebben a megközelítésben az OpenShift maga buildeli az image-eket közvetlenül a GitHub repóból, Docker Hub nem szükséges.

### 1) Projekt létrehozás

1. OpenShift Console → **Administrator** nézet
2. **Home → Projects → Create Project**: név legyen `photowebapp`

### 2) Build infrastruktúra – ImageStream-ek és BuildConfig-ok

1. **+Add → Import YAML**
2. Illeszd be az [`openshift/photowebapp-build.yaml`](openshift/photowebapp-build.yaml) teljes tartalmát
3. Kattints **Create**
4. **Builds → BuildConfigs** – a `photowebapp-backend-build` és `photowebapp-frontend-build` automatikusan elindulnak (ConfigChange trigger)
5. Várd meg, amíg mindkét build sikeresen befejezik (**Builds → Builds** → zöld pipa)

### 3) MySQL deploy

(Lásd fentebb az A megközelítésnél.)

### 4) Backend deploy

1. **+Add → Import YAML**
2. Illeszd be a [`backend/backend.yaml`](backend/backend.yaml) teljes tartalmát
3. Kattints **Create**
4. A Deployment az ImageStream trigger segítségével automatikusan frissül, amint a `photowebapp-backend:latest` kép elérhető

### 5) Frontend deploy

1. **+Add → Import YAML**
2. Illeszd be a [`frontend/frontend.yaml`](frontend/frontend.yaml) teljes tartalmát
3. Kattints **Create**
4. A Deployment az ImageStream trigger segítségével automatikusan frissül, amint a `photowebapp-frontend:latest` kép elérhető
5. **Networking → Routes** – a `frontend` route-on érhető el az alkalmazás (HTTPS)

### 6) Automatikus build GitHub push-ra (Webhook)

**Webhook URL-ek kinyerése az OpenShift UI-ból:**

1. **Administrator → Builds → BuildConfigs**
2. Nyisd meg a `photowebapp-backend-build` BuildConfigot
3. **Configuration** fül → **Webhooks** szakasz → **GitHub** sor → **Copy URL with Secret**
4. Ismételd meg a `photowebapp-frontend-build` BuildConfiggal

**Webhook hozzáadása GitHub-on:**

1. GitHub repo → **Settings → Webhooks → Add webhook**
2. **Payload URL**: a másolt OpenShift webhook URL
3. **Content type**: `application/json`
4. **Trigger**: Just the push event
5. Mentés után: a zöld pipa jelzi a sikeres kapcsolatot

---

## Megjegyzések

- A feltöltött képek PersistentVolumeClaim (`uploads-pvc`, 5Gi) volume-on tárolódnak – pod újraindítás esetén megmaradnak.
- A MySQL adatai szintén PVC-n tárolódnak (`mysql-pvc`, 5Gi).
- A MySQL image a hivatalos Red Hat registryből származik: `registry.access.redhat.com/rhscl/mysql-80-rhel7`.
- A `mysql/mysql.yaml`-ban lévő Secret-ben minden `CHANGE_THIS_*` értéket éles jelszóra kell cserélni az alkalmazás élesítése előtt.
- A `k8s/photowebapp.yaml` fejlesztési/tesztelési célra szolgál lokális Kubernetes clusterhez (pl. Minikube, Kind).

---

## Hasznos linkek

- [OpenShift Documentation – Creating images](https://docs.redhat.com/en/documentation/openshift_container_platform/4.21/html/images/creating-images)
- [OpenShift Documentation – Building applications](https://docs.redhat.com/en/documentation/openshift_container_platform/4.21/html/building_applications/index)
