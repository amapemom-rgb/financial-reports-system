# Cloud Build Trigger for Web UI
resource "google_cloudbuild_trigger" "web_ui_trigger" {
  name        = "web-ui-deploy-trigger"
  description = "Automatically deploy Web UI on push to main"
  project     = var.project_id

  github {
    owner = "amapemom-rgb"
    name  = "financial-reports-system"
    
    push {
      branch = "^main$"
    }
  }

  included_files = [
    "web-ui/**"
  ]

  filename = "web-ui/cloudbuild.yaml"

  substitutions = {
    _DEPLOY_REGION = var.region
  }
}

output "trigger_id" {
  description = "ID of the Cloud Build trigger"
  value       = google_cloudbuild_trigger.web_ui_trigger.id
}
