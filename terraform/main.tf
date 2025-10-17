# Financial Reports Analysis System - Main Terraform Configuration
# This file orchestrates all modules and creates the complete infrastructure

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for state storage
  backend "gcs" {
    bucket = "financial-reports-terraform-state"
    prefix = "terraform/state"
  }
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "pubsub.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
  ])
  
  service            = each.key
  disable_on_destroy = false
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "financial-reports"
  description   = "Docker repository for Financial Reports System microservices"
  format        = "DOCKER"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Storage module for file storage
module "storage" {
  source = "./modules/storage"
  
  project_id = var.project_id
  region     = var.region
  
  depends_on = [google_project_service.required_apis]
}

# Pub/Sub module for async messaging
module "pubsub" {
  source = "./modules/pubsub"
  
  project_id = var.project_id
  
  depends_on = [google_project_service.required_apis]
}

# IAM module for service accounts and permissions
module "iam" {
  source = "./modules/iam"
  
  project_id = var.project_id
  region     = var.region
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Build triggers module
module "cloud_build" {
  source = "./modules/cloud_build"
  
  project_id         = var.project_id
  region             = var.region
  github_connection  = var.github_connection
  github_owner       = var.github_owner
  github_repo        = var.github_repo
  artifact_repo_name = google_artifact_registry_repository.docker_repo.name
  
  depends_on = [
    google_project_service.required_apis,
    google_artifact_registry_repository.docker_repo
  ]
}

# Cloud Run services module
module "cloud_run" {
  source = "./modules/cloud_run"
  
  project_id            = var.project_id
  region                = var.region
  artifact_repo_name    = google_artifact_registry_repository.docker_repo.name
  service_account_email = module.iam.service_account_email
  
  # Environment variables for services
  env_vars = {
    PROJECT_ID                = var.project_id
    REGION                    = var.region
    REPORTS_BUCKET           = module.storage.reports_bucket_name
    TASKS_TOPIC              = module.pubsub.tasks_topic_name
    RESULTS_TOPIC            = module.pubsub.results_topic_name
    ORCHESTRATOR_URL         = "" # Will be populated after first deploy
    REPORT_READER_URL        = ""
    LOGIC_UNDERSTANDING_URL  = ""
    VISUALIZATION_URL        = ""
  }
  
  depends_on = [
    google_project_service.required_apis,
    module.iam,
    module.storage,
    module.pubsub,
    module.cloud_build
  ]
}

# Update service environment variables with actual URLs (requires second apply)
resource "null_resource" "update_service_urls" {
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      # This will be executed after Cloud Run services are deployed
      echo "Cloud Run services deployed. URLs:"
      echo "Frontend: ${module.cloud_run.frontend_url}"
      echo "Orchestrator: ${module.cloud_run.orchestrator_url}"
      echo "Report Reader: ${module.cloud_run.report_reader_url}"
      echo "Logic Understanding: ${module.cloud_run.logic_understanding_url}"
      echo "Visualization: ${module.cloud_run.visualization_url}"
    EOT
  }
  
  depends_on = [module.cloud_run]
}
