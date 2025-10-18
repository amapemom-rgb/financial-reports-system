# Outputs for Cloud Build module

output "trigger_ids" {
  description = "Map of service names to Cloud Build trigger IDs"
  value = {
    for k, v in google_cloudbuild_trigger.service_triggers : k => v.id
  }
}

output "trigger_names" {
  description = "Map of service names to Cloud Build trigger names"
  value = {
    for k, v in google_cloudbuild_trigger.service_triggers : k => v.name
  }
}

output "cloudbuild_service_account" {
  description = "Cloud Build service account email"
  value       = google_service_account.cloudbuild_sa.email
}
