# Az automatikus skálázódás konfigurációja OpenShift PaaS környezetben

## Környezeti háttér

Az alkalmazásom OpenShift PaaS környezetben fut, azon belül a `nagypalmarton-dev` nevű projektben. A skálázás szempontjából a lényeges komponensek a frontend és a backend Deploymentek, mert ezekből több példány is futhat párhuzamosan, ha a terhelés ezt indokolja. A konfigurációt az `openshift/hpa.yaml`, a `backend/backend.yaml` és a `frontend/frontend.yaml` fájlok tartalmazzák.

## A skálázás működése

A horizontális skálázást a Kubernetes Horizontal Pod Autoscaler, röviden HPA végzi. Ebben a projektben a frontend-hpa és a backend-hpa objektumok CPU-alapú skálázást használnak. A beállítások szerint a rendszer legalább 1, legfeljebb 5 replika között működhet, tehát van egy fix felső korlát, amelynél nem indul több példány. A skálázás a CPU kihasználtság alapján történik, és a célérték 75 százalékos átlagos kihasználtság.

## Felskálázási és visszaskálázási szabályok

A felskálázásnál beállítottam egy rövid stabilizációs ablakot, amely 15 másodperc, és a rendszer ilyenkor legfeljebb 2 podot adhat hozzá 30 másodpercenként. Ez azt jelenti, hogy a skálázás nem történik túl agresszíven, mégis gyorsan tud reagálni, ha megnő a terhelés. A visszaskálázásnál hosszabb, 30 másodperces stabilizációs ablakot használtam, és ebben az esetben a rendszer legfeljebb 1 podot tud eltávolítani 60 másodpercenként. Ez azért hasznos, mert csökkenti a fölösleges ki-be skálázást, és stabilabb működést ad, amikor a terhelés ingadozik.s