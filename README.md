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

A gyökérben található [devfile.yaml](devfile.yaml) importálás után az alapértelmezett `deploy` parancs a Kubernetes mintadeployt (`openshift/devfile-k8s-deploy.yaml`) alkalmazza, így a Devfile importáló biztosan talál `Deployment` erőforrást.

Az OpenShift teljes stack (`openshift/openshift-all.yaml`) továbbra is elérhető a `deploy-openshift-stack` paranccsal.

A devfile explicit endpointtal rögzíti a `targetPort: 8080` beállítást importáláskor.

A telepítés előtt futtasd a `scripts/generate-secrets.sh` szkriptet, hogy a `CHANGE_ME_*` placeholder értékek valódi titkokra legyenek cserélve. Részletekért lásd: [openshift/README.md](openshift/README.md).

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
