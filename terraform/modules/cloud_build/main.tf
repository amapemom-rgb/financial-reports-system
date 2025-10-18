# Cloud Build Triggers Module
# Creates automated build triggers for each microservice

locals {
  # Define all microservices
  services = {
    frontend = {
      name          = "frontend-service"
      description   = "Frontend Service - Main API gateway"
      path_filter   = "services/frontend-service/**"
      cloudbuild    = "services/frontend-service/cloudbuild.yaml"
    }
    orchestrator = {
      name          = "orchestrator-agent"
      description   = "Orchestrator Agent - Task coordination"
      path_filter   = "services/orchestrator-agent/**"
      cloudbuild    = "services/orchestrator-agent/cloudbuild.yaml"
    }
    report_reader = {
      name          = "report-reader-agent"
      description   = "Report Reader Agent - File parsing"
      path_filter   = "services/report-reader-agent/**"
      cloudbuild    = "services/report-reader-agent/cloudbuild.yaml"
    }
    logic_understanding = {
      name          = "logic-understanding-agent"
      description   = "Logic Understanding Agent - AI analysis with Reasoning Engine"
      path_filter   = "services/logic-understanding-agent/**"
      cloudbuild    = "services/logic-understanding-agent/cloudbuild.yaml"
    }
    visualization = {
      name          = "visualization-agent"
      description   = "Visualization Agent - Chart generation"
      path_filter   = "services/visualization-agent/**"
      cloudbuild    = "services/visualization-agent/cloudbuild.yaml"
    }
  }
}

# Cloud Build triggers for each service
resource "google_cloudbuild_trigger" "service_triggers" {
  for_each = local.services

  name        = "${each.value.name}-deploy"
  description = "Auto-deploy ${each.value.description} on push to main"
  location    = var.region

  # GitHub configuration using existing connection
  github {
    owner = var.github_owner
    name  = var.github_repo
    
    push {
      branch = "^main$"
    }
  }

  # Only trigger on changes to this service
  included_files = [each.value.path_filter]

  # Use the cloudbuild.yaml from the service directory
  filename = each.value.cloudbuild

  # Substitutions for build
  substitutions = {
    _SERVICE_NAME    = each.value.name
    _REGION          = var.region
    _ARTIFACT_REPO   = var.artifact_repo_name
    _PROJECT_ID      = var.project_id
  }

  tags = [
    "service:${each.value.name}",
    "managed-by:terraform",
    "auto-deploy"
  ]
}

# Service account for Cloud Build
resource "google_service_account" "cloudbuild_sa" {
  account_id   = "cloudbuild-deploy-sa"
  display_name = "Cloud Build Service Account"
  description  = "Service account for Cloud Build to deploy to Cloud Run"
}

# Grant Cloud Build SA permissions to deploy to Cloud Run
resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}

# Grant Cloud Build SA permissions to use service accounts
resource "google_project_iam_member" "cloudbuild_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}

# Grant Cloud Build SA permissions to push to Artifact Registry
resource "google_project_iam_member" "cloudbuild_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}

# Grant Cloud Build SA permissions to read from Storage
resource "google_project_iam_member" "cloudbuild_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}

# Grant Cloud Build SA logging permissions
resource "google_project_iam_member" "cloudbuild_logs_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloudbuild_sa.email}"
}
