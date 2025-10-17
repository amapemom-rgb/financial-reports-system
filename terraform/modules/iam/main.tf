# IAM Module
# Creates service accounts and IAM policies

# Service account for all microservices
resource "google_service_account" "microservices_sa" {
  account_id   = "financial-reports-sa"
  display_name = "Financial Reports Microservices Service Account"
  description  = "Service account for all Financial Reports microservices"
}

# Grant service account access to Cloud Storage
resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account access to Pub/Sub
resource "google_project_iam_member" "sa_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

resource "google_project_iam_member" "sa_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account access to Vertex AI
resource "google_project_iam_member" "sa_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account access to call other Cloud Run services
resource "google_project_iam_member" "sa_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account logging permissions
resource "google_project_iam_member" "sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account monitoring permissions
resource "google_project_iam_member" "sa_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account Cloud Trace permissions
resource "google_project_iam_member" "sa_trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}

# Grant service account Secret Manager access (for API keys, etc.)
resource "google_project_iam_member" "sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.microservices_sa.email}"
}
