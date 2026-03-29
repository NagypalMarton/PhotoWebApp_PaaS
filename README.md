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
- Minden képhez: név (max. 40 karakter) és feltöltési dátum (`ÉÉÉÉ-HH-NN ÓÓ:PP`)
- Lista név vagy dátum szerinti rendezéssel
- Listaelemre kattintva a kép részletes megjelenítése

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
│   ├── photowebapp-build.yaml             # ImageStream-ek + BuildConfig-ok
│   └── hpa.yaml                           # HorizontalPodAutoscaler – frontend és backend
└── k8s/
    └── photowebapp.yaml                   # Lokális Kubernetes manifest (fejlesztéshez)
```

---

## Telepítés – OpenShift BuildConfig

Az OpenShift maga buildeli az image-eket közvetlenül a GitHub repóból, Docker Hub nem szükséges.

### 1) Projekt létrehozás

1. OpenShift Console → **Administrator** nézet
2. **Home → Projects → Create Project**: név legyen `photowebapp`

### 2) Build infrastruktúra – ImageStream-ek és BuildConfig-ok

1. **+Add → Import YAML**
2. Illeszd be az [`openshift/photowebapp-build.yaml`](openshift/photowebapp-build.yaml) teljes tartalmát
3. Kattints **Create**
4. **Builds → BuildConfigs** – a `photowebapp-backend-build` és `photowebapp-frontend-build` automatikusan elindulnak (ConfigChange trigger)
5. Várd meg, amíg mindkét build sikeresen befejezik (**Builds → Builds** → zöld pipa)

**Fontos:** A webhook secret kulcsa `WebHookSecretKey` (ez az OpenShift követelménye). Ha ezt a kulcsot módosítod, a GitHub webhook beállításoknál is ugyanezt az értéket kell használnod.

### 3) MySQL deploy

1. **+Add → Import YAML**
2. Illeszd be a [`mysql/mysql.yaml`](mysql/mysql.yaml) tartalmát
3. **Fontos:** a `photowebapp-secrets` Secret-ben cseréld le az összes `CHANGE_THIS_*` értéket erős jelszavakra, és a `DATABASE_URL`-t tartsd szinkronban a `MYSQL_PASSWORD`-del
4. Kattints **Create**
5. **Workloads → Pods** – ellenőrizd, hogy a `mysql` pod **Running** állapotú

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

## Automatikus skálázás (HPA)

A frontend és a backend réteg `HorizontalPodAutoscaler` segítségével CPU-kihasználtság alapján automatikusan skálázódik.

| Komponens | Min replika | Max replika | CPU célkihasználtság |
|-----------|:-----------:|:-----------:|:--------------------:|
| frontend  | 1           | 5           | 50 %                 |
| backend   | 1           | 5           | 50 %                 |

A CPU request értékek szándékosan alacsonyak (**50m request / 200m limit**), hogy a terhelésteszt kis terhelés esetén is kiváltsa a skálázást.

**Megjegyzés a backendről:** Az `uploads-pvc` PVC `ReadWriteOnce` módban van, tehát a feltöltött képfájlok csak az azt felcsatoló podból érhetők el. Ha a klaszter storage class-ja támogat `ReadWriteMany` hozzáférési módot (pl. CephFS), módosítsd a `backend.yaml`-ban a PVC `accessModes` mezőjét. Az autentikáció és az adatbázis-műveletek RWO esetén is párhuzamosan skálázódnak.

### HPA telepítése

```bash
# 1. Alkalmazd az HPA konfigurációt:
oc apply -f openshift/hpa.yaml

# 2. Ellenőrizd az állapotot:
oc get hpa
oc describe hpa frontend-hpa
oc describe hpa backend-hpa
```

### Skálázás megfigyelése terhelés közben

```bash
# HPA állapot folyamatos figyelése:
watch oc get hpa

