terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

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
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "compute.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# Pub/Sub Topic
module "pubsub" {
  source = "./modules/pubsub"

  project_id = var.project_id
  topic_name = "task-queue-topic"
  subscription_names = [
    "orchestrator-subscription",
    "report-reader-subscription",
    "logic-agent-subscription"
  ]

  depends_on = [google_project_service.required_apis]
}

# Storage Buckets
module "reports_storage" {
  source = "./modules/storage"

  project_id    = var.project_id
  bucket_name   = "${var.project_id}-reports"
  location      = "US"
  public_access = false

  depends_on = [google_project_service.required_apis]
}

module "visualizations_storage" {
  source = "./modules/storage"

  project_id    = var.project_id
  bucket_name   = "${var.project_id}-visualizations"
  location      = "US"
  public_access = true

  depends_on = [google_project_service.required_apis]
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "financial-reports-sa"
  display_name = "Financial Reports Service Account"
  project      = var.project_id

  depends_on = [google_project_service.required_apis]
}

# IAM roles for service account
resource "google_project_iam_member" "cloud_run_sa_roles" {
  for_each = toset([
    "roles/run.invoker",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/storage.objectAdmin",
    "roles/aiplatform.user",
    "roles/secretmanager.secretAccessor"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"

  depends_on = [google_service_account.cloud_run_sa]
}

# Cloud Run Services
module "frontend_service" {
  source = "./modules/cloudrun"

  project_id            = var.project_id
  region                = var.region
  service_name          = "frontend-service"
  image                 = "${var.region}-docker.pkg.dev/${var.project_id}/financial-reports/frontend-service:latest"
  service_account_email = google_service_account.cloud_run_sa.email
  memory                = "512Mi"
  cpu                   = "1"
  max_instances         = 10
  allow_unauthenticated = true

  env_vars = {
    PROJECT_ID            = var.project_id
    REGION                = var.region
    ORCHESTRATOR_URL      = module.orchestrator_agent.service_url
    REPORT_READER_URL     = module.report_reader_agent.service_url
    LOGIC_AGENT_URL       = module.logic_agent.service_url
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.cloud_run_sa,
    google_project_iam_member.cloud_run_sa_roles
  ]
}

module "report_reader_agent" {
  source = "./modules/cloudrun"

  project_id            = var.project_id
  region                = var.region
  service_name          = "report-reader-agent"
  image                 = "${var.region}-docker.pkg.dev/${var.project_id}/financial-reports/report-reader-agent:latest"
  service_account_email = google_service_account.cloud_run_sa.email
  memory                = "1Gi"
  cpu                   = "2"
  max_instances         = 20
  allow_unauthenticated = false

  env_vars = {
    PROJECT_ID = var.project_id
    REGION     = var.region
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.cloud_run_sa,
    google_project_iam_member.cloud_run_sa_roles
  ]
}

module "logic_agent" {
  source = "./modules/cloudrun"

  project_id            = var.project_id
  region                = var.region
  service_name          = "logic-understanding-agent"
  image                 = "${var.region}-docker.pkg.dev/${var.project_id}/financial-reports/logic-understanding-agent:latest"
  service_account_email = google_service_account.cloud_run_sa.email
  memory                = "2Gi"
  cpu                   = "2"
  max_instances         = 10
  timeout               = 600
  allow_unauthenticated = false

  env_vars = {
    PROJECT_ID = var.project_id
    REGION     = var.region
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.cloud_run_sa,
    google_project_iam_member.cloud_run_sa_roles
  ]
}

module "visualization_agent" {
  source = "./modules/cloudrun"

  project_id            = var.project_id
  region                = var.region
  service_name          = "visualization-agent"
  image                 = "${var.region}-docker.pkg.dev/${var.project_id}/financial-reports/visualization-agent:latest"
  service_account_email = google_service_account.cloud_run_sa.email
  memory                = "1Gi"
  cpu                   = "2"
  max_instances         = 15
  allow_unauthenticated = false

  env_vars = {
    PROJECT_ID      = var.project_id
    REGION          = var.region
    STORAGE_BUCKET  = module.visualizations_storage.bucket_name
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.cloud_run_sa,
    google_project_iam_member.cloud_run_sa_roles,
    module.visualizations_storage
  ]
}

module "orchestrator_agent" {
  source = "./modules/cloudrun"

  project_id            = var.project_id
  region                = var.region
  service_name          = "orchestrator-agent"
  image                 = "${var.region}-docker.pkg.dev/${var.project_id}/financial-reports/orchestrator-agent:latest"
  service_account_email = google_service_account.cloud_run_sa.email
  memory                = "1Gi"
  cpu                   = "2"
  max_instances         = 10
  timeout               = 900
  allow_unauthenticated = false

  env_vars = {
    PROJECT_ID           = var.project_id
    REGION               = var.region
    PUBSUB_TOPIC         = module.pubsub.topic_name
    REPORT_READER_URL    = module.report_reader_agent.service_url
    LOGIC_AGENT_URL      = module.logic_agent.service_url
    VISUALIZATION_URL    = module.visualization_agent.service_url
    DATABASE_URL         = "sqlite:///./orchestrator.db" # TODO: Change to Cloud SQL
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.cloud_run_sa,
    google_project_iam_member.cloud_run_sa_roles,
    module.pubsub
  ]
}
