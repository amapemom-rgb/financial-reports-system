# Web UI Cloud Run Service
resource "google_cloud_run_service" "web_ui" {
  name     = "web-ui"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/web-ui:latest"
        
        ports {
          container_port = 8080
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "NODE_ENV"
          value = "production"
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"      = "10"
        "autoscaling.knative.dev/minScale"      = "1"
        "run.googleapis.com/client-name"        = "terraform"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  lifecycle {
    ignore_changes = [
      template[0].metadata[0].annotations["run.googleapis.com/client-name"],
      template[0].metadata[0].annotations["run.googleapis.com/client-version"],
    ]
  }
}

# Make Web UI publicly accessible (no authentication required)
resource "google_cloud_run_service_iam_member" "web_ui_public" {
  service  = google_cloud_run_service.web_ui.name
  location = google_cloud_run_service.web_ui.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the Web UI URL
output "web_ui_url" {
  value       = google_cloud_run_service.web_ui.status[0].url
  description = "URL of the Web UI"
}
