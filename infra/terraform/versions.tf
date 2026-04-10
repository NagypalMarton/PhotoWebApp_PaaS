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
      version = "~> 1.14"
    }
  }
}

provider "kubernetes" {
  host                   = var.openshift_server
  token                  = var.openshift_token
  cluster_ca_certificate = var.openshift_ca_cert
  load_config_file       = false
}

provider "kubectl" {
  host                   = var.openshift_server
  token                  = var.openshift_token
  cluster_ca_certificate = var.openshift_ca_cert
  load_config_file       = false
}
