# TASK4 - IaC OpenShift telepites Terraformmal

A TASK4 feladatban a PhotoWebApp OpenShiftes telepiteset Infrastructure-as-Code szemleletben, Terraform hasznalataval valositottam meg. A megoldas celja az volt, hogy az alkalmazas infrastrukturaja deklarativ modon legyen leirva, es a kesobbi frissitesek ne jarjanak az adatbazis elvesztesevel.

A munkamenetben a Terraformot hasznaltam fobb IaC eszkozkent, a Kubernetes providert a klaszteren beluli eroforrasok kezelesere, a Kubectl providert pedig az OpenShift Route letrehozasahoz. Az igy konfiguralt komponensek a kovetkezok: namespace, Secret, MySQL adatbazis PVC-vel, backend es frontend Deployment es Service, frontend Route, network policy szabalyok, valamint az opcionis HPA.

Az adatbazis perzisztenciajat PVC biztositja, a Terraform oldalon pedig prevent_destroy vedelem van beallitva, hogy egy kesobbi apply ne torolje le veletlenul a MySQL tarolot. Emiatt a rendszer megfelel annak a kovetelmenynek, hogy a szoftver folyamatosan frissitheto maradjon, mikozben az adatbazis tartalma megmarad.

## IaC altal kezelt eroforrasok

A Terraform a kovetkezo eroforrasokat kezeli:

- namespace (projekt)
- Secret az alkalmazas es az adatbazis konfiguraciojahoz
- MySQL PVC, Deployment es Service
- backend Deployment es Service
- frontend Deployment es Service
- OpenShift Route a frontend publikalasahoz
- network policy szabalyok
- opcionis backend es frontend HPA

Az IaC forrasok helye: [infra/terraform](../../infra/terraform)

## Folyamatos frissites es adatmegorzes

A MySQL adatok PVC-n tarolodnak, a PVC pedig Terraform oldalon prevent_destroy vedelmet kapott. Ennek eredmenyekent egy normal terraform apply csak a szukseges valtozasokat hajtja vegre, peldaul image frissitest, es nem hoz letre minden alkalommal uj, ures adatbazist.

## GitHub CI/CD kiegeszites

A build workflow utan egy kulon Terraform deploy workflow is lefut automatikusan. Ez a folyamat a friss image tagekkel elinditja a terraform apply muveletet, majd frissiti a backend es frontend deploymenteket.

Szukseges GitHub secrets:

- OPENSHIFT_SERVER
- OPENSHIFT_TOKEN
- DOCKERHUB_USERNAME
- MYSQL_PASSWORD
- MYSQL_ROOT_PASSWORD

## HPA es autoscaling

A Terraform implementacio tartalmazza a backend es frontend HPA eroforrasokat is, ezert az automatikus skalazodas is IaC-bol kezelheto. Az autoscaling CPU kihasznaltsag alapjan mukodik, 1 es 5 replika kozotti tartomanyban. A skala feltetele, hogy a Deploymentekben meg legyen adva a CPU request ertek, mert enelkul az HPA nem tud megbizhatoan donteni a novekedesrol vagy a visszaskalazasrol. A workflow a Terraform futtatasakor az `ENABLE_HPA` valtozo alapjan kapcsolja be vagy ki ezt a funkciot.
