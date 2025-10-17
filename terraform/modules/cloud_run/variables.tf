# Variables for Cloud Run module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "artifact_repo_name" {
  description = "Artifact Registry repository name"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for Cloud Run services"
  type        = string
}

variable "env_vars" {
  description = "Environment variables for all services"
  type        = map(string)
  default     = {}
}