# Podok számának változása:
watch oc get pods -l app=frontend
watch oc get pods -l app=backend
```

---

## Terhelésteszt (Locust)

A `locust/` könyvtár tartalmazza a Python-alapú [Locust](https://locust.io) terhelésteszt konfigurációját.

### Lefedett API funkciók

| Feladat | Végpont | Relatív arány |
|---------|---------|:-------------:|
| Állapot-ellenőrzés | `GET /api/health` | 1× |
| Fotólista (dátum) | `GET /api/photos` | 4× |
| Fotólista (név) | `GET /api/photos?sort=name` | 2× |
| Fotó feltöltése | `POST /api/photos` | 3× |
| Fotó megtekintése | `GET /api/photos/<id>` + `/image` | 3× |
| Fotó törlése | `DELETE /api/photos/<id>` | 1× |

Minden virtuális felhasználó `on_start`-kor regisztrál és bejelentkezik, majd a fenti feladatokat vegyesen hajtja végre 1–3 másodperces várakozásokkal.

### Futtatás OpenShift-ből (felhőből)

A feladatleírás előírja, hogy a terhelésteszt felhőből fusson. A Locust a `photowebapp` névtéren belül deployolható, ahonnan közvetlenül eléri a backend service-t.

```bash
oc apply -f locust/locust-openshift.yaml

# Web UI URL:
oc get route locust
```

A megjelenő HTTPS URL-en érhető el a Locust web felülete. Ajánlott beállítások:

- **Number of users:** 20–50
- **Spawn rate:** 5 user/s
- **Host:** `http://backend:5001`

### Lokális futtatás (fejlesztéshez)

```bash
pip install locust
cd locust
locust --host http://<frontend-route-url>
# Böngészőben: http://localhost:8089
```

### Locust eltávolítása

```bash
oc delete -f locust/locust-openshift.yaml
```

---

## Task 2: Automatikus skálázás és terheléseszt (OpenShift PaaS)

### Automatikus skálázás konfigurációja

A frontend és backend rétegek `HorizontalPodAutoscaler` (HPA) segítségével CPU-kihasználtság alapján automatikusan skálázódnak 1-5 replika között.

| Komponens | Min replika | Max replika | CPU célkihasználtság | Skálázási viselkedés |
|-----------|:-----------:|:-----------:|:--------------------:|---------------------|
| frontend  | 1           | 5           | 50 %                 | +2 pod/30s (felfelé), +1 pod/60s (lefelé) |
| backend   | 1           | 5           | 50 %                 | +2 pod/30s (felfelé), +1 pod/60s (lefelő) |

**Skálázási viselkedés:**
- **Felfelé skálázás:** 0 másodperc stabilizációs idő (azonnali reakció)
- **Lefelé skálázás:** 60 másodperc stabilizációs idő (hogy ne ugorjon fel/le)

**Erőforrás kérések (per pod):**
- Frontend: 100m CPU (kérés) / 200m CPU (limit), 128Mi memória (kérés) / 256Mi (limit)
- Backend: 100m CPU (kérés) / 500m CPU (limit), 128Mi memória (kérés) / 512Mi (limit)
- MySQL: 200m CPU (kérés) / 500m CPU (limit), 512Mi memória (kérés) / 1Gi (limit)

**Fontos megjegyzés a backendről:** Az `uploads-pvc` PVC `ReadWriteOnce` (RWO) módban van, tehát a feltöltött képfájlok csak az azt felcsatoló podból érhetők el. Ha a klaszter storage class-ja támogat `ReadWriteMany` (RWX) hozzáférési módot (pl. CephFS, NFS), módosítsd az `openshift/openshift-all.yaml`-ban az `uploads-pvc` `accessModes` mezőjét. Az autentikáció és az adatbázis-műveletek RWO esetén is párhuzamosan skálázódnak.

### HPA telepítése

```bash
# 1. Alkalmazd az összes konfigurációt (HPA is tartalmazza):
oc apply -f openshift/openshift-all.yaml

# 2. Vagy csak az HPA-t:
oc apply -f openshift/hpa.yaml

# 3. Ellenőrizd az állapotot:
oc get hpa
oc describe hpa frontend-hpa
oc describe hpa backend-hpa
```

