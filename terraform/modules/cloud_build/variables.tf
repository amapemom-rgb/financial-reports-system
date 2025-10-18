# Variables for Cloud Build module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "github_connection" {
  description = "GitHub connection ID (created manually)"
  type        = string
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "artifact_repo_name" {
  description = "Artifact Registry repository name"
  type        = string
}
