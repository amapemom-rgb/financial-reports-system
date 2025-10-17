output "frontend_url" {
  description = "Frontend Service URL"
  value       = module.frontend_service.service_url
}

output "orchestrator_url" {
  description = "Orchestrator Agent URL"
  value       = module.orchestrator_agent.service_url
}

output "pubsub_topic" {
  description = "Pub/Sub Topic Name"
  value       = module.pubsub.topic_name
}

output "reports_bucket" {
  description = "Reports Storage Bucket"
  value       = module.reports_storage.bucket_name
}

output "visualizations_bucket" {
  description = "Visualizations Storage Bucket"
  value       = module.visualizations_storage.bucket_name
}

output "service_account_email" {
  description = "Service Account Email"
  value       = google_service_account.cloud_run_sa.email
}
