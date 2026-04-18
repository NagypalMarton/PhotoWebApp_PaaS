# TASK4 - IaC OpenShift telepites Terraformmal

## Cel

A PhotoWebApp teljes futtatasi infrastrukturajanak deklarativ kezelese OpenShift platformon Terraform hasznalataval, ugy hogy a folyamatos frissites mellett az adatbazis adatai megmaradjanak.

## Valasztott IaC eszkoz

- Terraform
- Kubernetes provider
- Kubectl provider (OpenShift Route kezeleshez)

## IaC altal kezelt eroforrasok

A Terraform a kovetkezo eroforrasokat hozza letre es kezeli:

- Namespace (projekt)
- Secret az alkalmazas es adatbazis konfiguraciohoz
- MySQL PVC + Deployment + Service
- Backend Deployment + Service
- Frontend Deployment + Service
- OpenShift Route a frontend publikalasahoz
- NetworkPolicy szabalyok (default deny ingress + explicit allow)
- Opcionisan frontend/backend HPA

Terraform forrasok helye: [infra/terraform](../../infra/terraform)

## Folyamatos frissites es adatmegorzes

Az adatbazis perzisztenciaja ket szinten van biztositva:

- A MySQL adatokat PVC tarolja (mysql-pvc).
- A PVC Terraform oldalon prevent_destroy vedelmet kapott.

Ennek eredmenye, hogy egy normal terraform apply csak a szukseges valtozasokat hajtja vegre (peldaul image frissites), es nem all elo olyan helyzet, hogy mindig uj, ures adatbazis jon letre.

## GitHub CI/CD kiegeszites

A build workflow utan automatikusan fut egy Terraform deploy workflow:

- Workflow: [.github/workflows/iac-terraform-deploy.yml](../../.github/workflows/iac-terraform-deploy.yml)
- Trigger: Build and Push Docker Hub Images workflow sikeres lefutasa utan
- Mukoedes:
  - beolvassa a GitHub secreteket
  - a friss image tagekkel futtat terraform apply-t
  - frissiti a backend/frontend deploymenteket

Szukseges GitHub secrets:

- OPENSHIFT_SERVER
- OPENSHIFT_TOKEN
- OPENSHIFT_CA_CERT
- DOCKERHUB_USERNAME
- MYSQL_PASSWORD
- MYSQL_ROOT_PASSWORD
- BACKEND_SECRET_KEY (opcionalis)
- FRONTEND_SECRET_KEY (opcionalis)

Tovabbi opcionis GitHub valtozok:

- ENABLE_HPA (alapertelmezett: true)
- DEPLOY_ROLLOUT_TIMEOUT (alapertelmezett: 180s)

## Szorgalmi: automatikus skalazodas

A Terraform implementacio tartalmazza a backend/frontend HPA eroforrasokat is (enable_hpa kapcsoloval), igy az automatikus skalazodas IaC-bol kezelheto.

## Alkalmazas

Lokalis futtatas Terraformmal:

1. [infra/terraform/terraform.tfvars.example](../../infra/terraform/terraform.tfvars.example) fajl masolasa terraform.tfvars neven
2. valtozok kitoltese
3. terraform init
4. terraform plan
5. terraform apply
