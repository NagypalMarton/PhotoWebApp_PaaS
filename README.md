# PhotoWebApp_PaaS

Felhőalapú elosztott rendszerek laboratórium (2026) projekt: fényképalbum alkalmazás OpenShift (PaaS) környezetre.

## 1) Projektcél

A projekt célja egy OpenShift-en futó fotóalbum alkalmazás, az alábbi funkciókkal:

- kép feltöltés és törlés,
- képek neve (max. 40 karakter) és feltöltési dátuma,
- listázás és rendezés név/dátum szerint,
- listaelemből képmegjelenítés,
- felhasználókezelés (regisztráció, belépés, kilépés),
- feltöltés/törlés csak bejelentkezett felhasználónak.

## 2) Felépítés

- **Backend:** Flask API ([app.py](app.py))
- **Adatbázis séma:** [db/init.sql](db/init.sql)
- **Frontend:** [frontend/index.html](frontend/index.html), [frontend/nginx-cfg/default.conf](frontend/nginx-cfg/default.conf)
- **OpenShift erőforrások:** [openshift/openshift-all.yaml](openshift/openshift-all.yaml)
- **OpenShift telepítési leírás:** [openshift/README.md](openshift/README.md)

## 3) OpenShiftbe való importálás

A gyökérben található [devfile.yaml](devfile.yaml) importálás után az alapértelmezett `deploy` parancs egy lépésben alkalmazza az összes OpenShift réteget (`openshift/openshift-all.yaml`), és külön frontend, backend, ill. adatbázis munkaterhelést hoz létre:

- **frontend** – Deployment + Service + Route (port 8080)
- **backend** – Deployment + Service (port 3000)
- **db** – Deployment + Service (MySQL)

A régi, egypodos gyors demo (`devfile-k8s-deploy.yaml`) a `deploy-k8s-devfile-only` paranccsal elérhető marad, de az alapértelmezett deploy útvonal már nem tartalmazza.

A devfile explicit endpointtal rögzíti a `targetPort: 8080` beállítást importáláskor.

## 4) API összefoglaló

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/photos?sort=name|date&order=asc|desc`
- `POST /api/photos` (multipart/form-data: `name`, `photo`, max. 100 MB)
- `DELETE /api/photos/:id`

## 5) Megjegyzés

Ez a repository OpenShift célkörnyezetre van tisztítva; csak az OpenShift telepítéshez szükséges elemek maradtak.
