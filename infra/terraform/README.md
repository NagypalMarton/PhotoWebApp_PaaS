# Terraform IaC deployment for OpenShift

This folder contains Infrastructure-as-Code definitions for deploying the full PhotoWebApp runtime on OpenShift:

- namespace
- secrets
- dedicated service accounts for backend/frontend/mysql
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

By default `manage_namespace = false`, so Terraform deploys into an existing namespace (`var.namespace`) without trying to create it. This works with namespace-scoped tokens.

Set `manage_namespace = true` only if the token has cluster-level permissions to create/manage namespaces.

## OpenShift token permissions

The token used by Terraform must have namespace-scoped write permissions in `var.namespace`.

Minimum required resource permissions include create/update/get/list/watch on:

- serviceaccounts
- secrets
- services
- deployments.apps
- persistentvolumeclaims
- networkpolicies.networking.k8s.io
- horizontalpodautoscalers.autoscaling
- routes.route.openshift.io

If Terraform fails with `Unauthorized`, the token is valid but does not have enough RBAC rights for one or more resources.

## Local usage

```bash
terraform init
terraform plan
terraform apply
```

## GitHub Actions usage

The workflow `.github/workflows/iac-terraform-deploy.yml` runs Terraform automatically after image build and push.

The workflow uses Terraform Cloud remote state (with locking) via the `cloud` block in `versions.tf`.

Required GitHub repository settings:

- Secret: `TF_API_TOKEN`
- Variable: `DEPLOY_ROLLOUT_TIMEOUT` (optional, default: `180s`)
- Secret: `BACKEND_SECRET_KEY` (optional)
- Secret: `FRONTEND_SECRET_KEY` (optional)
- Variable: `ENABLE_HPA` (optional, default: `true`)

The organization and workspace are hardcoded in `versions.tf` (`cloud` block):

- Organization: `CloudBased_PhotoApp_PaaS`
- Workspace: `photowebapp-openshift`

To change organization or workspace names, edit `versions.tf`.
