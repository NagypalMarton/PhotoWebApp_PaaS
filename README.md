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

## 3) OpenShift telepítés (röviden)

```bash
oc apply -f openshift/openshift-all.yaml
oc start-build photowebapp-backend --follow
oc start-build photowebapp-frontend --follow
```

Route host lekérdezése:

```bash
oc get route photowebapp -o jsonpath='{.spec.host}'
```

Részletes lépések: [openshift/README.md](openshift/README.md).

### Devfile import (egylépéses stack deploy)

A gyökérben található [devfile.yaml](devfile.yaml) importálás után az `up` parancs egy lépésben alkalmazza az összes OpenShift réteget (`openshift/openshift-all.yaml`).

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
