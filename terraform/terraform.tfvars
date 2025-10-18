# Terraform Variables for Financial Reports Analysis System

# ===== REQUIRED: Project Configuration =====

# Your GCP Project ID
project_id = "financial-reports-ai-2024"

# GCP region for resources
region = "us-central1"

# ===== GitHub Connection (OPTIONAL) =====
# Cloud Build triggers are managed manually via Console
# Uncommenting this would enable Terraform to manage triggers
# github_connection = "projects/YOUR_PROJECT_NUMBER/locations/global/connections/github-YOUR_CONNECTION_ID"

# ===== OPTIONAL: Customize if needed =====

# GitHub repository details (for documentation purposes)
github_owner = "amapemom-rgb"
github_repo  = "financial-reports-system"

# Environment name
environment = "prod"

# Cloud Run configuration
cloud_run_cpu           = "1"
cloud_run_memory        = "512Mi"
cloud_run_max_instances = 10
cloud_run_min_instances = 0

# Storage configuration
storage_location       = "US"
storage_lifecycle_days = 90

# Pub/Sub configuration
pubsub_message_retention = "604800" # 7 days in seconds

# Logging and monitoring
enable_monitoring = true
log_level        = "INFO"

# AI/ML configuration
gemini_model              = "gemini-1.5-pro-002"
enable_reasoning_engine   = true
reasoning_engine_location = "us-central1"

# Security configuration
enable_authentication = true
allowed_cors_origins  = ["*"]

# Service account configuration
service_accounts = {
  create_service_account = true
  service_account_name   = "financial-reports-sa"
}

# Resource labels
labels = {
  project     = "financial-reports"
  managed_by  = "terraform"
  environment = "prod"
  team        = "data-engineering"
}
