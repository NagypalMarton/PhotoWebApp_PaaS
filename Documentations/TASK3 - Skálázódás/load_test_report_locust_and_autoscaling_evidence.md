# Terheléspróba jegyzőkönyv - Locust és az automatikus felskálázódás bizonyítéka

## A mérés célja

Ennek a terheléspróbának az volt a célja, hogy igazolja: az alkalmazás nagy terhelés alatt képes automatikusan felskálázódni, majd amikor a terhelés csökken, vissza is tud skálázódni az eredeti állapothoz közeli értékre. A vizsgálatot Locust eszközzel végeztem el, OpenShift környezetben, a backend API-t célozva. A terhelést a `locust/locustfile.py` fájl írja le, a cél host pedig a `http://backend:5001` cím volt.

## A terhelés beállítása

A méréshez példaként 60 felhasználót és 10-es spawn rate-et használtam, a futási idő pedig körülbelül 5 perc volt. Ez elég ahhoz, hogy látható legyen a rendszer viselkedése terhelés alatt, ugyanakkor nem túl hosszú ahhoz, hogy a teszt kezelhetetlenné váljon.

## A terhelés által lefedett funkciók

A terheléspróba lefedte az alkalmazás fő funkcióit is. A Locust szkript először regisztrációt végez, majd bejelentkezik, ezután különféle módokon lekéri a fotólistát rendezéssel együtt, például dátum és név szerint, növekvő és csökkenő sorrendben is. Ezen felül a teszt feltölt képet, lekéri egy kép metaadatait, megnyitja a képfájlt, végül pedig saját fotót is töröl. Így a mérés nem csak egyetlen végpontot terhel, hanem a rendszer több fontos működési pontját is lefedi.

## A mérés menete

A mérés menete a gyakorlatban úgy nézett ki, hogy először rögzítettem a kiinduló állapotot az `oc get hpa` és az `oc get deploy frontend backend` parancsokkal. Ezután elindítottam a Locust terhelést a webes felületen. A terhelés futása közben ismét ellenőriztem a HPA állapotát és a Deploymentek replika számát, valamint az OpenShift felületén az Observe -> Horizontal Pod Autoscalers nézetet is figyeltem. Miután leállítottam a terhelést, megint megnéztem a Deploymentek állapotát, hogy látható legyen a visszaskálázódás is.

## A dokumentálandó bizonyítékok

A jegyzőkönyvben érdemes mellékelni a Locust statisztika oldalának képernyőképét, mert azon látszik a kérésarány, a válaszidő és az esetleges hibaarány is. Ugyanígy fontos a HPA nézetről készült kép terhelés alatt, valamint a Deploymentek replika számának dokumentálása terhelés közben és terhelés után. Ezek mellett a `oc get hpa` és `oc get deploy frontend backend` parancsok kimenete is hasznos bizonyíték, mert ezek pontosan megmutatják, hogyan változott a rendszer állapota időben.
