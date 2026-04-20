# TASK4 - IaC OpenShift telepites Terraformmal

Ebben a feladatban a PhotoWebApp OpenShiftes futtatasat Infrastructure-as-Code szemleletben, Terraform hasznalataval valositottam meg. A munkam fo celja az volt, hogy az addig inkabb kezi es YAML-fajlokra epulo telepitest olyan deklarativ formara vigyem at, amely konnyen ujrafuttathato, atlathato, es hosszu tavon is fenntarthato. Emellett kulon figyelmet kaptam arra, hogy az alkalmazas frissitese ne veszelyeztesse a MySQL adatbazisban tarolt adatokat.

A terraformos forrasok az [infra/terraform](../../infra/terraform) mappaban talalhatok. A konfiguracio a Kubernetes providerre epul, a random provider pedig a biztonsagi kulcsok generalasanal segit. A state kezeleset Terraform Cloud vegzi, ami a gyakorlatban azt jelenti, hogy kozponti allapotfajlt es lockolast kap a projekt, igy csokken az egyideju futtatasbol adodo hibak eselye. A jelenlegi beallitas szerint a cloud organization neve CloudBased_PhotoApp_PaaS, a workspace pedig photowebapp-openshift.

## Mit kezel jelenleg az IaC megoldas

A Terraform a futtatashoz szukseges fo eroforrasokat deklarativan leirja. Ide tartozik az opcionalisan kezelt namespace, a harom dedikalt service account (backend, frontend, mysql), az alkalmazas secretek, a MySQL perzisztens tarolasa PVC-vel, valamint a backend es frontend deployment + service paros. Emellett a konfiguracio network policy szabalyokat is letrehoz, amelyekkel celzottan korlatozhato a komponensek kozotti halo zati forgalom. Az autoscaling funkcio szinten IaC-bol kapcsolhato, azaz a backend es frontend HPA eroforrasai az enable_hpa valtozotol fuggoen jonnek letre.

Fontos gyakorlati reszlet, hogy a frontend OpenShift Route jelenleg nem Terraform eroforraskent szerepel, hanem a CI/CD workflow egy kulon kubectl apply lepese hozza letre. Ennek oka, hogy a korabbi provider alapu route-kezeles RBAC szempontbol tobb kornyezetben problemat okozott, mig a workflow-bol torteno explicit letrehozas stabilabban mukodott.

## Perzisztencia es adatmegorzes

Az adatmegorzes kovetelmenyet a MySQL PVC-re epitettem. A mysql-pvc eroforrasnal lifecycle.prevent_destroy vedelem van beallitva, ezert egy szokasos terraform apply nem fogja torolni az adatokat tartalmazo kotetet. Gyakorlatban ez azt jelenti, hogy image-frissites vagy egyeb alkalmazasszintu valtozas eseten a rendszer in-place frissul, mikozben az adatbazis tartalma megmarad. Ez a megoldas kulcsfontossagu volt a feladat azon reszehez, hogy a szoftver folyamatosan frissitheto legyen adatvesztes nelkul.

## CI/CD integracio es deploy folyamat

A telepitesi folyamatot a [iac-terraform-deploy workflow](../../.github/workflows/iac-terraform-deploy.yml) automatizalja. A workflow ketfelekeppen indithato: egyreszt automatikusan, amikor a Docker image build/push workflow sikeresen lefut, masreszt manualisan workflow_dispatch eseten, ahol opcionalisan kulon image tag is megadhato.

A pipeline a gyakorlatban tobb lepcsoben ellenoriz es telepit. Eloszor validalja a szukseges secretek jelenletet, majd ellenorzi, hogy a backend es frontend image valoban elerheto-e a Docker Hubon. Ezutan lefut a terraform init es validate, majd kubectl alapon megtortenik az OpenShift API es RBAC preflight vizsgalat. A workflow tartalmaz stale ReplicaSet takaritast is quota-kimeles miatt, utana fut a terraform apply. A deploy vegen a pipeline letrehozza (vagy ha mar letezik, erintetlenul hagyja) a frontend Route-ot, majd rollout, PVC, HPA es route allapotot is verifikal.

## Szukseges GitHub beallitasok

A workflow futtatasahoz kotelezoen be kell allitani az OPENSHIFT_SERVER, OPENSHIFT_TOKEN, OPENSHIFT_CA_CERT, DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, TF_API_TOKEN, MYSQL_PASSWORD es MYSQL_ROOT_PASSWORD secreteket. Opcionalisan adhatok meg BACKEND_SECRET_KEY es FRONTEND_SECRET_KEY ertekeket is; ha ezek hianyoznak, a Terraform random kulcsot general. A repository valtozok kozul jellemzoen az OPENSHIFT_NAMESPACE, ENABLE_HPA es DEPLOY_ROLLOUT_TIMEOUT parametereket erdemes testre szabni, de ezek alapertelmezett ertekkel is mukodokepesek.

## HPA es uzemeltetesi megfontolasok

Az autoscaling CPU alapon mukodik, 1 es 5 replika kozotti tartomanyban, 75%-os celkihasznaltsaggal. A deploymentekben beallitott CPU request ertekek segitik, hogy a HPA megbizhato meresek alapjan dontson a fel- vagy visszaskalazasrol. Uzemeltetesi oldalrol plusz vedelmet ad, hogy a podok dedikalt service accounttal futnak, a service account token automount tiltott, valamint a network policy default deny ingress szemleletet kovet.

## Osszegzes

Osszessegeben a TASK4 soran egy olyan IaC-alapu OpenShift telepitesi megoldast sikerult kialakitanom, amely egyszerre tamogatja a reprodukalhato deploymentet, a CI/CD integraciot es az adatmegorzest. A Terraformos megkozelites miatt az infrastruktura valtozasai nyomon kovethetok es kontrollaltan alkalmazhatok, mikozben a rendszer frissitese a gyakorlatban is biztonsagosabb lett.
