# Kubernetes Deployment - PhotoWebApp_PAAS

Ez a mappa a projekt Kubernetes-re szabott, funkcióvesztés nélküli telepítését tartalmazza.

## Mit hoz létre?

A `kubernetes/photowebapp-paas.yaml` egy több rétegű, skálázható architektúrát hoz létre:

- Namespace: `photowebapp-paas`
- Backend: `Deployment/backend` + `Service/backend`
- Frontend: `Deployment/frontend` + `Service/frontend`
- Adatbázis: `StatefulSet/mysql` + `Service/mysql`
- Ingress: `Ingress/photowebapp`
- Skálázás: `HPA` backend és frontend réteghez
- Magas rendelkezésre állás: `PDB` backend és frontend
- Hálózati szeparáció: `NetworkPolicy` (MySQL csak a backendre nyitott)

Megjegyzés: Kubernetes eroforras-nevekben nem hasznalhato az `PhotoWebApp_PAAS` forma (nagybetu/underscore). Emiatt a technikai eroforrasnevek `photowebapp-paas` alakban szerepelnek, de a `app.kubernetes.io/part-of: PhotoWebApp_PAAS` label tartalmazza a kert nevet.

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
