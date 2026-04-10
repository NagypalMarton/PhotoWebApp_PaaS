# Terraform IaC deployment for OpenShift

This folder contains Infrastructure-as-Code definitions for deploying the full PhotoWebApp runtime on OpenShift:

- namespace
- secrets
- persistent MySQL database (PVC + Deployment + Service)
- backend and frontend deployments with services
- OpenShift Route for frontend
- ingress network policies
- optional horizontal pod autoscalers

## Why this meets the persistence requirement

MySQL data is stored on a PVC (`mysql-pvc`) and the PVC has `prevent_destroy = true`. Running Terraform apply updates workloads in place and does not recreate the database volume.

## Required variables

The OpenShift API connection and application secrets are passed through Terraform variables.

Use the example file:

1. copy `terraform.tfvars.example` to `terraform.tfvars`
2. fill in real credentials and secrets
3. run Terraform from this directory

## Local usage

```bash
terraform init
terraform plan
terraform apply
```

## GitHub Actions usage

The workflow `.github/workflows/iac-terraform-deploy.yml` runs Terraform automatically after image build and push.

The workflow uses Terraform Cloud remote state (with locking), so these repository settings are required:

- Secret: `TF_API_TOKEN`
- Variable: `TF_ORGANIZATION`
- Variable: `TF_WORKSPACE` (optional, default: `photowebapp-openshift`)
- Variable: `DEPLOY_ROLLOUT_TIMEOUT` (optional, default: `180s`)
