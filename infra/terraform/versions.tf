terraform {
  required_version = ">= 1.6.0"

  cloud {
    organization = "CloudBased_PhotoApp_PaaS"

    workspaces {
      name = "photowebapp-openshift"
    }
  }

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31"
    }
    kubectl = {
      source  = "alekc/kubectl"
      version = "~> 2.2"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

locals {
  use_insecure_tls = trimspace(var.openshift_ca_cert) == ""
}

provider "kubernetes" {
  host                   = var.openshift_server
  token                  = var.openshift_token
  cluster_ca_certificate = local.use_insecure_tls ? null : var.openshift_ca_cert
  insecure               = local.use_insecure_tls
  load_config_file       = false
}

provider "kubectl" {
  host                   = var.openshift_server
  token                  = var.openshift_token
  cluster_ca_certificate = local.use_insecure_tls ? null : var.openshift_ca_cert
  insecure               = local.use_insecure_tls
  load_config_file       = false
}
