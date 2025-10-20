# Variables for Pub/Sub module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "orchestrator_url" {
  description = "URL of the orchestrator Cloud Run service"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for Pub/Sub authentication"
  type        = string
}