### Skálázás megfigyelése

```bash
# HPA állapot folyamatos figyelése:
watch oc get hpa

# Podok számának változása:
watch oc get pods -l app=frontend
watch oc get pods -l app=backend

# HPA események:
oc get events --field-selector reason=SuccessfulRescale
```

### Terheléseszt konfigurációja (Locust)

A `locust/locustfile.py` tartalmazza a terheléseszt konfigurációt, amely lefedi az összes API funkciót:

| Feladat | Végpont | Relatív arány | Leírás |
|---------|---------|:-------------:|--------|
| Health check | `GET /api/health` | 1× | Állapot-ellenőrzés |
| List by date | `GET /api/photos?sort=date` | 4× | Fotólista dátum szerint |
| View photo | `GET /api/photos/<id>` + `/image` | 3× | Fotó megtekintése |
| Upload photo | `POST /api/photos` | 3× | Fotó feltöltése |
| List by name | `GET /api/photos?sort=name` | 2× | Fotólista név szerint |
| Delete photo | `DELETE /api/photos/<id>` | 1× | Fotó törlése |

**Terheléseszt futtatása OpenShift-ből (felhőből):**

```bash
# 1. Deployold a Locustot:
oc apply -f locust/locust-openshift.yaml

# 2. Szerezd be a web UI URL-t:
oc get route locust
# Web UI: https://locust-<namespace>.apps.<cluster>

# 3. Konfiguráció a web UI-ban:
#    - Number of users: 50
#    - Spawn rate: 5 users/s
#    - Host: http://backend:5001

# 4. Kattints "Start swarming" és figyeld a skálázást
```

**Terheléseszt futtatás helyi gépen:**

```bash
pip install locust
cd locust
locust --host http://backend:5001
# Böngészőben: http://localhost:8089
```

### Automatikus skálázás igazolása (Proof of Scaling)

A skálázás igazolásához gyűjtsd össze a következő információkat:

**1. Skálázás felfelé (terhelés alatt):**
```bash
# Előtte (1 replika):
oc get hpa
oc get pods -l app=frontend -o wide
oc get pods -l app=backend -o wide

# Utána (5 replika):
oc get hpa
oc get pods -l app=frontend -o wide
oc get pods -l app=backend -o wide

# Skálázási események:
oc get events --field-selector reason=SuccessfulRescale
```

**2. Skálázás lefelé (terhelés után):**
```bash
# Miután a terhelés csökkent:
oc get hpa
oc get pods -l app=frontend -o wide
oc get pods -l app=backend -o wide
```

**3. Teljesítmény metrikák:**
- Átlagos válaszidő: < 2 másodperc
- Hiba arány: < 1%
- Max CPU használat: < 70%
- Adatbázis kapcsolatok: stabil

**4. Screenshots:**
- HPA állapot a skálázás közben
- Pod szám változás grafikon
- Locust teszt eredmények
- Erőforrás használat grafikon

**Teljes tesztelési eljárás részletesen:** Lásd `openshift/task2-load-test-guide.md`

**Igazolási sablon:** Lásd `openshift/task2-proof-template.md`

---

## Megjegyzések

- A feltöltött képek PersistentVolumeClaim (`uploads-pvc`, 5Gi) volume-on tárolódnak – pod újraindítás esetén megmaradnak.
- A MySQL adatai szintén PVC-n tárolódnak (`mysql-pvc`, 5Gi).
- A MySQL image a hivatalos Red Hat registryből származik: `registry.access.redhat.com/rhscl/mysql-80-rhel7`.
- A `mysql/mysql.yaml`-ban lévő Secret-ben minden `CHANGE_THIS_*` értéket éles jelszóra kell cserélni az alkalmazás élesítése előtt.
- A `k8s/photowebapp.yaml` fejlesztési/tesztelési célra szolgál lokális Kubernetes clusterhez (pl. Minikube, Kind).
