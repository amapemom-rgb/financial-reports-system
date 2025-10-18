# Variables for Financial Reports Analysis System

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "financial-reports-ai-2024"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "github_connection" {
  description = "GitHub connection ID (OPTIONAL - only needed if Terraform manages Cloud Build triggers)"
  type        = string
  default     = null
  # Example: "projects/123456789/locations/global/connections/github-abcd1234"
  # Leave as null if managing triggers manually via Console
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "amapemom-rgb"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "financial-reports-system"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "enable_apis" {
  description = "Enable required GCP APIs automatically"
  type        = bool
  default     = true
}

variable "cloud_run_cpu" {
  description = "CPU allocation for Cloud Run services"
  type        = string
  default     = "1"
}

variable "cloud_run_memory" {
  description = "Memory allocation for Cloud Run services"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cloud_run_min_instances" {
  description = "Minimum number of Cloud Run instances (0 for scale to zero)"
  type        = number
  default     = 0
}

variable "storage_location" {
  description = "Location for Cloud Storage buckets"
  type        = string
  default     = "US"
}

variable "storage_lifecycle_days" {
  description = "Number of days before deleting old files in storage"
  type        = number
  default     = 90
}

variable "pubsub_message_retention" {
  description = "Message retention duration for Pub/Sub (in seconds)"
  type        = string
  default     = "604800" # 7 days
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Logging"
  type        = bool
  default     = true
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
  }
}

variable "gemini_model" {
  description = "Gemini model to use"
  type        = string
  default     = "gemini-1.5-pro-002"
}

variable "enable_reasoning_engine" {
  description = "Enable Vertex AI Reasoning Engine for Logic Understanding Agent"
  type        = bool
  default     = true
}

variable "reasoning_engine_location" {
  description = "Location for Reasoning Engine (must support Vertex AI)"
  type        = string
  default     = "us-central1"
}

variable "allowed_cors_origins" {
  description = "Allowed CORS origins for frontend service"
  type        = list(string)
  default     = ["*"]
}

variable "enable_authentication" {
  description = "Enable IAM authentication for Cloud Run services"
  type        = bool
  default     = true
}

variable "service_accounts" {
  description = "Service account configuration"
  type = object({
    create_service_account = bool
    service_account_name   = string
  })
  default = {
    create_service_account = true
    service_account_name   = "financial-reports-sa"
  }
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "financial-reports"
    managed_by  = "terraform"
    environment = "prod"
  }
}
