variable "openshift_server" {
  description = "OpenShift API URL"
  type        = string
}

variable "openshift_token" {
  description = "OpenShift API token"
  type        = string
  sensitive   = true
}

variable "openshift_ca_cert" {
  description = "OpenShift cluster CA cert in PEM format (optional when using insecure TLS mode)"
  type        = string
  default     = ""
}

variable "namespace" {
  description = "Target namespace"
  type        = string
  default     = "photowebapp"
}

variable "mysql_database" {
  description = "MySQL database name"
  type        = string
  default     = "photowebapp"
}

variable "mysql_user" {
  description = "MySQL application user"
  type        = string
  default     = "photouser"
}

variable "mysql_password" {
  description = "MySQL application password"
  type        = string
  sensitive   = true
}

variable "mysql_root_password" {
  description = "MySQL root password"
  type        = string
  sensitive   = true
}

variable "backend_secret_key" {
  description = "Flask secret key for backend (optional; random value generated when empty)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "frontend_secret_key" {
  description = "Flask secret key for frontend (optional; random value generated when empty)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "backend_image" {
  description = "Backend image reference (for example docker.io/org/image:tag)"
  type        = string
}

variable "frontend_image" {
  description = "Frontend image reference (for example docker.io/org/image:tag)"
  type        = string
}

variable "mysql_image" {
  description = "MySQL image reference"
  type        = string
  default     = "registry.access.redhat.com/rhscl/mysql-80-rhel7"
}

variable "mysql_storage_size" {
  description = "Persistent storage size for MySQL"
  type        = string
  default     = "5Gi"
}

variable "enable_hpa" {
  description = "Whether to create backend/frontend HPAs"
  type        = bool
  default     = true
}
