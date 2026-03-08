# Kubernetes Deployment - PhotoWebApp_PaaS

**Fontos:** A deployment neve legyen egyedi és informatív, ne csak "PhotoWebApp". Példák:
- photowebapp-backend
- photowebapp-frontend
- photowebapp-db
- photowebapp-uploads

Ez segít azonosítani a komponenseket és elkerülni a névütközéseket.

Ez a mappa a projekt Kubernetes-re szabott, funkcióvesztés nélküli telepítését tartalmazza.

## Mit hoz létre?

Az `kubernetes/photowebapp-paas.yaml` egy több rétegű, skálázható architektúrát hoz létre, ahol minden deployment neve egyedi:

* Namespace: `photowebapp-paas`
* Backend: `Deployment/photowebapp-backend` + `Service/photowebapp-backend`
* Frontend: `Deployment/photowebapp-frontend` + `Service/photowebapp-frontend`
* Adatbázis: `StatefulSet/photowebapp-db` + `Service/photowebapp-db`
* Ingress: `Ingress/photowebapp-frontend`
- Skálázás: `HPA` backend és frontend réteghez
- Magas rendelkezésre állás: `PDB` backend és frontend
- Hálózati szeparáció: `NetworkPolicy` (MySQL csak a backendre nyitott)

Megjegyzés: Kubernetes erőforrás-nevekben nem használható az `PhotoWebApp_PAAS` forma (nagybetű/underscore). Emiatt a technikai erőforrásnevek `photowebapp-paas` alakban szerepelnek, de a `app.kubernetes.io/part-of: PhotoWebApp_PAAS` label tartalmazza a kért nevet. A deployment neve minden komponensnél egyedi (pl. photowebapp-backend).

## Előfeltételek

- Működő Kubernetes cluster
- Ingress Controller (pl. NGINX Ingress)
- Metrics Server (HPA működéséhez)
- Olyan StorageClass, amely támogatja:
  - `ReadWriteOnce` (MySQL)
  - `ReadWriteMany` (uploads, backend skálázhatósághoz)

## Telepítés

```bash
kubectl apply -f kubernetes/photowebapp-paas.yaml
```

## Gyors ellenőrzés

```bash
kubectl get all -n photowebapp-paas
kubectl get ingress -n photowebapp-paas
kubectl get hpa -n photowebapp-paas
```

## Host név

Az alap Ingress host: `photowebapp.local`.
A helyi teszthez add a hosts fájlhoz az ingress IP-t ezzel a névvel, vagy módosítsd a hostot a manifestben.

## Titkok cseréje

Telepítés előtt erősen ajánlott átírni a következő Secret mezőket:

- `CHANGE_ME_STRONG_APP_SECRET`
- `CHANGE_ME_STRONG_DB_PASSWORD`
- `CHANGE_ME_STRONG_ROOT_PASSWORD`
